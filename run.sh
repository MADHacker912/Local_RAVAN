#!/usr/bin/env bash
# ravan terminal agent launcher script
# terminal me directly ravan command run karne ke liye banaya gaya hai

# symlink follow karke script ka exact real directory path nikal rahe hain
REAL_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
DIR="$(cd "$(dirname "$REAL_PATH")" >/dev/null 2>&1 && pwd)"
export PYTHONPATH="$DIR:/home/obito/hexstrike-ai:$PYTHONPATH"

# pehle check kar rahe hain ki hexstrike ka server 8888 port pe live chal raha hai ya nahi
if ! curl -s http://127.0.0.1:8888/health >/dev/null 2>&1; then
    echo -e "\033[93m[!] Warning: HexStrike server on port 8888 is not reachable.\033[0m"
    echo -e "\033[93m    You can start it with: systemctl --user start hexstrike or cd /home/obito/hexstrike-ai && python3 hexstrike_server.py\033[0m\n"
fi

# ravan main agent script ko execute kar rahe hain arguments ke sath
exec python3 "$DIR/hex_agent.py" "$@"
