<div align="center">

# ⚡ Mist Observability Showcase

### Juniper Mist → Nginx → FastAPI → Filebeat → Elasticsearch → Kibana

**A production-style observability pipeline for receiving, validating, enriching, shipping, and visualizing Mist webhook events.**

<p>
  <img src="https://img.shields.io/badge/Source-Juniper%20Mist-1F6FEB?style=for-the-badge" alt="Juniper Mist" />
  <img src="https://img.shields.io/badge/Edge-Nginx-009639?style=for-the-badge" alt="Nginx" />
  <img src="https://img.shields.io/badge/Ingest-FastAPI-009688?style=for-the-badge" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Shipping-Filebeat-6D28D9?style=for-the-badge" alt="Filebeat" />
  <img src="https://img.shields.io/badge/Search-Elasticsearch-FEC514?style=for-the-badge" alt="Elasticsearch" />
  <img src="https://img.shields.io/badge/Visualization-Kibana-F04E98?style=for-the-badge" alt="Kibana" />
</p>

<p>
  <img src="https://img.shields.io/badge/Use%20Case-Network%20Observability-111827?style=flat-square" alt="Use Case" />
  <img src="https://img.shields.io/badge/Architecture-Hybrid%20Lab-111827?style=flat-square" alt="Architecture" />
  <img src="https://img.shields.io/badge/Format-JSONL%20Event%20Pipeline-111827?style=flat-square" alt="Format" />
  <img src="https://img.shields.io/badge/Status-Operational-16A34A?style=flat-square" alt="Status" />
</p>

</div>

---

## ✨ Executive Summary

This repository captures a **real Mist-to-Elastic implementation** where **Juniper Mist Cloud** sends webhook events to a public HTTPS endpoint, **Nginx** proxies traffic to a **FastAPI** receiver, events are validated and stored as structured **JSONL**, then forwarded by **Filebeat** into **Elasticsearch** and analyzed in **Kibana**.

It is built to give fast operational visibility into:

- client activity and session behavior
- alarms, audits, and device up/down events
- switch port flap investigations
- site and SSID usage distribution
- data ingest flow and observability pipeline health

---

## 🧭 Architecture at a Glance

```mermaid
flowchart LR
    A[Juniper Mist Cloud] -->|HTTPS POST webhook| B[Nginx\nPublic endpoint]
    B --> C[FastAPI receiver\n/webhook/dnt]
    C --> D[Structured JSONL files\ncustomer/topic/day]
    D --> E[Filebeat filestream]
    E --> F[Elasticsearch data streams]
    F --> G[Kibana dashboards]
    F --> H[Kibana investigations / alerts]
    I[Mist API backup job] --> J[Snapshot / state data]
    J --> F
```

---

## 🎯 What This Project Shows

<table>
<tr>
<td width="33%">

### 🌐 Edge Layer
Public HTTPS exposure with Nginx, path-based routing, and a clean webhook entrypoint.

</td>
<td width="33%">

### ⚙️ Ingest Layer
FastAPI validates `x-mist-signature-v2`, enriches records, normalizes timestamps, and writes JSONL.

</td>
<td width="33%">

### 📊 Observability Layer
Filebeat ships events into Elasticsearch where Kibana dashboards expose trends, anomalies, and operations data.

</td>
</tr>
</table>

---

## 🏷️ Showcase Categories

<div align="center">

| Category | Purpose | Repo Area |
|---|---|---|
| **📡 Source** | Mist webhooks and event topics | `webhook/`, `docs/current-deployment-dnt.md` |
| **🛡️ Edge** | Public endpoint, TLS, reverse proxy | `nginx/` |
| **⚙️ Ingest** | Validation, normalization, enrichment, JSONL writes | `webhook/` |
| **🚚 Shipping** | File harvesting and forwarding | `filebeat/` |
| **🗃️ Search & Storage** | Data streams and queryable records | `elastic/` |
| **📈 Visualization** | Dashboards, tables, KQL ideas, analysis views | `kibana/` |
| **🧰 Operations** | Backup scripts, runbooks, next steps | `scripts/`, `docs/` |

