from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import hmac
import json
import logging
import os
import re

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()

BASE_DIR = Path(os.environ.get("MIST_WEBHOOK_BASE_DIR", "/var/log/mist-webhooks"))
BASE_DIR.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("mist-webhook")

# Customer -> env var name mapping
ORG_SECRET_ENV_VARS = {
    "dnt": "MIST_SECRET_DNT",
}

# Only persist a small, useful subset of headers
ALLOWED_HEADERS = {
    "content-type",
    "user-agent",
    "x-forwarded-for",
    "x-real-ip",
    "x-request-id",
}

# Topic -> dataset mapping
TOPIC_TO_DATASET = {
    "device-events": "mist.device_events-v2",
    "client-info": "mist.client_info-v2",
    "client-join": "mist.client_join-v2",
    "client-sessions": "mist.client_sessions-v2",
    "alarms": "mist.alarms-v2",
    "audits": "mist.audits-v2",
    "device-updowns": "mist.device_updowns-v2",
}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_iso8601_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_customer(customer: str) -> str:
    return customer.strip().lower()


_slug_invalid_re = re.compile(r"[^a-zA-Z0-9._-]+")


def slugify(value: str | None, fallback: str = "unknown") -> str:
    if not value:
        return fallback
    slug = _slug_invalid_re.sub("-", value.strip().lower()).strip("-._")
    return slug or fallback


def dataset_for_topic(topic: str) -> str:
    return TOPIC_TO_DATASET.get(topic, "mist.unknown-v2")


def get_customer_secret(customer: str) -> str | None:
    env_name = ORG_SECRET_ENV_VARS.get(customer)
    if not env_name:
        return None
    secret = os.environ.get(env_name)
    return secret if secret else None


def verify_signature_v2(secret: str, body: bytes, signature_header: str | None) -> bool:
    if not secret or not signature_header:
        return False
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header.strip())


def filter_headers(headers: Any) -> dict[str, str]:
    filtered: dict[str, str] = {}
    for key, value in headers.items():
        lowered = key.lower()
        if lowered in ALLOWED_HEADERS:
            filtered[lowered] = value
    return filtered


def parse_event_timestamp(value: Any) -> tuple[str | None, Any]:
    """
    Returns:
      (normalized_iso8601_z_or_none, original_raw_value)
    """
    if value is None:
        return None, None

    raw_value = value

    if isinstance(value, (int, float)):
        ts = float(value)
        if ts > 1_000_000_000_000:
            ts = ts / 1000.0
        try:
            return to_iso8601_z(datetime.fromtimestamp(ts, tz=timezone.utc)), raw_value
        except (OverflowError, OSError, ValueError):
            return None, raw_value

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None, raw_value

        try:
            numeric = float(stripped)
            normalized, _ = parse_event_timestamp(numeric)
            return normalized, raw_value
        except ValueError:
            pass

        try:
            normalized = stripped.replace("Z", "+00:00")
            return to_iso8601_z(datetime.fromisoformat(normalized)), raw_value
        except ValueError:
            return None, raw_value

    return None, raw_value


