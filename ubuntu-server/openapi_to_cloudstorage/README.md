# ubuntu server에서 진행되는 crontab

`# crontab -l`   
`5 0 * * * python3 ~PATH/crontab_strayanimal_data.py >> ~PATH/log/strayanimal_data_cron.log`

`/var/log/~~.log` 에 저장하는 것이 바람직하지만 편의를 위해 스크립트 위치에 로그를 남김