</div>

---

## 🧱 Technology Stack

| Layer | Component | Role |
|---|---|---|
| Source | **Juniper Mist** | Delivers webhook topics and API state data |
| Edge | **Nginx** | Exposes the webhook endpoint and proxies requests |
| Ingest | **FastAPI** | Validates signature, parses payloads, enriches records |
| Persistence | **JSONL files** | Durable local event spool per topic/day |
| Shipping | **Filebeat** | Harvests files and sends records onward |
| Storage | **Elasticsearch** | Stores Mist datasets as searchable time-series data |
| Visualization | **Kibana** | Dashboards, Lens visualizations, tables, filtering |
| Automation | **Python scripts** | Backup jobs and future enrichment/state sync |

---

## 🗂️ Repository Layout

```text
.
├── docs/              # Architecture, deployment notes, runbooks, roadmap
├── webhook/           # FastAPI Mist receiver
├── nginx/             # Reverse proxy configuration
├── filebeat/          # Filebeat ingest configuration
├── kibana/            # Dashboard notes and search patterns
├── scripts/           # Backup and operational helpers
├── elastic/           # Template and mapping examples
└── examples/          # API / saved-object helper examples
```

---

## 🚀 Key Features

- **Webhook verification** using Mist signature validation
- **Topic-aware dataset routing** into Elastic data streams
- **Structured event persistence** in JSONL for resilience and replay potential
- **Normalized timestamps** and repeatable event fingerprinting
- **Operational dashboards** for sites, SSIDs, alarms, sessions, and port behavior
- **Clear separation of concerns** across edge, ingest, transport, storage, and visualization

---

## 🔄 End-to-End Event Flow

```mermaid
sequenceDiagram
    autonumber
    participant Mist as Juniper Mist Cloud
    participant Nginx as Nginx
    participant API as FastAPI Receiver
    participant Disk as JSONL Storage
    participant FB as Filebeat
    participant ES as Elasticsearch
    participant Kibana as Kibana

    Mist->>Nginx: POST /webhook/dnt
    Nginx->>API: Forward request
    API->>API: Validate signature
    API->>API: Parse topic and events
    API->>Disk: Write JSONL records
    FB->>Disk: Harvest files
    FB->>ES: Ship events to data streams
    Kibana->>ES: Query dashboards and investigations
```

---

## ✅ Confirmed in the Current DNT Setup

The repository and supplied screenshots confirm the following:

- webhook endpoint: `https://mist.labmetrics.dev/webhook/dnt`
- webhook type: `HTTP POST`
- webhook status: enabled
- enabled Mist topics:
  - `Alerts`
  - `Audits`
  - `Client Information`
  - `Client Join`
  - `Client Sessions`
  - `Device Events`
  - `Device Up/Downs`
  - `Mist Edge Events`
  - `NAC Accounting`
  - `NAC Events`
- Kibana dashboard coverage includes:
  - event volume over time
  - events per site
  - alarms by severity
  - device event codes
  - top AP names
  - client activity over time
  - top SSIDs
  - port flap event tables
  - unique devices per SSID

---

## 🧪 Active Data Streams

### Explicitly mapped in `webhook/app.py`

- `logs-mist.device_events-v2-prod`
- `logs-mist.alarms-v2-prod`
- `logs-mist.client_join-v2-prod`
- `logs-mist.client_sessions-v2-prod`
- `logs-mist.client_info-v2-prod`
- `logs-mist.audits-v2-prod`
- `logs-mist.device_updowns-v2-prod`

### Currently falling back to `mist.unknown-v2`

These topics are enabled in Mist but do not yet have dedicated mappings:

- `mist-edge-events`
- `nac-accounting`
- `nac-events`

### Suggested future stream

