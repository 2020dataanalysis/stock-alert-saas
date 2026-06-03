function formatDate(value) {
    if (!value) {
        return "-";
    }

    return value.slice(0, 10);
}

function percentClass(value) {
    if (value > 0) {
        return "positive";
    }

    if (value < 0) {
        return "negative";
    }

    return "";
}

function formatNumber(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return value.toFixed(3);
}

function getGapRange() {
    const center = parseFloat(
        document.getElementById("gap-center").value
    );

    const tolerance = parseFloat(
        document.getElementById("gap-tolerance").value
    );

    return {
        lower: center - tolerance,
        upper: center + tolerance,
    };
}

function updateGapRangeLabel(lower, upper) {
    document.getElementById("gap-range-label").textContent =
        `Showing gaps from ${lower.toFixed(2)}% to ${upper.toFixed(2)}%`;
}

async function loadHealthTable() {
    const response = await fetch("/api/historical-data/health");
    const data = await response.json();

    const body = document.getElementById("health-body");
    body.innerHTML = "";

    for (const row of data.datasets) {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.symbol}</td>
            <td>${row.timeframe}</td>
            <td>${row.bar_count}</td>
            <td>${formatDate(row.earliest_timestamp)}</td>
            <td>${formatDate(row.latest_timestamp)}</td>
        `;

        body.appendChild(tr);
    }
}

async function loadGapStatisticsTable() {
    const range = getGapRange();

    updateGapRangeLabel(
        range.lower,
        range.upper
    );

    const response = await fetch(
        `/api/historical-data/watchlist/gaps/statistics?bucket_lower=${range.lower}&bucket_upper=${range.upper}&limit=500`
    );

    const data = await response.json();

    data.results.sort(
        (a, b) =>
            (b.average_day_return_pct ?? -999) -
            (a.average_day_return_pct ?? -999)
    );

    const body = document.getElementById("gap-body");
    body.innerHTML = "";

    for (const row of data.results) {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.symbol}</td>
            <td>${row.match_count}</td>
            <td class="${percentClass(row.average_day_return_pct)}">
                ${formatNumber(row.average_day_return_pct)}
            </td>
            <td class="negative">
                ${formatNumber(row.average_max_down_from_open_pct)}
            </td>
            <td class="positive">
                ${formatNumber(row.average_max_up_from_open_pct)}
            </td>
            <td>${row.green_day_pct ?? "-"}</td>
            <td>${row.red_day_pct ?? "-"}</td>
        `;

        body.appendChild(tr);
    }
}

async function loadOpeningSummaryTable() {
    const range = getGapRange();

    const response = await fetch(
        `/api/historical-data/watchlist/gaps/opening-summary?bucket_lower=${range.lower}&bucket_upper=${range.upper}&opening_minutes=30&limit=500`
    );

    const data = await response.json();

    data.results.sort(
        (a, b) =>
            (b.average_opening_return_pct ?? -999) -
            (a.average_opening_return_pct ?? -999)
    );

    const body = document.getElementById("opening-body");
    body.innerHTML = "";

    for (const row of data.results) {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.symbol}</td>
            <td>${row.match_count}</td>
            <td class="${percentClass(row.average_opening_return_pct)}">
                ${formatNumber(row.average_opening_return_pct)}
            </td>
            <td class="positive">
                ${formatNumber(row.average_opening_high_pct)}
            </td>
            <td class="negative">
                ${formatNumber(row.average_opening_low_pct)}
            </td>
            <td>${row.positive_opening_pct ?? "-"}</td>
            <td>${row.negative_opening_pct ?? "-"}</td>
        `;

        body.appendChild(tr);
    }
}

function refreshGapTables() {
    loadGapStatisticsTable();
    loadOpeningSummaryTable();
}

loadHealthTable();
refreshGapTables();
