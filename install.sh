#!/usr/bin/env bash
set -euo pipefail

# Thin wrapper around the Node installer. Prefer:
#   npx @lxy10086/oh-my-skills add --all
# This script exists for local checkouts and curl-based installs.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v node >/dev/null 2>&1; then
  echo "oh-my-skills requires Node.js 18+." >&2
  echo "Install Node, then run: npx @lxy10086/oh-my-skills add --all" >&2
  exit 1
fi

NODE_MAJOR="$(node -p "process.versions.node.split('.')[0]")"
if [ "$NODE_MAJOR" -lt 18 ]; then
  echo "oh-my-skills requires Node.js 18+. Found $(node -v)." >&2
  exit 1
fi

if [ "$#" -eq 0 ]; then
  exec node "$SCRIPT_DIR/bin/cli.js" add --all
fi

exec node "$SCRIPT_DIR/bin/cli.js" "$@"
