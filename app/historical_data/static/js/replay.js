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

async function loadReplaySummary() {
    const symbol = getQueryParam("symbol");
    const summaryElement = document.getElementById("replay-summary");

    if (!summaryElement) {
        console.error("Missing replay-summary element");
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

    if (!dataInfoElement) {
        console.error("Missing replay-data-info element");
        return;
    }

    if (!symbol) {
        dataInfoElement.textContent = "No symbol selected.";
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
        <div><strong>First Quote:</strong> ${firstQuote.timestamp}</div>
        <div><strong>Last Quote:</strong> ${lastQuote.timestamp}</div>
    `;
}



async function loadReplayDates() {
    const symbol = getQueryParam("symbol");

    const datesElement =
        document.getElementById("replay-dates");

    if (!symbol) {
        return;
    }

    const response = await fetch(
        `/api/replay/dates?symbol=${encodeURIComponent(symbol)}`
    );

    const dates = await response.json();

    datesElement.innerHTML = dates.map(
        (row) => `
            <div>
                ${row.trade_date}
                (${row.quote_count.toLocaleString()} quotes)
            </div>
        `
    ).join("");
}


loadReplaySummary();
loadReplayQuotes();
loadReplayDates();