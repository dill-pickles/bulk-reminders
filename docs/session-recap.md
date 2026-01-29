# bulk-reminders Session Recap

## What Was Built

A macOS CLI tool that bulk adds reminders to Apple Reminders from a CSV file.

**Repository:** https://github.com/dill-pickles/bulk-reminders

### Features Implemented
- `./bulk-reminders lists` - Show available Reminders lists
- `./bulk-reminders add <csv>` - Add reminders from CSV
- `--list <name>` - Specify target list (skip interactive prompt)
- `--dry-run` - Preview without adding
- CSV validation with helpful error messages
- Progress display and summary (X added, Y failed, Z skipped)

### Technical Details
- Single Python 3 script, no external dependencies
- Uses AppleScript via `osascript` for Reminders integration
- Batches all reminders into single AppleScript call for performance
- 15 passing tests

### Files
```
bulk-reminders          # Main CLI script (executable)
tests/                  # Unit tests
  test_bulk_reminders.py
  fixtures/             # Test CSV files
sample.csv              # Example CSV
README.md               # Documentation
docs/plans/             # Design and implementation docs
```

---

## Completed This Session

### ✅ Priority 1: Fixed Date Bug (Critical)
**Problem:** All reminders were added with due date `12/31/00 at 7:00 PM` instead of correct dates.

**Root cause:** AppleScript's `date "YYYY-MM-DD HH:MM"` string parsing is locale-dependent.

**Fix:** `build_applescript()` now builds dates explicitly by setting each component:
```applescript
set d to current date
set year of d to 2026
set month of d to 3
set day of d to 2
set hours of d to 10
set minutes of d to 0
set seconds of d to 0
make new reminder with properties {name:"Title", due date:d, body:"notes"}
```

**Location:** `build_applescript()` function, lines 95-133

---

### ✅ Priority 2: Better CSV Header Error Message
**Problem:** When CSV has `Title,Due Date,Notes` instead of `title,due_date,notes`, error said "CSV must have a 'title' column" - unclear it's a case/format issue.

**Fix:** Error now shows found headers and expected format:
```
CSV must have a 'title' column (found: Title, Due Date, Notes). Expected headers: title,due_date,notes
```

**Location:** `validate_csv()` function, lines 48-51

---

### ✅ Priority 3: Fixed Progress Counter Bug
**Problem:** Progress counter showed `[52/52]` immediately for all items instead of incrementing.

**Root cause:** The "show progress" loop ran before the batch `add_reminders()` call, printing all items rapidly with `\r` carriage return, so user only saw the last line. Misleading fake progress.

**Fix:** Removed fake progress loop. Now shows "Adding N reminder(s)..." during batch operation, then displays each result with `[1/N] ✓` after completion.

**Location:** `cmd_add()` function, lines 243-265

---

### ✅ Priority 4: Added CSV Template Download Link
**Task:** Added a downloadable CSV template link to README.

**Fix:** Added direct link to `sample.csv` in the CSV Format section:
```markdown
**[Download sample.csv template](https://raw.githubusercontent.com/dill-pickles/bulk-reminders/main/sample.csv)**
```

**Location:** `README.md`, line 120

---

### ✅ Priority 5: Added Easier Installation
**Problem:** Previous install required git clone + chmod.

**Fix:** Added curl one-liner as recommended install method:
```bash
curl -fsSL https://raw.githubusercontent.com/dill-pickles/bulk-reminders/main/bulk-reminders -o /usr/local/bin/bulk-reminders && chmod +x /usr/local/bin/bulk-reminders
```

**Location:** `README.md`, Installation section

---

## Remaining Items

### 6. BUG: Lists in folders not showing
**Status:** Needs further investigation

**Problem:** Apple Reminders lists nested inside folders may not appear in CLI list selection.

