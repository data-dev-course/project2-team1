import "../css/AnimalCard.css";
function AnimalCard(params) {
    return (
        <div className="animal-card">
            <img className="animal-image" src={params} alt=""/>
            <div className="animal-card-desc vertical">
                <div style={{fontWeight:600}}>종류</div><div>[개] 믹스견</div>
                <div style={{fontWeight:600}}>나이</div><div>2020년생</div>
                <div style={{fontWeight:600}}>상태</div><div>피부질환</div>
                <div style={{fontWeight:600}}>보호소 위치</div><div>하나동물병원 (전라북도 남원시 왕정동 67)</div>
            </div>
        </div>
    );
}

export default AnimalCard;