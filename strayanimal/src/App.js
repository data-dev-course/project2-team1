import './App.css';
function App() {
  return (
    <div className="App vertical">
      <header className="App-header horizontal">
        <i class="fa-solid fa-paw fa-2xl" style={{color:"#FF5F15", padding:"0 40px"}}></i>
        <div className="app-navibar for-not-mobile" style={{padding:"0 40px", gap:"20px"}}>
          {
            [...Array(3)].map((x, i) => <button>카테고리{i+1}</button>)
          }
        </div>
      </header>
      <div className="intro vertical">
        <hr className='intro-orange-line for-not-mobile' style={{left:-10}}></hr>
        <hr className='intro-orange-line for-not-mobile' style={{right:-10}}></hr>
        <div className="intro-typography">
          Animal<br></br>Stat-us<br></br>Tracker
        </div>
        <div className="intro-subtitle" style={{color:"#fff", padding:"20px 0", fontSize:"1.25rem", fontWeight:400}}>
          유기동물 및 반려동물 인포그래픽
        </div>
        <button className='next-page-button bounce2 ' style={{marginTop:"40px", position:"absolute", bottom: 40}}>
        <svg id="Layer_2" data-name="Layer 2" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48">
          <g id="invisible_box" data-name="invisible box">
            <rect id="사각형_4" data-name="사각형 4" width="48" height="48" fill="none"/>
          </g>
          <g id="icons_Q2" data-name="icons Q2">
            <path id="패스_3" data-name="패스 3" d="M24,27.2,13.4,16.6a1.9,1.9,0,0,0-3,.2,2.1,2.1,0,0,0,.2,2.7l12,11.9a1.9,1.9,0,0,0,2.8,0l12-11.9a2.1,2.1,0,0,0,.2-2.7,1.9,1.9,0,0,0-3-.2Z" fill="#ff5f15"/>
          </g>
        </svg>
        </button>
      </div>
    </div>
  );
}

export default App;
