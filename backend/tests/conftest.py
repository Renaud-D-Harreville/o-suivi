"""
Global test configuration.

Sets DATA_DIR environment variable to tests/resources/data/ so that
tests never touch the production data/ folder.
"""

import json
import os
import shutil
from pathlib import Path

# --- Set DATA_DIR env var BEFORE any app module is imported ---
_TEST_DATA_DIR = Path(__file__).resolve().parent / "resources" / "data"
os.environ["DATA_DIR"] = str(_TEST_DATA_DIR)

import pytest  # noqa: E402

# Minimal organizer user for tests
_TEST_USERS = [
    {
        "id": "usr_001",
        "username": "renaud",
        "password": "arvik",
        "role": "organizer",
    }
]


@pytest.fixture(autouse=True)
def _reset_data_between_tests():
    """Clean templates and events before each test, restore users.json."""
    templates_dir = _TEST_DATA_DIR / "templates"
    events_dir = _TEST_DATA_DIR / "events"
    users_file = _TEST_DATA_DIR / "users.json"

    # Clean
    if templates_dir.exists():
        shutil.rmtree(templates_dir)
    templates_dir.mkdir(parents=True, exist_ok=True)

    if events_dir.exists():
        shutil.rmtree(events_dir)
    events_dir.mkdir(parents=True, exist_ok=True)

    # Restore users.json to a clean state
    users_file.write_text(json.dumps(_TEST_USERS, indent=2))

    yield

    # Restore users.json after test (in case test modified it)
    users_file.write_text(json.dumps(_TEST_USERS, indent=2))
