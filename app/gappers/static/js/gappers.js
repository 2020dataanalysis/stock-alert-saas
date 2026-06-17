function formatPercent(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    const prefix = value > 0 ? "+" : "";
    return `${prefix}${value.toFixed(2)}%`;
}

function formatNumber(value) {
    if (value === null || value === undefined) {
        return "-";
    }

    return Number(value).toLocaleString();
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

async function loadGappers() {
    const minimumGapPct = document.getElementById("minimum-gap-pct").value;
    const limit = document.getElementById("gappers-limit").value;

    const summary = document.getElementById("gappers-summary");
    const body = document.getElementById("gappers-body");

    body.innerHTML = `
        <tr>
            <td colspan="10">Loading gappers...</td>
        </tr>
    `;

    try {
        const response = await fetch(
            `/api/gappers?minimum_gap_pct=${minimumGapPct}&limit=${limit}`
        );

        if (!response.ok) {
            throw new Error("Failed to load gappers");
        }

        const data = await response.json();

        summary.textContent =
            `Source: ${data.source} | Movers checked: ${data.mover_count} | Gappers: ${data.gapper_count}`;

        if (!data.gappers.length) {
            body.innerHTML = `
                <tr>
                    <td colspan="10">No gappers found for this filter.</td>
                </tr>
            `;
            return;
        }

        body.innerHTML = data.gappers.map((row) => `
            <tr>
                <td>
                    <a href="/gappers/${row.symbol}/${row.trade_date}">
                        ${row.symbol}
                    </a>
                </td>
                <td class="${row.gap_pct > 0 ? "positive" : "negative"}">
                    ${formatPercent(row.gap_pct)}
                </td>
                <td>${row.direction}</td>
                <td>${row.previous_close ?? "-"}</td>
                <td>${row.open ?? "-"}</td>
                <td>${row.last ?? "-"}</td>
                <td class="${row.net_percent_change > 0 ? "positive" : "negative"}">
                    ${formatPercent(row.net_percent_change)}
                </td>
                <td>${formatNumber(row.volume)}</td>
                <td>${yesNo(row.is_shortable)}</td>
                <td>${yesNo(row.hard_to_borrow)}</td>
            </tr>
        `).join("");

    } catch (error) {
        body.innerHTML = `
            <tr>
                <td colspan="10">Error loading gappers.</td>
            </tr>
        `;
        console.error(error);
    }
}

function formatSnapshotTime(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}

async function loadGappersSnapshots() {
    const body = document.getElementById("gappers-snapshots-body");
    const summary = document.getElementById("gappers-snapshots-summary");

    if (!body) {
        return;
    }

    body.innerHTML = `
        <tr>
            <td colspan="8">Loading snapshots...</td>
        </tr>
    `;

    try {
        const response = await fetch("/api/gappers/snapshots?limit=25");

        if (!response.ok) {
            throw new Error("Failed to load gappers snapshots");
        }

        const data = await response.json();
        const snapshots = data.snapshots || [];

        if (summary) {
            summary.textContent = `Recent snapshots: ${snapshots.length}`;
        }

        if (!snapshots.length) {
            body.innerHTML = `
                <tr>
                    <td colspan="8">No snapshots saved yet.</td>
                </tr>
            `;
            return;
        }

        body.innerHTML = snapshots.map((snapshot) => {
            const url = `/api/gappers/snapshots/${snapshot.id}`;

            return `
                <tr>
                    <td>#${snapshot.id}</td>
                    <td>${formatSnapshotTime(snapshot.captured_at)}</td>
                    <td>${snapshot.snapshot_key}</td>
                    <td>${snapshot.gapper_count ?? "-"}</td>
                    <td>${snapshot.mover_count ?? "-"}</td>
                    <td>${snapshot.payload_hash_short ?? "-"}</td>
                    <td>
                        <a href="${url}" target="_blank">👁 View</a>
                    </td>
                    <td>
                        <a href="${url}/download">⬇ Export</a>
                    </td>
                </tr>
            `;
        }).join("");

    } catch (error) {
        body.innerHTML = `
            <tr>
                <td colspan="8">Error loading snapshots.</td>
            </tr>
        `;
        console.error(error);
    }
}

loadGappers();
loadGappersSnapshots();
