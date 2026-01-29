# Welcome Header Design

**Date:** 2026-01-29

## Overview

Add a persistent welcome header that appears when users run `bulk-reminders` with no arguments or `--help`. Provides quick-reference guidance in a clean, two-column layout.

## Behavior

The welcome header appears in two situations:
- **No arguments** - User runs `bulk-reminders` with nothing else
- **Help flag** - User runs `bulk-reminders --help` or `-h`

All other commands (`add`, `lists`) remain unchanged with clean output.

**Current behavior (no args):**
```
usage: bulk-reminders [-h] {lists,add} ...
bulk-reminders: error: the following arguments are required: command
```

**New behavior (no args):**
```
╭────────────────────────────────────────────────────────────────────────────────╮
│  bulk-reminders · Add reminders to Apple Reminders from CSV                    │
│                                                                                │
│  add <csv>   Add reminders from CSV            dill-pickles/bulk-reminders     │
│  lists       Show available lists                                              │
╰────────────────────────────────────────────────────────────────────────────────╯
```

No error message - just helpful guidance.

## Visual Design

**Layout** (80 characters wide):
- Line 1: Tool name + separator dot + tagline
- Line 2: Empty (breathing room)
- Line 3: Primary command (`add`) left, GitHub link right
- Line 4: Secondary command (`lists`) left-aligned under `add`

**Color accent** (TTY only):
- Tool name "bulk-reminders" in cyan - stands out without being loud
- Everything else remains default terminal color
- Falls back to plain text when piped or redirected

**Box characters:** Unicode box-drawing (`╭╮╰╯│─`)

## Implementation

**Code changes in `bulk-reminders`:**

1. **New function `print_welcome()`**
   - Generates and prints the header box
   - Detects TTY with `sys.stdout.isatty()`
   - Applies cyan color to tool name if TTY
   - Handles box drawing and alignment

2. **Modify `main()`**
   - Change `required=True` to `required=False` on subparsers
   - Show welcome when `args.command` is None

3. **Modify `--help`**
   - Show welcome header instead of standard argparse help

**Testing:**
- Test `print_welcome()` output content
- Test no-args behavior (shows welcome, exits cleanly)
- Test TTY detection (colors when TTY, plain when not)
