/*
|--------------------------------------------------------------------------
| File: live_mode.js
|--------------------------------------------------------------------------
| Live market-state polling and live chart buffer updates.
|--------------------------------------------------------------------------
*/

function appendLivePoint(result) {
    if (!result.features) {
        return;
    }

    liveDataBuffer.push({
        price: Number(result.price),
        shock: Number(result.features.shock_score),
        trend: Number(result.features.trend_score),
        noise: Number(result.features.noise_score),
        state: result.state,
        permission: result.trade_permission
    });

    if (liveDataBuffer.length > 200) {
        liveDataBuffer.shift();
    }
}

function fetchLatestMarketState() {
    const symbol = getCurrentSymbol();

    fetch("/api/market-state/latest?symbol=" + symbol)
        .then(function(response) {
            return response.json();
        })
        .then(function(result) {
            appendLivePoint(result);
            updateHudFromLiveResult(result);
            drawPriceChart();
            updateReplayStatus();
        })
        .catch(function(error) {
            console.error("Live market-state fetch failed:", error);
        });
}

function startLiveMode() {
    pauseReplay();
    setModeLabel("LIVE");

    if (liveTimer !== null) {
        return;
    }

    liveDataBuffer = [];

    fetchLatestMarketState();

    liveTimer = setInterval(function() {
        fetchLatestMarketState();
    }, 2000);
}

function stopLiveMode() {
    setModeLabel("REPLAY");

    if (liveTimer !== null) {
        clearInterval(liveTimer);
        liveTimer = null;
    }
}

function bindLiveModeControls() {
    document.getElementById("live-mode-button").addEventListener(
        "click",
        startLiveMode
    );

    document.getElementById("stop-live-button").addEventListener(
        "click",
        stopLiveMode
    );
}
