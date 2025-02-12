"""Tests for the ``io`` module."""

from __future__ import annotations

import json
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import pytest

import ialirt_data_access


@pytest.fixture()
def mock_urlopen():
    """Mock urlopen to return a file-like object."""
    mock_data = b"Mock file content"
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = mock_data
        yield mock_urlopen


def _set_mock_data(mock_urlopen: unittest.mock.MagicMock, data: bytes):
    """Set the data returned by the mock urlopen."""
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = data


def test_request_errors(mock_urlopen: unittest.mock.MagicMock):
    """Test that invalid URLs raise an appropriate HTTPError or URLError."""
    # Set up the mock to raise an HTTPError
    mock_urlopen.side_effect = HTTPError(
        url="http://example.com", code=404, msg="Not Found", hdrs={}, fp=BytesIO()
    )
    query_params = {"year": "2024", "doy": "045", "instance": "1"}
    with pytest.raises(ialirt_data_access.io.IALIRTDataAccessError, match="HTTP Error"):
        ialirt_data_access.query(**query_params)

    # Set up the mock to raise an URLError
    mock_urlopen.side_effect = URLError(reason="Not Found")
    mock_urlopen.side_effect = URLError(reason="Not Found")
    with pytest.raises(ialirt_data_access.io.IALIRTDataAccessError, match="URL Error"):
        ialirt_data_access.query(**query_params)


def test_query(mock_urlopen: unittest.mock.MagicMock):
    """Test a basic call to the Query API."""
    filename = "flight_iois_1.log.2024-045T16-54-46_123456.txt"
    query_params = {"year": "2024", "doy": "045", "instance": "1"}
    _set_mock_data(mock_urlopen, json.dumps([filename]).encode("utf-8"))
    response = ialirt_data_access.query(**query_params)
    assert response == ["flight_iois_1.log.2024-045T16-54-46_123456.txt"]

    # Should have only been one call to urlopen
    mock_urlopen.assert_called_once()
    # Assert that the correct URL was used for the query
    urlopen_call = mock_urlopen.mock_calls[0].args[0]
    called_url = urlopen_call.full_url
    expected_url_encoded = (
        f"https://ialirt.test.com/ialirt-log-query?{urlencode(query_params)}"
    )
    assert called_url == expected_url_encoded


def test_query_bad_params(mock_urlopen: unittest.mock.MagicMock):
    """Test a call to the Query API that has invalid parameters."""
    with pytest.raises(
        TypeError, match="got an unexpected keyword argument 'bad_param'"
    ):
        ialirt_data_access.query(bad_param="test")

    assert mock_urlopen.call_count == 0


def test_download(mock_urlopen: unittest.mock.MagicMock, tmp_path: Path):
    """Test the download function."""
    filename = "flight_iois_1.log.2024-045T16-54-46_123456.txt"
    downloaded_file = ialirt_data_access.download(filename, downloads_dir=tmp_path)

    # Assert that the file was created
    assert downloaded_file.exists()

    # Verify the file was saved to the correct location
    expected_path = tmp_path / filename
    assert downloaded_file == expected_path

    # Verify that the file contains the expected content
    with open(downloaded_file, "rb") as f:
        assert f.read() == b"Mock file content"

    # Check that urlopen was called with the correct URL
    mock_urlopen.assert_called_once()
    urlopen_call = mock_urlopen.mock_calls[0].args[0]
    called_url = urlopen_call.full_url
    expected_url = f"https://ialirt.test.com/ialirt-log-download/logs/{filename}"
    assert called_url == expected_url
    assert urlopen_call.method == "GET"


def test_download_already_exists(mock_urlopen: unittest.mock.MagicMock, tmp_path: Path):
    """Test that downloading a file that already exists does not make any requests."""
    filename = "flight_iois_1.log.2024-045T16-54-46_123456.txt"

    # Set up the destination and create the file
    downloads_dir = tmp_path / "Downloads"
    destination = downloads_dir / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.touch(exist_ok=True)

    result = ialirt_data_access.download(filename, downloads_dir=downloads_dir)
    assert result == destination
    # Assert no HTTP request was made
    assert mock_urlopen.call_count == 0


def test_algorithm_query(mock_urlopen: unittest.mock.MagicMock):
    """Test a basic call to the algorithm query API with multiple query parameters."""
    query_params = {
        "met_start": "100",
        "met_end": "130",
        "product_name": "codicelo_product_1",
    }
    # Test that algorithm_query correctly retrieves, decodes, and returns the JSON data
    expected_response = [{"result": "data"}]
    _set_mock_data(mock_urlopen, json.dumps(expected_response).encode("utf-8"))

    response = ialirt_data_access.algorithm_query(
        met_start="100", met_end="130", product_name="codicelo_product_1"
    )
    assert response == expected_response

    # Should have only been one call to urlopen
    mock_urlopen.assert_called_once()

    urlopen_call = mock_urlopen.mock_calls[0].args[0]
    expected_query = urlencode(query_params)
    expected_url = f"https://ialirt.test.com/ialirt-db-query/query?{expected_query}"
    assert urlopen_call.full_url == expected_url
