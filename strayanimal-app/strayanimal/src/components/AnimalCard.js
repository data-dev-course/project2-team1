import "../css/AnimalCard.css";
function AnimalCard(params) {
    const {age, weight, colorCd, sexCd, careNm, status, kind, src} = params
    return (
        <div className="animal-card">
            <img className="animal-image" src={src} alt=""/>
            <div className="animal-card-desc vertical">
                <div style={{fontWeight:600}}>종류</div><div>{kind}</div>
                <div style={{fontWeight:600}}>나이/무게</div><div>{age}살 / {weight}</div>
                <div style={{fontWeight:600}}>성별/색깔</div><div>{sexCd ==="F"?'암컷':"수컷"}/{colorCd}</div>
                <div style={{fontWeight:600}}>상태</div><div>{status}</div>
                <div style={{fontWeight:600}}>보호소 위치</div><div>{careNm}</div>
            </div>
        </div>
    );
}

export default AnimalCard;