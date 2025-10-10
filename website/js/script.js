function previewFile() {
    const file = document.getElementById('fileInput').files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        document.getElementById('emailContent').value = e.target.result;
    };

    if (file) {
        reader.readAsText(file);
    }
}

async function adminLoginPrompt() {
    const email = prompt("Enter admin email:");
    if (!email) return alert("Login cancelled.");

    const password = prompt("Enter password:");
    if (!password) return alert("Login cancelled.");

    try {
        const response = await fetch('/admin-login-json', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password: password })
        });

        const result = await response.json();

        if (result.success) {
            window.location.href = "/admin";
        } else {
            alert("Login failed: " + result.error);
        }
    } catch (err) {
        alert("An error occurred during login.");
    }
}

//dashboard data fetching and chart updates
let myPieChart, myBarChart;

async function fetchDashboardData() {
    try {
        const response = await fetch('/api/dashboard-data');
        if (!response.ok) {
            throw new Error('Failed to fetch dashboard data');
        }
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

function updateDashboard(data) {
    //update stat cards
    document.getElementById('safeEmailCount').textContent = data.safe_count;
    document.getElementById('phishingEmailCount').textContent = data.phishing_count;
    
    //update pie 
    if (myPieChart) {
        myPieChart.data.datasets[0].data = [data.phishing_count, data.safe_count];
        myPieChart.update();
    } else {
        initializePieChart(data.phishing_count, data.safe_count);
    }
    
    //update bar
    const keywords = data.top_keywords.map(item => item.keyword);
    const counts = data.top_keywords.map(item => item.count);
    
    if (myBarChart) {
        myBarChart.data.labels = keywords;
        myBarChart.data.datasets[0].data = counts;
        const maxCount = Math.max(...counts, 5);
        myBarChart.options.scales.yAxes[0].ticks.max = Math.ceil(maxCount / 5) * 5;
        myBarChart.update();
    } else {
        initializeBarChart(keywords, counts);
    }
}

function initializePieChart(phishingCount, safeCount) {
    Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
    Chart.defaults.global.defaultFontColor = '#292b2c';
    
    const ctx = document.getElementById("myPieChart");
    const total = phishingCount + safeCount;
    
    myPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ["Phishing", "Safe"],
            datasets: [{
                data: [phishingCount, safeCount],
                backgroundColor: ['#dc3545', '#28a745'],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                position: 'bottom',
                labels: {
                    padding: 15,
                    fontSize: 13
                }
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem, data) {
                        const dataset = data.datasets[tooltipItem.datasetIndex];
                        const currentValue = dataset.data[tooltipItem.index];
                        const label = data.labels[tooltipItem.index];
                        return label + ': ' + currentValue + ' emails';
                    }
                }
            },
            animation: {
                onComplete: function() {
                    drawPiePercentages(this);
                }
            }
        }
    });
}

//function to draw percentages inside pie slices
function drawPiePercentages(chart) {
    const ctx = chart.chart.ctx;
    const dataset = chart.config.data.datasets[0];
    const meta = chart.getDatasetMeta(0);
    const total = dataset.data.reduce((acc, val) => acc + val, 0);
    
    ctx.font = Chart.helpers.fontString(16, 'bold', Chart.defaults.global.defaultFontFamily);
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    meta.data.forEach((element, index) => {
        const position = element.tooltipPosition();
        const value = dataset.data[index];
        const percentage = ((value / total) * 100).toFixed(1) + '%';
        ctx.fillText(percentage, position.x, position.y);
    });
}

function initializeBarChart(keywords, counts) {
    Chart.defaults.global.defaultFontFamily = '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
    Chart.defaults.global.defaultFontColor = '#292b2c';
    
    const ctx = document.getElementById("myBarChart");
    const maxCount = Math.max(...counts, 5);
    const yAxisMax = Math.ceil(maxCount / 5) * 5;
    const totalKeywords = counts.reduce((acc, val) => acc + val, 0);
    
    myBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: keywords,
            datasets: [{
                label: "Frequency",
                backgroundColor: "rgba(2,117,216,0.8)",
                borderColor: "rgba(2,117,216,1)",
                data: counts,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    gridLines: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 5
                    }
                }],
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 60,
                        stepSize: 30,
                        callback: function(value) {
                            return value;
                        }
                    },
                    gridLines: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }],
            },
            legend: {
                display: false
            },
            tooltips: {
                callbacks: {
                    label: function(tooltipItem) {
                        const count = tooltipItem.yLabel;
                        const percentage = ((count / totalKeywords) * 100).toFixed(1);
                        return 'Count: ' + count + ' (' + percentage + '% of all keywords)';
                    }
                }
            },
            animation: {
                onComplete: function() {
                    drawBarLabels(this);
                }
            }
        }
    });
}

//function to draw numbers inside bars
function drawBarLabels(chart) {
    const ctx = chart.chart.ctx;
    ctx.font = Chart.helpers.fontString(14, 'bold', Chart.defaults.global.defaultFontFamily);
    ctx.fillStyle = '#fff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';

    chart.data.datasets.forEach(function(dataset, i) {
        const meta = chart.getDatasetMeta(i);
        meta.data.forEach(function(bar, index) {
            const data = dataset.data[index];
            if (data > 0) {
                ctx.fillText(data, bar._model.x, bar._model.y + 20);
            }
        });
    });
}

//initialize dashboard when page loads
if (document.getElementById('myPieChart')) {
    fetchDashboardData();
    
    //auto-refresh every 30 seconds
    setInterval(fetchDashboardData, 30000);
}