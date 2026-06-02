let liveChart = null;

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

async function loadLiveChart(symbol) {
    const normalizedSymbol = symbol.trim().toUpperCase();

    if (!normalizedSymbol) {
        return;
    }

    document.getElementById(
        "manual-symbol-input"
    ).value = normalizedSymbol;

    document.getElementById(
        "selected-symbol-heading"
    ).textContent = `Live: ${normalizedSymbol}`;

    setStatus(`Loading ${normalizedSymbol}...`);

    const response = await fetch(
        `/api/chart-data/${normalizedSymbol}`
    );

    const data = await response.json();

    const prices = data.prices || [];
    const timestamps = data.timestamps || [];
    const alerts = data.alerts || [];

    if (!prices.length) {
        setStatus(`No chart data found for ${normalizedSymbol}.`);
        return;
    }

    const alertPoints = alerts.map((alert) => {
        if (alert.index === null || alert.index === undefined) {
            return null;
        }

        return {
            x: alert.index,
            y: prices[alert.index],
        };
    }).filter((point) => point !== null);

    const canvas = document.getElementById("live-chart");
    const ctx = canvas.getContext("2d");

    if (liveChart) {
        liveChart.destroy();
    }

    liveChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: timestamps,
            datasets: [
                {
                    label: normalizedSymbol,
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

    setStatus(
        `Loaded ${prices.length.toLocaleString()} points for ${normalizedSymbol}.`
    );
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

bindSymbolButtons();
