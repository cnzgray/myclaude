#!/bin/bash

# Output the explanatory mode instructions as additionalContext
# This mimics the deprecated Explanatory output style

# Get the context file from argument or use default
CONTEXT_FILE="${1:-engineer-professional.md}"
CONTEXT_FILE="output-styles/$CONTEXT_FILE"
CONTEXT_PATH="$(dirname "$0")/$CONTEXT_FILE"

# Check if the file exists
if [ ! -f "$CONTEXT_PATH" ]; then
    echo "Error: Context file '$CONTEXT_PATH' not found" >&2
    exit 1
fi

# Read content from the specified context file
CONTEXT_CONTENT=$(cat "$CONTEXT_PATH" | sed 's/\\/\\\\/g; s/"/\\"/g' | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/\\n/g')

cat << EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "$CONTEXT_CONTENT"
  }
}
EOF

exit 0
