"""Global pytest configuration for package."""

import pytest

import ialirt_data_access


@pytest.fixture(autouse=True)
def _set_global_config(monkeypatch: pytest.fixture):
    """Set the test url."""
    monkeypatch.setitem(
        ialirt_data_access.config, "DATA_ACCESS_URL", "https://ialirt.test.com"
    )
