let currentIndex = 0;
let playbackTimer = null;
let playbackIntervalMs = 500;

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

function clearActiveRows() {
    getRows().forEach(function(row) {
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

    document.getElementById("replay-index").textContent =
        (currentIndex + 1) + " / " + rows.length;

    document.getElementById("replay-speed").textContent =
        playbackIntervalMs + "ms";
}

function drawPriceChart() {
    const svg = document.getElementById("price-chart");
    const data = getReplayData();

    if (!svg || data.length === 0) {
        return;
    }

    svg.innerHTML = "";

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

    const points = data.map(function(point) {
        return (
            xScale(point.index) + "," +
            yScale(point.price)
        );
    }).join(" ");

    const polyline = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "polyline"
    );

    polyline.setAttribute("points", points);
    polyline.setAttribute("class", "price-line");

    svg.appendChild(polyline);

    const cursorLine = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line"
    );

    cursorLine.setAttribute("id", "price-cursor-line");
    cursorLine.setAttribute("class", "price-cursor");
    cursorLine.setAttribute("y1", padding);
    cursorLine.setAttribute("y2", height - padding);

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
    const data = getReplayData();

    if (data.length === 0) {
        return;
    }

    const width = 1000;
    const height = 300;
    const padding = 20;

    const prices = data.map(function(point) {
        return point.price;
    });

    const minPrice = Math.min.apply(null, prices);
    const maxPrice = Math.max.apply(null, prices);
    const priceRange = maxPrice - minPrice || 1;

    const point = data[currentIndex];

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

    const x = xScale(point.index);
    const y = yScale(point.price);

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
    updateChartCursor();
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
    drawPriceChart();
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
