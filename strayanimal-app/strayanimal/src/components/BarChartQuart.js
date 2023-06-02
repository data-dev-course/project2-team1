import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function BarChartQuart() {
    const chartRef = useRef(null);

    useEffect(() => {
        const data = [
            {"year":"2021","quarter":"1","count":"23871"},
            {"year":"2022","quarter":"1","count":"21796"},
            {"year":"2023","quarter":"1","count":"22779"},
            {"year":"2020","quarter":"2","count":"12663"},
            {"year":"2020","quarter":"3","count":"37412"},
            {"year":"2021","quarter":"3","count":"32311"},
            {"year":"2022","quarter":"3","count":"31967"},
            {"year":"2021","quarter":"2","count":"32399"},
            {"year":"2022","quarter":"2","count":"32462"},
            {"year":"2023","quarter":"2","count":"20097"},
            {"year":"2020","quarter":"4","count":"27287"},
            {"year":"2021","quarter":"4","count":"28490"},
            {"year":"2022","quarter":"4","count":"25993"}
        ];
    
        const groupedData = data.reduce((result, item) => {
            const { year, quarter, count } = item;
                if (!result[quarter]) {
                result[quarter] = [];
            }
            result[quarter].push({ year, count });
            return result;
        }, {});
    
        const quarters = Object.keys(groupedData)
            .sort((a, b) => parseInt(a) - parseInt(b))
            .map(quarter => `Q${quarter}`);
    
        const years = data
            .map(item => item.year)
            .filter((year, index, self) => self.indexOf(year) === index)
            .sort();
    
        const getColorByYear = (year) => {
            const colorset = [
                "#F7464A",
                "#46BFBD",
                "#FDB45C"
            ]
            // 여기에서 원하는 색상 선택 로직을 작성하세요.
            // 예시로 각 연도마다 다른 랜덤 색상을 선택하도록 구현합니다.
            let mode = year % 3;
            return colorset[mode];
        };

        const datasets = years.map(year => {
            const counts = quarters.map(quarter => {
            const quarterData = groupedData[quarter.replace('Q', '')];
            const dataForYear = quarterData.find(item => item.year === year);
            return dataForYear ? parseInt(dataForYear.count) : 0;
            });

        return {
            label: year,
            data: counts,
            backgroundColor:getColorByYear(year),
            borderColor: getColorByYear(year),
            borderWidth: 1,
            hoverOffset: 4,
        };
        });
        if(window.mybarchart instanceof Chart) {
            window.mybarchart.destroy();
        }
        const ctx = chartRef.current.getContext('2d');
        
        window.mybarchart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: quarters,
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: {
                beginAtZero: true
                }
            },
            plugins: {
                customCanvasBackgroundColor: {
                    color: '#212121',
                }
            }
        },
        });
    }, []);

    return (
        <div>
        <canvas ref={chartRef} width="800" height="400" />
        </div>
    );
}

export default BarChartQuart;