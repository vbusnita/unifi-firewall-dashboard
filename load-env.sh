#!/usr/bin/env bash
# load-env.sh - Safely load .env into current shell

set -euo pipefail

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found in current directory."
    exit 1
fi

echo "Loading variables from $ENV_FILE into shell..."

# Export all variables from .env
set -a
source "$ENV_FILE"
set +a

# Count non-comment, non-empty lines for feedback
LOADED_COUNT=$(grep -v '^#' "$ENV_FILE" | grep -v '^$' | wc -l | xargs)

echo "Done! Loaded $LOADED_COUNT variables."
echo "Test example: echo \$GRAYLOG_API_TOKEN"
echo "               echo \$GROK_API_KEY"
