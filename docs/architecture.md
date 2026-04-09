# Arkitektur

## Hovedflyt

```text
Mist Cloud
  └─ Webhook (HTTPS POST)
       URL: https://mist.labmetrics.dev/webhook/dnt
                |
                v
        Nginx reverse proxy (TLS terminering)
                |
                v
        FastAPI webhook receiver (webhook/app.py)
                |
                v
 /var/log/mist-webhooks/<customer>/<topic>/YYYY-MM-DD.jsonl
                |
                v
     Filebeat filestream + ndjson parser
                |
                v
      Elasticsearch data streams (logs-mist.*)
                |
                v
      Kibana dashboards / Lens / Controls
```

## Komponenter

### 1. Mist webhook

Mist sender `HTTP POST` til `/webhook/dnt`.

Webhooken er konfigurert med disse topicene:

- Alerts
- Audits
- Client Information
- Client Join
- Client Sessions
- Device Events
- Device Up/Downs
- Mist Edge Events
- NAC Accounting
- NAC Events

### 2. Nginx

Nginx publiserer `mist.labmetrics.dev` på port 443 med Let's Encrypt-sertifikat og proxier:

- `/webhook/dnt` -> `http://127.0.0.1:9001/webhook/dnt`
- `/health` -> `http://127.0.0.1:9001/health`

Alt annet returnerer `404`.

### 3. FastAPI receiver

Receiveren:

- validerer `x-mist-signature-v2`
- normaliserer customer og topic
- mapper topic til `data_stream.dataset`
- bygger ECS-lignende dokumenter
- skriver ett JSONL-record per event til disk

### 4. Filebeat

Filebeat leser alle filer under:

```text
/var/log/mist-webhooks/*/*/*.jsonl
```

og sender videre til Elastic med indeksnavn bygget fra `data_stream.*`.

## Viktige mapping-prinsipper

- `data_stream.dataset` må matche template / data stream eksakt
- `event.dataset` bør følge samme navn som `data_stream.dataset`
- `@timestamp` bør settes fra event-tid når den finnes
- `mist.event.timestamp` bør være `date` i mapping
- stabil struktur gjør dashboards enkle å vedlikeholde

## Nåværende gap

Disse topicene er aktivert i Mist, men mangler egen mapping i `TOPIC_TO_DATASET`:

- `mist-edge-events`
- `nac-accounting`
- `nac-events`

De vil derfor i dag havne i `mist.unknown-v2`.