def compute_event_fingerprint(customer: str, topic: str, event: dict[str, Any]) -> str:
    fingerprint_source = {
        "customer": customer,
        "topic": topic,
        "timestamp": event.get("timestamp"),
        "type": event.get("type"),
        "mac": event.get("mac"),
        "device_mac": event.get("device_mac"),
        "device_id": event.get("device_id"),
        "site_id": event.get("site_id"),
        "org_id": event.get("org_id"),
        "text": event.get("text"),
        "message": event.get("message"),
        "raw": event,
    }
    raw = json.dumps(
        fingerprint_source,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def topic_filename(customer: str, topic: str, dt: datetime) -> Path:
    topic_slug = slugify(topic, fallback="unknown-topic")
    out_dir = BASE_DIR / customer / topic_slug
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{dt.strftime('%Y-%m-%d')}.jsonl"


def base_record(
    *,
    received_at: str,
    customer: str,
    request: Request,
    topic: str,
    filtered_request_headers: dict[str, str],
) -> dict[str, Any]:
    dataset = dataset_for_topic(topic)

    return {
        "@timestamp": received_at,
        "data_stream": {
            "type": "logs",
            "dataset": dataset,
            "namespace": "prod",
        },
        "event": {
            "module": "mist",
            "dataset": dataset,
            "ingested": received_at,
            "kind": "event",
        },
        "service": {
            "name": "mist-webhook",
            "type": "webhook",
        },
        "labels": {
            "customer": customer,
        },
        "url": {
            "path": str(request.url.path),
        },
        "http": {
            "request": {
                "method": request.method,
            }
        },
        "mist": {
            "topic": topic,
            "webhook": {
                "request_headers": filtered_request_headers,
            },
        },
    }


def enrich_common_fields(record: dict[str, Any], event: dict[str, Any]) -> None:
    if isinstance(event.get("site_name"), str):
        record["mist"]["site_name"] = event["site_name"]
        record.setdefault("site", {})["name"] = event["site_name"]

    if isinstance(event.get("site_id"), str):
        record["mist"]["site_id"] = event["site_id"]
        record.setdefault("site", {})["id"] = event["site_id"]

    if isinstance(event.get("org_id"), str):
        record["organization"] = {"id": event["org_id"]}

    if isinstance(event.get("device_name"), str):
        record.setdefault("observer", {})["name"] = event["device_name"]

    if isinstance(event.get("device_type"), str):
        record.setdefault("observer", {})["type"] = event["device_type"]

    if isinstance(event.get("model"), str):
        record.setdefault("observer", {})["product"] = event["model"]

    if isinstance(event.get("mac"), str):
        record.setdefault("observer", {})["mac"] = event["mac"]


def enrich_audit_fields(record: dict[str, Any], event: dict[str, Any]) -> None:
    record["event"]["category"] = ["configuration"]
    record["event"]["type"] = ["change"]

    if isinstance(event.get("message"), str):
        record["message"] = event["message"]

        msg = event["message"].lower()
        if msg.startswith("accessed "):
            record["event"]["action"] = "access"
        elif msg.startswith("update "):
            record["event"]["action"] = "update"
        elif msg.startswith("create "):
            record["event"]["action"] = "create"
        elif msg.startswith("delete "):
            record["event"]["action"] = "delete"
        else:
            record["event"]["action"] = "audit"

    record["event"]["outcome"] = "success"

    if isinstance(event.get("admin_name"), str):
        record["user"] = {"name": event["admin_name"]}

    if isinstance(event.get("src_ip"), str):
        record["source"] = {"ip": event["src_ip"]}

    audit_target: dict[str, Any] = {}

    if isinstance(event.get("device_id"), str):
        audit_target["target_type"] = "device"
        audit_target["target_id"] = event["device_id"]
        record.setdefault("host", {})["id"] = event["device_id"]

    if isinstance(event.get("site_id"), str) and "target_type" not in audit_target:
        audit_target["target_type"] = "site"
        audit_target["target_id"] = event["site_id"]

    if audit_target:
        record["mist"]["audit"] = audit_target


def enrich_device_updown_fields(record: dict[str, Any], event: dict[str, Any]) -> None:
    record["event"]["category"] = ["network"]
    record["event"]["type"] = ["change"]
    record["event"]["outcome"] = "success"

    action = "device_change"
    status = None

    event_type = event.get("type")
    message = event.get("message")

    if isinstance(event_type, str):
        lowered = event_type.lower()
        if "down" in lowered:
            action = "device_down"
            status = "down"
        elif "up" in lowered:
            action = "device_up"
            status = "up"

    if status is None and isinstance(message, str):
        lowered = message.lower()
        if " down" in lowered or lowered.startswith("down"):
            action = "device_down"
            status = "down"
        elif " up" in lowered or lowered.startswith("up"):
            action = "device_up"
            status = "up"

    record["event"]["action"] = action

    if status:
        record.setdefault("mist", {}).setdefault("device", {})["status"] = status

    if isinstance(event.get("device_name"), str):
        record.setdefault("host", {})["name"] = event["device_name"]

    if isinstance(event.get("device_id"), str):
        record.setdefault("host", {})["id"] = event["device_id"]


def build_event_record(
    *,
    received_at: str,
    customer: str,
    request: Request,
    topic: str,
    filtered_request_headers: dict[str, str],
    event: dict[str, Any],
) -> dict[str, Any]:
    record = base_record(
        received_at=received_at,
        customer=customer,
        request=request,
        topic=topic,
        filtered_request_headers=filtered_request_headers,
    )

    event_ts, event_ts_raw = parse_event_timestamp(event.get("timestamp"))

    normalized_event = dict(event)
    if event_ts:
        record["@timestamp"] = event_ts
        normalized_event["timestamp"] = event_ts
        normalized_event["timestamp_raw"] = event_ts_raw

    fingerprint = compute_event_fingerprint(customer, topic, event)

    record["event"].update(
        {
            "id": fingerprint,
            "original": json.dumps(event, ensure_ascii=False, separators=(",", ":")),
        }
    )

    record["mist"]["event"] = normalized_event
    record["mist"]["fingerprint"] = fingerprint

    if isinstance(event.get("type"), str):
        record["event"]["code"] = event["type"]
    if isinstance(event.get("text"), str):
        record["message"] = event["text"]

    enrich_common_fields(record, event)

    if topic == "audits":
        enrich_audit_fields(record, event)
    elif topic == "device-updowns":
        enrich_device_updown_fields(record, event)

    return record


def build_payload_record(
    *,
    received_at: str,
    customer: str,
    request: Request,
    topic: str,
    filtered_request_headers: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    record = base_record(
        received_at=received_at,
        customer=customer,
        request=request,
        topic=topic,
        filtered_request_headers=filtered_request_headers,
    )
    record["event"]["kind"] = "state"
    record["mist"]["payload_type"] = "raw_payload"
    record["mist"]["raw_payload"] = payload
    record["mist"]["event_count"] = (
        len(payload.get("events", []))
        if isinstance(payload.get("events"), list)
        else 0
    )
    return record


def append_jsonl(records: list[dict[str, Any]], filename: Path) -> None:
    try:
        with filename.open("a", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
    except OSError as exc:
        logger.exception("Failed to write webhook records to %s", filename)
        raise HTTPException(status_code=500, detail="Failed to persist webhook payload") from exc


@app.on_event("startup")
async def validate_configuration() -> None:
    missing = [env for env in ORG_SECRET_ENV_VARS.values() if not os.environ.get(env)]
    if missing:
        logger.warning("Missing Mist webhook secrets for env vars: %s", ", ".join(sorted(missing)))
    else:
        logger.info("Mist webhook secrets loaded for all configured customers")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook/{customer}")
async def webhook(customer: str, request: Request) -> dict[str, Any]:
    customer = normalize_customer(customer)
    secret = get_customer_secret(customer)
    if secret is None:
        raise HTTPException(status_code=404, detail="Unknown customer")

    body = await request.body()
    sig_v2 = request.headers.get("x-mist-signature-v2")
    if not verify_signature_v2(secret, body, sig_v2):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    received_dt = utcnow()
    received_at = to_iso8601_z(received_dt)
    topic = slugify(payload.get("topic"), fallback="unknown-topic")
    filtered_request_headers = filter_headers(request.headers)
    events = payload.get("events", [])

    filename = topic_filename(customer, topic, received_dt)
    records: list[dict[str, Any]] = []

    if isinstance(events, list) and events:
        for item in events:
            if isinstance(item, dict):
                records.append(
                    build_event_record(
                        received_at=received_at,
                        customer=customer,
                        request=request,
                        topic=topic,
                        filtered_request_headers=filtered_request_headers,
                        event=item,
                    )
                )
            else:
                records.append(
                    build_payload_record(
                        received_at=received_at,
                        customer=customer,
                        request=request,
                        topic=topic,
                        filtered_request_headers=filtered_request_headers,
                        payload={"topic": payload.get("topic"), "events": [item]},
                    )
                )
    else:
        records.append(
            build_payload_record(
                received_at=received_at,
                customer=customer,
                request=request,
                topic=topic,
                filtered_request_headers=filtered_request_headers,
                payload=payload if isinstance(payload, dict) else {"raw_payload": payload},
            )
        )

    append_jsonl(records, filename)

    logger.info(
        "Stored %s record(s) for customer=%s topic=%s dataset=%s file=%s",
        len(records),
        customer,
        topic,
        dataset_for_topic(topic),
        filename,
    )

    return {
        "status": "ok",
        "customer": customer,
        "topic": topic,
        "dataset": dataset_for_topic(topic),
        "records_written": len(records),
    }