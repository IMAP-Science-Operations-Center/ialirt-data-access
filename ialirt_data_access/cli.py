#!/usr/bin/env python3

"""Command line interface to query IALIRT database and query/download directories in s3.

Usage:
    ialirt-data-access --debug --url <url> ialirt-log-query
    --year <year> --doy <doy> --instance <instance>

    ialirt-data-access --url <url> ialirt-packet-query
    --year 2025 --doy 148 --hh 16 --mm 24

    ialirt-data-access --debug --url <url> ialirt-download
    --filename <filename> --downloads_dir <downloads_dir>

    ialirt-data-access --debug --url <url> ialirt-db-query
    --met_start <met_start> --met_end <met_end>
"""

import argparse
import logging
from pathlib import Path

import ialirt_data_access

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _download_parser(args: argparse.Namespace):
    """Download an I-ALiRT log.

    Parameters
    ----------
    args : argparse.Namespace
        An object containing the parsed arguments and their values
    """
    try:
        ialirt_data_access.download(args.filename, args.filetype, args.downloads_dir)
    except ialirt_data_access.io.IALIRTDataAccessError as e:
        print(e)


def _log_query_parser(args: argparse.Namespace):
    """Query the I-ALiRT log API.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments including year, doy, and instance.

    Returns
    -------
    None
    """
    query_params = {
        "year": args.year,
        "doy": args.doy,
        "instance": args.instance,
    }
    # Remove any keys with None values.
    query_params = {k: v for k, v in query_params.items() if v is not None}
    try:
        query_results = ialirt_data_access.log_query(**query_params)
        logger.info("Query results: %s", query_results)
        print(query_results)
    except ialirt_data_access.io.IALIRTDataAccessError as e:
        logger.error("An error occurred: %s", e)
        print(e)


def _packet_query_parser(args: argparse.Namespace):
    """Query the I-ALiRT packet API.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments including year, doy, hh, mm, ss.

    Returns
    -------
    None
    """
    query_params = {
        "year": args.year,
        "doy": args.doy,
        "hh": args.hh,
        "mm": args.mm,
        "ss": args.ss,
    }
    # Remove any keys with None values.
    query_params = {k: v for k, v in query_params.items() if v is not None}
    try:
        query_results = ialirt_data_access.packet_query(**query_params)
        logger.info("Query results: %s", query_results)
        print(query_results)
    except ialirt_data_access.io.IALIRTDataAccessError as e:
        logger.error("An error occurred: %s", e)
        print(e)
    except ValueError as e:
        logger.error("Invalid input: %s", e)
        print(e)


def _data_product_query_parser(args: argparse.Namespace):
    """Query the I-ALiRT Algorithm DynamoDB.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed arguments.

    Returns
    -------
    None
    """
    query_params = {
        "met_start": args.met_start,
        "met_end": args.met_end,
        "met_in_utc_start": args.met_in_utc_start,
        "met_in_utc_end": args.met_in_utc_end,
        "last_modified_start": args.last_modified_start,
        "last_modified_end": args.last_modified_end,
    }
    # Remove any keys with None values.
    query_params = {k: v for k, v in query_params.items() if v is not None}
    try:
        query_results = ialirt_data_access.data_product_query(**query_params)
        logger.info("Query results: %s", query_results)
        print(query_results)
    except Exception as e:
        logger.error("An error occurred: %s", e)
        print(f"Error: {e}")


def main():
    """Parse the command line arguments.

    Run the command line interface to the I-ALiRT Data Access API.
    """
    url_help = (
        "URL of the IALIRT API. "
        "The default is https://ialirt.dev.imap-mission.com. This can also be "
        "set using the IALIRT_DATA_ACCESS_URL environment variable."
    )

    parser = argparse.ArgumentParser(prog="ialirt-data-access")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {ialirt_data_access.__version__}",
    )
    parser.add_argument("--url", type=str, required=False, help=url_help)
    # Logging level
    parser.add_argument(
        "--vv",
        "--debug",
        help="Print lots of debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Add verbose output",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    subparsers = parser.add_subparsers(required=True)

    # Log query command
    log_query_parser = subparsers.add_parser("ialirt-log-query")
    log_query_parser.add_argument(
        "--year", type=str, required=True, help="Year of the logs (e.g., 2024)."
    )
    log_query_parser.add_argument(
        "--doy", type=str, required=True, help="Day of year of the logs (e.g., 045)."
    )
    log_query_parser.add_argument(
        "--instance",
        type=str,
        required=True,
        help="Instance number (e.g., 1).",
        choices=[
            "1",
            "2",
        ],
    )
    log_query_parser.set_defaults(func=_log_query_parser)

    # Packet query command
    packet_query_parser = subparsers.add_parser("ialirt-packet-query")
    packet_query_parser.add_argument(
        "--year", type=str, required=True, help="Year of the packet (e.g., 2025)."
    )
    packet_query_parser.add_argument(
        "--doy", type=str, required=True, help="Day of year of the packet (e.g., 148)."
    )
    packet_query_parser.add_argument(
        "--hh", type=str, required=False, help="Hour (0 to 23)."
    )
    packet_query_parser.add_argument(
        "--mm", type=str, required=False, help="Minute (0 to 59)."
    )
    packet_query_parser.add_argument(
        "--ss", type=str, required=False, help="Second (0 to 59)."
    )
    packet_query_parser.set_defaults(func=_packet_query_parser)

    # Download command
    download_parser = subparsers.add_parser("ialirt-download")
    download_parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="Example: flight_iois.log.YYYY-DOYTHH:MM:SS.ssssss",
    )
    download_parser.add_argument(
        "--filetype",
        type=str,
        choices=["logs", "packets", "archive"],
        required=True,
        help="Filetype: logs, packets, or archive",
    )
    download_parser.add_argument(
        "--downloads_dir",
        type=Path,
        required=False,
        help="Example: /path/to/downloads/dir",
    )
    download_parser.set_defaults(func=_download_parser)

    # Query DB command
    db_query_parser = subparsers.add_parser("ialirt-db-query")
    db_query_parser.add_argument(
        "--met_start", type=int, required=False, help="Start of mission elapsed time."
    )
    db_query_parser.add_argument(
        "--met_end", type=int, required=False, help="End of mission elapsed time."
    )
    db_query_parser.add_argument(
        "--met_in_utc_start", type=str, required=False, help="Start of met time in utc."
    )
    db_query_parser.add_argument(
        "--met_in_utc_end", type=str, required=False, help="End of met time in utc."
    )
    db_query_parser.add_argument(
        "--last_modified_start",
        type=str,
        required=False,
        help="Start of last_modified time.",
    )
    db_query_parser.add_argument(
        "--last_modified_end",
        type=str,
        required=False,
        help="End of last_modified time.",
    )
    db_query_parser.set_defaults(func=_data_product_query_parser)

    # Parse the arguments and set the values
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    if args.url:
        # Explicit url from the command line
        ialirt_data_access.config["DATA_ACCESS_URL"] = args.url

    args.func(args)


if __name__ == "__main__":
    main()
