# Runbook: webhook -> fil -> filebeat -> elastic

## 1. Sjekk tjenester

```bash
sudo systemctl status mist-webhook --no-pager
sudo systemctl status filebeat --no-pager
ps -ef | grep [f]ilebeat
```

## 2. Sjekk at filer skrives

```bash
sudo find /var/log/mist-webhooks/dnt -maxdepth 2 -type f -name '*.jsonl' -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\n' | sort | tail -n 20
```

## 3. Sjekk innhold i filer

```bash
sudo tail -n 5 /var/log/mist-webhooks/dnt/device-events/$(date +%F).jsonl
sudo tail -n 5 /var/log/mist-webhooks/dnt/alarms/$(date +%F).jsonl
sudo tail -n 5 /var/log/mist-webhooks/dnt/client-join/$(date +%F).jsonl
sudo tail -n 5 /var/log/mist-webhooks/dnt/client-sessions/$(date +%F).jsonl
sudo tail -n 5 /var/log/mist-webhooks/dnt/client-info/$(date +%F).jsonl
```

## 4. Test Filebeat

```bash
sudo filebeat test config -c /etc/filebeat/filebeat.yml
sudo filebeat test output -c /etc/filebeat/filebeat.yml
```

## 5. Sjekk vanlige feil

```bash
sudo journalctl -u filebeat -n 100 --no-pager
sudo grep -iE "401|403|400|Cannot index event|document_parsing_exception|illegal_argument_exception|failed|dropped|unauthorized|lock" /var/log/filebeat/filebeat*.ndjson
```

## 6. Elasticsearch checks

```http
GET _data_stream/logs-mist.*-v2-prod
GET logs-mist.device_events-v2-prod/_count
GET logs-mist.alarms-v2-prod/_count
GET logs-mist.client_join-v2-prod/_count
GET logs-mist.client_sessions-v2-prod/_count
GET logs-mist.client_info-v2-prod/_count
GET logs-mist.device_updowns-v2-prod/_count
```

## 7. Mapping sanity

```http
GET logs-mist.device_events-v2-prod/_mapping/field/data_stream.dataset,mist.event.timestamp
GET logs-mist.alarms-v2-prod/_mapping/field/data_stream.dataset,mist.event.timestamp
```

## 8. Filebeat lock recovery

```bash
sudo systemctl stop filebeat
sudo pkill -f /usr/share/filebeat/bin/filebeat
ps -ef | grep [f]ilebeat
sudo rm -f /var/lib/filebeat/filebeat.lock
sudo systemctl reset-failed filebeat
sudo systemctl start filebeat
sudo systemctl status filebeat --no-pager
```
