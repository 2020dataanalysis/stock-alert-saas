let replaySessions = [];
let selectedSessionIndex = 0;
let replayChart = null;
let candleSeries = null;

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


function buildQuoteUrl(symbol, tradeDate = null) {
    const params = new URLSearchParams();
    params.set("symbol", symbol);

    if (tradeDate) {
        params.set("trade_date", tradeDate);
    }

    return `/api/replay/quotes?${params.toString()}`;
}

function resizeChart() {
    const chartElement = document.getElementById("replay-chart");

    if (!replayChart || !chartElement) {
        return;
    }

    const width = chartElement.getBoundingClientRect().width;

    replayChart.resize(width, 500);
}

function initializeChart() {
    const chartElement = document.getElementById("replay-chart");

    if (!chartElement || replayChart) {
        return;
    }

    const width = chartElement.getBoundingClientRect().width;

    replayChart = LightweightCharts.createChart(chartElement, {
        width: width,
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
            rightOffset: 0,
        },
    });

    candleSeries = replayChart.addSeries(
        LightweightCharts.CandlestickSeries
    );

    window.addEventListener("resize", resizeChart);
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



function renderChart(quotes) {
    initializeChart();

    if (!candleSeries) {
        return;
    }

    const candles = buildOneMinuteCandles(quotes);

    candleSeries.setData(candles);

    requestAnimationFrame(() => {
        resizeChart();
        replayChart.timeScale().fitContent();
    });
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

    renderChart(quotes);
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

loadReplaySummary();
loadReplayDates();
