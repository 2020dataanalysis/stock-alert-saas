/*
|--------------------------------------------------------------------------
| File: hud.js
|--------------------------------------------------------------------------
| HUD value updates and market-state mode display.
|--------------------------------------------------------------------------
*/

function setHudValues(state, permission, shock, trend, noise) {
    document.getElementById("hud-state").textContent = state;
    document.getElementById("hud-permission").textContent = permission;

    document.getElementById("hud-shock").textContent =
        Number(shock).toFixed(2);

    document.getElementById("hud-trend").textContent =
        Number(trend).toFixed(2);

    document.getElementById("hud-noise").textContent =
        Number(noise).toFixed(2);

    document.getElementById("hud-shock-bar").style.width =
        (Number(shock) * 20) + "%";

    document.getElementById("hud-trend-bar").style.width =
        (Number(trend) * 20) + "%";

    document.getElementById("hud-noise-bar").style.width =
        (Number(noise) * 20) + "%";
}

function updateHudFromRow(row) {
    setHudValues(
        row.dataset.state,
        row.dataset.permission,
        row.dataset.shock,
        row.dataset.trend,
        row.dataset.noise
    );
}

function updateHudFromLiveResult(result) {
    if (!result.features) {
        return;
    }

    setHudValues(
        result.state,
        result.trade_permission,
        result.features.shock_score,
        result.features.trend_score,
        result.features.noise_score
    );
}

function setModeLabel(mode) {
    const modeElement = document.getElementById(
        "market-state-mode"
    );

    if (!modeElement) {
        return;
    }

    modeElement.textContent = mode;
}

function updateReplayStatus() {
    const rows = getRows();

    if (liveDataBuffer.length > 0) {
        document.getElementById("replay-index").textContent =
            liveDataBuffer.length + " live";

        document.getElementById("replay-speed").textContent =
            "LIVE";

        return;
    }

    document.getElementById("replay-index").textContent =
        (currentIndex + 1) + " / " + rows.length;

    document.getElementById("replay-speed").textContent =
        playbackIntervalMs + "ms";
}
