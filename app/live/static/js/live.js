let liveChart = null;
let selectedSymbol = null;
let refreshTimer = null;

const REFRESH_INTERVAL_MS = 5000;

function getManualSymbol() {
    const input = document.getElementById(
        "manual-symbol-input"
    );

    return input.value.trim().toUpperCase();
}

function setStatus(message) {
    document.getElementById(
        "live-chart-status"
    ).textContent = message;
}

async function fetchChartData(symbol) {
    const response = await fetch(
        `/api/chart-data/${symbol}`
    );

    return response.json();
}

function buildAlertPoints(alerts, prices) {
    return alerts.map((alert) => {
        if (alert.index === null || alert.index === undefined) {
            return null;
        }

        return {
            x: alert.index,
            y: prices[alert.index],
        };
    }).filter((point) => point !== null);
}

function renderChart(symbol, data) {
    const prices = data.prices || [];
    const timestamps = data.timestamps || [];
    const alerts = data.alerts || [];

    if (!prices.length) {
        setStatus(`No chart data found for ${symbol}.`);
        return;
    }

    const alertPoints = buildAlertPoints(
        alerts,
        prices
    );

    const canvas = document.getElementById("live-chart");
    const ctx = canvas.getContext("2d");

    if (!liveChart) {
        liveChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: timestamps,
                datasets: [
                    {
                        label: symbol,
                        data: prices,
                        borderWidth: 2,
                        tension: 0.2,
                    },
                    {
                        label: "Alerts",
                        data: alertPoints,
                        pointRadius: 6,
                        showLine: false,
                    },
                ],
            },
            options: {
                responsive: true,
                animation: false,
                scales: {
                    x: {
                        display: false,
                    },
                },
            },
        });

        return;
    }

    liveChart.data.labels = timestamps;
    liveChart.data.datasets[0].label = symbol;
    liveChart.data.datasets[0].data = prices;
    liveChart.data.datasets[1].data = alertPoints;
    liveChart.update("none");
}







async function refreshSelectedChart() {
    if (!selectedSymbol) {
        return;
    }

    const data = await fetchChartData(
        selectedSymbol
    );

    renderChart(
        selectedSymbol,
        data
    );

    updateQuoteHeader(
        selectedSymbol,
        data
    );

    setStatus(
        `Loaded ${(data.prices || []).length.toLocaleString()} points for ${selectedSymbol}. Auto-refreshing every ${REFRESH_INTERVAL_MS / 1000}s.`
    );
}







function startAutoRefresh() {
    stopAutoRefresh();

    refreshTimer = window.setInterval(() => {
        refreshSelectedChart();
    }, REFRESH_INTERVAL_MS);
}

function stopAutoRefresh() {
    if (refreshTimer) {
        window.clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

async function loadLiveChart(symbol) {
    const normalizedSymbol = symbol.trim().toUpperCase();

    if (!normalizedSymbol) {
        return;
    }

    selectedSymbol = normalizedSymbol;

    document.getElementById(
        "manual-symbol-input"
    ).value = normalizedSymbol;

    document.getElementById(
        "selected-symbol-heading"
    ).textContent = `Live: ${normalizedSymbol}`;

    setStatus(`Loading ${normalizedSymbol}...`);

    await refreshSelectedChart();

    startAutoRefresh();
}

function bindSymbolButtons() {
    document
        .querySelectorAll(".symbol-button")
        .forEach((button) => {
            button.onclick = () => {
                loadLiveChart(button.dataset.symbol);
            };
        });
}

document
    .getElementById("load-symbol-button")
    .addEventListener("click", () => {
        loadLiveChart(getManualSymbol());
    });

document
    .getElementById("add-favorite-button")
    .addEventListener("click", () => {
        const symbol = getManualSymbol();

        if (!symbol) {
            return;
        }

        alert(`Add to Favorites coming later: ${symbol}`);
    });




function updateQuoteHeader(
    symbol,
    data
) {
    const prices = data.prices || [];
    const timestamps = data.timestamps || [];

    if (!prices.length) {
        return;
    }

    const latestPrice =
        prices[prices.length - 1];

    const firstPrice =
        prices[0];

    const change =
        latestPrice - firstPrice;

    const changePct =
        firstPrice === 0
            ? 0
            : (change / firstPrice) * 100;

    const latestTimestamp =
        timestamps[timestamps.length - 1];

    document.getElementById(
        "quote-header"
    ).innerHTML = `
        <div><strong>${symbol}</strong></div>
        <div>Price: ${latestPrice.toFixed(2)}</div>
        <div>Change: ${change.toFixed(2)}</div>
        <div>Change %: ${changePct.toFixed(2)}%</div>
        <div>Points: ${prices.length.toLocaleString()}</div>
        <div>Last Quote: ${latestTimestamp}</div>
    `;
}






bindSymbolButtons();
