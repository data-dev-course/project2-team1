import os
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

ERROR_CNT = 0
MAX_RETRIES = 10
URL = "http://apis.data.go.kr/1543061/abandonmentPublicSrvc/abandonmentPublic"

KEY = "본인의 KEY"


def date_range(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    dates = [
        (start + timedelta(days=i)).strftime("%Y%m%d")
        for i in range((end - start).days)
    ]
    return dates


today = datetime.now().strftime("%Y-%m-%d")
before_one_month = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m-%d")


params = {
    "serviceKey": KEY,
    "bgnde": "yyyymmdd",
    "endde": "yyyymmdd",
    "numOfRows": "1000",
    "_type": "json",
}

error_date = set()
result_df = pd.DataFrame(
    columns=[
        "desertionNo",
        "filename",
        "happenDt",
        "happenPlace",
        "kindCd",
        "colorCd",
        "age",
        "weight",
        "noticeNo",
        "noticeSdt",
        "noticeEdt",
        "popfile",
        "processState",
        "sexCd",
        "neuterYn",
        "specialMark",
        "careNm",
        "careTel",
        "careAddr",
        "orgNm",
        "chargeNm",
        "officetel",
    ]
)
daily_data_cnt = 0

print("ㅡ" * 30)
dates = date_range(before_one_month, today)
for date in dates:
    params["bgnde"] = date
    params["endde"] = date
    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(URL, params=params, timeout=5)

            if "SERVICE_KEY_IS_NOT_REGISTERED_ERROR" in response.text:
                raise Exception("Server error -> SERVICE_KEY_IS_NOT_REGISTERED_ERROR")
            else:
                df_dailydata = pd.DataFrame(
                    json.loads(response.text)["response"]["body"]["items"]["item"]
                )  # daily data json -> df
                result_df = pd.concat([result_df, df_dailydata], ignore_index=True)
                daily_data_cnt += df_dailydata.shape[0]
                print(
                    date,
                    "성공 데이터 :",
                    df_dailydata.shape[0],
                    "/",
                    "총 데이터 :",
                    daily_data_cnt,
                )
                break

        except requests.exceptions.Timeout as errb:
            print("Timeout Error :", errb)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting :", errc)
        except requests.exceptions.HTTPError as errd:
            print("Http Error : ", errd)
        except Exception as e:
            print(date, "error :", e)
    else:
        print("error_date 추가", date)
        error_date.add(date)
    print("ㅡ" * 20)


SAVE_PATH = "/home/ubuntu/openAPI/data/strayanimal_data_" + dates[-1] + ".csv"
if len(error_date) > 0:
    print("ㅡ" * 20)
    print("ㅣ" + "error date 목록 :", list(error_date).sort(), "ㅣ")
    print("ㅡ" * 20)
else:
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)

    result_df.to_csv(SAVE_PATH, encoding="utf-8-sig")
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    print("ㅣ data 저장 성공 ㅣ")
    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
    exec(open("/home/ubuntu/openAPI/uploader/data_uploader.py").read())
    print("ㅡ" * 30)
    exec(open("/home/ubuntu/openAPI/updater/animal_status_bigquery_update.py").read())
    print("ㅡ" * 30)
    exec(open("/home/ubuntu/openAPI/updater/animal_info_bigquery_update.py").read())
    print("ㅡ" * 30)
