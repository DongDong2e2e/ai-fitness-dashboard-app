import React from 'react';
import { Line } from 'react-chartjs-2';
import { chartColors } from './chartUtils';

const MultiLineChart = ({ title, chartData }) => {
    const options = {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: title },
        },
        scales: {
            y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: { display: true, text: 'kg' }
            },
            y1: {
                type: 'linear',
                display: true,
                position: 'right',
                title: { display: true, text: '%' },
                grid: {
                    drawOnChartArea: false, // only show the grid for the first y-axis
                },
            },
        }
    };

    const data = {
        labels: chartData.labels || [],
        datasets: [
            {
                label: '체중(kg)',
                data: chartData.weight || [],
                borderColor: chartColors.blue,
                yAxisID: 'y',
            },
            {
                label: '골격근량(kg)',
                data: chartData.muscle || [],
                borderColor: chartColors.red,
                yAxisID: 'y',
            },
            {
                label: '체지방률(%)',
                data: chartData.fatPercent || [],
                borderColor: chartColors.purple,
                yAxisID: 'y1',
            },
        ],
    };

    return <Line options={options} data={data} />;
}

export default MultiLineChart;