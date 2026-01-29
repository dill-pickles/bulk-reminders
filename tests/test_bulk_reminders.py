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


def test_dry_run_progress_shows_incremental_counts():
    """Dry run should show progress as [1/N], [2/N], etc., not [N/N] for all."""
    result = subprocess.run(
        [sys.executable, "bulk-reminders", "add",
         os.path.join(FIXTURES, "valid.csv"),
         "--dry-run", "--list", "Reminders"],
        capture_output=True,
        text=True
    )

    # Should show incremental progress: [1/3], [2/3], [3/3]
    assert "[1/3]" in result.stdout
    assert "[2/3]" in result.stdout
    assert "[3/3]" in result.stdout


def test_add_shows_results_after_batch_not_fake_progress():
    """Non-dry-run should show results after batch, not misleading progress before."""
    import io
    from contextlib import redirect_stdout
    from argparse import Namespace

    bulk_reminders = get_module()

    # Mock add_reminders to avoid actual AppleScript call
    with patch.object(bulk_reminders, 'add_reminders', return_value=(3, [])) as mock_add, \
         patch.object(bulk_reminders, 'get_reminder_lists', return_value=['Reminders', 'Work']), \
         patch.object(bulk_reminders, 'validate_csv', return_value=([
             {"title": "Item 1", "due_date": "2026-03-02 10:00", "notes": ""},
             {"title": "Item 2", "due_date": None, "notes": ""},
             {"title": "Item 3", "due_date": "2026-03-15 14:30", "notes": ""},
         ], [])):

        args = Namespace(
            csv_file="test.csv",
            list_name="Reminders",
            dry_run=False
        )

        output = io.StringIO()
        with redirect_stdout(output):
            bulk_reminders.cmd_add(args)

        stdout = output.getvalue()

        # Should show each item with result marker (✓ or ✗) ONCE
        # Count occurrences of progress markers
        count_1 = stdout.count("[1/3]")
        count_2 = stdout.count("[2/3]")
        count_3 = stdout.count("[3/3]")

        # Each should appear exactly once (in the results section)
        assert count_1 == 1, f"[1/3] appeared {count_1} times, expected 1"
        assert count_2 == 1, f"[2/3] appeared {count_2} times, expected 1"
        assert count_3 == 1, f"[3/3] appeared {count_3} times, expected 1"

        # Results should show success markers
        assert "✓" in stdout or "✗" in stdout


def test_spinner_starts_and_stops():
    """Spinner should start and stop without errors."""
    import time
    bulk_reminders = get_module()

    spinner = bulk_reminders.Spinner("Testing...")
    spinner.start()
    time.sleep(0.15)  # Let it cycle at least once
    spinner.stop()

    # Spinner should have cleaned up (thread joined)
    assert spinner._stop.is_set()
    assert not spinner._thread.is_alive()
