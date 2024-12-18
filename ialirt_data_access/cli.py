#!/usr/bin/env python3

"""Command line interface to query the IALIRT log API.

Usage:
    ialirt_data_access --debug --url <url> ialirt-log-query --year <year> --doy <doy> --instance <instance>
"""

import argparse
import logging

import ialirt_data_access


def _query_parser(args: argparse.Namespace):
    """Query the IALIRT log API.

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
        print(query_results)
    except ialirt_data_access.io.IALIRTDataAccessError as e:
        print(e)
        return


def main():
    """Parse the command line arguments.

    Run the command line interface to the IALIRT Data Access API.
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

    # Query command
    subparsers = parser.add_subparsers(required=True)
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

    # Parse the arguments and set the values
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    if args.url:
        # We got an explicit url from the command line
        ialirt_data_access.config["DATA_ACCESS_URL"] = args.url

    # Now process through the respective function for the invoked command
    # (set with set_defaults on the subparsers above)
    args.func(args)


if __name__ == "__main__":
    main()
