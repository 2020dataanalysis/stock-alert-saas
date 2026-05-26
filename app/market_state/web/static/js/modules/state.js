/*
|--------------------------------------------------------------------------
| File: state.js
|--------------------------------------------------------------------------
| Shared browser-side state for market-state replay/live UI.
|--------------------------------------------------------------------------
*/

let currentIndex = 0;
let playbackTimer = null;
let playbackIntervalMs = 500;
let showShockMarkers = true;
let liveTimer = null;
let liveDataBuffer = [];
