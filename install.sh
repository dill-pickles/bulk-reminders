#!/bin/bash
set -e

INSTALL_DIR="/usr/local/bin"
BINARY_NAME="bulk-reminders"
REPO_URL="https://raw.githubusercontent.com/dill-pickles/bulk-reminders/main/bulk-reminders"

# Download and install
curl -fsSL "$REPO_URL" -o "$INSTALL_DIR/$BINARY_NAME"
chmod +x "$INSTALL_DIR/$BINARY_NAME"

# Success message
echo ""
echo "╭─────────────────────────────────────────────╮"
echo "│                                             │"
echo "│   bulk-reminders              installed!    │"
echo "│                                             │"
echo "├─────────────────────────────────────────────┤"
echo "│                                             │"
echo "│   Get started:                              │"
echo "│     bulk-reminders lists    View lists      │"
echo "│     bulk-reminders add      Import CSV      │"
echo "│                                             │"
echo "╰─────────────────────────────────────────────╯"
echo ""
