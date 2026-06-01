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

function renderSelectedSession(row) {
    const selectedSessionElement = document.getElementById("selected-session");

    selectedSessionElement.innerHTML = `
        <div><strong>Date:</strong> ${row.trade_date}</div>
        <div><strong>Start:</strong> ${formatTimestamp(row.first_quote)}</div>
        <div><strong>End:</strong> ${formatTimestamp(row.last_quote)}</div>
        <div><strong>Quotes:</strong> ${formatNumber(row.quote_count)}</div>
    `;
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

async function loadReplayQuotes() {
    const symbol = getQueryParam("symbol");
    const dataInfoElement = document.getElementById("replay-data-info");

    if (!dataInfoElement || !symbol) {
        return;
    }

    const response = await fetch(
        `/api/replay/quotes?symbol=${encodeURIComponent(symbol)}`
    );

    const quotes = await response.json();

    if (!quotes.length) {
        dataInfoElement.textContent = "No quote data found.";
        return;
    }

    const firstQuote = quotes[0];
    const lastQuote = quotes[quotes.length - 1];

    dataInfoElement.innerHTML = `
        <div><strong>Loaded Quotes:</strong> ${formatNumber(quotes.length)}</div>
        <div><strong>First Quote:</strong> ${formatTimestamp(firstQuote.timestamp)}</div>
        <div><strong>Last Quote:</strong> ${formatTimestamp(lastQuote.timestamp)}</div>
    `;
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

    datesElement.innerHTML = dates.map((row, index) => {
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
            renderSelectedSession(dates[index]);
        });
    });
}

loadReplaySummary();
loadReplayQuotes();
loadReplayDates();
