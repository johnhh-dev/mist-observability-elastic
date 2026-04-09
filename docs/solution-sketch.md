# Solution Sketch

This document provides a compact visual overview of the Mist observability solution documented in this repository.

## 1. High-Level Architecture

```mermaid
flowchart LR
    A[Juniper Mist Cloud] -->|Webhook topics| B[Nginx]
    B --> C[FastAPI receiver]
    C --> D[JSONL event spool]
    D --> E[Filebeat]
    E --> F[Elasticsearch data streams]
    F --> G[Kibana dashboards]
    H[Backup / state sync job] --> F
```

## 2. Logical Responsibility Split

```mermaid
flowchart TD
    A[Source Layer] --> A1[Mist webhooks]
    B[Edge Layer] --> B1[Nginx TLS + reverse proxy]
    C[Ingest Layer] --> C1[FastAPI validation]
    C --> C2[Timestamp normalization]
    C --> C3[Event enrichment]
    C --> C4[JSONL persistence]
    D[Transport Layer] --> D1[Filebeat filestream]
    E[Storage Layer] --> E1[Elasticsearch data streams]
    F[Presentation Layer] --> F1[Kibana dashboards]
    F --> F2[Investigations / filters]
```

## 3. Topic to Dataset Mapping

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

## 4. Request Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant Mist as Mist
    participant Nginx as Nginx
    participant API as FastAPI
    participant Disk as JSONL
    participant FB as Filebeat
    participant ES as Elasticsearch
    participant KB as Kibana

    Mist->>Nginx: POST webhook payload
    Nginx->>API: Reverse proxy request
    API->>API: Verify x-mist-signature-v2
    API->>API: Parse topic and events
    API->>Disk: Append structured records
    FB->>Disk: Read JSONL files
    FB->>ES: Forward events
    KB->>ES: Query and visualize data
```

## 5. Troubleshooting Path

```mermaid
flowchart TD
    A[Dashboard empty] --> B{Data in Elasticsearch?}
    B -->|Yes| C[Check Kibana filters, time range, saved object config]
    B -->|No| D{Data in Filebeat output?}
    D -->|Yes| E[Check ES permissions, templates, ingest path]
    D -->|No| F{JSONL files present?}
    F -->|Yes| G[Check Filebeat path, filestream offsets, parsing]
    F -->|No| H[Check Nginx route, FastAPI logs, webhook signature]
```

## 6. Suggested Next Evolution

```mermaid
flowchart LR
    A[Current pipeline] --> B[Add explicit mapping for Mist Edge + NAC topics]
    B --> C[Version-control Kibana saved objects]
    C --> D[Add pipeline health dashboards]
    D --> E[Add alerting and replay strategy]
    E --> F[Ingest config snapshots / state history]
```

