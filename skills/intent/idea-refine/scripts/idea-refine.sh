#!/bin/bash
set -e

# This script can initialize the ideas directory after persistence is approved.
# The default is a read-only readiness probe so invoking the skill cannot imply
# that the user approved a durable artifact.

IDEAS_DIR="docs/ideas"

if [ "${1:-}" != "--apply" ]; then
  printf '{"status": "ready", "directory": "%s", "would_create": %s}\n' \
    "$IDEAS_DIR" "$([ -d "$IDEAS_DIR" ] && echo false || echo true)"
  exit 0
fi

if [ ! -d "$IDEAS_DIR" ]; then
  mkdir -p "$IDEAS_DIR"
  echo "Created directory: $IDEAS_DIR" >&2
else
  echo "Directory already exists: $IDEAS_DIR" >&2
fi

echo "{\"status\": \"ready\", \"directory\": \"$IDEAS_DIR\"}"
