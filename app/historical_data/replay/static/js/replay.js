let replaySessions = [];
let selectedSessionIndex = 0;

let replayChart = null;
let candleSeries = null;
let replayMarkersPlugin = null;

let replayQuotes = [];
let replaySimulatedAlerts = [];
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

function formatSessionCardDate(tradeDate) {
    const date = new Date(`${tradeDate}T00:00:00`);

    return date.toLocaleDateString("en-US", {
        weekday: "short",
        month: "short",
        day: "numeric",
    });
}

function formatMonthHeading(tradeDate) {
    const date = new Date(`${tradeDate}T00:00:00`);

    return date.toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
    });
}

function getWeekStartDate(tradeDate) {
    const date = new Date(`${tradeDate}T00:00:00`);
    const day = date.getDay();
    const diffToMonday = day === 0 ? -6 : 1 - day;

    date.setDate(date.getDate() + diffToMonday);

    return date;
}

function formatWeekHeading(tradeDate) {
    const weekStart = getWeekStartDate(tradeDate);

    return `Week of ${weekStart.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
    })}`;
}

function formatPacificTime(timestamp) {
    if (!timestamp) {
        return "";
    }

    const date = new Date(timestamp);

    return date.toLocaleTimeString("en-US", {
        timeZone: "America/Los_Angeles",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function formatSessionTimeRange(row) {
    return `${formatPacificTime(row.first_quote)} → ${formatPacificTime(row.last_quote)} PT`;
}

function groupReplaySessionsByMonthAndWeek(sessions) {
    const grouped = [];

    sessions.forEach((row, index) => {
        const monthKey = row.trade_date.slice(0, 7);
        const weekStart = getWeekStartDate(row.trade_date);
        const weekKey = weekStart.toISOString().slice(0, 10);

        let monthGroup = grouped.find((group) => group.key === monthKey);

        if (!monthGroup) {
            monthGroup = {
                key: monthKey,
                label: formatMonthHeading(row.trade_date),
                weeks: [],
            };
            grouped.push(monthGroup);
        }

        let weekGroup = monthGroup.weeks.find((week) => week.key === weekKey);

        if (!weekGroup) {
            weekGroup = {
                key: weekKey,
                label: formatWeekHeading(row.trade_date),
                sessions: [],
            };
            monthGroup.weeks.push(weekGroup);
        }

        weekGroup.sessions.push({
            ...row,
            index,
        });
    });

    return grouped;
}

function renderReplaySessionCards() {
    const datesElement = document.getElementById("replay-dates");

    if (!datesElement) {
        return;
    }

    const groups = groupReplaySessionsByMonthAndWeek(replaySessions);

    datesElement.innerHTML = groups.map((monthGroup) => {
        const weeksHtml = monthGroup.weeks.map((weekGroup) => {
            const cardsHtml = weekGroup.sessions.map((row) => {
                const selectedClass = row.index === selectedSessionIndex
                    ? " selected"
                    : "";

                const selectedText = row.index === selectedSessionIndex
                    ? `<div style="margin-top: 6px; font-weight: 700;">✓ Selected</div>`
                    : "";

                return `
                    <button
                        type="button"
                        class="replay-session-card${selectedClass}"
                        data-session-index="${row.index}"
                    >
                        <div style="font-weight: 700;">
                            ${formatSessionCardDate(row.trade_date)}
                        </div>
                        <div>
                            ${formatNumber(row.quote_count)} quotes
                        </div>
                        <div style="font-size: 0.9em; opacity: 0.85;">
                            ${formatSessionTimeRange(row)}
                        </div>
                        ${selectedText}
                    </button>
                `;
            }).join("");

            return `
                <div style="margin-top: 16px;">
                    <div style="font-weight: 700; margin-bottom: 8px;">
                        ${weekGroup.label}
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        ${cardsHtml}
                    </div>
                </div>
            `;
        }).join("");

        return `
            <section style="margin-top: 24px;">
                <h3>${monthGroup.label}</h3>
                ${weeksHtml}
            </section>
        `;
    }).join("");

    document.querySelectorAll(".replay-session-card").forEach((button) => {
        button.addEventListener("click", () => {
            const index = Number(button.dataset.sessionIndex);
            selectSession(index);
        });
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

function buildReplayDownloadUrl(symbol, tradeDate = null, format = "csv") {
    const params = new URLSearchParams();
    params.set("symbol", symbol);
    params.set("format", format);

    if (tradeDate) {
        params.set("trade_date", tradeDate);
    }

    return `/api/replay/quotes?${params.toString()}`;
}

function buildMarketDataDownloadUrl(symbol, days = 10, format = "csv") {
    const params = new URLSearchParams();
    params.set("days", String(days));
    params.set("interval", "1m");
    params.set("need_extended_hours_data", "true");
    params.set("format", format);

    return `/api/market-data/history/${encodeURIComponent(symbol)}?${params.toString()}`;
}

function updateReplayDownloadLinks(tradeDate = null) {
    const symbol = getQueryParam("symbol");

    const sessionCsvLink = document.getElementById("download-session-csv-link");
    const symbolCsvLink = document.getElementById("download-symbol-csv-link");
    const allDataLink = document.getElementById("download-all-symbol-data-link");

    if (!symbol || !sessionCsvLink || !symbolCsvLink || !allDataLink) {
        return;
    }

    sessionCsvLink.href = buildReplayDownloadUrl(symbol, tradeDate, "csv");
    symbolCsvLink.href = buildMarketDataDownloadUrl(symbol, 10, "csv");
    allDataLink.href = buildReplayDownloadUrl(symbol, null, "csv");

    const latestTradeDate = replaySessions.length
        ? replaySessions[replaySessions.length - 1].trade_date
        : null;

    sessionCsvLink.textContent = tradeDate === latestTradeDate
        ? `Export Today (${tradeDate})`
        : tradeDate
            ? `Export ${tradeDate}`
            : "Export Session";

    symbolCsvLink.textContent = "Export Last 10 Days";
    allDataLink.textContent = "Export All Data";
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


function getVisibleReplayAlerts() {
    if (!replayCurrentTimestamp) {
        return [];
    }

    return replaySimulatedAlerts.filter((alert) => {
        const alertTime = new Date(alert.timestamp).getTime();
        return alertTime <= replayCurrentTimestamp;
    });
}

function renderReplayAlertsTable() {
    const tableBody = document.getElementById("replay-alerts-body");

    if (!tableBody) {
        return;
    }

    const visibleAlerts = getVisibleReplayAlerts();

    if (!visibleAlerts.length) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7">No replay alerts fired yet.</td>
            </tr>
        `;
        return;
    }

    tableBody.innerHTML = visibleAlerts.slice(-50).reverse().map((alert) => {
        const details = alert.details || {};

        return `
            <tr>
                <td>${formatTimestamp(alert.timestamp)}</td>
                <td>${alert.symbol}</td>
                <td>${alert.rule_type}</td>
                <td>${alert.direction}</td>
                <td>${Number(alert.last).toFixed(2)}</td>
                <td>${details.price_change_pct ?? ""}%</td>
                <td>${details.volume_change_pct ?? ""}%</td>
            </tr>
        `;
    }).join("");
}


function setReplayPlaybackState(state) {
    const playButton = document.getElementById("play-button");
    const pauseButton = document.getElementById("pause-button");

    if (!playButton || !pauseButton) {
        return;
    }

    playButton.dataset.replayState = state;
    pauseButton.dataset.replayState = state;

    if (state === "playing") {
        playButton.disabled = true;
        playButton.textContent = "Playing...";
        playButton.style.opacity = "0.55";
        playButton.style.cursor = "not-allowed";
        playButton.style.background = "#4b5563";

        pauseButton.disabled = false;
        pauseButton.textContent = "Pause";
        pauseButton.style.opacity = "1";
        pauseButton.style.cursor = "pointer";
        pauseButton.style.background = "#2563eb";
        return;
    }

    if (state === "finished") {
        playButton.disabled = false;
        playButton.textContent = "Replay Finished";
        playButton.style.opacity = "0.85";
        playButton.style.cursor = "pointer";
        playButton.style.background = "#6b7280";

        pauseButton.disabled = true;
        pauseButton.textContent = "Pause";
        pauseButton.style.opacity = "0.55";
        pauseButton.style.cursor = "not-allowed";
        pauseButton.style.background = "#4b5563";
        return;
    }

    playButton.disabled = false;
    playButton.textContent = "Play";
    playButton.style.opacity = "1";
    playButton.style.cursor = "pointer";
    playButton.style.background = "#16a34a";

    pauseButton.disabled = true;
    pauseButton.textContent = "Pause";
    pauseButton.style.opacity = "0.55";
    pauseButton.style.cursor = "not-allowed";
    pauseButton.style.background = "#4b5563";
}

function getReplayAlertMarkerTime(alert) {
    const alertDate = new Date(alert.timestamp);
    alertDate.setSeconds(0, 0);
    return Math.floor(alertDate.getTime() / 1000);
}

function buildReplayAlertMarkers() {
    return getVisibleReplayAlerts().slice(-200).map((alert) => {
        const isDrop = alert.direction === "down";

        return {
            time: getReplayAlertMarkerTime(alert),
            position: isDrop ? "belowBar" : "aboveBar",
            shape: isDrop ? "arrowDown" : "arrowUp",
            color: isDrop ? "#ef4444" : "#22c55e",
            text: isDrop ? "Drop" : "Spike",
        };
    });
}

function applyReplayAlertMarkers() {
    if (!candleSeries) {
        return;
    }

    const markers = buildReplayAlertMarkers();

    if (
        window.LightweightCharts &&
        typeof LightweightCharts.createSeriesMarkers === "function"
    ) {
        if (replayMarkersPlugin && typeof replayMarkersPlugin.setMarkers === "function") {
            replayMarkersPlugin.setMarkers(markers);
            return;
        }

        replayMarkersPlugin = LightweightCharts.createSeriesMarkers(
            candleSeries,
            markers
        );
        return;
    }

    if (typeof candleSeries.setMarkers === "function") {
        candleSeries.setMarkers(markers);
    }
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
    const visibleAlerts = getVisibleReplayAlerts();

    statusElement.innerHTML = `
        <div><strong>Replay Time:</strong> ${formatReplayTimestamp(replayCurrentTimestamp)}</div>
        <div><strong>Replay Speed:</strong> ${speed}x</div>
        <div><strong>Visible Quotes:</strong> ${formatNumber(visibleQuotes.length)} / ${formatNumber(replayQuotes.length)}</div>
        <div><strong>Replay Alerts Fired:</strong> ${formatNumber(visibleAlerts.length)} / ${formatNumber(replaySimulatedAlerts.length)}</div>
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
    applyReplayAlertMarkers();

    requestAnimationFrame(() => {
        resizeChart();
        replayChart.timeScale().fitContent();
    });

    updatePlaybackStatus();
    renderReplayAlertsTable();
}

function resetReplay(quotes) {
    pauseReplay();

    replayQuotes = quotes;

    if (!replayQuotes.length) {
        replayStartTimestamp = null;
        replayCurrentTimestamp = null;
        setReplayPlaybackState("paused");
        renderReplayAtCurrentTime();
        return;
    }

    replayStartTimestamp = new Date(replayQuotes[0].timestamp).getTime();
    replayCurrentTimestamp = replayStartTimestamp;

    setReplayPlaybackState("paused");
    renderReplayAtCurrentTime();
}

function playReplay() {
    if (!replayQuotes.length || !replayCurrentTimestamp) {
        return;
    }

    pauseReplay();
    setReplayPlaybackState("playing");

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
            setReplayPlaybackState("finished");
        }
    }, REPLAY_TICK_MS);
}

function pauseReplay() {
    if (replayTimer) {
        window.clearInterval(replayTimer);
        replayTimer = null;
    }

    if (replayCurrentTimestamp && replayQuotes.length) {
        const lastTimestamp = new Date(
            replayQuotes[replayQuotes.length - 1].timestamp
        ).getTime();

        if (replayCurrentTimestamp >= lastTimestamp) {
            setReplayPlaybackState("finished");
            return;
        }
    }

    setReplayPlaybackState("paused");
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
    updateReplayDownloadLinks(selectedSession.trade_date);
    renderReplaySessionCards();
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
        updateReplayDownloadLinks(null);
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

    const payload = await response.json();

    const quotes = payload.quotes || [];
    const simulatedAlerts = payload.simulated_alerts || [];

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
        <div><strong>Simulated Alerts:</strong> ${formatNumber(simulatedAlerts.length)}</div>
    `;

    replaySimulatedAlerts = simulatedAlerts;

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

    renderReplaySessionCards();

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

setReplayPlaybackState("paused");

loadReplaySummary();
loadReplayDates();
