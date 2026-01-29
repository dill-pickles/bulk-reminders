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
