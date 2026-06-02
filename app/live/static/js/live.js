console.log("Live module loaded");

function getManualSymbol() {
    const input = document.getElementById(
        "manual-symbol-input"
    );

    return input.value.trim().toUpperCase();
}

function selectSymbol(symbol) {
    if (!symbol) {
        return;
    }

    document.getElementById(
        "manual-symbol-input"
    ).value = symbol;

    document.getElementById(
        "selected-symbol-heading"
    ).textContent = `Live: ${symbol}`;

    document.getElementById(
        "live-chart"
    ).innerHTML = `
        <div>
            Selected Symbol:
            <strong>${symbol}</strong>
        </div>
    `;
}

function bindSymbolButtons() {
    document
        .querySelectorAll(".symbol-button")
        .forEach((button) => {

            button.onclick = () => {
                selectSymbol(
                    button.dataset.symbol
                );
            };

        });
}

document
    .getElementById("load-symbol-button")
    .addEventListener("click", () => {

        selectSymbol(
            getManualSymbol()
        );

    });

document
    .getElementById("add-favorite-button")
    .addEventListener("click", () => {

        const symbol =
            getManualSymbol();

        if (!symbol) {
            return;
        }

        alert(
            `Add to Favorites coming later: ${symbol}`
        );

    });

bindSymbolButtons();
