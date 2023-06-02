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
    </div>
  );
}

export default App;
