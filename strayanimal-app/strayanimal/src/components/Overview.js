import { useEffect, useState } from "react";
import "../css/Overview.css";
import EndStateChart from "./EndStateChart";
import BarChartQuart from "./BarChartQuart";
import { useQuery } from "@tanstack/react-query";
import db from "../firebase.js";
import {
	collection,
	getDocs,
	query,
	where,
	documentId,
} from "firebase/firestore";
import BarChartLoc from "./BarChartLoc";
import BarChartIncome from "./BarChartIncome";
import PieChartAge from "./PieChartAge";
import KoreaMap from "./KoreaMap";
import TreeMapKind from "./TreeMapKind";

function PieChartView(params) {
	const [viewType, setViewType] = useState(params.values[0]);
	return (
		<div className="pie-chart-view">
			<div
				className="highlight-title"
				style={{ transform: "translateY(0)" }}
			>
				{" "}
				{params.title}{" "}
			</div>
			<div
				className="endStateSelect horizontal"
				style={{ margin: "10px 0" }}
			>
				{params.values.map((data, i) => (
					<button
						className="type-select-button"
						key={i}
						onClick={() => setViewType(data)}
						style={{
							backgroundColor:
								viewType === data ? "#FF5F15" : "#4E4E4E",
						}}
					>
						{data}
						{data === "개" ? (
							<i
								className="fa-solid fa-dog"
								style={{ padding: "0 0 0 4px" }}
							></i>
						) : data === "고양이" ? (
							<i
								className="fa-solid fa-cat"
								style={{ padding: "0 0 0 4px" }}
							></i>
						) : data === "기타축종" ? (
							<i
								className="fa-solid fa-dove"
								style={{ padding: "0 0 0 4px" }}
							></i>
						) : (
							""
						)}
					</button>
				))}
			</div>
			<div className="pie-chart-wrap vertical align-center">
				<EndStateChart type={viewType} />
			</div>
		</div>
	);
}

function NumberHighlightChart(params) {
	const [counter, setCounter] = useState(0);
	const counterFunc = (minimum, maximum) => {
		for (let count = minimum; count <= maximum; count++) {
			setTimeout(() => {
				setCounter(count);
			}, 1);
		}
	};
	useEffect(() => {
		counterFunc(0, params.num);
	}, [params.num]);
	return (
		<div className="number-highlight-chart vertical">
			<div className="highlight-title">
				{params.title}{" "}
				<i
					className="fa-solid fa-feather fa-lg"
					style={{ color: "#ffffff", padding: " 0 4px" }}
				></i>
			</div>
			<div className="horizontal justify-end align-center">
				<div className="number-highlight-line"></div>
				<div className="highlight-num horizontal">
					<div className="highlight-num" id="count-word">
						{counter ? counter : ""}
					</div>
					<div className="num-unit">마리</div>
				</div>
			</div>
		</div>
	);
}

