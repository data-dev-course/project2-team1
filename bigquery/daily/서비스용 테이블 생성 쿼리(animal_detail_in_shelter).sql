CREATE OR REPLACE TABLE `analytics.animal_detail_in_shelter` as
SELECT 
A.desertionNo,
A.happenDt,
B.popfile,
A.kindCd,
A.kindSpcs,
A.colorCd,
A.age,
A.weight,
A.sexCd,
A.specialMark,
A.careNm,
A.careAddr
FROM analytics.animal_analytics A 
  JOIN `raw_data.animal_info` B ON A.desertionNo = B.desertionNo
WHERE 
  A.processState = '보호중'
  AND A.happenDt >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
