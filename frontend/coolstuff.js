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
document.addEventListener("DOMContentLoaded", async () => {
    const tableBody = document.getElementById("sensor-table-body");

    try {
        // Fetch live data from your endpoint
        const response = await fetch("http://vibrator.d3llie.tech/data");
        if (!response.ok) throw new Error("Network response was not ok");

        const data = await response.json();
        console.log("Fetched data:", data);

        // Clear table
        tableBody.innerHTML = "";

        // Loop through each reading (assuming array of objects)
        data.forEach((reading) => {
            const { Temp, HeartRate, AccelX, AccelY, AccelZ } = reading;

            // Determine status
            let statusText = "Normal";
            let statusClass = "normal";

            if (HeartRate > 100 || Temp > 38) {
                statusText = "Danger";
                statusClass = "danger";
            } else if (HeartRate > 85 || Temp > 37.5) {
                statusText = "Warning";
                statusClass = "warning";
            }

            // Create row
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${Temp.toFixed(2)}</td>
                <td>${HeartRate.toFixed(2)}</td>
                <td>(${AccelX.toFixed(2)}, ${AccelY.toFixed(2)}, ${AccelZ.toFixed(2)})</td>
                <td class="status ${statusClass}">${statusText}</td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error("Error fetching data:", error);
        tableBody.innerHTML = `<tr><td colspan="4">Error loading data</td></tr>`;
    }
});
document.addEventListener("DOMContentLoaded", () => {
    // Check if the employee-name element exists (so it only runs on the right page)
    const nameElement = document.getElementById("employee-name");
    if (nameElement) {
        // Get the 'name' parameter from the URL
        const urlParams = new URLSearchParams(window.location.search);
        const employeeName = urlParams.get("name");

        if (employeeName) {
            nameElement.textContent = employeeName;
        } else {
            nameElement.textContent = "Unknown Employee";
        }
    }
});