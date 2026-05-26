/*
|--------------------------------------------------------------------------
| File: event_log.js
|--------------------------------------------------------------------------
| Market event log polling and rendering.
|--------------------------------------------------------------------------
*/

function renderMarketEvents(events) {
    const container = document.getElementById(
        "market-event-log"
    );

    if (!container) {
        return;
    }

    if (!events || events.length === 0) {
        container.innerHTML =
            '<div class="event-log-empty">No events yet.</div>';
        return;
    }

    container.innerHTML = events.map(function(event) {
        return (
            '<div class="event-log-item">' +
            event.event_type +
            ' - ' +
            event.message +
            '</div>'
        );
    }).join("");
}

function fetchMarketEvents() {
    fetch("/api/market-state/events?limit=25")
        .then(function(response) {
            return response.json();
        })
        .then(function(result) {
            renderMarketEvents(result.events);
        })
        .catch(function(error) {
            console.error("Market event fetch failed:", error);
        });
}

function bindEventLogPolling() {
    fetchMarketEvents();

    setInterval(function() {
        fetchMarketEvents();
    }, 3000);
}
