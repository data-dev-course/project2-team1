--차트01 어제의 유기숫자
SELECT count(*) AS cnt
FROM raw_data.animal_info
WHERE happenDt in (SELECT  happenDt 
    FROM raw_data.animal_info
    ORDER BY happenDt DESC
    limit 1 );

--차트02 보호중인 유기동 마리수
SELECT count(processState) as cnt
FROM `strayanimal.raw_data.animal_info`
WHERE processState = '보호중'
  AND CAST(CAST(happenDt AS STRING) AS DATE FORMAT 'YYYYMMDD') >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH);

--차트03 보호 종료 시 상태 비율
SELECT endState AS endState, COUNT(*) AS count
FROM analytics.animal_analytics
WHERE endState IS NOT NULL
GROUP BY endState
ORDER BY count DESC;

--차트04 60일 기준 동물 보호 종료 상태 비율
WITH count_by_it60Day AS (
SELECT lt60Day, endState, COUNT(*) AS count
FROM `analytics.animal_analytics`
WHERE
  lt60Day IS NOT NULL
  AND endState IS NOT NULL
GROUP BY lt60Day, endState
)

SELECT
a.lt60Day, a.endState, a.count, ROUND((a.count / b.count_by_it60Day) * 100, 2) AS percentage
FROM count_by_it60Day a
  JOIN (SELECT lt60Day, SUM(count) AS count_by_it60Day FROM count_by_it60Day GROUP BY lt60Day) b
    ON a.lt60Day = b.lt60Day
ORDER BY a.lt60Day;

--차트05 지역별 보호 종료 상태 비율
SELECT orgNm,
      endState,
      COUNT(*) AS count,
FROM `analytics`.`animal_analytics`
WHERE `endState` IS NOT NULL
GROUP BY `orgNm`,
        `endState`
ORDER BY count DESC;

--차트06 유기건수 축종 내 보호 종료 후 상태
SELECT kindCd,
      endState,
      COUNT(*) AS count
FROM `analytics.animal_analytics`
WHERE `endState` IS NOT NULL
GROUP BY `kindCd`,
        `endState`
ORDER BY count DESC;

--차트07 분기별 유기발생 건수
SELECT format_date("%Y", happenDt) AS `year`,
        format_date('%Q', happenDt) AS `quarter`,
        COUNT(*) AS `count`
FROM `analytics.animal_analytics`
GROUP BY `year`,`quarter`
ORDER BY count DESC;

--차트08 모든 날짜별 분기별 지역별 유기동물 발생 횟수
SELECT `name`,
      count(*) AS `count`
FROM
(WITH A AS
    (SELECT *,
            TRIM(SUBSTR(orgNm, 1, INSTR(orgNm, ' '))) AS extracted
    FROM `strayanimal.analytics.animal_analytics`)
  SELECT *
  FROM A
  LEFT JOIN `strayanimal.raw_data.iso_kr` B ON A.extracted = B.name) AS `virtual_table`
GROUP BY `name`;

--차트09 지역별 소득수준 및 유기건수
SELECT *
FROM `analytics.case_count_with_income_Top10`;

--차트10 연령대 별 유기 발생 비율
SELECT age, ageCount, ROUND(ageCount / SUM(ageCount) OVER(),3) as agePercent
FROM
(
  SELECT age, count(age) as ageCount
  FROM analytics.animal_analytics A 
  GROUP BY age
  HAVING (COUNT(*))>2
)
ORDER BY ageCount DESC;

--차트11 품종 견,묘에 대한 등록/유기 비율
SELECT *
FROM `analytics.percent_stary_register_spcs`
ORDER BY registerCnt DESC
LIMIT 100;

--차트12_1 공고 유기동물 detail_개
SELECT A.desertionNo, A.happenDt, B.popfile, A.kindCd, A.kindSpcs,
  A.colorCd, A.age, A.weight, A.sexCd, A.specialMark, A.careNm, A.careAddr
FROM analytics.animal_analytics A 
JOIN `raw_data.animal_info` B ON A.desertionNo = B.desertionNo
WHERE 
  A.processState = '보호중'
  AND A.happenDt >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
  AND A.kindCd ="개";

--차트12_1 공고 유기동물 detail_고양이
SELECT A.desertionNo, A.happenDt, B.popfile, A.kindCd, A.kindSpcs,
  A.colorCd, A.age, A.weight, A.sexCd, A.specialMark, A.careNm, A.careAddr
FROM analytics.animal_analytics A 
JOIN `raw_data.animal_info` B ON A.desertionNo = B.desertionNo
WHERE 
  A.processState = '보호중'
  AND A.happenDt >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
  AND A.kindCd ="고양이";