function Overview(params) {
	const { status, data } = useQuery(
		["strayanimal", "chart-overview"],
		async () => {
			const colref = collection(db, "strayanimal");
			const q = await getDocs(
				query(
					colref,
					where(documentId(), "in", [
						"차트01_어제의_유기숫자",
						"차트02_보호중인_유기동물_마리수",
					])
				)
			);
			const docList = q.docs.map((doc) => {
				const data = doc.data();
				return data.data[0];
			});
			return docList;
		}
	);

	return (
		<div
			className="overview vertical"
			style={{ marginTop: "20vh", padding: "20px" }}
		>
			{status === "success" ? (
				<NumberHighlightChart
					title="어제 유기된 동물 수"
					num={data[0].cnt}
				/>
			) : (
				""
			)}
			<div style={{ height: "3rem", width: "50%" }}></div>
			{status === "success" ? (
				<NumberHighlightChart
					title="현재 보호 중인 유기동물 수"
					num={data[1].cnt}
				/>
			) : (
				""
			)}
			<div style={{ height: "8rem", width: "50%" }}></div>
			<div className="section-title"> 보호 상태 분석 </div>
			<p>
				유기동물 보호소에서 보호중인 동물들은 각 지자체에서 정한 일정
				보호기간 이후 보호가 종료됩니다.
				<br />
				보호 종료 상태는 입양 | 자연사 | 안락사 | 반환 | 기증 | 방사 |
				기타로 나누어집니다.
			</p>
			<div className="pie-chart-container">
				<PieChartView
					title="보호 종료 후 상태 비율"
					values={["전체", "60일 기준"]}
				/>
				<PieChartView
					title="축종 내 보호 종료 상태"
					values={["전체 축종", "개", "고양이", "기타축종"]}
				/>
			</div>
			<div style={{ height: "6rem", width: "50%" }}></div>
			<div
				className="highlight-title"
				style={{ transform: "translateY(0)", margin: "10px 0" }}
			>
				{" "}
				지역별 보호 종료 후 상태{" "}
			</div>
			<p>
				각 시도군구의 총 유기건수에 대해 보호 종료 후 상태에 따른
				유기건수 비율을 볼 수 있습니다.
				<br /> 제주특별자치도의 유기건수가 아주 많고 그 중 높은 비율로
				안락사가 진행되었음을 보여주고 있습니다.
				<br />
				범례의 항목을 선택해 원하는 항목만 데이터를 볼 수 있습니다.
			</p>

			<BarChartLoc />
			<div style={{ height: "6rem", width: "50%" }}></div>
			<div className="section-title"> 분기별 유기발생 수 </div>
			<p>
				2020년 2분기부터 2023년 2분기까지의 유기건수를 분기별로 나누어
				보여주는 차트입니다 (2020년 2분기는 분기 기간내 전체 데이터가
				아닌 일부 기간의 데이터임을 알립니다). <br />
				범례의 항목을 선택해 원하는 항목의 데이터를 볼 수 있습니다.
			</p>
			<BarChartQuart />
			<div style={{ height: "6rem", width: "50%" }}></div>
			<div className="section-title"> 지역별 분석 </div>
			<div
				className="highlight-title"
				style={{ transform: "translateY(0)", margin: "10px 0" }}
			>
				{" "}
				지역별 유기동물 발생 횟수{" "}
			</div>
			<p>
				각 시도의 누적 유기동물 발생 횟수를 지도로 표현했습니다. <br />{" "}
				원하는 지역을 선택해 유기건수를 확인할 수 있습니다.
			</p>
			<KoreaMap />
			<div style={{ height: "6rem", width: "50%" }}></div>
			<div
				className="highlight-title"
				style={{ transform: "translateY(0)", margin: "10px 0" }}
			>
				{" "}
				지역별 소득수준 및 유기건수{" "}
			</div>
			<p>
				2021년 가구 소득 기준 상위 10개 지역과 하위 10개 지역을 각
				지역의 유기건수와 함께 보여주는 차트입니다. <br /> 성남시를
				제외한 다른 소득 상위 지역들은 모두 유기 건수가 하위지역에 비해
				낮음을 알 수 있습니다.
				<br />
				범례의 항목을 선택해 원하는 항목의 데이터를 볼 수 있습니다.
			</p>
			<BarChartIncome />
			<div style={{ height: "6rem", width: "50%" }}></div>
			<div className="section-title"> 나이별 유기건수 </div>
			<p>
				유기건수를 나이별로 분류해 보여주고 있습니다. 태어난지 1살
				전후로 가장 많이 유기되고 있음을 알 수 있습니다. <br /> 0살은
				태어난 지 60일 미만된 동물들을 의미합니다. <br /> 나이가 많은
				동물의 유기건수에 대해 보호소에서 상태변경이나 등록을 진행하지
				않았을 수 있는 점 참고 바랍니다.
				<br />
				범례의 항목을 선택해 원하는 항목의 데이터를 볼 수 있습니다.
			</p>
			<PieChartAge />
			<div style={{ height: "6rem", width: "50%" }}></div>
			<div className="section-title"> 축종별 품종 비율 </div>
			<p>
				반려동물 인식칩을 통해 등록된 동물과 유기된 동물의 품종을
				보여주고 있습니다. 등록 동물 축종의 한계로, 개와 고양이에 대해서
				나타냈습니다. <br /> 개의 등록건수가 고양이에 비해 압도적으로
				많아, 등록동물 차트에서 고양이의 점유 부분이 선으로 나타납니다.
				<br /> 비슷하게 등록되고 유기되는 경향이 있지만, 예시로 진도견과
				리브라도 리트리버의 경우 많이 유기되지만, 상대적으로 등록건수가
				많지 않습니다.
			</p>
			<TreeMapKind />
			<div style={{ height: "6rem", width: "50%" }}></div>
		</div>
	);
}

export default Overview;
