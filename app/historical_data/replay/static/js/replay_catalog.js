async function loadReplayCatalog() {
    const tableBody = document.getElementById("replay-catalog-body");

    try {
        const response = await fetch("/api/replay/catalog");

        if (!response.ok) {
            throw new Error("Failed to load replay catalog");
        }

        const rows = await response.json();

        if (!rows.length) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8">No replay data available.</td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = rows.map((row) => {
            const replayUrl = `/historical-data/replay?symbol=${encodeURIComponent(row.symbol)}`;

            return `
                <tr>
                    <td>${row.symbol}</td>
                    <td>${row.start_date}</td>
                    <td>${row.end_date}</td>
                    <td>${row.start_time}</td>
                    <td>${row.end_time}</td>
                    <td>${row.duration}</td>
                    <td>${row.data_points.toLocaleString()}</td>
                    <td>
                        <a href="${replayUrl}">Replay</a>
                    </td>
                </tr>
            `;
        }).join("");

    } catch (error) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8">Error loading replay catalog.</td>
            </tr>
        `;
        console.error(error);
    }
}

loadReplayCatalog();
