import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import Loading from './Loading';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { getDoc, doc } from "firebase/firestore";

function colorize(opaque) {
    const colorset = ["#00876c","#7daa83","#c4ceaf","#d4d8bd", "#ebd1af","#e9c39d","#e18866","#d43d51"];
    return (ctx) => {
      const v = ctx.parsed.x;
      const c = v < 400 ? 7
        : v < 900 ? 6
        : v < 1200 ? 5
        : v < 1500 ? 4
        : v < 2000 ? 3
        : v < 4000 ? 2
        : v < 6000 ? 1
        : 0;
  
      return colorset[c];
    };
}

function BarChartIncome() {
    const chartRef = useRef(null);
    const {status, data} = useQuery(["strayanimal", "incomerelated"], async () => {
        const docSnap = await getDoc(doc(db, "strayanimal", "차트09_지역별_소득수준_및_유기건수"));
        return docSnap.data().data;
    })
   
    useEffect(()=> {
        if (status === "success" && data !== undefined) {
            const groupType = ["income_avg", "caseNum"]
            const sortedData = data.sort(function(a, b) {
                return b.income_avg-a.income_avg;
            });
            const datasets = groupType.map((type, i) => {
                return ({
                    data: sortedData.map((elem)=> {return {"y":elem.location, "x":elem[type]}}),
                    backgroundColor: colorize(i),
                    hoverOffset: 5,
                    label: type,
                })
            });
            let chartStatus = Chart.getChart("bar_chart_income")
            if(chartStatus !== undefined) {
                chartStatus.destroy()
            }
            const ctx = chartRef.current.getContext('2d');
            window.mybarchart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [...new Set(sortedData.map((d)=>d.location))],
                datasets: datasets,
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        stacked: false,
                    },
                    y: {
                        stacked: false,
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                var index = context.dataIndex;
                                return context.dataset.label + ': ' + context.dataset.data[index]["x"];
                            }
                        }
                    },    
                }
            },
            });
        }
    }, [status, data])

    if (status === "loading") {
        return <Loading/>;
    }
    return <canvas id="bar_chart_income" ref={chartRef} width="800" height="400" />;
}

export default BarChartIncome;