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

function formatSignedPercent(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    const prefix = value > 0 ? "+" : "";
    return `${prefix}${value.toFixed(4)}%`;
}

function formatSignedDollars(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    const prefix = value > 0 ? "+" : "";
    return `${prefix}$${value.toFixed(4)}`;
}

function shortTime(timestamp) {
    if (!timestamp) {
        return "-";
    }

    return timestamp.slice(11, 19);
}

function yesNo(value) {
    if (value === true) {
        return "Yes";
    }

    if (value === false) {
        return "No";
    }

    return "-";
}

function renderDayProfileSummary(profile) {
    const summary = document.getElementById("day-profile-summary");
    const range = profile.range || {};
    const context = profile.prior_day_context || {};
    const volume = profile.volume || {};
    const quality = profile.data_quality || {};

    summary.innerHTML = `
        <h3>Summary</h3>

        <table>
            <tbody>
                <tr>
                    <th>Symbol</th>
                    <td>${profile.symbol}</td>
                    <th>Date</th>
                    <td>${profile.trade_date}</td>
                </tr>
                <tr>
                    <th>Raw Quotes</th>
                    <td>${profile.raw_quote_count}</td>
                    <th>Clean Quotes</th>
                    <td>${profile.clean_quote_count}</td>
                </tr>
                <tr>
                    <th>Bad Ticks</th>
                    <td>${profile.bad_tick_count}</td>
                    <th>Bad Tick Rate</th>
                    <td>${quality.bad_tick_rate_pct ?? "-"}%</td>
                </tr>
                <tr>
                    <th>Open</th>
                    <td>${range.open ?? "-"}</td>
                    <th>Close</th>
                    <td>${range.close ?? "-"}</td>
                </tr>
                <tr>
                    <th>High</th>
                    <td>${range.high ?? "-"}</td>
                    <th>Low</th>
                    <td>${range.low ?? "-"}</td>
                </tr>
                <tr>
                    <th>Range $</th>
                    <td>${formatSignedDollars(range.range_dollars)}</td>
                    <th>Range %</th>
                    <td>${formatSignedPercent(range.range_pct)}</td>
                </tr>
                <tr>
                    <th>Inside Day</th>
                    <td>${yesNo(context.inside_day)}</td>
                    <th>Outside Day</th>
                    <td>${yesNo(context.outside_day)}</td>
                </tr>
                <tr>
                    <th>Broke Prior High</th>
                    <td>${yesNo(context.broke_previous_high)}</td>
                    <th>Broke Prior Low</th>
                    <td>${yesNo(context.broke_previous_low)}</td>
                </tr>
                <tr>
                    <th>Volume Change</th>
                    <td>${volume.total_volume_change ?? "-"}</td>
                    <th>Max Volume Delta</th>
                    <td>${volume.max_delta ?? "-"}</td>
                </tr>
                <tr>
                    <th>Volume P90 Delta</th>
                    <td>${volume.p90_delta ?? "-"}</td>
                    <th>Volume P95 Delta</th>
                    <td>${volume.p95_delta ?? "-"}</td>
                </tr>
            </tbody>
        </table>
    `;
}

function renderDayProfileMoves(profile) {
    const body = document.getElementById("day-profile-moves-body");
    body.innerHTML = "";

    for (const row of profile.largest_move_windows || []) {
        const up = row.largest_up || {};
        const down = row.largest_down || {};
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.window}</td>
            <td class="positive">
                ${formatSignedDollars(up.move_dollars)}
                / ${formatSignedPercent(up.move_pct)}
            </td>
            <td>${shortTime(up.start_time)} → ${shortTime(up.end_time)}</td>
            <td class="negative">
                ${formatSignedDollars(down.move_dollars)}
                / ${formatSignedPercent(down.move_pct)}
            </td>
            <td>${shortTime(down.start_time)} → ${shortTime(down.end_time)}</td>
        `;

        body.appendChild(tr);
    }
}

async function loadDayProfile() {
    const symbol = document
        .getElementById("day-profile-symbol")
        .value
        .trim()
        .toUpperCase();

    const tradeDate = document
        .getElementById("day-profile-date")
        .value;

    if (!symbol || !tradeDate) {
        return;
    }

    const response = await fetch(
        `/api/statistics/day-profile?symbol=${symbol}&trade_date=${tradeDate}`
    );

    const profile = await response.json();

    renderDayProfileSummary(profile);
    renderDayProfileMoves(profile);
}

loadDayProfile();
