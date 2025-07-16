const BASEURL = 'http://127.0.0.1:5000/api'
const urlParams = new URLSearchParams(window.location.search);
const timeframe = urlParams.get('timeframe');

// * Function to render doughnut chart
async function renderDoughnutChart() {
    try {
        const response = await fetch(`${BASEURL}/trades/?timeframe=${timeframe}`);
        const data = await response.json();

        const pieChart = new Chart(
            document.querySelector("#pie-chart").getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Winning trades', 'Losing trades', 'BE trades'],
                    datasets: [{
                        label: "All trades",
                        data: [
                            data.winning,
                            data.losing,
                            data.be
                        ],
                        backgroundColor: ["#77DD77", "#DD7777", "#7777DD"],
                        hoverBackgroundColor: ["#77DD77", "#DD7777", "#7777DD"],
                        hoverOffset: 5
                    }]
                }
            }
        );
    } catch (error) {
        return;
    }
}

// * Function to render line chart
async function renderLineChart() {
    try {
        const response = await fetch(`${BASEURL}/history/?timeframe=${timeframe}`);
        const data = await response.json();

        const lineChart = new Chart(
            document.querySelector("#line-chart").getContext('2d'), {
                type: 'line',
                data: {
                    labels: Array(data.pnl.length).fill(''),
                    datasets: [{
                        label: 'Trade history',
                        data: data.pnl,
                        fill: true,
                        borderColor: '#7777DD',
                        tension: 0.1
                    }]
                },
                options: {
                    scales: {
                        x: {
                            display: false,
                            ticks: {
                                maxTicksLimit: data.pnl.length
                            }
                        },
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            }
        )
    }
    catch (error) {return;}
}

// & Rendering charts
renderDoughnutChart();
renderLineChart();