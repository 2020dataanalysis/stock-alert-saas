#!/bin/zsh

APP_DIR="/Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas"
PYTHON="/Users/ultrasupersam/apps/stock-alert-platform/.venv/bin/python"

cd "$APP_DIR" || exit 1

mkdir -p "$APP_DIR/logs"

echo "STARTING STREAMER $(date)" >> "$APP_DIR/logs/debug.log"

if [ ! -x "$PYTHON" ]; then
  echo "ERROR: Python not found at $PYTHON" >> "$APP_DIR/logs/debug.log"
  exit 1
fi

echo "USING PYTHON $PYTHON" >> "$APP_DIR/logs/debug.log"

"$PYTHON" -u -m app.streamer.quote_streamer_config >> "$APP_DIR/logs/streamer.out.log" 2>> "$APP_DIR/logs/streamer.err.log"