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
                <td>${row.symbol}</td>
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

loadGappers();
