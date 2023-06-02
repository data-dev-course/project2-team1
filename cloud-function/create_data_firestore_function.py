from google.cloud import bigquery
from google.cloud import firestore
import json
import datetime
import sys
import math

def create_document_in(data, context):
  print(data, context)
  create_document()

def create_document():
  query =[
  {"차트01_어제의_유기숫자":
  """
  SELECT count(*) AS cnt
  FROM raw_data.animal_info
  WHERE happenDt in (SELECT  happenDt 
      FROM raw_data.animal_info
      ORDER BY happenDt DESC
      limit 1 )
  """},

  {"차트02_보호중인_유기동물_마리수":
  """
  SELECT count(processState) as cnt
  FROM `strayanimal.raw_data.animal_info`
  WHERE processState = '보호중'
      AND CAST(CAST(happenDt AS STRING) AS DATE FORMAT 'YYYYMMDD') >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
  """},

  {"차트03_보호_종료_시_상태_비율":
  """
  SELECT endState AS endState, COUNT(*) AS count
  FROM analytics.animal_analytics
  WHERE endState IS NOT NULL
      GROUP BY endState
      ORDER BY count DESC
  """},

  {"차트04_60일_보호_종료_상태_비율":
  """
  WITH count_by_it60Day AS (
  SELECT lt60Day, endState,COUNT(*) AS count
  FROM `analytics.animal_analytics`
  WHERE lt60Day IS NOT NULL AND endState IS NOT NULL
  GROUP BY lt60Day, endState
  )
  SELECT a.lt60Day, a.endState, a.count,ROUND((a.count / b.count_by_it60Day) * 100, 2) AS percentage
  FROM count_by_it60Day a
  JOIN (SELECT lt60Day, SUM(count) AS count_by_it60Day FROM count_by_it60Day GROUP BY lt60Day) b
      ON a.lt60Day = b.lt60Day
  ORDER BY a.lt60Day
  """},

  {"차트05_지역별_보호_종료_상태_비율":
  """
  SELECT orgNm, endState, COUNT(*) AS count,
  FROM `analytics`.`animal_analytics`
  WHERE `endState` IS NOT NULL
  GROUP BY orgNm, endState
  ORDER BY count DESC
  """},

  {"차트06_유기건수_축종_내_보호_종료_후_상태":
  """
  SELECT kindCd, endState, COUNT(*) AS count
  FROM `analytics.animal_analytics`
  WHERE `endState` IS NOT NULL
  GROUP BY kindCd, endState
  ORDER BY count DESC
  """},

  {"차트07_분기별_유기발생_건수":
  """
  SELECT format_date("%Y", happenDt) AS `year`, format_date('%Q', happenDt) AS `quarter`, COUNT(*) AS `count`
  FROM `analytics.animal_analytics`
  GROUP BY `year`,`quarter`
  ORDER BY count DESC
  """},

  {"차트08_모든_날짜별_분기별_지역별_유기동물_발생_횟수":
  """
  SELECT `code`, count(*) AS `count`
  FROM
  (WITH A AS
      (SELECT *, TRIM(SUBSTR(orgNm, 1, INSTR(orgNm, ' '))) AS extracted
      FROM `strayanimal.analytics.animal_analytics`)
  SELECT *
  FROM A LEFT JOIN `strayanimal.raw_data.iso_kr` B ON A.extracted = B.name) AS `virtual_table`
  GROUP BY `code`
  """},

  {"차트09_지역별_소득수준_및_유기건수":
  """
  SELECT *
  FROM `analytics.case_count_with_income_Top10`
  """},

  {"차트10_연령대_별_유기_발생_비율":
  """
  SELECT age, ageCount, ROUND(ageCount / SUM(ageCount) OVER(),3) as agePercent
  FROM
  (
      SELECT age, count(age) as ageCount
      FROM analytics.animal_analytics A 
      GROUP BY age
      HAVING (COUNT(*))>2
  )
  ORDER BY ageCount DESC
  """},

  {"차트11_품종_견묘_등록_유기_비율":
  """
  SELECT *
  FROM `analytics.percent_stary_register_spcs`
  ORDER BY registerCnt DESC LIMIT 100
  """
  },
  {"차트12_유기동물_detail_개":
  """
  SELECT *
  FROM analytics.animal_detail_in_shelter
  WHERE kindCd = "개"
  """}
  ,
  {"차트12_유기동물_detail_고양이":
  """
  SELECT *
  FROM analytics.animal_detail_in_shelter
  WHERE kindCd = "고양이"
  """}
]
  client = bigquery.Client()

  for q in query:
    file_name, query = list(q.items())[0]
    query_job = client.query(
      query
    )
    results = query_job.result()  
    json_data = []
    for row in results:
      dic_row = dict(row.items())
      for col in dic_row:
        # datetime 형식을 string으로 변환
        if isinstance(dic_row[col], datetime.date):
          dic_row[col] = dic_row[col].strftime('%Y-%m-%d')
      json_data.append(dic_row)

    # 크기가 큰 경우 분할할 사이즈 구하기 
    memorysize = sys.getsizeof(json_data)
    div_size = math.ceil(memorysize / 20000)
    div_list_size = math.ceil(len(json_data)/div_size)
    
    db = firestore.Client()
    
    if "차트12" in file_name :
      parent_doc_ref = db.collection('test_collection').document("차트12_유기동물_detail")
      n=0
      # 분할한 데이터를 서브 컬렉션에 저장
      for i in range(0, len(json_data), div_list_size):
        filed_data = json_data[i:i+div_list_size]
        collection_name = file_name+"_"+str(n)
        subcollaction_ref = parent_doc_ref.collection(collection_name).document(file_name)
        subcollaction_ref.set({"data":filed_data})
        n += 1
    else:
      db.collection('test_collection').document(file_name).set({"data":json_data})
  
    print("document 생성 완료 : "+ file_name)
    
if __name__ == "__main__":
    create_document()
