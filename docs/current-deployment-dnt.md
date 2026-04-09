# Nåværende DNT-oppsett

Denne filen oppsummerer det som er synlig i de vedlagte skjermbildene og filene.

## Mist webhook

- Status: `Enabled`
- Webhook type: `HTTP POST`
- Navn: `Webhook`
- URL: `https://mist.labmetrics.dev/webhook/dnt`

### Valgte topics

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

## Nginx-publicering

Publisert hostname:

- `mist.labmetrics.dev`

Proxy-regler:

- `/webhook/dnt` -> lokal FastAPI på `127.0.0.1:9001`
- `/health` -> lokal health-endpoint på `127.0.0.1:9001/health`

## Kibana dashboard: Mist Overview - DNT

Skjermbildene viser at dashboardet er delt i minst to visninger med disse panelene.

### Infrastruktur-del

- Events over time by dataset
- Events per site
- Alarms by severity
- Device event codes
- Top AP names

### Klient- og SSID-del

- Client activity over time
- Top SSID
- Port flap events
- Unique devices per SSID (bar)
- Unique devices per SSID (line)
- Unique devices per SSID (pie)

## Observerte felter i visualiseringene

Felter som ser ut til å være i bruk i dashboardet:

- `@timestamp`
- `data_stream.dataset`
- `site.name.keyword`
- `observer.name.keyword`
- `observer.mac`
- `mist.event.ssid.keyword`
- `mist.site_name.keyword`
- `mist.event.port_id`
- `event.code.keyword`

## Kommentar

Panelene bekrefter at løsningen nå brukes både til:

- overblikk per datasett
- per lokasjon/site
- alarmnivåer
- switch-port hendelser (`SW_PORT_UP` / `SW_PORT_DOWN`)
- klientaktivitet og SSID-fordeling
