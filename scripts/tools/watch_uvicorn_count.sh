#!/bin/zsh

PROCESS_PATTERN="${1:-uvicorn}"

PID=$(pgrep -f "$PROCESS_PATTERN" | head -n 1)

if [[ -z "$PID" ]]; then
    echo "No process found matching: $PROCESS_PATTERN"
    exit 1
fi

echo "Watching PID=$PID ($PROCESS_PATTERN)"
echo

while true; do
    FD_COUNT=$(lsof -p "$PID" 2>/dev/null | wc -l)

    echo "$(date '+%H:%M:%S') PID=$PID FD_COUNT=$FD_COUNT"

    sleep 5
done