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
- 13 passing tests

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

## Remaining Items (Priority Ordered)

### 3. ENHANCEMENT: Add CSV template to README
**Status:** Not started

**Task:** Add a downloadable CSV template link to README so users know the exact format.

---

### 4. ENHANCEMENT: Easier installation
**Status:** Not started

**Problem:** Current install requires git clone + chmod.

**Options to consider:**
- **Homebrew tap:** `brew install dill-pickles/tap/bulk-reminders`
- **Direct curl install:** `curl -sSL https://raw.githubusercontent.com/.../bulk-reminders | sudo tee /usr/local/bin/bulk-reminders`
- **Release binaries:** GitHub Releases with download link

**Recommended:** Homebrew tap or simple curl one-liner in README.

---

### 5. ENHANCEMENT: Lists in folders not showing
**Status:** Not started (low priority)

**Problem:** Apple Reminders lists inside folders don't appear in CLI list selection.

**Likely cause:** AppleScript `get name of every list` may not traverse folder hierarchy.

**Location to investigate:** `get_reminder_lists()` function, lines 16-32

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
| 199-276 | `cmd_add()` | Handler for `add` command (main flow) |
| 279-304 | `main()` | CLI argument parsing |

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

13 tests in `tests/test_bulk_reminders.py`:
- CLI argument parsing (3 tests)
- `get_reminder_lists()` (1 test)
- `validate_csv()` (4 tests) - valid file, invalid date, missing title, wrong headers
- `prompt_list_selection()` (3 tests) - default, number, invalid input
- `escape_applescript_string()` (1 test)
- `build_applescript()` (1 test) - verifies explicit date building
