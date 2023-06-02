# FLOW

![ubuntu-server](https://github.com/data-dev-course/project2-team1/assets/89768234/620c2d08-aed7-45d1-830e-599cf95e93cf)

<br>

##
# 데이터 수집

OpenAPI 사용 : [링크](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15098931)

- 상세기능에서 Dropdown -> 유기동물 조회

<br>

##
# Compute Engine or Cloud Functions

디테일한 API 호출과 Cloud Functions 사용 경험이 없어 고전적인 방식을 사용

1. Compute Engine에 Ubuntu 설치
2. Python으로 스크립트 작성
3. Crontab을 사용해 작업 예약
    - `$ crontab -l`
    - `5 0 * * * python3 /openAPI/crontab_strayanimal_data.py >> /openAPI/log/strayanimal_data_cron.log` 추가
4. 추가적으로 Compute Engine 인스턴스에도 일정 예약
    

<br>

- Ubuntu 설치는 20.04 이상 why? 

    - Ubuntu 18은 기본적으로 python3.6까지만 지원
    - google 라이브러리는 python3.7 이상만 지원




<br>

## ubuntu 서버 접속 
### (계정 : ubuntu PW:~~~~)

<br>

터미널 접근시, ssh 사용해서 그냥 접근   

vsCode 접근시, 다음 <a herf='https://jstar0525.tistory.com/14'>링크</a> 참고, 세팅 config 파일 수정은 개인설정에 맞춰 비슷하게 수정

+ [추가]   
    만약 py 실행시에는 python3 ~~.py 로 실행   
    pip 필요시에는 python3 -m pip install ~~ 로 사용하셔야 합니다!   
    (가상환경을 만들지 않고 글로벌하게 진행)