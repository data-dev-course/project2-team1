import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { getDoc, doc } from "firebase/firestore";
import Loading from "./Loading.js";

export const getColorByNum = (num) => {
    const colorset = [
        "#F7464A",
        "#46BFBD",
        "#FDB45C",
        "#6bb167"
    ]
    let mode = num % 4;
    return colorset[mode];
};

function dataSetModification(data) {
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
    
    const datasets = years.map(year => {
            const counts = quarters.map(quarter => {
            const quarterData = groupedData[quarter.replace('Q', '')];
            const dataForYear = quarterData.find(item => item.year === year);
            return dataForYear ? parseInt(dataForYear.count) : 0;
        });
        return {
            label: year,
            data: counts,
            backgroundColor:getColorByNum(year),
            borderColor: getColorByNum(year),
            borderWidth: 1,
            hoverOffset: 4,
        };
    });
    return [quarters, datasets];
}

function BarChartQuart() {
    const chartRef = useRef(null);
    const {status, data, error} = useQuery(["strayanimal", "quarterdata"], async () => {
        const docSnap = await getDoc(doc(db, "strayanimal", "차트07_분기별_유기발생_건수"));
        return docSnap.data().data;
    })
    useEffect(() => {
        if (status === 'success' && data !== undefined) {
            const [quarters, datasets] = dataSetModification(data)
            let chartStatus = Chart.getChart("bar_chart_q_endstate")
            if(chartStatus !== undefined) {
                chartStatus.destroy()
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
                }
            },
            });
        }
    }, [data, status])
    if (status === "loading") {
        return <Loading/>;
    }
    return <canvas id="bar_chart_q_endstate" ref={chartRef} width="800" height="400" />;
}

export default BarChartQuart;