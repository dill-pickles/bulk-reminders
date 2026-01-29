import subprocess
import sys

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
