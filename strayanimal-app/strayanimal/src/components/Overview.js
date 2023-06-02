import { useEffect, useRef, useState } from "react";
import "../css/Overview.css";
import EndStateChart from "./EndStateChart";
import BarChartQuart from "./BarChartQuart";
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { collection, getDocs, query, where, documentId } from "firebase/firestore";
import Loading from "./Loading";
import BarChartLoc from "./BarChartLoc";
import BarChartIncome from "./BarChartIncome";
import PieChartAge from "./PieChartAge";
import KoreaMap from "./koreamap";

function PieChartView(params) {
    const [viewType, setViewType] = useState(params.values[0]);
    return (
        <div className="pie-chart-view">
            <div className="highlight-title" style={{transform:"translateY(0)"}}> {params.title} </div>
            <div className="endStateSelect horizontal" style={{margin: "10px 0"}}>
                {params.values.map((data) => 
                <button className="type-select-button" 
                    onClick={() => setViewType(data)} 
                    style={{backgroundColor: viewType===data? "#FF5F15": "#4E4E4E"}}>
                    {data} 
                    {data==="개"? <i class="fa-solid fa-dog" style={{padding:"0 0 0 4px"}}></i>:
                    data==="고양이"? <i class="fa-solid fa-cat" style={{padding:"0 0 0 4px"}}></i>:
                    data==="기타축종"? <i class="fa-solid fa-dove" style={{padding:"0 0 0 4px"}}></i>:
                    ""}
                </button>)}
            </div>
            <div className="pie-chart-wrap vertical align-center">
                <EndStateChart type={viewType}/>
            </div>
        </div>
    );
}

function NumberHighlightChart(params) {
    const [counter, setCounter] = useState(0)
    const counterFunc = (minimum, maximum) => {
        for (let count = minimum; count <= maximum; count++) {
            setTimeout(() => {
                setCounter(count);
            }, 1);
        }
    }
    useEffect(()=>{
        counterFunc(0, params.num);
    },[])
    return (
        <div className="number-highlight-chart vertical">
            <div className="highlight-title">{params.title} <i class="fa-solid fa-feather fa-lg" style={{color: "#ffffff", padding:" 0 4px"}}></i></div>
            <div className="horizontal justify-end align-center">
                <div className="number-highlight-line"></div>
                <div className="highlight-num horizontal" >
                    <div className="highlight-num" id="count-word">{counter?counter: ""}</div>
                    <div className="num-unit">마리</div>
                </div>
            </div>
        </div>
    );
}

function Overview(params) {
    const { status, data, error } = useQuery(["strayanimal", "chart-overview"], async () => {
        const colref = collection(db, "strayanimal");
        const q = await getDocs(query(colref, where(documentId(), "in", ['차트01_어제의_유기숫자', '차트02_보호중인_유기동물_마리수'])))
        const docList = q.docs.map((doc) => {
                const data = doc.data();
                return data.data[0];
            })
        return docList
    });

    return(
        <div className="overview vertical" style={{marginTop: "20vh", padding:"20px"}}>
            {status==="success"?<NumberHighlightChart title="어제 유기된 동물 수" num={data[0].cnt}/>:""}
            <div style={{height:'3rem', width:"50%"}}></div>
            {status==="success"?<NumberHighlightChart title="현재 보호 중인 유기동물 수" num={data[1].cnt}/>:""}
            <div style={{height:'8rem', width:"50%"}}></div>
            <div className="pie-chart-container">
                <PieChartView title="보호 종료 후 상태 비율" values={["전체", "60일 기준"]}/>
                <PieChartView title="축종 내 보호 종료 상태" values={["전체 축종", "개", "고양이", "기타축종"]}/>
            </div>
            <div style={{height:'6rem', width:"50%"}}></div>
            <div className="highlight-title" style={{transform:"translateY(0)", margin:"10px 0"}}> 지역별 보호 종료 후 상태 </div>
            <BarChartLoc/>
            <div style={{height:'6rem', width:"50%"}}></div>
            <div className="highlight-title" style={{transform:"translateY(0)", margin:"10px 0"}}> 분기별 유기발생 수 </div>
            <BarChartQuart/>
            <div style={{height:'6rem', width:"50%"}}></div>
            <div className="highlight-title" style={{transform:"translateY(0)", margin:"10px 0"}}> 지역 별 유기동물 발생 횟수 </div>
            <KoreaMap/>
            <div style={{height:'6rem', width:"50%"}}></div>
            <div className="highlight-title" style={{transform:"translateY(0)", margin:"10px 0"}}> 지역별 소득수준 및 유기건수 </div>
            <BarChartIncome/>
            <div style={{height:'6rem', width:"50%"}}></div>
            <div className="highlight-title" style={{transform:"translateY(0)", margin:"10px 0"}}> 나이별 유기건수 </div>
            <PieChartAge/>
            <div style={{height:'6rem', width:"50%"}}></div>
        </div>
    );
}

export default Overview;