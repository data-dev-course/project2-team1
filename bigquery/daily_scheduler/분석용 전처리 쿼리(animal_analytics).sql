
-- Table 생성
CREATE OR REPLACE TABLE analytics.animal_analytics(
  desertionNo INT64 NOT NULL,
  happenDt DATE,
  happenPlace STRING,
  kindCd STRING,
  kindSpcs STRING,
  colorCd STRING,
  birth STRING,
  age INT64,
  lt60Day INT64,
  weight STRING,
  noticeNo STRING,
  noticeSdt DATE,
  noticeEdt DATE,
  processState STRING,
  endState STRING,
  sexCd STRING,
  neuterYn STRING,
  specialMark STRING,
  careNm STRING,
  careAddr STRING,
  orgNm STRING,
  chargeNm STRING,
  officeTel STRING,
  noticeComment STRING
);


-- Table 적재
INSERT INTO analytics.animal_analytics 
SELECT 
  desertionNo,
  CAST(CAST(happenDt AS STRING)AS DATE FORMAT 'YYYYMMDD') AS happenDt,
  happenPlace,
  REGEXP_EXTRACT(kindCd, r'\[(.*?)\]') AS kindCd,  --"[" "]" 사이에있는 값 추출
  REGEXP_EXTRACT(kindCd, r'\] (.*)') AS kindSpcs,   -- "] " 뒤에 있는 값 추출
  colorCd,
  birth,
  CASE WHEN age LIKE '%(60일미만)%' THEN 0
    ELSE CAST(SUBSTRING(cast(noticeSdt AS STRING), 1, 4) AS INT) - CAST(SUBSTRING(birth, 1, 4) AS INT) +1
  END AS age,
  CASE WHEN REGEXP_CONTAINS(age, '(60일미만)') = TRUE THEN 1
    ELSE 0 END as lt60Day, -- "(60일미만)"이 포함되어있는 경우 true 반환
  weight,
  -- CAST(                     -- 몸무게 float형으로 변환 (예시data: 1.7(kg))
  --   REGEXP_REPLACE(         
  --     REGEXP_REPLACE(
  --       REGEXP_EXTRACT(
  --         weight,r'(.*)\('    -- (kg)제거하기 위해 '(' 뒤의 문자 추출
  --       ),
  --       r'^\.', '0'           -- '.'으로 시작되는 data를 0으로 변경 (예시data: .(kg))
  --     ),
  --     r'[^0-9\.]|\.{2,}','.' -- 숫자와 '.'외의 다른 문자 or '.'이 여러개 있는 문자를 '.'으로 변경 (예시data: 3~5(kg), 2...3(kg)) 
  --   ) AS FLOAT64) as weight,
  noticeNo,
  CAST(CAST(noticeSdt AS STRING)AS DATE FORMAT 'YYYYMMDD') AS noticeSdt,
  CAST(CAST(noticeEdt AS STRING)AS DATE FORMAT 'YYYYMMDD') AS noticeEdt,
  CASE WHEN processState = '보호중' THEN processState
    ELSE REGEXP_EXTRACT(processState, r'(.*)\(') END AS processState,
  REGEXP_EXTRACT(processState, r'\((.*?)\)') AS endState,
  sexCd,
  neuterYn,
  specialMark,
  careNm,
  careAddr,
  orgNm,
  chargeNm ,
  officeTel,
  noticeComment
FROM 
(
  SELECT
  *,
    SUBSTR(
      CASE WHEN LENGTH(REGEXP_EXTRACT(age, r'(.*)\(')) = 1
        THEN CONCAT("200",REGEXP_EXTRACT(age, r'(.*)\('))
      WHEN LENGTH(REGEXP_EXTRACT(age, r'(.*)\(')) = 2
        THEN CONCAT("20",REGEXP_EXTRACT(age, r'(.*)\('))
      ELSE
        REGEXP_EXTRACT(age, r'(.*)\(') END, 0,4) as birth
  FROM raw_data.animal_info
);

