import "../css/Intro.css";
import Overview from "./Overview";

function IntroTop() {
    return (
    <div className="intro vertical">
        <hr className='intro-orange-line for-not-mobile' style={{left:0}}></hr>
        <hr className='intro-orange-line for-not-mobile' style={{right:0}}></hr>
        <div className="intro-typography">
            Animal<br></br>STAT-US<br></br>Tracker
        </div>
        <i className="fa-solid fa-paw fa-xl step-animation step-1" style={{color:"#fff"}}></i>
        <i className="fa-solid fa-paw fa-xl step-animation step-2" style={{color:"#fff"}}></i>
        <i className="fa-solid fa-paw fa-xl step-animation step-3" style={{color:"#fff"}}></i>
        <div className="intro-subtitle">
            유기동물 및 반려동물 통계 및 정보
        </div>
        <button className='next-page-button bounce2 ' style={{marginTop:"40px", position:"absolute", bottom: 40}}>
            <i className="fa-solid fa-arrow-down fa-2xl" style={{color: "#FF5F15"}}></i>
        </button>
    </div>
    );
}

function Intro() {
    return (
        <div className="intro-container vertical" style={{width:"100%", maxWidth:"1280px"}}>
            <IntroTop/>
            <Overview/>
        </div>
    );
}


export default Intro;