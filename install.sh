#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$HOME/.local/bin"

ln -sf "$DIR/run.sh" "$HOME/.local/bin/ravan"
ln -sf "$DIR/run.sh" "$HOME/.local/bin/hex-agent"
chmod +x "$DIR/run.sh" "$DIR/hex_agent.py"

echo "[+] RAVAN setup complete. You can run 'ravan' from any terminal."
