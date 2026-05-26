/*
|--------------------------------------------------------------------------
| File: market_state.js
|--------------------------------------------------------------------------
| Page bootstrap for market-state replay/live UI.
|--------------------------------------------------------------------------
*/

document.addEventListener("DOMContentLoaded", function() {
    drawPriceChart();
    showCurrentRow();
    bindOverlayControls();
    bindReplayControls();
    bindLiveModeControls();
});
