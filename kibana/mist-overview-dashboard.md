# Mist Overview - DNT

## Anbefalt dataview

`logs-mist.*-v2-prod`

## Dashboard-struktur fra skjermbilder

### Rad 1 – Infrastruktur

1. **Events over time by dataset**
2. **Events per site**
3. **Alarms by severity**
4. **Device event codes**
5. **Top AP names**

### Rad 2 – Klienter og SSID

6. **Client activity over time**
7. **Top SSID**
8. **Port flap events**
9. **Unique devices per SSID** (bar)
10. **Unique devices per SSID** (line)
11. **Unique devices per SSID** (pie)

## Forslag til controls

- `site.name.keyword` -> label: `Lokasjon`
- `data_stream.dataset` -> label: `Datastream`
- `mist.event.ssid.keyword` -> label: `SSID`
- `observer.name.keyword` -> label: `Enhet`

## Nyttige KQL

Alle DNT-events:

```kql
labels.customer : "dnt"
```

Infrastruktur-events:

```kql
labels.customer : "dnt" and data_stream.dataset : ("mist.device_events-v2" or "mist.alarms-v2" or "mist.device_updowns-v2" or "mist.audits-v2")
```

Klient-events:

```kql
labels.customer : "dnt" and data_stream.dataset : ("mist.client_join-v2" or "mist.client_sessions-v2" or "mist.client_info-v2")
```

Port flap view:

```kql
labels.customer : "dnt" and event.code.keyword : ("SW_PORT_DOWN" or "SW_PORT_UP")
```

## Felter som ser ut til å være brukt i panelene

- `@timestamp`
- `data_stream.dataset`
- `site.name.keyword`
- `observer.name.keyword`
- `observer.mac`
- `mist.event.ssid.keyword`
- `mist.event.port_id`
- `event.code.keyword`
