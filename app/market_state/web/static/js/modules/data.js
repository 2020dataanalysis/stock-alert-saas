/*
|--------------------------------------------------------------------------
| File: data.js
|--------------------------------------------------------------------------
| DOM row access and replay/live chart data shaping.
|--------------------------------------------------------------------------
*/

function getRows() {
    return Array.from(
        document.querySelectorAll("[data-replay-row]")
    );
}

function getReplayData() {
    return getRows().map(function(row, index) {
        return {
            index: index,
            price: Number(row.dataset.price),
            shock: Number(row.dataset.shock),
            trend: Number(row.dataset.trend),
            noise: Number(row.dataset.noise),
            state: row.dataset.state,
            permission: row.dataset.permission
        };
    });
}

function getChartData() {
    if (liveDataBuffer.length > 0) {
        return liveDataBuffer.map(function(point, index) {
            return {
                index: index,
                price: point.price,
                shock: point.shock,
                trend: point.trend,
                noise: point.noise,
                state: point.state,
                permission: point.permission
            };
        });
    }

    return getReplayData();
}

function getCurrentSymbol() {
    const symbolInput = document.querySelector(
        "input[name='symbol']"
    );

    if (!symbolInput) {
        return "TSLA";
    }

    return symbolInput.value || "TSLA";
}

function clearActiveRows() {
    getRows().forEach(function(row) {
        row.classList.remove("active-row");
    });
}
