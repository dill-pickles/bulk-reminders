# Bulk Reminders CLI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that bulk adds reminders to Apple Reminders from a CSV file.

**Architecture:** Single-file Python script using argparse for CLI, stdlib csv for parsing, and subprocess to call osascript for AppleScript integration. All reminders batched into a single AppleScript call for performance.

**Tech Stack:** Python 3 (stdlib only), AppleScript via osascript

---

### Task 1: Project Setup & CLI Skeleton

**Files:**
- Create: `bulk-reminders` (executable Python script)
- Create: `tests/test_bulk_reminders.py`

**Step 1: Write the failing test for CLI argument parsing**

```python
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
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_bulk_reminders.py -v`
Expected: FAIL (file not found or import error)

**Step 3: Write minimal CLI skeleton**

```python
#!/usr/bin/env python3
"""Bulk add reminders to Apple Reminders from a CSV file."""

import argparse
import sys


def cmd_lists(args):
    """List available Reminders lists."""
    pass


def cmd_add(args):
    """Add reminders from CSV file."""
    pass


def main():
    parser = argparse.ArgumentParser(
        prog="bulk-reminders",
        description="Bulk add reminders to Apple Reminders from a CSV file."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # lists command
    subparsers.add_parser("lists", help="Show available Reminders lists")

    # add command
    add_parser = subparsers.add_parser("add", help="Add reminders from CSV file")
    add_parser.add_argument("csv_file", help="Path to CSV file")
    add_parser.add_argument("--list", dest="list_name", help="Target Reminders list")
    add_parser.add_argument("--dry-run", action="store_true", help="Preview without adding")

    args = parser.parse_args()

    if args.command == "lists":
        cmd_lists(args)
    elif args.command == "add":
        cmd_add(args)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_bulk_reminders.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add bulk-reminders tests/test_bulk_reminders.py
git commit -m "feat: add CLI skeleton with argparse"
```

---

### Task 2: AppleScript Integration - Get Lists

**Files:**
- Modify: `bulk-reminders`
- Modify: `tests/test_bulk_reminders.py`

**Step 1: Write the failing test for get_reminder_lists**

Add to `tests/test_bulk_reminders.py`:

```python
def test_get_reminder_lists_returns_list():
    """get_reminder_lists should return a list of strings."""
    # Import after file exists
    sys.path.insert(0, ".")
    from importlib import import_module
    bulk_reminders = import_module("bulk-reminders".replace("-", "_"))

    # This test requires Reminders app access - will fail in CI
    # but validates the function signature and basic behavior
    result = bulk_reminders.get_reminder_lists()
    assert isinstance(result, list)
    # macOS always has at least one default list
    assert len(result) >= 1
    assert all(isinstance(name, str) for name in result)
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_bulk_reminders.py::test_get_reminder_lists_returns_list -v`
Expected: FAIL (function not defined or import error)

**Step 3: Implement get_reminder_lists**

Add to `bulk-reminders` before `cmd_lists`:

```python
import subprocess


def get_reminder_lists():
    """Get all available Reminders list names via AppleScript."""
    script = 'tell application "Reminders" to get name of every list'
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error getting lists: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    # AppleScript returns comma-separated list
    raw = result.stdout.strip()
    if not raw:
        return []
    return [name.strip() for name in raw.split(", ")]
```

Update `cmd_lists`:

```python
def cmd_lists(args):
    """List available Reminders lists."""
    lists = get_reminder_lists()
    print("Available lists:")
    for i, name in enumerate(lists, 1):
        print(f"  {i}. {name}")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_bulk_reminders.py::test_get_reminder_lists_returns_list -v`
Expected: PASS (may prompt for Reminders access on first run)

**Step 5: Manual verification**

Run: `python bulk-reminders lists`
Expected: Shows numbered list of your Reminders lists

**Step 6: Commit**

```bash
git add bulk-reminders tests/test_bulk_reminders.py
git commit -m "feat: add get_reminder_lists via AppleScript"
```

---

### Task 3: CSV Parsing & Validation

**Files:**
- Modify: `bulk-reminders`
- Modify: `tests/test_bulk_reminders.py`
- Create: `tests/fixtures/valid.csv`
- Create: `tests/fixtures/invalid_date.csv`
- Create: `tests/fixtures/missing_title.csv`

**Step 1: Create test fixtures**

