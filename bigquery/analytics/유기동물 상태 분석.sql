/* 유기동물 상태 비율 */
SELECT (CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
GROUP BY endState;

/* 유기동물 상태 비율; 축종 */
SELECT kindCd, (CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
GROUP BY kindCd, endState;

/* 유기동물 상태 비율; 품종별
- 비품종/품종으로 나눌까요?
*/
/* 개 */
SELECT kindSpcs, (CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
WHERE kindCd='개'
GROUP BY kindSpcs, endState
ORDER BY kindSpcs;

/* 고양이 */
SELECT kindSpcs, (CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
WHERE kindCd='고양이'
GROUP BY kindSpcs, endState
ORDER BY kindSpcs;

/* 기타축종 (drop empty)*/
SELECT kindSpcs, (CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
WHERE kindCd='기타축종' AND kindSpcs != "."
GROUP BY kindSpcs, endState
ORDER BY kindSpcs;

/* 유기동물 상태 비율; 연령별 */
SELECT 
(CASE WHEN 
  CAST(age AS INT64)=extract(year from current_date) AND lt60Day=1 
  THEN 0 
  ELSE extract(year from current_date)-CAST(age AS INT64)+1 
  END) as ageToday, 
(CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state,
COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
GROUP BY ageToday, endState
ORDER BY ageToday;

/* 유기동물 상태 비율; 지역별 */
SELECT orgNm, (CASE WHEN endState IS NOT NULL THEN endState ELSE '보호중' END) AS state, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
GROUP BY orgNm, endState;
