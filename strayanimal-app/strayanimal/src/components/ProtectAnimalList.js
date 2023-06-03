import AnimalCard from "./AnimalCard";
import Loading from './Loading';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { getDoc, collection, doc, query, where, documentId } from "firebase/firestore";
import "../css/Overview.css";
import "../css/AnimalCard.css";
import { Link, Outlet, useParams, useOutletContext } from "react-router-dom";
import { useEffect, useState } from "react";

export function InnerProtectAnimalList() {
    const [kindType, setKindType] = useOutletContext();
    let { pageNum } = useParams();
    const MAX_LIST_NUM = 2272;
    const {status, data, error} = useQuery(["strayanimal", "detailpost", kindType], async () => {
        const docref = doc(db, "strayanimal", "차트12_유기동물_detail");
        let collect_num = 0;
        if (pageNum* 10 > MAX_LIST_NUM) {
            collect_num = parseInt(pageNum*10 / MAX_LIST_NUM);
        }
        const q = doc(docref, `차트12_유기동물_detail_${kindType}_${collect_num}`, `차트12_유기동물_detail_${kindType}`);
        const docsnap = await getDoc(q);
        return docsnap.data().data;
    })

    if (status === "loading") {
        return <div style={{height:"200px", width:"100%"}}><Loading/></div>
    }
    return (
        <div className="protect-animal-list" style={{margin:"0 0 20px 0"}}>
            <div className="horizontal align-start" style={{width:"100%"}}>
                <button className="type-select-button" onClick={()=>setKindType("개")} style={{backgroundColor: kindType==="개"? "#FF5F15": "#4E4E4E"}}>개</button>
                <button className="type-select-button" onClick={()=>setKindType("고양이")} style={{backgroundColor: kindType==="고양이"? "#FF5F15": "#4E4E4E"}}>고양이</button>
            </div>
            {data.slice((pageNum-1)*10, pageNum*10).map((elem) => 
                <AnimalCard key={elem.desertionNo} src={elem.popfile} age={elem.age} color={elem.colorCd}
                careNm={elem.careNm+"("+elem.careAddr+")"} 
                kind={elem.kindCd+" "+elem.kindSpcs}
                sexCd={elem.sexCd} status={elem.specialMark} weight={elem.weight}
                />
            )}
        </div>
    );
}

function ProtectAnimalList() {
    let { pageNum } = useParams();
    const [hasNext, setHasNext] = useState(true);
    const [hasBefore, setHasBefore] = useState(false);
    const [kindType, setKindType] = useState("개");
    useEffect(()=> {
        if (pageNum === "1") {
            setHasBefore(false);
        } else {
            setHasBefore(true);
        }
        if (pageNum === "227"){
            setHasNext(false);
        } else {
            setHasNext(true);
        }
    },[pageNum])
    return (
        <div className="protect-animal-list-wrap vertical align-start" style={{width:"100%", maxWidth:"1240px", padding:"20px"}}>
            <div className="highlight-title" style={{transform: "translateY(0)", padding:"0 20px"}}>유기동물 공고 목록</div>
            <div className="number-highlight-line" style={{margin: "20px 0"}}></div>
            <Outlet context={[kindType, setKindType]}/>
            <div className="horizontal align-center justify-center-wrap" style={{width:"100%", margin:"0 0 60px 0"}}>
            {
                hasBefore?<Link to={`/protect-animal-list/${parseInt(pageNum)-1}`} className="page-button type-select-button">이전</Link>:""
            }
            <div className="page-button type-select-button">{pageNum}</div>
            {
                hasNext?<Link to={`/protect-animal-list/${parseInt(pageNum)+1}`} className="page-button type-select-button">다음</Link>:""
            }
            </div>
        </div>
    )
}

export default ProtectAnimalList;