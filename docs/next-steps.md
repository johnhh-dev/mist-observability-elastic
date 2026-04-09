# Neste steg

## Dashboard-rekkefølge

1. Mist Overview
2. Mist Infrastructure
3. Mist Clients
4. Ingest / Pipeline Health

## Alerts å vurdere

- ingen device_events siste 15 min
- ingen client_join siste 30 min
- critical alarms
- mange SW_PORT_DOWN på kort tid
- streams som stopper helt

## Ny foreslått stream

- `logs-mist.switch_ports_config-v1-prod`
- API-basert snapshot, ikke webhook
