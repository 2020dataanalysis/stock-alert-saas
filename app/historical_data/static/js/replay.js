function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function initializeReplayPage() {
    const symbol = getQueryParam("symbol");
    const symbolElement = document.getElementById("replay-symbol");

    symbolElement.textContent = symbol || "No symbol selected";

    console.log("Replay page initialized", {
        symbol,
    });
}

initializeReplayPage();
