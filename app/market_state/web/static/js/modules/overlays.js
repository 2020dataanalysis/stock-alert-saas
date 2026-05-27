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

    const stateToggle = document.getElementById(
        "toggle-state-markers"
    );

    const permissionToggle = document.getElementById(
        "toggle-permission-markers"
    );

    if (shockToggle) {
        shockToggle.addEventListener(
            "change",
            function() {
                showShockMarkers = shockToggle.checked;
                drawPriceChart();
                updateChartCursor();
            }
        );
    }

    if (stateToggle) {
        stateToggle.addEventListener(
            "change",
            function() {
                showStateMarkers = stateToggle.checked;
                drawPriceChart();
                updateChartCursor();
            }
        );
    }

    if (permissionToggle) {
        permissionToggle.addEventListener(
            "change",
            function() {
                showPermissionMarkers = permissionToggle.checked;
                drawPriceChart();
                updateChartCursor();
            }
        );
    }
}
