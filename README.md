# bulk-reminders

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white)
![Python 3](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)

A macOS CLI tool to bulk add reminders to Apple Reminders from a CSV file.

**Features:**
- Batch import reminders from CSV (Excel, Google Sheets, etc.)
- Native macOS file picker for easy file selection
- Preserves due dates and notes
- Dry-run mode to preview before adding
- No external dependencies - just Python 3 and macOS

## Installation

### Quick install (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/dill-pickles/bulk-reminders/main/bulk-reminders -o /usr/local/bin/bulk-reminders && chmod +x /usr/local/bin/bulk-reminders
```

### Or clone the repository

```bash
git clone https://github.com/dill-pickles/bulk-reminders.git
cd bulk-reminders
chmod +x bulk-reminders

# Optionally, add to your PATH for global access
cp bulk-reminders /usr/local/bin/
```

No dependencies required - uses only Python 3 standard library and macOS built-in tools.

---

## Quick Start

1. Format your data as CSV (export from Excel, Google Sheets, or any spreadsheet):

```csv
title,due_date,notes
Buy groceries,2026-03-02 10:00,Don't forget milk
Call dentist,,
Finish report,2026-03-15 17:00,Q1 summary
```

2. Run the tool:

```bash
./bulk-reminders add
```

A file picker will open—select your CSV file.

3. Select which Reminders list to add to (or press Enter for default).

That's it! Your reminders are now in Apple Reminders.

## Usage

### List available Reminders lists

```bash
./bulk-reminders lists
```

Output:
```
Available lists:
  1. Reminders
  2. Work
  3. Shopping
```

### Add reminders from a CSV file

```bash
# Opens a file picker to select your CSV
./bulk-reminders add

# Or provide the path directly
./bulk-reminders add tasks.csv

# Specify the list directly (skips list selection prompt)
./bulk-reminders add tasks.csv --list Work

# Preview what would be added (no changes made)
./bulk-reminders add tasks.csv --dry-run
```

**Tip:** You can drag a file from Finder directly into the Terminal window to paste its path.

### Example output

```
Validating tasks.csv...
Found 3 valid reminder(s)

Available lists:
  1. Reminders
  2. Work

Select list [1]: 2

Adding to "Work":
  [1/3] ✓ Buy groceries (due: Mar 2 at 10:00 AM)
  [2/3] ✓ Call dentist (no due date)
  [3/3] ✓ Finish report (due: Mar 15 at 5:00 PM)

Done: 3 added, 0 failed
```

---

## CSV Format

Your CSV file needs a header row with column names. Only `title` is required.

| Column | Required | Format | Example |
|--------|----------|--------|---------|
| `title` | Yes | Text | `Buy groceries` |
| `due_date` | No | `YYYY-MM-DD HH:MM` | `2026-03-02 10:00` |
| `notes` | No | Text | `Don't forget milk` |

### Example CSV

```csv
title,due_date,notes
Weekly review,2026-03-02 10:00,Review goals and progress
Call mom,,Don't forget birthday
"Dentist appointment, cleaning",2026-03-15 14:30,Bring insurance card
Finish project,2026-03-20 17:00,"Wrap up documentation, send to team"
```

**Tips:**
- Use quotes around fields that contain commas: `"Meeting prep, slides"`
- Leave `due_date` empty for reminders without a specific time
- Dates are interpreted in your local time zone

**[Download sample.csv template](https://raw.githubusercontent.com/dill-pickles/bulk-reminders/main/sample.csv)** - Right-click → Save As

---

## Validation

The tool validates your CSV before adding anything:

- Checks that `title` column exists
- Skips rows with empty titles
- Validates date format (`YYYY-MM-DD HH:MM`)
- Catches invalid dates (like February 30th)

If there are validation errors, you'll see them before any reminders are added:

```
Validating tasks.csv...

  ⚠ Row 3: Empty title, skipping
  ⚠ Row 5: Invalid date format "March 5th" (expected YYYY-MM-DD HH:MM)

Found 8 valid reminder(s) (2 skipped)
Continue? [Y/n]:
```

---

## Requirements

- **macOS** (uses AppleScript to communicate with Reminders)
- **Python 3** (pre-installed on macOS)
- **Reminders app** access (you'll be prompted on first run)

## First Run

The first time you run the tool, macOS will ask for permission to control the Reminders app. Click "OK" to allow access.

If you accidentally denied access, you can fix it in:
**System Preferences → Privacy & Security → Automation → Terminal** (or your terminal app)

---

## Known Limitations

- **Lists in folders:** Reminder lists nested inside folders in the Reminders app may not appear in the list selection. Move lists out of folders if they don't show up.

---

## License

MIT
