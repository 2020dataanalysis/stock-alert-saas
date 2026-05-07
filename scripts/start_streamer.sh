#!/bin/zsh

echo "STARTING STREAMER $(date)" >> logs/debug.log

cd /Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas

PYTHON="/Users/ultrasupersam/apps/stock-alert-platform/.venv/bin/python"

if [ ! -f "$PYTHON" ]; then
    echo "ERROR: Python not found at $PYTHON" >> logs/debug.log
    exit 1
fi

echo "USING PYTHON $PYTHON" >> logs/debug.log

$PYTHON -m app.streamer.quote_streamer_config >> logs/streamer.out.log 2>> logs/streamer.err.log