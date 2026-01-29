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
- 12 passing tests

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

## Feedback from First Use (Priority Ordered)

### 1. BUG (Critical): Due dates not working
**Problem:** All 52 reminders were added successfully, but every entry had due date set to `12/31/00 at 7:00 PM` instead of the correct dates from the CSV.

**Likely cause:** AppleScript date parsing is locale-dependent. The format `date "2026-03-02 10:00"` may not parse correctly on all Macs.

**Known fix from design doc:** Build dates explicitly instead of string parsing:
```applescript
set d to current date
set year of d to 2026
set month of d to 3
set day of d to 2
set hours of d to 10
set minutes of d to 0
set seconds of d to 0
```

**Location to fix:** `build_applescript()` function in `bulk-reminders`

---

### 2. ENHANCEMENT: Better error message for CSV headers
**Problem:** When CSV has `Title,Due Date,Notes` instead of `title,due_date,notes`, error says "CSV must have a 'title' column" - not clear that it's a case/format issue.

**Requested fix:** Error message should explain the expected format so user knows how to fix it.

**Also:** Add a downloadable CSV template link to README.

---

### 3. ENHANCEMENT: Lists in folders not showing
**Problem:** Apple Reminders lists that are inside folders don't appear in the CLI list selection.

**Priority:** Low (user noted this is not high priority)

**Likely cause:** AppleScript `get name of every list` may not traverse folder hierarchy. May need different AppleScript approach.

---

### 4. ENHANCEMENT: Easier installation
**Problem:** Current install requires git clone + chmod. User mentioned other CLI tools have easier installs.

**Options to consider:**
- **Homebrew tap:** `brew install dill-pickles/tap/bulk-reminders`
- **Direct curl install:** `curl -sSL https://raw.githubusercontent.com/.../bulk-reminders | sudo tee /usr/local/bin/bulk-reminders`
- **Release binaries:** GitHub Releases with download link
- **pip install:** Package on PyPI (adds dependency but familiar to Python users)

**Recommended:** Homebrew tap is most familiar to macOS users, or a simple curl one-liner in README.

---

## Next Steps (Suggested Priority)

1. **Fix date bug** - Critical, tool doesn't work correctly without this
2. **Better CSV header error message** - Quick win, improves UX
3. **Add CSV template to README** - Quick win
4. **Easier install** - Add curl one-liner or Homebrew
5. **Lists in folders** - Lower priority enhancement

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
```
