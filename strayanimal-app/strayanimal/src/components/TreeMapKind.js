import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { doc, getDoc } from "firebase/firestore";
import Loading from "./Loading.js";
import { useEffect, useState, useRef } from "react";
import { Chart } from 'chart.js';
import {TreemapController, TreemapElement} from 'chartjs-chart-treemap';

function TreeMapKind() {
    const chartRef = useRef(null);
    const [selectViewType, setSelectViewType] = useState("staryCnt")
    const {status, data} = useQuery(["strayanimal", "animalkindmap"], async ()=> {
        const docSnap = await getDoc(doc(db, "strayanimal", "차트11_품종_견묘_등록_유기_비율"));
        return docSnap.data().data;
    })
    useEffect(()=> {
        if (status === "success" && data !== undefined) {
            const datasets = data.map((d) => {return ({value:d[selectViewType], kindCd: d.kindCd, label:"품종", "kindSpcs":d.kindSpcs})});
            Chart.register(TreemapController, TreemapElement);
            let chartStatus = Chart.getChart("treemap")
            if(chartStatus !== undefined) {
                chartStatus.destroy()
            }
            const ctx = chartRef.current.getContext('2d');
            window.mybarchart = new Chart(ctx, {
              type: 'treemap',
              data: {
                datasets: [
                  {
                    tree: datasets,
                    treeLeafKey: "kindSpcs", 
                    key: 'value',
                    groups:['kindCd', 'kindSpcs'],
                    borderWidth: 0,
                    borderRadius: 2,
                    spacing: 1,
                    backgroundColor(ctx) {
                      const colorset1 = ["#374c80"
                                      ,"#6e5193"
                                      ,"#a75094"
                                      ,"#d85085"
                                      ,"#fa5e68"
                                      ,"#ff7d42"
                                      ,"#ffa600"]
                      const colorset2 = ["#01778c","#3486a4","#5695ba","#78a3ce","#99b2e1","#bac0f1","#dbcfff","#dab9f1","#dda3df","#e18bc7","#e372ab"
                      ,"#e1598a","#db4066"]
                      if (ctx.type !== 'data' || !ctx.raw._data.kindSpcs) {
                        return 'transparent';
                      }
                      const val = ctx.raw._data.value;
                      if (ctx.raw._data.kindCd==="개") {
                        return colorset1[val>20000?6:val>10000?5:val>5000?4:val>1000?3:val>400?2:val>200?1:0]
                      }
                      return colorset2[val>500?0:val>300?1:val>200?2:val>50?3:4];
                    },
                    hoverBackgroundColor(ctx) {
                      if (ctx.type !== 'data' || !ctx.raw._data.kindSpcs) {
                        return '#3b3b3b';
                      }
                      return;
                    },
                    labels: {
                      align: 'left',
                      display: true,
                      formatter(ctx) {
                        if (ctx.type !== 'data' || !ctx.raw._data.kindSpcs) {
                          return;
                        }
                        return [ctx.raw._data.kindSpcs, '# ' + ctx.raw.v];
                      },
                      color: ['white', 'whiteSmoke'],
                      font: [{size: 14, weight: 'bold'}, {size: 12}],
                      position: 'top',
                      overflow: 'fit'
                    },
                    captions: {
                      align: 'left',
                      display: true,
                      color: '#fff',
                      font: {
                        size: 18,
                        weight: 'bold'
                      },
                      padding: 10,
                      overflow: 'fit'
                    },
                  }
                ],
              },
              options: {
                plugins: {
                  title: {
                    display: false,
                  },
                  legend: {
                    display: false
                  },
                  tooltip: {
                    enabled: true,
                    callbacks: {
                      title(items) {
                        return items[0].raw._data.kindCd;
                      },
                      label(item) {
                        const dataItem = item.raw;
                        const obj = dataItem._data;
                        const label = obj.kindSpcs || obj.kindCd;
                        return label + ': ' + dataItem.v;
                      }
                    }
                  }
                }
              }
            });
        }
    }, [data, status, selectViewType])

    if (status === "loading") {
        return <Loading/>;
    }
    return (
    <div id="treeWrapper">
      <div className="horizontal align-start" style={{padding: "10px 0"}}>
        <button className="type-select-button"
          onClick={() => setSelectViewType("staryCnt")} 
          style={{backgroundColor: selectViewType==="staryCnt"? "#FF5F15": "#4E4E4E"}}>
            유기동물
        </button>
        <button className="type-select-button"
          onClick={() => setSelectViewType("registerCnt")} 
          style={{backgroundColor: selectViewType==="registerCnt"? "#FF5F15": "#4E4E4E"}}>
            등록동물
        </button>
      </div>
      <canvas id="treemap" ref={chartRef} width="800" height="400"/>
    </div>);
}

export default TreeMapKind;