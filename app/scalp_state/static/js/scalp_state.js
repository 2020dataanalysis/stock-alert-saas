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
                <td class="${row.state}">${row.state}</td>
                <td>${row.previous_state ?? "-"}</td>
                <td>${row.duration_seconds}s</td>
                <td>${row.state_changed ? "🔥" : "-"}</td>
                <td class="score">${row.score}</td>
                <td class="${row.action}">${row.action}</td>
                <td>${row.range_pct ?? "-"}</td>
                <td>${row.latest ?? "-"}</td>
                <td>${row.volume_samples ?? "-"}</td>
                <td>${row.reason}</td>
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

            tr.innerHTML = `
                <td>${transition.timestamp}</td>
                <td>${transition.symbol}</td>
                <td>${transition.previous_state ?? "-"}</td>
                <td class="${transition.current_state}">
                    ${transition.current_state}
                </td>
                <td>${transition.transition_type ?? "-"}</td>
                <td class="${transition.priority}">
                    ${transition.priority ?? "-"}
                </td>
                <td>${transition.duration_seconds}s</td>
                <td>${transition.score}</td>
                <td>${transition.range_pct ?? "-"}</td>
            `;

            tbody.appendChild(tr);
        }
    } catch (err) {
        console.error("Failed loading state transitions:", err);
    }
}


loadScalpState();
loadStateTransitions();

setInterval(loadScalpState, 5000);
setInterval(loadStateTransitions, 5000);