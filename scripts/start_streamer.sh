#!/bin/zsh
# stock-alert-saas/scripts/start_streamer.sh

APP_DIR="/Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas"
PYTHON="/Users/ultrasupersam/apps/stock-alert-platform/.venv/bin/python"

cd "$APP_DIR" || exit 1

mkdir -p logs

echo "STARTING STREAMER $(date)" >> logs/debug.log
echo "PWD $(pwd)" >> logs/debug.log
echo "PYTHON $PYTHON" >> logs/debug.log
echo "PYTHON VERSION $($PYTHON --version)" >> logs/debug.log
echo "CONFIG FILES:" >> logs/debug.log
ls -la config >> logs/debug.log

export PYTHONPATH="$APP_DIR"

if [ ! -f "$PYTHON" ]; then
    echo "ERROR: Python not found at $PYTHON" >> logs/debug.log
    exit 1
fi

"$PYTHON" -u -m app.streamer.quote_streamer \
    >> logs/streamer.out.log \
    2>> logs/streamer.err.log

EXIT_CODE=$?

echo "STREAMER EXITED (code=$EXIT_CODE) $(date)" >> logs/debug.log

exit $EXIT_CODE
