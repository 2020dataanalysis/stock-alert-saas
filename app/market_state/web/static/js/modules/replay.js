/*
|--------------------------------------------------------------------------
| File: replay.js
|--------------------------------------------------------------------------
| Replay stepping, playback timing, and replay navigation controls.
|--------------------------------------------------------------------------
*/

function showCurrentRow() {
    const rows = getRows();

    if (rows.length === 0) {
        return;
    }

    liveDataBuffer = [];

    if (currentIndex >= rows.length) {
        currentIndex = rows.length - 1;
    }

    if (currentIndex < 0) {
        currentIndex = 0;
    }

    clearActiveRows();

    const row = rows[currentIndex];

    row.classList.add("active-row");

    updateHudFromRow(row);
    updateReplayStatus();
    drawPriceChart();
}

function stepForward() {
    setModeLabel("REPLAY");

    const rows = getRows();

    if (currentIndex < rows.length - 1) {
        currentIndex += 1;
        showCurrentRow();
    }
}

function stepBackward() {
    setModeLabel("REPLAY");

    if (currentIndex > 0) {
        currentIndex -= 1;
        showCurrentRow();
    }
}

function startPlaybackTimer() {
    playbackTimer = setInterval(function() {
        const rows = getRows();

        if (currentIndex >= rows.length - 1) {
            pauseReplay();
            return;
        }

        stepForward();
    }, playbackIntervalMs);
}

function playReplay() {
    stopLiveMode();
    setModeLabel("REPLAY");

    if (playbackTimer !== null) {
        return;
    }

    startPlaybackTimer();
}

function pauseReplay() {
    if (playbackTimer !== null) {
        clearInterval(playbackTimer);
        playbackTimer = null;
    }
}

function setPlaybackSpeed(intervalMs) {
    playbackIntervalMs = intervalMs;

    const wasPlaying = playbackTimer !== null;

    pauseReplay();
    updateReplayStatus();

    if (wasPlaying) {
        startPlaybackTimer();
    }
}

function bindReplayControls() {
    document.getElementById("play-button").addEventListener(
        "click",
        playReplay
    );

    document.getElementById("pause-button").addEventListener(
        "click",
        pauseReplay
    );

    document.getElementById("step-forward-button").addEventListener(
        "click",
        stepForward
    );

    document.getElementById("step-backward-button").addEventListener(
        "click",
        stepBackward
    );

    document.getElementById("speed-1x-button").addEventListener(
        "click",
        function() {
            setPlaybackSpeed(1000);
        }
    );

    document.getElementById("speed-5x-button").addEventListener(
        "click",
        function() {
            setPlaybackSpeed(500);
        }
    );

    document.getElementById("speed-20x-button").addEventListener(
        "click",
        function() {
            setPlaybackSpeed(100);
        }
    );

    document.getElementById("speed-100x-button").addEventListener(
        "click",
        function() {
            setPlaybackSpeed(25);
        }
    );
}
