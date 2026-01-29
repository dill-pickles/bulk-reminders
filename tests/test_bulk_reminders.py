import subprocess
import sys
from importlib import import_module

def test_cli_no_args_shows_usage():
    """CLI with no args should show usage and exit non-zero."""
    result = subprocess.run(
        [sys.executable, "bulk-reminders"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "usage:" in result.stderr.lower()

def test_cli_lists_command_exists():
    """CLI should accept 'lists' command."""
    result = subprocess.run(
        [sys.executable, "bulk-reminders", "lists", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0

def test_cli_add_command_requires_csv():
    """CLI 'add' command should require a CSV file argument."""
    result = subprocess.run(
        [sys.executable, "bulk-reminders", "add"],
        capture_output=True,
        text=True
    )
    assert result.returncode != 0
    assert "csv_file" in result.stderr.lower() or "required" in result.stderr.lower()


def test_get_reminder_lists_returns_list():
    """get_reminder_lists should return a list of strings."""
    # Import after file exists
    sys.path.insert(0, ".")
    bulk_reminders = import_module("bulk-reminders".replace("-", "_"))

    # This test requires Reminders app access - will fail in CI
    # but validates the function signature and basic behavior
    result = bulk_reminders.get_reminder_lists()
    assert isinstance(result, list)
    # macOS always has at least one default list
    assert len(result) >= 1
    assert all(isinstance(name, str) for name in result)
