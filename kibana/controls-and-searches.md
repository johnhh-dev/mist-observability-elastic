# Controls og søk

## Globalt DNT-filter

```kql
labels.customer : "dnt"
```

## Unike enheter per SSID

KQL:

```kql
labels.customer : "dnt" and data_stream.dataset : ("mist.client_join-v2" or "mist.client_sessions-v2" or "mist.client_info-v2")
```

Lens:
- Horizontal axis: `mist.event.ssid.keyword`
- Vertical axis: `Unique count`
- Unique count field: `observer.mac` eller `observer.mac.keyword`

## Port flap events

KQL:

```kql
labels.customer : "dnt" and event.code.keyword : ("SW_PORT_DOWN" or "SW_PORT_UP")
```

Foreslåtte kolonner i tabell:

- `@timestamp` (30 min bucketing)
- `site.name.keyword`
- `observer.name.keyword`
- `mist.event.port_id`
- `event.code.keyword`
- `Count of records`

## Events per site

KQL:

```kql
labels.customer : "dnt"
```

Lens:
- X-axis: `site.name.keyword`
- Y-axis: `Count`
- Breakdown optional: `data_stream.dataset`

## Device event codes

KQL:

```kql
labels.customer : "dnt" and data_stream.dataset : "mist.device_events-v2"
```

Lens:
- X-axis: `event.code.keyword`
- Y-axis: `Count`

## Forskjell på streams

- `client-join`: tilkoblingsøyeblikk
- `client-sessions`: avsluttet eller oppsummert sesjon med varighet og disconnect
- `client-info`: klientmetadata og klientrelatert kontekst
- `device-events`: hendelser fra nettverksutstyr, inkludert port-hendelser
- `device-updowns`: device-status opp/ned
- `audits`: administrative endringer
