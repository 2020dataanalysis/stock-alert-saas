let audioAlertsEnabled = false;
let audioContext = null;
let seenTransitionKeys = new Set();


function enableAudioAlerts() {
    audioAlertsEnabled = true;

    audioContext = new (
        window.AudioContext ||
        window.webkitAudioContext
    )();

    audioContext.resume();

    const button = document.getElementById("enable-audio-button");

    if (button) {
        button.textContent = "Audio Alerts Enabled";
        button.disabled = true;
    }

    playTone(660, 120);
}


function playTone(frequency, durationMs) {
    if (!audioAlertsEnabled || !audioContext) {
        return;
    }

    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.frequency.value = frequency;
    oscillator.type = "sine";

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    gainNode.gain.setValueAtTime(
        0.2,
        audioContext.currentTime
    );

    oscillator.start();

    oscillator.stop(
        audioContext.currentTime + durationMs / 1000
    );
}


function playTransitionAlert(transition) {
    if (!audioAlertsEnabled) {
        return;
    }

    if (
        transition.priority === "HIGH" &&
        transition.current_state === "ACTIVE_EXPANSION"
    ) {
        playTone(880, 180);

        setTimeout(
            () => playTone(1175, 180),
            220
        );
    }
}


function getTransitionKey(transition) {
    return [
        transition.timestamp,
        transition.symbol,
        transition.previous_state,
        transition.current_state,
        transition.transition_type
    ].join("|");
}


function isActionableTransition(transition) {
    return (
        transition.priority === "HIGH" &&
        transition.current_state === "ACTIVE_EXPANSION"
    );
}


function handleNewTransitions(transitions) {
    for (const transition of transitions) {
        const key = getTransitionKey(transition);

        if (seenTransitionKeys.has(key)) {
            continue;
        }

        seenTransitionKeys.add(key);

        if (!isActionableTransition(transition)) {
            continue;
        }

        playTransitionAlert(transition);
    }
}


async function loadScalpState() {
    try {
        const response = await fetch("/api/scalp-state");
        const data = await response.json();

        const tbody = document.getElementById("scalp-state-body");
        tbody.innerHTML = "";

        for (const row of data.rows) {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${row.symbol}</td>

                <td class="${row.state}">
                    ${row.state}
                </td>

                <td>
                    ${row.previous_state ?? "-"}
                </td>

                <td>
                    ${row.duration_seconds ?? "-"}s
                </td>

                <td>
                    ${row.state_changed ? "🔥" : "-"}
                </td>

                <td class="score">
                    ${row.score}
                </td>

                <td class="${row.action}">
                    ${row.action}
                </td>

                <td>
                    ${row.range_pct ?? "-"}
                </td>


                <td>
                    ${row.range_velocity ?? "-"}
                </td>

                <td>
                    ${row.older_range_pct ?? "-"}
                </td>

                <td>
                    ${row.recent_range_pct ?? "-"}
                </td>


                <td>
                    ${row.latest ?? "-"}
                </td>

                <td>
                    ${row.volume_samples ?? "-"}
                </td>

                <td>
                    ${row.reason}
                </td>
            `;

            tbody.appendChild(tr);
        }

    } catch (err) {
        console.error("Failed loading scalp state:", err);
    }
}


async function loadStateTransitions() {
    try {
        const response = await fetch("/api/scalp-state/transitions");
        const data = await response.json();

        const tbody = document.getElementById("transition-body");
        tbody.innerHTML = "";

        for (const transition of data.transitions) {
            const tr = document.createElement("tr");

            if (isActionableTransition(transition)) {
                tr.classList.add("flash-row");
            }

            tr.innerHTML = `
                <td>${transition.timestamp}</td>

                <td>
                    ${transition.symbol}
                </td>

                <td>
                    ${transition.previous_state ?? "-"}
                </td>

                <td class="${transition.current_state}">
                    ${transition.current_state}
                </td>

                <td>
                    ${transition.transition_type ?? "-"}
                </td>

                <td class="${transition.priority}">
                    ${transition.priority ?? "-"}
                </td>

                <td>
                    ${transition.duration_seconds ?? "-"}s
                </td>

                <td>
                    ${transition.score}
                </td>

                <td>
                    ${transition.range_pct ?? "-"}
                </td>
            `;

            tbody.appendChild(tr);
        }

        handleNewTransitions(data.transitions);

    } catch (err) {
        console.error("Failed loading state transitions:", err);
    }
}


document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("enable-audio-button");

    if (button) {
        button.addEventListener("click", enableAudioAlerts);
    }

    loadScalpState();
    loadStateTransitions();

    setInterval(loadScalpState, 5000);
    setInterval(loadStateTransitions, 5000);
});