`tests/fixtures/valid.csv`:
```csv
title,due_date,notes
Buy groceries,2026-03-02 10:00,Don't forget milk
Call dentist,,
"Meeting, prep",2026-03-06 09:00,"Review Q1, print"
```

`tests/fixtures/invalid_date.csv`:
```csv
title,due_date,notes
Valid item,2026-03-02 10:00,notes
Bad date,March 5th,notes
```

`tests/fixtures/missing_title.csv`:
```csv
title,due_date,notes
Good item,2026-03-02 10:00,notes
,2026-03-03 10:00,no title here
```

**Step 2: Write the failing tests for CSV validation**

Add to `tests/test_bulk_reminders.py`:

```python
import os

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

def get_module():
    sys.path.insert(0, ".")
    from importlib import import_module
    return import_module("bulk-reminders".replace("-", "_"))

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
```

**Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_bulk_reminders.py -k "validate_csv" -v`
Expected: FAIL (function not defined)

**Step 4: Implement validate_csv**

Add to `bulk-reminders`:

```python
import csv
import re
from datetime import datetime


DATE_FORMAT = "%Y-%m-%d %H:%M"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")


def validate_csv(csv_path):
    """
    Validate CSV file and return (valid_rows, errors).

    Each valid row is a dict with keys: title, due_date (str or None), notes (str or None)
    """
    valid_rows = []
    errors = []

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Check for required 'title' column
            if "title" not in reader.fieldnames:
                return [], ["CSV must have a 'title' column"]

            for row_num, row in enumerate(reader, start=2):  # Row 1 is header
                title = row.get("title", "").strip()
                due_date = row.get("due_date", "").strip() or None
                notes = row.get("notes", "").strip() or None

                # Validate title
                if not title:
                    errors.append(f"Row {row_num}: Empty title, skipping")
                    continue

                # Validate due_date if provided
                if due_date:
                    if not DATE_PATTERN.match(due_date):
                        errors.append(f"Row {row_num}: Invalid date format \"{due_date}\" (expected YYYY-MM-DD HH:MM)")
                        continue
                    # Also validate it's a real date
                    try:
                        datetime.strptime(due_date, DATE_FORMAT)
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid date \"{due_date}\"")
                        continue

                valid_rows.append({
                    "title": title,
                    "due_date": due_date,
                    "notes": notes
                })

    except FileNotFoundError:
        return [], [f"File not found: {csv_path}"]
    except Exception as e:
        return [], [f"Error reading CSV: {e}"]

    return valid_rows, errors
```

**Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_bulk_reminders.py -k "validate_csv" -v`
Expected: PASS

**Step 6: Commit**

```bash
mkdir -p tests/fixtures
git add bulk-reminders tests/
git commit -m "feat: add CSV parsing and validation"
```

---

### Task 4: List Selection Prompt

**Files:**
- Modify: `bulk-reminders`
- Modify: `tests/test_bulk_reminders.py`

**Step 1: Write the failing test for prompt_list_selection**

Add to `tests/test_bulk_reminders.py`:

```python
from unittest.mock import patch

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
```

**Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_bulk_reminders.py -k "prompt_list_selection" -v`
Expected: FAIL (function not defined)

**Step 3: Implement prompt_list_selection**

Add to `bulk-reminders`:

```python
def prompt_list_selection(lists):
    """Prompt user to select a list by number. Returns list name."""
    print("Available lists:")
    for i, name in enumerate(lists, 1):
        print(f"  {i}. {name}")

    while True:
        try:
            choice = input(f"\nSelect list [1]: ").strip()
            if choice == "":
                return lists[0]

            idx = int(choice) - 1
            if 0 <= idx < len(lists):
                return lists[idx]
            else:
                print(f"Please enter a number between 1 and {len(lists)}")
        except ValueError:
            print(f"Please enter a number between 1 and {len(lists)}")
```

**Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_bulk_reminders.py -k "prompt_list_selection" -v`
Expected: PASS

**Step 5: Commit**

```bash
git add bulk-reminders tests/test_bulk_reminders.py
git commit -m "feat: add interactive list selection prompt"
```

---

### Task 5: AppleScript - Add Reminders (Batched)

**Files:**
- Modify: `bulk-reminders`
- Modify: `tests/test_bulk_reminders.py`

**Step 1: Write the failing test for escape_applescript_string**

Add to `tests/test_bulk_reminders.py`:

```python
def test_escape_applescript_string():
    """escape_applescript_string should escape quotes and backslashes."""
    bulk_reminders = get_module()

    assert bulk_reminders.escape_applescript_string('hello') == 'hello'
    assert bulk_reminders.escape_applescript_string('say "hi"') == 'say \\"hi\\"'
    assert bulk_reminders.escape_applescript_string('back\\slash') == 'back\\\\slash'
    assert bulk_reminders.escape_applescript_string('both "and" \\') == 'both \\"and\\" \\\\'
```

**Step 2: Write the failing test for build_applescript**

Add to `tests/test_bulk_reminders.py`:

```python
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
    assert 'due date:date "2026-03-02 10:00"' in script
    assert 'body:"some notes"' in script
    assert 'name:"No date"' in script
    # Second item should not have due date property
    lines = script.split("\n")
    no_date_line = [l for l in lines if 'name:"No date"' in l][0]
    assert "due date:" not in no_date_line
```

**Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/test_bulk_reminders.py -k "applescript" -v`
Expected: FAIL (functions not defined)

**Step 4: Implement escaping and AppleScript building**

Add to `bulk-reminders`:

```python
def escape_applescript_string(s):
    """Escape a string for use in AppleScript."""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_applescript(list_name, reminders):
    """
    Build AppleScript to add multiple reminders.
    Returns the script as a string.
    """
    lines = [
        'tell application "Reminders"',
        f'    tell list "{escape_applescript_string(list_name)}"',
    ]

    for r in reminders:
        title = escape_applescript_string(r["title"])
        notes = escape_applescript_string(r["notes"]) or ""

        if r["due_date"]:
            props = f'name:"{title}", due date:date "{r["due_date"]}", body:"{notes}"'
        else:
            props = f'name:"{title}", body:"{notes}"'

        lines.append(f"        make new reminder with properties {{{props}}}")

    lines.append("    end tell")
    lines.append("end tell")

    return "\n".join(lines)
```

**Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_bulk_reminders.py -k "applescript" -v`
Expected: PASS

**Step 6: Implement add_reminders function**

Add to `bulk-reminders`:

```python
def add_reminders(list_name, reminders, dry_run=False):
    """
    Add reminders to the specified list.
    Returns (success_count, failures) where failures is a list of error messages.
    """
    if not reminders:
        return 0, []

    script = build_applescript(list_name, reminders)

    if dry_run:
        return len(reminders), []

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # If the whole batch fails, report it
        return 0, [f"AppleScript error: {result.stderr.strip()}"]

    return len(reminders), []
```

**Step 7: Commit**

```bash
git add bulk-reminders tests/test_bulk_reminders.py
git commit -m "feat: add batched AppleScript reminder creation"
```

---

### Task 6: Wire Up cmd_add with Full Flow

**Files:**
- Modify: `bulk-reminders`

**Step 1: Implement the full cmd_add flow**

Replace `cmd_add` in `bulk-reminders`:

```python
def format_due_date(due_date):
    """Format due date for display (e.g., 'Mar 2 at 10:00 AM')."""
    if not due_date:
        return "no due date"
    dt = datetime.strptime(due_date, DATE_FORMAT)
    return f"due: {dt.strftime('%b %-d at %-I:%M %p')}"


def cmd_add(args):
    """Add reminders from CSV file."""
    # Validate CSV
    print(f"Validating {args.csv_file}...")
    valid_rows, errors = validate_csv(args.csv_file)

    if errors:
        print()
        for err in errors:
            print(f"  ⚠ {err}")
        print()

    if not valid_rows:
        print("No valid reminders found.")
        sys.exit(1)

    skipped = len(errors)
    print(f"Found {len(valid_rows)} valid reminder(s)" + (f" ({skipped} skipped)" if skipped else ""))

    # Determine target list
    lists = get_reminder_lists()

    if args.list_name:
        if args.list_name not in lists:
            print(f"Error: List '{args.list_name}' not found.", file=sys.stderr)
            print(f"Available lists: {', '.join(lists)}", file=sys.stderr)
            sys.exit(1)
        target_list = args.list_name
    else:
        print()
        target_list = prompt_list_selection(lists)

    # Confirm if there were validation errors
    if errors and not args.dry_run:
        try:
            confirm = input("\nContinue? [Y/n]: ").strip().lower()
            if confirm and confirm != "y":
                print("Aborted.")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)

    # Add reminders
    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{prefix}Adding to \"{target_list}\":")

    # Show progress
    for i, r in enumerate(valid_rows, 1):
        due_str = format_due_date(r["due_date"])
        print(f"  [{i}/{len(valid_rows)}] {'○' if args.dry_run else '...'} {r['title']} ({due_str})", end="", flush=True)
        if not args.dry_run:
            print("\r", end="")  # Will overwrite with result

    if args.dry_run:
        print(f"\n{prefix}Done: {len(valid_rows)} would be added")
        return

    # Actually add them
    success, failures = add_reminders(target_list, valid_rows, dry_run=args.dry_run)

    # Re-print with results
    print()  # Clear the progress line
    for i, r in enumerate(valid_rows, 1):
        due_str = format_due_date(r["due_date"])
        if failures:
            print(f"  [{i}/{len(valid_rows)}] ✗ {r['title']} ({due_str})")
        else:
            print(f"  [{i}/{len(valid_rows)}] ✓ {r['title']} ({due_str})")

    # Summary
    failed = len(failures)
    print(f"\nDone: {success} added, {failed} failed" + (f", {skipped} skipped (validation)" if skipped else ""))

    if failures:
        for f in failures:
            print(f"  Error: {f}", file=sys.stderr)
        sys.exit(1)
```

