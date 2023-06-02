/* 지역별 유기동물 발생 수 */
SELECT orgNm, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
GROUP BY orgNm;

/* 연도별 증감 정도 */
SELECT orgNm, EXTRACT(YEAR FROM happenDt) AS year, COUNT(desertionNo) as caseNum
FROM `analytics.animal_analytics`
GROUP BY orgNm, EXTRACT(YEAR FROM happenDt);

/* 동물 등록 테이블의 지역별 등록 동물 수와 유기동물 발생 수의 상관관계
CREATE OR REPLACE TABLE `analytics.case_register_count_location` as
*/
SELECT A.orgNm, A.caseNum, B.registerNum
FROM (
  SELECT orgNm, COUNT(desertionNo) AS caseNum 
  FROM `analytics.animal_analytics` 
  GROUP BY orgNm) A
JOIN (
  SELECT CTPV, SGG, SUM(CNT) AS registerNum 
  FROM raw_data.animal_register 
  GROUP BY CTPV, SGG) B
ON A.orgNm = CONCAT(B.CTPV, ' ', B.SGG);

/* 지역별 소득수준에 따른 유기동물 발생 수
CREATE OR REPLACE TABLE `analytics.case_count_with_income` as
 */
SELECT A.location, A.income_avg, B.caseNum
FROM (
  SELECT 
  CONCAT(SPLIT(adstrd_nm, ' ')[offset(0)], ' ', SPLIT(adstrd_nm, ' ')[offset(1)]) AS location, 
  AVG(ave_income_amt) as income_avg
  FROM `raw_data.family_income_info`
  GROUP BY location
  ) A
JOIN (
  SELECT orgNm, COUNT(desertionNo) AS caseNum 
  FROM `analytics.animal_analytics` 
  GROUP BY orgNm
) B
ON A.location = B.orgNm
ORDER BY A.income_avg DESC;

/* 지역별 소득수준에 따른 유기동물 발생 수 (각 소득, 발생 수 TOP10)
CREATE OR REPLACE TABLE `analytics.case_count_with_income_Top10` as
 */
SELECT *
FROM (
  SELECT *
  FROM analytics.case_count_with_income
  ORDER BY income_avg DESC LIMIT 10
) as t1
UNION ALL
SELECT *
FROM(
  SELECT *
  FROM analytics.case_count_with_income
  ORDER BY caseNum DESC LIMIT 10
) as t2
