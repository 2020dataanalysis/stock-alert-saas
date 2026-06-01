let replaySessions = [];
let selectedSessionIndex = 0;

let replayChart = null;
let candleSeries = null;

let replayQuotes = [];
let replayStartTimestamp = null;
let replayCurrentTimestamp = null;
let replayTimer = null;

const REPLAY_TICK_MS = 250;

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function formatNumber(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return Number(value).toLocaleString();
}

function formatTimestamp(timestamp) {
    if (!timestamp) {
        return "";
    }

    return timestamp.replace("T", " ").replace("+00:00", "");
}

function formatDayOfWeek(tradeDate) {
    if (!tradeDate) {
        return "";
    }

    const date = new Date(`${tradeDate}T00:00:00`);

    return date.toLocaleDateString("en-US", {
        weekday: "long",
    });
}

function formatReplayTimestamp(unixMs) {
    if (!unixMs) {
        return "";
    }

    const date = new Date(unixMs);

    return date.toLocaleString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
    });
}

function buildQuoteUrl(symbol, tradeDate = null) {
    const params = new URLSearchParams();
    params.set("symbol", symbol);

    if (tradeDate) {
        params.set("trade_date", tradeDate);
    }

    return `/api/replay/quotes?${params.toString()}`;
}

function resizeChart() {
    if (!replayChart) {
        return;
    }

    replayChart.resize(900, 500);
}

function initializeChart() {
    const chartElement = document.getElementById("replay-chart");

    if (!chartElement || replayChart) {
        return;
    }

    replayChart = LightweightCharts.createChart(chartElement, {
        width: 900,
        height: 500,
        layout: {
            background: { color: "#111827" },
            textColor: "#d1d5db",
        },
        grid: {
            vertLines: { color: "#1f2937" },
            horzLines: { color: "#1f2937" },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            rightOffset: 5,
        },
    });

    candleSeries = replayChart.addSeries(
        LightweightCharts.CandlestickSeries
    );
}

function buildOneMinuteCandles(quotes) {
    const candleMap = new Map();

    quotes.forEach((quote) => {
        if (quote.last === null || quote.last === undefined) {
            return;
        }

        const quoteDate = new Date(quote.timestamp);
        quoteDate.setSeconds(0, 0);

        const time = Math.floor(quoteDate.getTime() / 1000);
        const price = Number(quote.last);

        if (!candleMap.has(time)) {
            candleMap.set(time, {
                time,
                open: price,
                high: price,
                low: price,
                close: price,
            });
            return;
        }

        const candle = candleMap.get(time);

        candle.high = Math.max(candle.high, price);
        candle.low = Math.min(candle.low, price);
        candle.close = price;
    });

    return Array.from(candleMap.values()).sort((a, b) => a.time - b.time);
}

function getVisibleReplayQuotes() {
    if (!replayCurrentTimestamp) {
        return [];
    }

    return replayQuotes.filter((quote) => {
        const quoteTime = new Date(quote.timestamp).getTime();
        return quoteTime <= replayCurrentTimestamp;
    });
}

function updatePlaybackStatus() {
    const statusElement = document.getElementById("replay-playback-status");

    if (!statusElement) {
        return;
    }

    if (!replayQuotes.length || !replayCurrentTimestamp) {
        statusElement.textContent = "Replay ready.";
        return;
    }

    const speedElement = document.getElementById("replay-speed");
    const speed = Number(speedElement.value || 1);

    const visibleQuotes = getVisibleReplayQuotes();

    statusElement.innerHTML = `
        <div><strong>Replay Time:</strong> ${formatReplayTimestamp(replayCurrentTimestamp)}</div>
        <div><strong>Replay Speed:</strong> ${speed}x</div>
        <div><strong>Visible Quotes:</strong> ${formatNumber(visibleQuotes.length)} / ${formatNumber(replayQuotes.length)}</div>
    `;
}

function renderReplayAtCurrentTime() {
    initializeChart();

    if (!candleSeries) {
        return;
    }

    const visibleQuotes = getVisibleReplayQuotes();
    const candles = buildOneMinuteCandles(visibleQuotes);

    candleSeries.setData(candles);

    requestAnimationFrame(() => {
        resizeChart();
        replayChart.timeScale().fitContent();
    });

    updatePlaybackStatus();
}

function resetReplay(quotes) {
    pauseReplay();

    replayQuotes = quotes;

    if (!replayQuotes.length) {
        replayStartTimestamp = null;
        replayCurrentTimestamp = null;
        renderReplayAtCurrentTime();
        return;
    }

    replayStartTimestamp = new Date(replayQuotes[0].timestamp).getTime();
    replayCurrentTimestamp = replayStartTimestamp;

    renderReplayAtCurrentTime();
}

function playReplay() {
    if (!replayQuotes.length || !replayCurrentTimestamp) {
        return;
    }

    pauseReplay();

    const lastTimestamp = new Date(
        replayQuotes[replayQuotes.length - 1].timestamp
    ).getTime();

    let lastRealTimestamp = Date.now();

    replayTimer = window.setInterval(() => {
        const now = Date.now();
        const realElapsedMs = now - lastRealTimestamp;

        lastRealTimestamp = now;

        const speedElement = document.getElementById("replay-speed");
        const speed = Number(speedElement.value || 1);

        const marketElapsedMs = realElapsedMs * speed;

        replayCurrentTimestamp = Math.min(
            replayCurrentTimestamp + marketElapsedMs,
            lastTimestamp
        );

        renderReplayAtCurrentTime();

        if (replayCurrentTimestamp >= lastTimestamp) {
            pauseReplay();
        }
    }, REPLAY_TICK_MS);
}

