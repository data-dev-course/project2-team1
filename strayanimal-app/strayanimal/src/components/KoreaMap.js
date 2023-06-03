import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { feature } from 'topojson-client';
import korea from '../assets/korea-topo.json';
import countdata from '../assets/export-data_예약8_모든_날짜별_분기별_지역별_유기동물_발생_횟수000000000000.json';

const featureData = feature(korea, korea.objects['korea-topo']);

const KoreaMap = () => {
    const chart = useRef(null);

    const printD3 = () => {
        const width = 600;
        const height = 600;
        const projection = d3.geoMercator().scale(1).translate([0, 0]);
        const path = d3.geoPath().projection(projection);
        const bounds = path.bounds(featureData);
        const dx = bounds[1][0] - bounds[0][0];
        const dy = bounds[1][1] - bounds[0][1];
        const x = (bounds[0][0] + bounds[1][0]) / 2;
        const y = (bounds[0][1] + bounds[1][1]) / 2;
        const scale = 0.9 / Math.max(dx / width, dy / height);
        const translate = [width / 2 - scale * x, height / 2 - scale * y];
        projection.scale(scale).translate(translate);

        const colorScale = d3.scaleLinear()
            .domain([d3.max(countdata, d => parseInt(d.count)), 0])
            .range(['#FF5F15', '#f0f0f0']);
        
        d3.select("svg").remove(); 
        const svg = d3
            .select(chart.current)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const mapLayer = svg.append('g');

        mapLayer
            .selectAll('path')
            .data(featureData.features)
            .enter()
            .append('path')
            .attr('d', path)
            .style('fill', d => {
                const name = d.properties.CTP_KOR_NM;
                const matchingData = countdata.find(item => item.name === name);
                
                if (matchingData) {
                    const count = parseInt(matchingData.count);
                    return colorScale(count);
                } else {
                    return '#666';
                }
            });

        mapLayer
            .selectAll('text')
            .data(featureData.features)
            .enter()
            .append('text')
            .attr('x', d => path.centroid(d)[0])
            .attr('y', d => path.centroid(d)[1])
            .attr('text-anchor', 'middle')
            .attr('alignment-baseline', 'central')
            .attr('font-size', '12px')
            .style('fill', '#fff')
            .text(d => '');

        const legend = svg.append('g')
            .attr('class', 'legend')
            .attr('transform', 'translate(10, 10)');

        const legendItemHeight = 20;
        const legendItems = legend.selectAll('.legend-item')
            .data(colorScale.ticks(5))
            .enter()
            .append('g')
            .attr('class', 'legend-item')
            .attr('transform', (d, i) => `translate(0, ${i * legendItemHeight+10})`)
            .style("fill", "#Fff");

        legendItems.append('rect')
            .attr('width', 10)
            .attr('height', 10)
            .style('fill', d => colorScale(d));

        legendItems.append('text')
            .attr('x', 20)
            .attr('y', 9)
            .attr('font-size', '12px')
            .text(d => d);

        mapLayer
            .selectAll('path')
            .on('mouseover', function (event, d) {
                const [x, y] = d3.pointer(event);
                const name = d.properties.CTP_KOR_NM;
                const matchingData = countdata.find(item => item.name === name);

                let value = 'No data';
                if (matchingData) {
                    value = matchingData.count;
                }

                d3.select(this)
                    .style('fill', '#00B3A0');

                const box = svg.append('g')
                    .attr('class', 'value-box')
                    .attr('transform', `translate(${x},${y - 30})`);

                const boxWidth = 8 * 20;
                const boxHeight = 2 * 13;
                const boxX = -boxWidth / 2;
                const boxY = -boxHeight / 2;

                box.append('rect')
                    .attr('class', 'value-box')
                    .attr('x', boxX)
                    .attr('y', boxY)
                    .attr('width', boxWidth)
                    .attr('height', boxHeight)
                    .attr('rx', 2)
                    .attr('ry', 2)
                    .style('fill', '#Fafafa');

                box.append('text')
                    .attr('class', 'value')
                    .attr('text-anchor', 'middle')
                    .attr('alignment-baseline', 'middle')
                    .attr('font-size', '14px')
                    .attr('dy', 0)
                    .text(name+": "+value);

                d3.select(this)
                    .on('mouseout', function () {
                        d3.select(this)
                            .style('fill', d => {
                                const name = d.properties.CTP_KOR_NM;
                                const matchingData = countdata.find(item => item.name === name);

                                if (matchingData) {
                                    const count = parseInt(matchingData.count);
                                    return colorScale(count);
                                } else {
                                    return '#666';
                                }
                            });

                        svg.select('.value-box').remove();
                    });
            });
    };

    useEffect(() => {
        printD3();
    }, []);

    return (
        <div ref={chart}></div>
    );
};

export default KoreaMap;