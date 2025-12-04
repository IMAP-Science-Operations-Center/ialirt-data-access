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
    api_key = ialirt_data_access.config.get("API_KEY")
    if api_key:
        request.headers["x-api-key"] = api_key

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


def _validate_query_params(  # noqa: PLR0913
    year: str,
    doy: str,
    instance: Optional[str] = "1",
    hh: Optional[str] = None,
    mm: Optional[str] = None,
    ss: Optional[str] = None,
):
    """Validate the query parameters for the IALIRT API.

    Parameters
    ----------
    year : str
        Year, must be a 4-digit string (e.g., '2024').
    doy : str
        Day of year, must be a string between '001' and '366'.
    instance : str, optional
        Instance number, must be either '1' or '2'.
    hh : str, optional
        Hour of day, 00 to 23.
    mm : str, optional
        Minute, 00 to 59.
    ss : str, optional
        Second, 00 to 59.

    Raises
    ------
    ValueError
        If any parameter is invalid.
    """
    if not (year.isdigit() and len(year) == 4):
        raise ValueError("Year must be a 4-digit string (e.g., '2024').")
    if not (doy.isdigit() and 1 <= int(doy) <= 366):
        raise ValueError("DOY must be a string between '001' and '366'.")
    if instance not in {"1", "2"}:
        raise ValueError("Instance must be '1' or '2'.")

    if hh is not None and (not hh.isdigit() or not 0 <= int(hh) <= 23):
        raise ValueError("Hour must be a string between '00' and '23'.")
    if mm is not None and (not mm.isdigit() or not 0 <= int(mm) <= 59):
        raise ValueError("Minute must be a string between '00' and '59'.")
    if ss is not None and (not ss.isdigit() or not 0 <= int(ss) <= 59):
        raise ValueError("Second must be a string between '00' and '59'.")


def log_query(*, year: str, doy: str, instance: str) -> list[str]:
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


def packet_query(
    *,
    year: str,
    doy: str,
    hh: Optional[str] = None,
    mm: Optional[str] = None,
    ss: Optional[str] = None,
) -> list[str]:
    """Query the I-ALiRT packet files by partial datetime.

    Parameters
    ----------
    year : str
        Year, e.g., '2025'
    doy : str
        Day of year, e.g., '148'
    hh : str, optional
        Hour of day, 0 to 23
    mm : str, optional
        Minute, 0 to 59
    ss : str, optional
        Second, 0 to 59

    Returns
    -------
    list of str
        Matching packet file names.
    """
    query_params = {"year": year, "doy": doy}

    if hh:
        query_params["hh"] = hh
    if mm:
        query_params["mm"] = mm
    if ss:
        query_params["ss"] = ss

    _validate_query_params(**query_params)

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/ialirt-packet-query?{urlencode(query_params)}"

    logger.info("Querying packets for %s with url %s", query_params, url)
    request = urllib.request.Request(url, method="GET")
    with _get_url_response(request) as response:
        items = response.read().decode("utf-8")
        logger.debug("Packet query response: %s", items)
        items = json.loads(items)

    return items


def download(
    filename: str, filetype: str, downloads_dir: Optional[Path] = None
) -> Path:
    """Download the logs.

    Parameters
    ----------
    filename : str
        Filename
    filetype : str
        Filetype
    downloads_dir : Path
        Directory to save the file

    Returns
    -------
    destination: pathlib.Path
        Path to the downloaded file
    """
    if downloads_dir is None:
        downloads_dir = Path.home() / "Downloads" / filetype

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/ialirt-download/{filetype}/{filename}"

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
    instrument: Optional[str] = None,
    time_utc_start: Optional[str] = None,
    time_utc_end: Optional[str] = None,
    met_in_utc_start: Optional[str] = None,
    met_in_utc_end: Optional[str] = None,
) -> list:
    """Query the algorithm API endpoint.

    This function constructs a URL using the base URL from
    `ialirt_data_access.config` and sends a GET request with the provided
    query parameters. For example, calling:

        data_product_query(instrument="mag", time_utc_start="2025-11-22T05:30:00")

    will send a GET request to:

        https://ialirt.imap-mission.com/api-key/space-weather?instrument=mag&time_utc_start=2025-11-22T05:30:00

    Parameters
    ----------
    instrument : Optional[str]
        Instrument to query. Options include:
        "hit", "mag", "codice_lo", "codice_hi", "swapi", "swe",
        "spice", "<instrument>_hk", "spacecraft".
    time_utc_start : Optional[str]
        Start of utc_time filter.
    time_utc_end : Optional[str]
        End of utc_time filter.
    met_in_utc_start : Optional[str]
        Start of utc_time filter.
    met_in_utc_end : Optional[str]
        End of utc_time filter.

    Returns
    -------
    list
        List of items returned by the algorithm query endpoint.
    """
    query_params = {}
    if instrument is not None:
        query_params["instrument"] = instrument
    if time_utc_start is not None:
        query_params["time_utc_start"] = time_utc_start
    if time_utc_end is not None:
        query_params["time_utc_end"] = time_utc_end
    if met_in_utc_start is not None:
        query_params["met_in_utc_start"] = met_in_utc_start
    if met_in_utc_end is not None:
        query_params["met_in_utc_end"] = met_in_utc_end

    url = f"{ialirt_data_access.config['DATA_ACCESS_URL']}"
    url += f"/space-weather?{urlencode(query_params)}"

    logger.info("Algorithm query: GET %s", url)
    request = urllib.request.Request(url, method="GET")
    with _get_url_response(request) as response:
        items = response.read().decode("utf-8")
        logger.debug("Algorithm query response: %s", items)
        items = json.loads(items)

    return items
