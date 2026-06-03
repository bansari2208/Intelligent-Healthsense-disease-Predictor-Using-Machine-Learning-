    const trendLabels = ["24 May", "25 May"];
    const trendData = [0, 4];

    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    let gradientTrend = ctxTrend.createLinearGradient(0, 0, 0, 250);
    gradientTrend.addColorStop(0, 'rgba(16, 185, 129, 0.2)');
    gradientTrend.addColorStop(1, 'rgba(16, 185, 129, 0)');

    new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: trendLabels,
            datasets: [{
                label: 'Predictions',
                data: trendData,
                borderColor: '#10b981',
                backgroundColor: gradientTrend,
                borderWidth: 3,
                pointBackgroundColor: '#10b981',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'white',
                    titleColor: '#111827',
                    bodyColor: '#374151',
                    borderColor: '#f3f4f6',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return ' Predictions: ' + context.raw;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#6b7280', font: { family: "'Inter', sans-serif" } }
                },
                y: {
                    min: 0,
                    suggestedMax: 5,
                    grid: { borderDash: [4, 4], color: '#f3f4f6' },
                    ticks: { stepSize: 1, color: '#6b7280', font: { family: "'Inter', sans-serif" } },
                    border: { display: false }
                }
            }
        });
