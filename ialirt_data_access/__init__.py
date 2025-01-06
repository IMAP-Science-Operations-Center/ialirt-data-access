"""Data Access for I-ALiRT.

This package contains the data access tools for the I-ALiRT logs.
Provides a convenient way to query and download log files.
"""

import os

from ialirt_data_access.io import download, query

__all__ = [
    "query",
    "download",
]
__version__ = "0.1.0"


config = {
    "DATA_ACCESS_URL": os.getenv("IALIRT_DATA_ACCESS_URL")
    or "https://ialirt.dev.imap-mission.com",
}
"""Settings configuration dictionary.

DATA_ACCESS_URL : This is the URL of the data access API.
"""
