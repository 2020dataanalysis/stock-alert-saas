let currentIndex = 0;
let playbackTimer = null;
let playbackIntervalMs = 500;
let showShockMarkers = true;
let liveTimer = null;
let liveDataBuffer = [];

function getRows() {
    return Array.from(
        document.querySelectorAll("[data-replay-row]")
    );
}

function getReplayData() {
    return getRows().map(function(row, index) {
        return {
            index: index,
            price: Number(row.dataset.price),
            shock: Number(row.dataset.shock),
            trend: Number(row.dataset.trend),
            noise: Number(row.dataset.noise),
            state: row.dataset.state,
            permission: row.dataset.permission
        };
    });
}

function getChartData() {
    if (liveDataBuffer.length > 0) {
        return liveDataBuffer.map(function(point, index) {
            return {
                index: index,
                price: point.price,
                shock: point.shock,
                trend: point.trend,
                noise: point.noise,
                state: point.state,
                permission: point.permission
            };
        });
    }

    return getReplayData();
}

function clearActiveRows() {
    getRows().forEach(function(row) {
        row.classList.remove("active-row");
    });
}

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

function buildChartScales(data) {
    const width = 1000;
    const height = 300;
    const padding = 20;

    const prices = data.map(function(point) {
        return point.price;
    });

    const minPrice = Math.min.apply(null, prices);
    const maxPrice = Math.max.apply(null, prices);
    const priceRange = maxPrice - minPrice || 1;

    function xScale(index) {
        if (data.length === 1) {
            return padding;
        }

        return padding +
            (index / (data.length - 1)) *
            (width - padding * 2);
    }

    function yScale(price) {
        return height - padding -
            ((price - minPrice) / priceRange) *
            (height - padding * 2);
    }

    return {
        width: width,
        height: height,
        padding: padding,
        xScale: xScale,
        yScale: yScale
    };
}

function drawShockMarkers(svg, data, scales) {
    if (!showShockMarkers) {
        return;
    }

    data.forEach(function(point) {
        if (point.shock < 1.0) {
            return;
        }

        const marker = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "circle"
        );

        marker.setAttribute("cx", scales.xScale(point.index));
        marker.setAttribute("cy", scales.yScale(point.price));
        marker.setAttribute("r", Math.min(3 + point.shock, 12));
        marker.setAttribute("class", "shock-marker");
        marker.setAttribute("data-shock", point.shock.toFixed(2));

        svg.appendChild(marker);
    });
}

function drawPriceChart() {
    const svg = document.getElementById("price-chart");
    const data = getChartData();

    if (!svg || data.length === 0) {
        return;
    }

    svg.innerHTML = "";

    const scales = buildChartScales(data);

    const points = data.map(function(point) {
        return (
            scales.xScale(point.index) + "," +
            scales.yScale(point.price)
        );
    }).join(" ");

    const polyline = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "polyline"
    );

    polyline.setAttribute("points", points);
    polyline.setAttribute("class", "price-line");

    svg.appendChild(polyline);

    drawShockMarkers(svg, data, scales);

    const cursorLine = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line"
    );

    cursorLine.setAttribute("id", "price-cursor-line");
    cursorLine.setAttribute("class", "price-cursor");
    cursorLine.setAttribute("y1", scales.padding);
    cursorLine.setAttribute("y2", scales.height - scales.padding);

    svg.appendChild(cursorLine);

    const cursorDot = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "circle"
    );

    cursorDot.setAttribute("id", "price-cursor-dot");
    cursorDot.setAttribute("class", "price-dot");
    cursorDot.setAttribute("r", 5);

    svg.appendChild(cursorDot);

    updateChartCursor();
}

function updateChartCursor() {
    const data = getChartData();

    if (data.length === 0) {
        return;
    }

    const scales = buildChartScales(data);

    const index = liveDataBuffer.length > 0
        ? data.length - 1
        : currentIndex;

    const point = data[index];

    const x = scales.xScale(point.index);
    const y = scales.yScale(point.price);

    const cursorLine = document.getElementById(
        "price-cursor-line"
    );

    const cursorDot = document.getElementById(
        "price-cursor-dot"
    );

    if (cursorLine) {
        cursorLine.setAttribute("x1", x);
        cursorLine.setAttribute("x2", x);
    }

    if (cursorDot) {
        cursorDot.setAttribute("cx", x);
        cursorDot.setAttribute("cy", y);
    }
}

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

function getCurrentSymbol() {
    const symbolInput = document.querySelector(
        "input[name='symbol']"
    );

    if (!symbolInput) {
        return "TSLA";
    }

    return symbolInput.value || "TSLA";
}

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

function bindOverlayControls() {
    const shockToggle = document.getElementById(
        "toggle-shock-markers"
    );

    if (!shockToggle) {
        return;
    }

    shockToggle.addEventListener(
        "change",
        function() {
            showShockMarkers = shockToggle.checked;
            drawPriceChart();
            updateChartCursor();
        }
    );
}

function bindPlaybackControls() {
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

    document.getElementById("live-mode-button").addEventListener(
        "click",
        startLiveMode
    );

    document.getElementById("stop-live-button").addEventListener(
        "click",
        stopLiveMode
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

document.addEventListener("DOMContentLoaded", function() {
    drawPriceChart();
    showCurrentRow();
    bindOverlayControls();
    bindPlaybackControls();
});
