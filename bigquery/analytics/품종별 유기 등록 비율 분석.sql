-- 유기 및 등록 동물 축종별 품종 비율 (품종있는 동물만 진행)
WITH

registerAnimal AS
(
  SELECT
    LVSTCK_KND,
    SPCS,
    SUM(CNT) AS registerCnt
  FROM `raw_data.animal_register` 
  WHERE SPCS NOT IN ('한국 고양이','믹스견','믹스묘','기타')
  GROUP BY 
    LVSTCK_KND,
    SPCS
)
,staryAnimal AS
(
SELECT
  kindCd,
  kindSpcs,
  COUNT(desertionNo) as staryCnt
FROM `analytics.animal_analytics`
WHERE kindSpcs NOT IN ('한국 고양이','믹스견','믹스묘','기타')
GROUP BY
  kindCd,
  kindSpcs
)
,final AS
(
  SELECT
    B.kindCd,
    B.kindSpcs,
    A.registerCnt,
    B.staryCnt,
  FROM registerAnimal A 
    JOIN staryAnimal B ON A.SPCS = B.kindSpcs

  WHERE
    registerCnt > 1
  ORDER BY
    B.kindCd,
    B.staryCnt DESC
)

SELECT
  A.kindCd,
  kindSpcs,
  registerCnt,
  ROUND(registerCnt / regTotal,3) as registerPersent,
  staryCnt,
  ROUND(staryCnt / staryTotal,3) as staryPersent

FROM final A JOIN
(
  SELECT kindCd, SUM(registerCnt) as regTotal, SUM(staryCnt) as staryTotal
  FROM final
  GROUP BY kindCd
) B ON A.kindCd = B.kindCd
ORDER BY registerCnt DESC

