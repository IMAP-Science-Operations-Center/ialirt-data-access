"""The ``io`` module."""

import contextlib
import json
import logging
import urllib.request
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

import ialirt_data_access

logger = logging.getLogger(__name__)


class IALIRTDataAccessError(Exception):
    """Base class for exceptions in this module."""

    pass


@contextlib.contextmanager
def _get_url_response(request: urllib.request.Request):
    """Get the response from a URL request.

    This is a helper function to make it easier to handle
    the different types of errors that can occur when
    opening a URL and write out the response body.
    """
    try:
        # Open the URL and yield the response
        with urllib.request.urlopen(request) as response:
            yield response

    except HTTPError as e:
        message = (
            f"HTTP Error: {e.code} - {e.reason}\n"
            f"Server Message: {e.read().decode('utf-8')}"
        )
        raise IALIRTDataAccessError(message) from e
    except URLError as e:
        message = f"URL Error: {e.reason}"
        raise IALIRTDataAccessError(message) from e


def _validate_query_params(year: str, doy: str, instance: str):
    """Validate the query parameters for the IALIRT log API.

    Parameters
    ----------
    year : str
        Year, must be a 4-digit string (e.g., '2024').
    doy : str
        Day of year, must be a string between '001' and '365'.
    instance : str
        Instance number, must be either '1' or '2'.

    Raises
    ------
    ValueError
        If any parameter is invalid.
    """
    if not (year.isdigit() and len(year) == 4):
        raise ValueError("Year must be a 4-digit string (e.g., '2024').")
    if not (doy.isdigit() and 1 <= int(doy) <= 366):
        raise ValueError("DOY must be a string between '001' and '365'.")
    if instance not in {"1", "2"}:
        raise ValueError("Instance must be '1' or '2'.")


def query(*, year: str, doy: str, instance: str) -> list[str]:
    """Query the logs.

    Parameters
    ----------
    year : str
        Year
    doy : str
        Day of year
    instance : str
        Instance number

    Returns
    -------
    list
        List of files matching the query
    """
    query_params = {
        "year": year,
        "doy": doy,
        "instance": instance,
    }
    _validate_query_params(**query_params)

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/ialirt-log-query?{urlencode(query_params)}"

    logger.info("Querying for %s with url %s", query_params, url)
    request = urllib.request.Request(url, method="GET")
    with _get_url_response(request) as response:
        # Retrieve the response as a list of files
        items = response.read().decode("utf-8")
        logger.debug("Received response: %s", items)
        # Decode the JSON string into a list
        items = json.loads(items)
        logger.debug("Decoded JSON: %s", items)
    return items


def download(filename: str, downloads_dir: Optional[Path] = None) -> Path:
    """Download the logs.

    Parameters
    ----------
    filename : str
        Filename
    downloads_dir : Path
        Directory to save the file

    Returns
    -------
    destination: pathlib.Path
        Path to the downloaded file
    """
    if downloads_dir is None:
        downloads_dir = Path.home() / "Downloads"

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/ialirt-log-download/logs/{filename}"

    downloads_dir.mkdir(parents=True, exist_ok=True)
    destination = downloads_dir / filename

    if destination.exists():
        logger.info("File already exists: %s", destination)
        return destination

    logger.info("Downloading %s with url %s", filename, url)
    request = urllib.request.Request(url, method="GET")
    with _get_url_response(request) as response:
        logger.debug("Received response: %s", response)
        with open(destination, "wb") as local_file:
            local_file.write(response.read())
            print(f"Successfully downloaded the file to: {destination}")

    return destination


def data_product_query(
    *,
    met_start: Optional[str] = None,
    met_end: Optional[str] = None,
    insert_time_start: Optional[str] = None,
    insert_time_end: Optional[str] = None,
    product_name: Optional[str] = None,
) -> list:
    """Query the algorithm API endpoint.

    This function constructs a URL using the base URL from
    `ialirt_data_access.config` and sends a GET request with the provided
    query parameters. For example, calling:

        data_product_query(met_start="100")

    will send a GET request to:

        https://ialirt.dev.imap-mission.com/ialirt-db-query/query?met_start=100

    Parameters
    ----------
    met_start : Optional[str]
        Start of MET filter.
    met_end : Optional[str]
        End of MET filter.
    insert_time_start : Optional[str]
        Start of insert_time filter.
    insert_time_end : Optional[str]
        End of insert_time filter.
    product_name : Optional[str]
        Filter on product name. If ending with '*', the backend treats it
        as a prefix search.

    Returns
    -------
    list
        List of items returned by the algorithm query endpoint.
    """
    query_params = {}
    if met_start is not None:
        query_params["met_start"] = met_start
    if met_end is not None:
        query_params["met_end"] = met_end
    if insert_time_start is not None:
        query_params["insert_time_start"] = insert_time_start
    if insert_time_end is not None:
        query_params["insert_time_end"] = insert_time_end
    if product_name is not None:
        query_params["product_name"] = product_name

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/ialirt-db-query/query?{urlencode(query_params)}"

    logger.info("Algorithm query: GET %s", url)
    request = urllib.request.Request(url, method="GET")
    with _get_url_response(request) as response:
        items = response.read().decode("utf-8")
        logger.debug("Algorithm query response: %s", items)
        items = json.loads(items)
    return items
