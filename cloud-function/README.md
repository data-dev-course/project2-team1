# Cloud Funtion - Pub/Sub Work Flow

## 1. FLOW

![프로젝트2-3팀-1조 (3)](https://github.com/data-dev-course/project2-team1/assets/57780594/3bbc305e-4574-48c6-bea3-a47dc8b92941)


1. BigQuery에서 Table update 시 message발생
2. Pub/Sub에서 해당 message에 대한 Topic(주제)를 파악 후 trigger 발생
3. trigger에 연결된 Cloud Function실행 (본 프로젝트에서는 BigQuery에 query를 보내는 요청을 구현)
4. BigQuery에서 Query에 따른 data를 반환
5. data를 받은 Cloud Function은 Firestore에 적재가능한 형태로 변환 후 적재

<br>

## 2. Pub/Sub
    ⭐️ Pub/Sub란?
    - 메세지 큐 시스템, 메세징 패턴 중 하나
    - 메세지 큐 : 프로세스 또는 프로그램 간에 데이터를 교환할 때 사용하는 통신 방법 중에 하나로, 메세지 지향 미들웨어를 구현한 시스템을 의미
    - pub(publisher)가 topic에 메세지를 보내면 해당 topic을 구독해놓은 sub(subscriber) 모두에게 메세지가 전송되면서 데이터 교환이 이루어지는 방법
    - 비동기식 메세징 패턴이기 때문에 publisher가 연산해야 할 다른 topic(task)을 publish하면 topic과 연결된 subscriber가 해당 task를 처리하고, 그 동안 publisher는 다른 작업을 수행할 수 있다는 장점이 있음

![프로젝트2-3팀-1조 (1)](https://github.com/data-dev-course/project2-team1/assets/57780594/c1b1f7a9-ee31-41a5-9575-7cc771acb0ac)
1. publisher(게시자)
<br> &nbsp;- publisher는 message를 생성한 뒤에, topic에 담아두도록 전달해주는 서버
2. message(메세지)
<br> &nbsp;- message는 publisher로 부터 subscriber에게 최종적으로 전달되는 데이터와 property의 조합 (Api끼리 통신을 할 데이터라고 할 수 있음)
3. topic(주제)
<br> &nbsp;- topic은 task, 즉 업무이며 publisher가 message를 전달하는 리소스
4. subscription(구독)
<br> &nbsp;- subscription은 message스트림이 subscriber들에게 전달되는 과정을 나타내는 이름을 가지고 있는 리소스 
5. subscriber(구독자)
<br> &nbsp;- subscriber는 message를 수신하려는 서버

<br>

## 3. BigQuery - Pub/Sub - Cloud Function 구성방법

