const BASEURL = 'https://project-investora.onrender.com/api/team'
const teamId = document.querySelector("#team-id").innerHTML;

// * Function to render doughnut chart
async function renderDoughnutChart() {
    try {
        const response = await fetch(`${BASEURL}/${teamId}/trades/`);
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
        const response = await fetch(`${BASEURL}/${teamId}/history/`);
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