function pauseReplay() {
    if (replayTimer) {
        window.clearInterval(replayTimer);
        replayTimer = null;
    }
}

function renderSelectedSession(row) {
    const selectedSessionElement = document.getElementById("selected-session");

    selectedSessionElement.innerHTML = `
        <div><strong>Date:</strong> ${row.trade_date} (${formatDayOfWeek(row.trade_date)})</div>
        <div><strong>Start:</strong> ${formatTimestamp(row.first_quote)}</div>
        <div><strong>End:</strong> ${formatTimestamp(row.last_quote)}</div>
        <div><strong>Quotes:</strong> ${formatNumber(row.quote_count)}</div>
    `;
}

function updateSessionNavigationButtons() {
    const previousButton = document.getElementById("previous-session-button");
    const nextButton = document.getElementById("next-session-button");

    if (!previousButton || !nextButton) {
        return;
    }

    previousButton.disabled = selectedSessionIndex <= 0;
    nextButton.disabled = selectedSessionIndex >= replaySessions.length - 1;
}

function selectSession(index) {
    if (!replaySessions.length) {
        return;
    }

    if (index < 0 || index >= replaySessions.length) {
        return;
    }

    selectedSessionIndex = index;

    const selectedSession = replaySessions[selectedSessionIndex];

    renderSelectedSession(selectedSession);
    loadReplayQuotes(selectedSession.trade_date);
    updateSessionNavigationButtons();
}

async function loadReplaySummary() {
    const symbol = getQueryParam("symbol");
    const summaryElement = document.getElementById("replay-summary");

    if (!summaryElement) {
        return;
    }

    if (!symbol) {
        summaryElement.textContent = "No symbol selected.";
        return;
    }

    const response = await fetch(
        `/api/replay/summary?symbol=${encodeURIComponent(symbol)}`
    );

    const summary = await response.json();

    if (!summary.found) {
        summaryElement.textContent = summary.message;
        return;
    }

    summaryElement.innerHTML = `
        <div><strong>Symbol:</strong> ${summary.symbol}</div>
        <div><strong>Start Date:</strong> ${summary.start_date}</div>
        <div><strong>End Date:</strong> ${summary.end_date}</div>
        <div><strong>Start Time:</strong> ${summary.start_time}</div>
        <div><strong>End Time:</strong> ${summary.end_time}</div>
        <div><strong>Duration:</strong> ${summary.duration}</div>
        <div><strong>Data Points:</strong> ${formatNumber(summary.data_points)}</div>
    `;
}

async function loadReplayQuotes(tradeDate = null) {
    const symbol = getQueryParam("symbol");
    const dataInfoElement = document.getElementById("replay-data-info");

    if (!dataInfoElement || !symbol) {
        return;
    }

    dataInfoElement.textContent = "Loading quote data...";

    const response = await fetch(
        buildQuoteUrl(symbol, tradeDate)
    );

    const quotes = await response.json();

    if (!quotes.length) {
        dataInfoElement.textContent = "No quote data found.";
        resetReplay([]);
        return;
    }

    const firstQuote = quotes[0];
    const lastQuote = quotes[quotes.length - 1];

    const label = tradeDate
        ? `Loaded Quotes for ${tradeDate}`
        : "Loaded Quotes";

    dataInfoElement.innerHTML = `
        <div><strong>${label}:</strong> ${formatNumber(quotes.length)}</div>
        <div><strong>First Quote:</strong> ${formatTimestamp(firstQuote.timestamp)}</div>
        <div><strong>Last Quote:</strong> ${formatTimestamp(lastQuote.timestamp)}</div>
    `;

    resetReplay(quotes);
}

async function loadReplayDates() {
    const symbol = getQueryParam("symbol");
    const datesElement = document.getElementById("replay-dates");

    if (!datesElement || !symbol) {
        return;
    }

    const response = await fetch(
        `/api/replay/dates?symbol=${encodeURIComponent(symbol)}`
    );

    const dates = await response.json();

    if (!dates.length) {
        datesElement.textContent = "No replay sessions found.";
        return;
    }

    replaySessions = dates;

    datesElement.innerHTML = replaySessions.map((row, index) => {
        return `
            <button
                type="button"
                class="replay-session-button"
                data-session-index="${index}"
                style="display: block; margin-bottom: 8px;"
            >
                ${row.trade_date} (${formatNumber(row.quote_count)} quotes)
            </button>
        `;
    }).join("");

    document.querySelectorAll(".replay-session-button").forEach((button) => {
        button.addEventListener("click", () => {
            const index = Number(button.dataset.sessionIndex);
            selectSession(index);
        });
    });

    document.getElementById("previous-session-button").addEventListener("click", () => {
        selectSession(selectedSessionIndex - 1);
    });

    document.getElementById("next-session-button").addEventListener("click", () => {
        selectSession(selectedSessionIndex + 1);
    });

    selectSession(0);
}

document.getElementById("play-button").addEventListener("click", playReplay);
document.getElementById("pause-button").addEventListener("click", pauseReplay);

loadReplaySummary();
loadReplayDates();
