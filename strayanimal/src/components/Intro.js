import "../css/Intro.css";
import Overview from "./Overview";
import { useLoaderData } from "react-router-dom";

function IntroTop() {
    return (
    <div className="intro vertical">
        <hr className='intro-orange-line for-not-mobile' style={{left:-10}}></hr>
        <hr className='intro-orange-line for-not-mobile' style={{right:-10}}></hr>
        <div className="intro-typography">
          Animal<br></br>Stat-us<br></br>Tracker
        </div>
        <div className="intro-subtitle">
          유기동물 및 반려동물 통계 및 정보
        </div>
        <button className='next-page-button bounce2 ' style={{marginTop:"40px", position:"absolute", bottom: 40}}>
          <i class="fa-solid fa-arrow-down fa-2xl" style={{color: "#FF5F15"}}></i>
        </button>
    </div>
    );
}

function Intro() {
    return (
        <div className="intro-container vertical">
            <IntroTop/>
            <Overview/>
        </div>
    )
}

export default Intro;