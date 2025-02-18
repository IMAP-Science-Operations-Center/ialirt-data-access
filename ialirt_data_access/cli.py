#!/usr/bin/env python3

"""Command line interface to query IALIRT database and logs in the s3 bucket.

Usage:
    ialirt-data-access --debug --url <url> ialirt-log-query
    --year <year> --doy <doy> --instance <instance>

    ialirt-data-access --debug --url <url> ialirt-log-download
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
        ialirt_data_access.download(args.filename, args.downloads_dir)
    except ialirt_data_access.io.IALIRTDataAccessError as e:
        print(e)


def _query_parser(args: argparse.Namespace):
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
    try:
        query_results = ialirt_data_access.query(**query_params)
        logger.info("Query results: %s", query_results)
        print(query_results)
    except ialirt_data_access.io.IALIRTDataAccessError as e:
        logger.error("An error occurred: %s", e)
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
        "insert_time_start": args.insert_time_start,
        "insert_time_end": args.insert_time_end,
        "product_name": args.product_name,
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

    # Query command
    query_parser = subparsers.add_parser("ialirt-log-query")
    query_parser.add_argument(
        "--year", type=str, required=True, help="Year of the logs (e.g., 2024)."
    )
    query_parser.add_argument(
        "--doy", type=str, required=True, help="Day of year of the logs (e.g., 045)."
    )
    query_parser.add_argument(
        "--instance",
        type=str,
        required=True,
        help="Instance number (e.g., 1).",
        choices=[
            "1",
            "2",
        ],
    )
    query_parser.set_defaults(func=_query_parser)

    # Download command
    download_parser = subparsers.add_parser("ialirt-log-download")
    download_parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="Example: flight_iois.log.YYYY-DOYTHH:MM:SS.ssssss",
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
        "--insert_time_start", type=str, required=False, help="Start of insert time."
    )
    db_query_parser.add_argument(
        "--insert_time_end", type=str, required=False, help="End of insert time."
    )
    # TODO: Point help to valid options.
    db_query_parser.add_argument(
        "--product_name", type=str, required=False, help="Product name."
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