**Step 2: Manual test with real CSV**

Create `test.csv`:
```csv
title,due_date,notes
Test reminder 1,2026-03-02 10:00,Test notes
Test reminder 2,,No date
```

Run: `python bulk-reminders add test.csv --dry-run`
Expected: Shows dry run output with both reminders

Run: `python bulk-reminders add test.csv --list Reminders`
Expected: Actually adds reminders (verify in Reminders app)

**Step 3: Commit**

```bash
git add bulk-reminders
git commit -m "feat: implement full add command flow with progress"
```

---

### Task 7: Make Executable & Final Polish

**Files:**
- Modify: `bulk-reminders`

**Step 1: Make script executable**

Run: `chmod +x bulk-reminders`

**Step 2: Test as executable**

Run: `./bulk-reminders --help`
Expected: Shows help

Run: `./bulk-reminders lists`
Expected: Shows lists

**Step 3: Add file not found handling**

Already handled in `validate_csv`, but verify:

Run: `./bulk-reminders add nonexistent.csv`
Expected: Clean error message about file not found

**Step 4: Commit final version**

```bash
git add bulk-reminders
git commit -m "chore: make script executable"
```

---

### Task 8: Create Sample CSV & README

**Files:**
- Create: `sample.csv`
- Create: `README.md`

**Step 1: Create sample CSV**

```csv
title,due_date,notes
Weekly review,2026-03-02 10:00,Review goals and progress
Call mom,,Don't forget birthday
"Dentist appointment, cleaning",2026-03-15 14:30,Bring insurance card
Finish project,2026-03-20 17:00,"Wrap up documentation, send to team"
```

**Step 2: Create README**

```markdown
# bulk-reminders

A macOS CLI tool to bulk add reminders to Apple Reminders from a CSV file.

## Usage

```bash
# List available Reminders lists
./bulk-reminders lists

# Add reminders from CSV (prompts for list selection)
./bulk-reminders add tasks.csv

# Add to a specific list
./bulk-reminders add tasks.csv --list Work

# Preview what would be added (dry run)
./bulk-reminders add tasks.csv --dry-run
```

## CSV Format

```csv
title,due_date,notes
Buy groceries,2026-03-02 10:00,Don't forget milk
Call dentist,,
"Meeting prep, slides",2026-03-06 09:00,"Review Q1 numbers"
```

- **title** (required): Reminder title
- **due_date** (optional): Format `YYYY-MM-DD HH:MM` in local time
- **notes** (optional): Additional notes

See `sample.csv` for an example.

## Requirements

- macOS with Reminders app
- Python 3
- First run may prompt for Reminders app access
```

**Step 3: Commit**

```bash
git add sample.csv README.md
git commit -m "docs: add README and sample CSV"
```

---

## Summary

8 tasks covering:
1. CLI skeleton with argparse
2. AppleScript integration for listing
3. CSV parsing and validation
4. Interactive list selection
5. Batched reminder creation
6. Full command flow with progress
7. Make executable
8. Documentation

Each task follows TDD where applicable, with frequent commits.
