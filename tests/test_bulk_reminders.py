import os
import subprocess
import sys
from importlib import import_module
from unittest.mock import patch

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def get_module():
    sys.path.insert(0, ".")
    return import_module("bulk-reminders".replace("-", "_"))

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


def test_validate_csv_valid_file():
    """validate_csv should return valid rows and no errors for good CSV."""
    bulk_reminders = get_module()
    valid_rows, errors = bulk_reminders.validate_csv(os.path.join(FIXTURES, "valid.csv"))

    assert len(valid_rows) == 3
    assert len(errors) == 0
    assert valid_rows[0]["title"] == "Buy groceries"
    assert valid_rows[0]["due_date"] == "2026-03-02 10:00"
    assert valid_rows[1]["due_date"] is None  # Empty due_date
    assert valid_rows[2]["title"] == "Meeting, prep"  # Comma in title


def test_validate_csv_invalid_date():
    """validate_csv should report invalid date formats."""
    bulk_reminders = get_module()
    valid_rows, errors = bulk_reminders.validate_csv(os.path.join(FIXTURES, "invalid_date.csv"))

    assert len(valid_rows) == 1  # Only the valid row
    assert len(errors) == 1
    assert "row 2" in errors[0].lower() or "row 3" in errors[0].lower()
    assert "date" in errors[0].lower()


def test_validate_csv_missing_title():
    """validate_csv should report empty titles."""
    bulk_reminders = get_module()
    valid_rows, errors = bulk_reminders.validate_csv(os.path.join(FIXTURES, "missing_title.csv"))

    assert len(valid_rows) == 1
    assert len(errors) == 1
    assert "title" in errors[0].lower()


def test_validate_csv_wrong_headers():
    """validate_csv should show helpful error for wrong column names."""
    bulk_reminders = get_module()
    valid_rows, errors = bulk_reminders.validate_csv(os.path.join(FIXTURES, "wrong_headers.csv"))

    assert len(valid_rows) == 0
    assert len(errors) == 1
    # Error should mention what was found
    assert "Title" in errors[0] or "found" in errors[0].lower()
    # Error should mention expected format
    assert "title,due_date,notes" in errors[0].lower() or "expected" in errors[0].lower()


def test_prompt_list_selection_with_default():
    """prompt_list_selection should return first list on empty input."""
    bulk_reminders = get_module()
    lists = ["Reminders", "Work", "Shopping"]

    with patch("builtins.input", return_value=""):
        result = bulk_reminders.prompt_list_selection(lists)

    assert result == "Reminders"


def test_prompt_list_selection_with_number():
    """prompt_list_selection should return selected list by number."""
    bulk_reminders = get_module()
    lists = ["Reminders", "Work", "Shopping"]

    with patch("builtins.input", return_value="2"):
        result = bulk_reminders.prompt_list_selection(lists)

    assert result == "Work"


def test_prompt_list_selection_invalid_then_valid():
    """prompt_list_selection should re-prompt on invalid input."""
    bulk_reminders = get_module()
    lists = ["Reminders", "Work"]

    with patch("builtins.input", side_effect=["99", "abc", "1"]):
        result = bulk_reminders.prompt_list_selection(lists)

    assert result == "Reminders"


def test_escape_applescript_string():
    """escape_applescript_string should escape quotes and backslashes."""
    bulk_reminders = get_module()

    assert bulk_reminders.escape_applescript_string('hello') == 'hello'
    assert bulk_reminders.escape_applescript_string('say "hi"') == 'say \\"hi\\"'
    assert bulk_reminders.escape_applescript_string('back\\slash') == 'back\\\\slash'
    assert bulk_reminders.escape_applescript_string('both "and" \\') == 'both \\"and\\" \\\\'


def test_build_applescript_basic():
    """build_applescript should generate valid AppleScript."""
    bulk_reminders = get_module()

    reminders = [
        {"title": "Test item", "due_date": "2026-03-02 10:00", "notes": "some notes"},
        {"title": "No date", "due_date": None, "notes": None},
    ]

    script = bulk_reminders.build_applescript("Work", reminders)

    assert 'tell list "Work"' in script
    assert 'name:"Test item"' in script
    assert 'body:"some notes"' in script
    assert 'name:"No date"' in script

    # Date should be built explicitly (not string parsing) to avoid locale issues
    # Must set each component: year, month, day, hours, minutes, seconds
    assert 'set year of d to 2026' in script
    assert 'set month of d to 3' in script
    assert 'set day of d to 2' in script
    assert 'set hours of d to 10' in script
    assert 'set minutes of d to 0' in script
    assert 'set seconds of d to 0' in script
    assert 'due date:d' in script

    # Should NOT use string-based date parsing (locale-dependent, causes bugs)
    assert 'date "2026-03-02 10:00"' not in script

    # Second item should not have due date property
    lines = script.split("\n")
    no_date_line = [l for l in lines if 'name:"No date"' in l][0]
    assert "due date:" not in no_date_line
