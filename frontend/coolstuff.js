document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector("#employee-status table");
    const tbody = table.querySelector("tbody");

    // Convert rows to an array
    const rows = Array.from(tbody.querySelectorAll("tr"));

    // Define the correct class and colors for each status
    const statusConfig = {
        danger:  { class: "danger",  text: "Danger",  color: "#ef4444", textColor: "white" },
        warning: { class: "warning", text: "Warning", color: "#facc15", textColor: "black" },
        normal:  { class: "normal",  text: "Normal",  color: "#22c55e", textColor: "white" }
    };

    // Priority order (lower number = higher priority)
    const priority = { danger: 1, warning: 2, normal: 3 };

    rows.forEach(row => {
        const statusEl = row.querySelector(".status");
        if (!statusEl) return;

        // Normalize text (remove spaces, lowercase)
        const text = statusEl.textContent.trim().toLowerCase();

        // Find which status it matches
        let matched = null;
        for (const key in statusConfig) {
            if (text.includes(key)) {
                matched = statusConfig[key];
                break;
            }
        }

        // If found, fix the class and color
        if (matched) {
            statusEl.className = `status ${matched.class}`;
            statusEl.style.backgroundColor = matched.color;
            statusEl.style.color = matched.textColor;
            statusEl.textContent = matched.text; // normalize the label
        }
    });

    // Sort rows based on corrected status
    rows.sort((a, b) => {
        const statusA = a.querySelector(".status").classList[1];
        const statusB = b.querySelector(".status").classList[1];
        return priority[statusA] - priority[statusB];
    });

    // Clear and re-add in sorted order
    tbody.innerHTML = "";
    rows.forEach(row => tbody.appendChild(row));
});
