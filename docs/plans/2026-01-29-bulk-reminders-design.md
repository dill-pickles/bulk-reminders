# Bulk Reminders CLI Tool Design

## Overview

A macOS CLI tool that bulk adds reminders to Apple Reminders from a CSV file. Uses Python for CSV parsing and AppleScript (via `osascript`) for Reminders integration.

## CLI Interface

```
bulk-reminders add <csv_file> [--list <name>] [--dry-run]
bulk-reminders lists
```

**Commands:**
- `add` - Add reminders from CSV file
- `lists` - Show available Reminders lists

**Flags:**
- `--list <name>` - Target list (if omitted, prompts with numbered selection)
- `--dry-run` - Preview what would be added without actually adding

## CSV Format

```csv
title,due_date,notes
Buy groceries,2026-03-02 10:00,Don't forget milk
Call dentist,,
"Meeting prep, slides",2026-03-06 09:00,"Review Q1 numbers"
```

- `title` - Required, non-empty
- `due_date` - Optional, format `YYYY-MM-DD HH:MM` (local time)
- `notes` - Optional

## Validation

**CSV validation (before processing):**
- File exists and is readable
- Has required `title` column header
- Recognizes `due_date` and `notes` columns (warns about unknown columns)
- Each row has a non-empty title
- If `due_date` provided, validates format

**Behavior:**
- Invalid rows are skipped, valid rows continue
- User prompted to confirm after validation shows issues
- Never aborts mid-batch

## Code Structure

Single executable Python script: `bulk-reminders`

**Components:**
- `parse_args()` - argparse for CLI
- `get_reminder_lists()` - calls osascript, returns list names
- `prompt_list_selection()` - numbered menu if --list not provided
- `validate_csv()` - returns (valid_rows, errors)
- `add_reminders()` - batched osascript call for all reminders
- `main()` - orchestrates flow

## AppleScript Integration

**Get lists:**
```applescript
tell application "Reminders" to get name of every list
```

**Add reminders (batched):**
```applescript
tell application "Reminders"
    tell list "Work"
        make new reminder with properties {name:"Item 1", due date:date "2026-03-02 10:00", body:"notes"}
        make new reminder with properties {name:"Item 2", body:""}
    end tell
end tell
```

**Date handling:**
- Python parses `YYYY-MM-DD HH:MM`, reformats for AppleScript
- AppleScript interprets in local time
- Note: If locale issues arise, switch to explicit date building:
  ```applescript
  set d to current date
  set year of d to 2026
  set month of d to 3
  set day of d to 2
  set hours of d to 10
  set minutes of d to 0
  set seconds of d to 0
  ```

**Escaping:** Titles and notes escaped for AppleScript (backslashes, quotes).

## Output

**Example session:**
```
$ ./bulk-reminders add tasks.csv
Available lists:
  1. Reminders
  2. Work
  3. Shopping

Select list [1]: 2

Validating CSV... 3 reminders found

Adding to "Work":
  [1/3] ✓ Buy groceries (due: Mar 2 at 10:00 AM)
  [2/3] ✓ Call dentist (no due date)
  [3/3] ✓ Meeting prep, slides (due: Mar 6 at 9:00 AM)

Done: 3 added, 0 failed
```

**Summary format:**
```
Done: X added, Y failed, Z skipped (validation)
```

## Dry Run

- Validates CSV (same as normal)
- Verifies target list exists
- Prints what would be added with `[DRY RUN]` prefix
- Does not call AppleScript to add reminders
