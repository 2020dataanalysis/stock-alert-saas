let currentIndex = 0;
let playbackTimer = null;
let playbackIntervalMs = 500;

function getRows() {
    return Array.from(
        document.querySelectorAll("[data-replay-row]")
    );
}

function clearActiveRows() {
    const rows = getRows();

    rows.forEach(function(row) {
        row.classList.remove("active-row");
    });
}

function updateHudFromRow(row) {
    document.getElementById("hud-state").textContent =
        row.dataset.state;

    document.getElementById("hud-permission").textContent =
        row.dataset.permission;

    document.getElementById("hud-shock").textContent =
        Number(row.dataset.shock).toFixed(2);

    document.getElementById("hud-trend").textContent =
        Number(row.dataset.trend).toFixed(2);

    document.getElementById("hud-noise").textContent =
        Number(row.dataset.noise).toFixed(2);

    document.getElementById("hud-shock-bar").style.width =
        (Number(row.dataset.shock) * 20) + "%";

    document.getElementById("hud-trend-bar").style.width =
        (Number(row.dataset.trend) * 20) + "%";

    document.getElementById("hud-noise-bar").style.width =
        (Number(row.dataset.noise) * 20) + "%";
}

function updateReplayStatus() {
    const rows = getRows();

    const indexDisplay = document.getElementById(
        "replay-index"
    );

    const speedDisplay = document.getElementById(
        "replay-speed"
    );

    if (indexDisplay) {
        indexDisplay.textContent =
            (currentIndex + 1) + " / " + rows.length;
    }

    if (speedDisplay) {
        speedDisplay.textContent =
            playbackIntervalMs + "ms";
    }
}

function showCurrentRow() {
    const rows = getRows();

    if (rows.length === 0) {
        return;
    }

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
}

function stepForward() {
    const rows = getRows();

    if (currentIndex < rows.length - 1) {
        currentIndex += 1;
        showCurrentRow();
    }
}

function stepBackward() {
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

document.addEventListener("DOMContentLoaded", function() {
    showCurrentRow();

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
});
