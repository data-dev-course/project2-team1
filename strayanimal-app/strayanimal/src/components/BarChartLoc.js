/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import Loading from './Loading';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { getDoc, doc } from "firebase/firestore";

function BarChartLoc() {
    const chartRef = useRef(null);
    const { status, data } = useQuery(["strayanimal", "locStatedata"], async () => {
        const docSnap = await getDoc(doc(db, "strayanimal", "차트05_지역별_보호_종료_상태_비율"));
        return docSnap.data().data;
    })
    const colorset = ["#374c80"
        ,"#6e5193"
        ,"#a75094"
        ,"#d85085"
        ,"#fa5e68"
        ,"#ff7d42"
        ,"#ffa600"]
    useEffect(()=> {
        if (status === "success" && data !== undefined) {
            const endStateList = [...new Set(data.map((d)=>d.endState))]
            const datasets = endStateList.map((type, i) => {
                return ({
                    data: (data.filter((d) => d.endState === type)).map((elem)=> {return {"x":elem.orgNm, "y":elem.count}}),
                    backgroundColor: colorset[i],
                    hoverOffset: 5,
                    label: type,
                })
            });
            let chartStatus = Chart.getChart("bar_chart_loc_state")
            if(chartStatus !== undefined) {
                chartStatus.destroy()
            }
            const ctx = chartRef.current.getContext('2d');
            window.mybarchart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [...new Set(data.map((d)=>d.orgNm))],
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
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
                                var label = context.dataset.label;
                                return label + ': ' + context.dataset.data[index]["y"];
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
    return <canvas id="bar_chart_loc_state" ref={chartRef} width="800" height="400" />;
}

export default BarChartLoc;