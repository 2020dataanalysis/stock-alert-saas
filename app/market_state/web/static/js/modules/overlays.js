/*
|--------------------------------------------------------------------------
| File: overlays.js
|--------------------------------------------------------------------------
| Chart overlay toggle bindings and overlay visibility state.
|--------------------------------------------------------------------------
*/

function bindOverlayControls() {
    const shockToggle = document.getElementById(
        "toggle-shock-markers"
    );

    if (!shockToggle) {
        return;
    }

    shockToggle.addEventListener(
        "change",
        function() {
            showShockMarkers = shockToggle.checked;
            drawPriceChart();
            updateChartCursor();
        }
    );
}
