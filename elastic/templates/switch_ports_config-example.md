# Foreslått stream

`logs-mist.switch_ports_config-v1-prod`

Brukes til API-basert snapshot av switchport-konfigurasjon.

- ett dokument per port
- hentes periodisk via Mist API
- brukes til korrelasjon mot `mist.device_events-v2`
