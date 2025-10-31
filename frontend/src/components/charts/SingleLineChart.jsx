import React from 'react';
import { Line } from 'react-chartjs-2';
import { chartColors } from './chartUtils';

const SingleLineChart = ({ title, chartData }) => {
    const options = {
        responsive: true,
        plugins: {
            legend: { display: false },
            title: { display: true, text: title },
        },
    };
    const data = {
        labels: chartData.labels || [],
        datasets: [
            {
                label: title,
                data: chartData.data || [],
                borderColor: chartColors.green,
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            },
        ],
    };
    return <Line options={options} data={data} />;
};

export default SingleLineChart;
