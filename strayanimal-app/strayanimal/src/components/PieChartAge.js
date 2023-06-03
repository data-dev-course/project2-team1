import { useEffect, useState, useRef } from "react";
import Chart from 'chart.js/auto';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { doc, getDoc } from "firebase/firestore";
import Loading from "./Loading.js";

function PieChartAge(params) {
    const chartRef = useRef(null);
    const {status, data, error} = useQuery(["strayanimal", "casePerAgeData"], async () => {
        const docSnap = await getDoc(doc(db, "strayanimal", "차트10_연령대_별_유기_발생_비율"));
        return docSnap.data().data;
    })
    const colorset = ["#01778c","#3486a4","#5695ba","#78a3ce","#99b2e1","#bac0f1","#dbcfff","#dab9f1","#dda3df","#e18bc7","#e372ab"
        ,"#e1598a","#db4066"]
    const dataconfig = (dataset , option="ageCount") => {
        return ({
            type: 'pie',
            data: {
                labels: dataset.map((elem)=> elem.age),
                datasets: [
                    {
                        label: option==="ageCount"?"#":"%",
                        data: dataset.map((elem) => parseFloat(elem[option])),
                        backgroundColor: colorset,
                        borderWidth: 1,
                        hoverOffset: 4,
                    },
                ],
            },
            options: {
                plugins: {
                    legend: {
                        position: "bottom",
                    }
                }
            }
        })
    }
    useEffect(() => {
        if (status === 'success' && data !== undefined) {
            const sortedData = data.sort(function(a, b) {
                return a.age-b.age;
            });
            let chartStatus = Chart.getChart("pie_chart_per_age")
            if(chartStatus !== undefined) {
                chartStatus.destroy()
            }
            const ctx = chartRef.current.getContext('2d');
            new Chart(ctx, dataconfig(sortedData, params.unit));
        }
    }, [data, status, params.unit])
    if (status === "loading") {
        return <Loading/>
    }
    return <div style={{maxWidth: "500px"}}><canvas id="pie_chart_per_age" ref={chartRef}/></div>
}

export default PieChartAge;