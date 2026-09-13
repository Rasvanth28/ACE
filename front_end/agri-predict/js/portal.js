const crop = localStorage.getItem("selectedCrop");

if (!crop) {
    window.location.href = "index.html";
}

// Load JSON file
async function loadData() {
    const response = await fetch("testing.json");
    const data = await response.json();

    const commodity = data.report_metadata.commodity;
    document.getElementById("cropTitle").innerText =
        commodity + " Market Analysis";

    // State average latest prediction
    const stateForecast = data.state_summary.forecast_series;
    const latestStatePrice =
        stateForecast[stateForecast.length - 1].avg_predicted_price;

    document.getElementById("currentPrice").innerText =
        "₹ " + latestStatePrice.toFixed(2);

    document.getElementById("priceChange").innerText =
        "3 Month Forecast Active";

    // Extract months (x-axis)
    const labels = stateForecast.map(item => item.month);

    // Build datasets for each market
    const datasets = data.market_details.map((market, index) => {

        const colors = [
            "#c20a66",
            "#22c55e",
            "#3b82f6",
            "#f59e0b",
            "#8b5cf6"
        ];

        return {
            label: market.market_name,
            data: market.forecast_series.map(item => item.price),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + "20",
            borderWidth: 3,
            tension: 0.4,
            pointRadius: 4
        };
    });

    // Destroy previous chart if exists
    if (window.priceChartInstance) {
        window.priceChartInstance.destroy();
    }

    window.priceChartInstance = new Chart(
        document.getElementById("priceChart"),
        {
            type: "line",
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: "#22c55e"
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#22c55e" },
                        grid: { color: "rgba(255,255,255,0.05)" }
                    },
                    y: {
                        ticks: { color: "#22c55e" },
                        grid: { color: "rgba(255,255,255,0.05)" }
                    }
                }
            }
        }
    );
}

// Auto load when page opens
loadData();




