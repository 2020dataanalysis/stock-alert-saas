#!/bin/zsh

PID=$(ps aux | awk '/[q]uote_streamer/ {print $2}')

if [ -z "$PID" ]; then
    echo "quote_streamer process not found"
    exit 1
fi

echo "Monitoring PID=$PID"
echo

while true; do
    echo -n "$(date '+%H:%M:%S') PID=$PID FD_COUNT="
    lsof -p "$PID" | wc -l
    sleep 5
done
