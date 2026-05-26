let currentIndex = 0;
let playbackTimer = null;

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

    row.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
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

function playReplay() {
    if (playbackTimer !== null) {
        return;
    }

    playbackTimer = setInterval(function() {
        const rows = getRows();

        if (currentIndex >= rows.length - 1) {
            pauseReplay();
            return;
        }

        stepForward();
    }, 500);
}

function pauseReplay() {
    if (playbackTimer !== null) {
        clearInterval(playbackTimer);
        playbackTimer = null;
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
});
