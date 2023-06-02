import { useEffect, useRef } from "react";
import "../css/KoreaMap.css";
import * as d3 from "d3";
import korea from '../assets/korea_large.json'
import { feature } from 'topojson-client'

const featureData = feature(korea, korea.objects['korea_large'])
const center = d3.geoCentroid(featureData);

const KoreaMap = () => {
 
    // svg를 그릴 엘리먼트 설정을 위한 ref
    const chart = useRef(null)
   
    const printD3 = () => {
   
      // 지도 svg의 너비와 높이
      const width = 500
      const height = 500
   
   
      // 메르카토르 투영법 설정
      // 우리가 가장 많이 쓰는 도법으로 구형인 지구를 평면으로 표현하는 하나의 방법이라고 하네요??
      const projection = d3.geoMercator().scale(1).translate([0, 0])
      const path = d3.geoPath().projection(projection)
      const bounds = path.bounds(featureData)
      
      // svg의 크기에 따른 지도의 크기와 위치값을 설정합니다.
      const dx = bounds[1][0] - bounds[0][0]
      const dy = bounds[1][1] - bounds[0][1]
      const x = (bounds[0][0] + bounds[1][0]) / 2.0
      const y = (bounds[0][1] + bounds[1][1]) / 2.0
      const scale = 1.0 / Math.max(dx / width, dy / height)
      const translate = [width / 2.0 - scale * x, height / 2.0 - scale * y]
   
      projection.scale(scale).translate(translate)
        
      // svg를 만들고
      const svg = d3
        .select(chart.current)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
   
      const mapLayer = svg.append('g')
      
      // topoJSON의 데이터를 그려줍니다.
      mapLayer
        .selectAll('path')
        .data(featureData.features)
        .enter().append('path') 
        .attr('d', path)
        .style('fill', '#fff')
    }
   
    useEffect(() => {
      printD3()
    }, [])
   
    return (
      <div ref={chart}></div>
    )
  }
   
  export default KoreaMap