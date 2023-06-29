import AnimalCard from "./AnimalCard";
import Loading from './Loading';
import { useQuery } from "@tanstack/react-query";
import "../css/Overview.css";
import "../css/AnimalCard.css";
import { useEffect, useState } from "react";
import { fetchPostData , getTotalDoc } from "../loader/postDataLoader";

function ProtectAnimalList() {
    const [page, setPage] = useState(0)
    const [kindType, setKindType] = useState("개");
    const [lastSnap, setLastSnap] = useState(undefined);
    const [lookLast, setLookLast] = useState(true);
    const [endPage, setEndPage] = useState(-1);
    const {
        isLoading,
        data,
        isFetching,
    } = useQuery({
        queryKey: ['strayanimal', kindType, page],
        queryFn: () => fetchPostData(page, kindType, lastSnap, lookLast),
        keepPreviousData : true
    })
    
    useEffect(() => {
        window.scrollTo(0, 0)
    }, [kindType, page])

    useEffect(() => {
        setPage(0);
        getTotalDoc().then((e) => setEndPage(~~(e/10)));
    }, [kindType])

    return (
        <div className="protect-animal-list-wrap vertical align-start" style={{width:"100%", maxWidth:"1240px", padding:"20px"}}>
            <div className="highlight-title" style={{transform: "translateY(0)", padding:"0 20px"}}>유기동물 공고 목록</div>
            <div className="number-highlight-line" style={{margin: "20px 0"}}></div>
            
            <div className="protect-animal-list">
                <div className="horizontal align-start" style={{width:"100%"}}>
                    <button className="type-select-button" onClick={()=>setKindType("개")} style={{backgroundColor: kindType==="개"? "#FF5F15": "#4E4E4E"}}>개</button>
                    <button className="type-select-button" onClick={()=>setKindType("고양이")} style={{backgroundColor: kindType==="고양이"? "#FF5F15": "#4E4E4E"}}>고양이</button>
                </div>
                {
                    isLoading || isFetching? <div style={{height:"400px", width:"100%"}}><Loading/></div>:
                    data.pages.map((elem) => (
                        <AnimalCard key={elem.desertionNo} src={elem.popfile} age={elem.age} color={elem.colorCd}
                        careNm={elem.careNm+" ( "+elem.careAddr+" )"} 
                        kind={elem.kindSpcs}
                        sexCd={elem.sexCd} status={elem.specialMark} weight={elem.weight}
                        />
                    ))
                    
                }
            </div>
            
            <div className="horizontal align-center justify-center-wrap" style={{width:"100%", margin:"0 0 60px 0"}}>
                {page===0? null: <button className="page-button type-select-button"
                    onClick={() => {setPage(0);}}>처음</button>}
                {page===0? null: <button className="page-button type-select-button"
                    onClick={() => {setPage(page-1); setLookLast(false); setLastSnap(data.firstId)}}>
                    이전
                </button>}
                <div className="page-button type-select-button">{page+1}</div>
                {page===endPage? null: <button className="page-button type-select-button"
                    onClick={() => {setPage(page+1); setLookLast(true); setLastSnap(data.lastId)}}>다음</button>}
                {page===endPage? null: <button className="page-button type-select-button"
                    onClick={() => {setPage(endPage); setLookLast(true); setLastSnap(-1)}}>끝</button>}
            </div>
        </div>
    )
}

export default ProtectAnimalList;