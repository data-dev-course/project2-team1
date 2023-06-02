-- 지역별, 월별 유기동물 발견횟수와 인구수 비교

WITH

population AS
(
  SELECT
    baseYm,
    location,
    SUM(total) AS total,
    SUM(man) AS man,
    SUM(woman) AS woman
  FROM 
  (
    SELECT 
      CASE WHEN SPLIT(citySubNm,' ')[offset(0)] IS NULL OR cityNm = '제주특별자치도'
        THEN cityNm ELSE CONCAT(cityNm,' ',SPLIT(citySubNm, ' ')[offset(0)])  END as location, 
      total, 
      man, 
      woman,
      CAST(baseDT AS STRING FORMAT 'YYYYMM') as baseYm
    FROM `raw_data.monthly_population`
  )
  GROUP BY
    baseYm,
    location
)
,staryAnimal AS
(
  SELECT 
    baseYm,
    orgNm,
    COUNT(desertionNo) as caseNum
  FROM 
  (
    SELECT 
      CAST(happenDt AS STRING FORMAT 'YYYYMM') as baseYm,
      orgNm,
      desertionNo
    FROM `analytics.animal_analytics`
  )
  GROUP BY
    baseYm,
    orgNm
)

SELECT CAST(A.baseYm AS DATE FORMAT "YYYYMM") as baseYm, orgNm as location, caseNum, total, man, woman
FROM staryAnimal A JOIN population B
  ON A.baseYm = B.baseYm AND A.orgNm = B.location;
