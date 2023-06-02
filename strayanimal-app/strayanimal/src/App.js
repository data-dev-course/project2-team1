import './css/App.css';
import React, { useEffect } from 'react';
import { Outlet, Link } from "react-router-dom";

function App() {

  useEffect(() => {
    
  }, []);
  return (
    <div className="App vertical">
      <header className="App-header horizontal">
        <Link to="/"><i className="fa-solid fa-paw fa-2xl" style={{color:"#FF5F15", padding:"0 40px"}}></i></Link>
        <div className="app-navibar" style={{padding:"0 40px", gap:"20px"}}>
          <a href={`/protect-animal-list`} style={{fontSize:"1rem"}}>유기동물 공고 보기</a>
        </div>
      </header>
      <Outlet/>
      <footer className='App-footer'>
        <div className='footer-wrap' style={{padding: "0 20px"}}>
        <div className='footer-title'>Animal STAT-US Tracker</div>
        <div style={{fontWeight:600}}>DevCourse Data Engineering</div>
        <div style={{color:"#F5F5F5"}}>Data Warehouse & Dashboard Construct Project</div>
        <div style={{height: "10px", width: "100%"}}></div>
        <div>강다혜 @kangdaia</div>
        <div>박태준 @ih-tjpark</div>
        <div>전성현 @Jeon-peng</div>
        <div>최민수 @usiohc</div>
        </div>
      </footer>
    </div>
  );
}

export default App;