- `logs-mist.switch_ports_config-v1-prod`

---

## 🧠 Topic Mapping Overview

```mermaid
flowchart TD
    A[device-events] --> A1[mist.device_events-v2]
    B[client-info] --> B1[mist.client_info-v2]
    C[client-join] --> C1[mist.client_join-v2]
    D[client-sessions] --> D1[mist.client_sessions-v2]
    E[alarms] --> E1[mist.alarms-v2]
    F[audits] --> F1[mist.audits-v2]
    G[device-updowns] --> G1[mist.device_updowns-v2]
    H[mist-edge-events] --> H1[mist.unknown-v2]
    I[nac-accounting] --> I1[mist.unknown-v2]
    J[nac-events] --> J1[mist.unknown-v2]
```

---

## 📷 Showcase Highlights

<details>
<summary><strong>Dashboard perspective</strong></summary>

The DNT Kibana dashboard shows both high-level and troubleshooting-oriented views, including event timelines, event code counts, site distribution, SSID usage, and unique client/device perspectives.

</details>

<details>
<summary><strong>Webhook perspective</strong></summary>

The Mist webhook configuration confirms the public endpoint, enabled topics, and the current scope of the integration. This is directly reflected in the repository documentation.

</details>

<details>
<summary><strong>Pipeline perspective</strong></summary>

The repo documents the path from webhook receipt to analytics: **Mist → Nginx → FastAPI → JSONL → Filebeat → Elasticsearch → Kibana**.

</details>

---

## 🛠️ Quick Start Reading Order

Start here if you want the fastest way to understand the implementation:

1. `README.md`
2. `docs/solution-sketch.md`
3. `webhook/app.py`
4. `nginx/mist.labmetrics.dev.conf`
5. `filebeat/filebeat.yml`
6. `kibana/mist-overview-dashboard.md`
7. `docs/runbook-filebeat-elastic.md`
8. `scripts/backup_mist.py`

---

## 🚨 Current Gaps

- missing explicit dataset mappings for `mist-edge-events`, `nac-accounting`, and `nac-events`
- Kibana saved objects are not yet version-controlled in exported JSON form
- ingest health is not yet visualized end-to-end as a dedicated operational dashboard
- no built-in replay pipeline or dead-letter handling for malformed/nonstandard event shapes
- configuration snapshot ingestion is still only partially represented in the repo

---

## 🗺️ Roadmap

- [ ] Add explicit dataset mappings for all enabled Mist webhook topics
- [ ] Export and version-control Kibana saved objects
- [ ] Build pipeline health dashboards
- [ ] Add alerting for missing events and abnormal port flap patterns
- [ ] Ingest switch-port configuration snapshots and backup state data
- [ ] Add deployment examples for lab and production-style environments

---

## 🧩 Troubleshooting View

```mermaid
flowchart TD
    A[No data in Kibana] --> B{Data in Elasticsearch?}
    B -->|No| C{Data in Filebeat logs?}
    B -->|Yes| D[Check dashboard filters and time range]
    C -->|No| E{JSONL files written by FastAPI?}
    C -->|Yes| F[Check Elasticsearch ingest / index template / permissions]
    E -->|No| G[Check Nginx routing, webhook signature, app logs]
    E -->|Yes| H[Check Filebeat path, parsing, and filestream state]
```

---

## 📌 Evidence Reflected in This Repo

This showcase README and the surrounding docs were updated from the provided materials:

- DNT Mist webhook configuration screenshot
- Kibana dashboard screenshots for `Mist Overview - DNT`
- uploaded `app.py` webhook receiver implementation
- uploaded Nginx configuration for the public endpoint

---

## 📄 Usage Note

This repository is best treated as a **reference implementation / lab-style deployment**. Before reusing it elsewhere, adjust:

- customer IDs and names
- URLs and hostnames
- local file paths
- secret handling
- environment variable conventions
- data stream naming and retention strategy