**Initial investigation:**
- Tested `get name of every list` - returns all lists from all accounts (iCloud + Local)
- All 6 lists on test system appeared correctly in CLI
- Lists across multiple accounts (iCloud, Local) are properly returned
- macOS Ventura's visual "folder grouping" feature may not be fully exposed via AppleScript API

**Workaround documented:** Added note to README advising users to move lists out of folders if they don't appear.

**Next steps:** Reproduce with lists actually nested in folders (not just multiple accounts). May need to investigate AppleScript's handling of Reminders folder hierarchy.

**Location to investigate:** `get_reminder_lists()` function, lines 16-32

---

### 7. ENHANCEMENT: Re-think Quick Start section in README
**Status:** Not started

**Problem:** The Quick Start section awkwardly says "Create a CSV file" as step 1, showing terminal code block. This doesn't match the real use case.

**Real use case:** User already has a spreadsheet/list of reminders (e.g., from Excel, Google Sheets, or a text file) and wants to bulk import them.

**Ideas to explore:**
- Lead with "Export your reminders to CSV" or "Prepare your CSV"
- Show how to export from common sources (Excel, Google Sheets)
- Make the CSV format requirements clearer upfront
- Consider the workflow: user has data → formats as CSV → runs tool

**Location:** `README.md`, Quick Start section

---

### 8. ENHANCEMENT: Easier CSV file selection
**Status:** Not started (needs research)

**Problem:** Users must type the full filepath to their CSV, which can be cumbersome.

**Options to explore:**
- **macOS file picker dialog:** Can AppleScript/osascript present a file chooser? Would need to call from Python.
- **Drag-and-drop:** Terminal supports dragging files to insert path - document this as a tip?
- **Current directory default:** If user runs from same directory as CSV, just `./bulk-reminders add myfile.csv` works
- **Tab completion:** Already works in most shells - document as tip?
- **Clipboard path:** Read path from clipboard? (probably overkill)

**Research needed:** What's possible within a Python CLI on macOS for file selection UX?

---

## Code Map (bulk-reminders)

| Lines | Function | Purpose |
|-------|----------|---------|
| 12-13 | Constants | `DATE_FORMAT`, `DATE_PATTERN` for validation |
| 16-32 | `get_reminder_lists()` | Calls AppleScript to get list names. **Known issue: doesn't see lists in folders** |
| 35-85 | `validate_csv()` | Parses CSV, validates rows. ✅ Fixed: better error for wrong headers |
| 88-92 | `escape_applescript_string()` | Escapes quotes/backslashes for AppleScript |
| 95-133 | `build_applescript()` | Generates AppleScript to create reminders. ✅ Fixed: explicit date building |
| 136-159 | `add_reminders()` | Executes the AppleScript via osascript |
| 162-180 | `prompt_list_selection()` | Interactive list picker |
| 183-188 | `format_due_date()` | Formats dates for display |
| 191-196 | `cmd_lists()` | Handler for `lists` command |
| 199-271 | `cmd_add()` | Handler for `add` command (main flow). ✅ Fixed: progress display |
| 274-299 | `main()` | CLI argument parsing |

---

## How to Resume

```bash
cd /Users/patrickvanwagoner/Projects/bulk-reminders
source venv/bin/activate  # For running tests
```

To run tests:
```bash
python -m pytest tests/ -v
```

To test manually:
```bash
./bulk-reminders add sample.csv --dry-run
./bulk-reminders add sample.csv --list "Reminders" --dry-run
```

---

## Test Coverage

15 tests in `tests/test_bulk_reminders.py`:
- CLI argument parsing (3 tests)
- `get_reminder_lists()` (1 test)
- `validate_csv()` (4 tests) - valid file, invalid date, missing title, wrong headers
- `prompt_list_selection()` (3 tests) - default, number, invalid input
- `escape_applescript_string()` (1 test)
- `build_applescript()` (1 test) - verifies explicit date building
- Progress display (2 tests) - dry-run incremental counts, results after batch
