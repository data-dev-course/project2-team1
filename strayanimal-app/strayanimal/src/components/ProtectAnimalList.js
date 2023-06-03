import AnimalCard from "./AnimalCard";
import Loading from './Loading';
import { useQuery} from "@tanstack/react-query";
import db from '../firebase.js';
import { getDocs, collection } from "firebase/firestore";
import "../css/Overview.css";
import "../css/AnimalCard.css";
function ProtectAnimalList() {
    return (
        <div className="protect-animal-list-wrap vertical align-start" style={{width:"100%", maxWidth:"1240px", padding:"20px"}}>
            <div className="highlight-title" style={{transform: "translateY(0)"}}>유기동물 공고 목록</div>
            <div className="number-highlight-line" style={{margin: "20px 0"}}></div>
            <div className="protect-animal-list">
                <AnimalCard src=""/>
                <AnimalCard src=""/>
                <AnimalCard src=""/>
                <AnimalCard src=""/>
            </div>
        </div>
    )
}

export default ProtectAnimalList;