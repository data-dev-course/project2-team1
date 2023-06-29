/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useState, useRef } from "react";
import Chart from 'chart.js/auto';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { collection, getDocs, query, where, documentId } from "firebase/firestore";
import Loading from "./Loading.js";
import "../css/Overview.css";

function EndStateChart(params) {
    const chartRef = useRef(null);

    const lt60dayChart = (dataset) => {
        let low60Day = dataset.filter(d => d.lt60Day === 1)
        let above60Day = dataset.filter(d => d.lt60Day === 0)
        const lt60DayDataset = [
            low60Day.reduce((partialSum, a) => partialSum + parseInt(a.count), 0), 
            above60Day.reduce((partialSum, a) => partialSum + parseInt(a.count), 0)]
        const subDatasetlt60Day = [...low60Day, ...above60Day]
        const backgroundColor = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            ];
        const datalabels = dataset.map((elem)=> elem.endState)
        return ({
            type: 'doughnut',
            data: {
                labels:["60일 미만", "60일 이상"],
                datasets: [{
                    label: '종료상태',
                    data: subDatasetlt60Day.map((elem) => parseInt(elem.count)),
                    backgroundColor: backgroundColor,
                    borderColor: backgroundColor,
                    spacing: 4,
                    labels: datalabels,
                    borderWidth: 0,
                    hoverOffset: 5,
                },
                {
                    label: "60일 기준",
                    data: lt60DayDataset,
                    labels: ["60일 미만", "60일 이상"],
                    backgroundColor: ["#F7464A","#00B3A0"],
                    borderColor: ["#F7464A","#00B3A0"],
                    weight: 1.5,
                    spacing: 1,
                    borderWidth: 0,
                    hoverOffset: 2,
                },]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                        legendText : ["60일 미만", "60일 이상"],
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                var index = context.dataIndex;
                                return context.dataset.labels[index] + ': ' + context.dataset.data[index];
                            }
                        }
                    },    
                }
            }
        });
    }

    const dataconfig = (dataset , option="count") => {
        return ({
            type: 'doughnut',
            data: {
                labels: dataset.map((elem)=> elem.endState),
                datasets: [
                    {
                        label: '#',
                        data: dataset.map((elem) => parseFloat(elem[option])),
                        backgroundColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        ],
                        borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        ],
                        borderWidth: 1,
                        hoverOffset: 4,
                    },
                ],
            }
        })
    }
    const [doughnutData, setDoughnutData] = useState(null);
    const {status, data} = useQuery(["strayanimal, endstate"], async ( )=> {
        const colref = collection(db, "strayanimal");
        const q = await getDocs(query(colref, where(documentId(), "in", ['차트03_보호_종료_시_상태_비율', '차트04_60일_보호_종료_상태_비율', '차트06_유기건수_축종_내_보호_종료_후_상태'])))
        const docList = q.docs.map((doc) => {
                const data = doc.data();
                return data.data;
        })
        return docList
    });
    useEffect(() => {
        if (status === "success") {
            const percent_kind = [
                {"endState": "개", "count": data[2].filter(data => data.kindCd === "개").reduce((sum, a) => sum+parseInt(a.count), 0)},
                {"endState": "고양이", "count":data[2].filter(data => data.kindCd === "고양이").reduce((sum, a) => sum+parseInt(a.count), 0)},
                {"endState": "기타축종", "count":data[2].filter(data => data.kindCd === "기타축종").reduce((sum, a) => sum+parseInt(a.count), 0)}
            ]
            if (params.type === "전체") {
                setDoughnutData(dataconfig(data[0]))
            } else if (params.type === "60일 기준") {
                setDoughnutData(lt60dayChart(data[1]))
            } else if (params.type === "전체 축종") {
                setDoughnutData(dataconfig(percent_kind))
            } else if (params.type === "개") {
                setDoughnutData(dataconfig(data[2].filter(data => data.kindCd === "개")))
            } else if (params.type === "고양이") {
                setDoughnutData(dataconfig(data[2].filter(data => data.kindCd === "고양이")))
            } else {
                setDoughnutData(dataconfig(data[2].filter(data => data.kindCd === "기타축종")))
            }
        }
        
    }, [status, params.type])

    useEffect(() => {
        if (status === "success" && doughnutData != null) {
            let chartStatus = Chart.getChart(params.type)
            if(chartStatus !== undefined) {
                chartStatus.destroy()
            }
            const ctx = chartRef.current.getContext('2d');
            new Chart(ctx, doughnutData);
        }
    }, [doughnutData, status])

    if (status === "loading" || doughnutData === null) {
        return <Loading/>
    }
    return <div><canvas id={params.type} ref={chartRef}/></div>
}

export default EndStateChart;