#!/usr/bin/env python3
"""
Mist API snapshot-backup.

Bruk:
  export MIST_BASE_URL="https://api.<region>.mist.com"
  export MIST_API_TOKEN="..."
  export MIST_ORG_ID="..."
  python3 backup_mist.py

Fyll inn endpoint-listene under med paths fra Mist API Reference.
Scriptet lagrer rå JSON som snapshot per dag.
"""

import json
import os
import pathlib
import sys
import time
from datetime import datetime, timezone
from typing import Any

import requests

BASE_URL = os.environ.get("MIST_BASE_URL", "").rstrip("/")
API_TOKEN = os.environ.get("MIST_API_TOKEN", "")
ORG_ID = os.environ.get("MIST_ORG_ID", "")
PAGE_LIMIT = int(os.environ.get("MIST_PAGE_LIMIT", "100"))

if not BASE_URL or not API_TOKEN or not ORG_ID:
    print("Missing one of MIST_BASE_URL, MIST_API_TOKEN, MIST_ORG_ID", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Accept": "application/json",
}

BACKUP_ROOT = pathlib.Path("mist-backup") / datetime.now(timezone.utc).strftime("%Y-%m-%d")
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)


def save_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def request_json(path: str, page: int | None = None) -> requests.Response:
    headers = dict(HEADERS)
    if page is not None:
        headers["X-Page-Limit"] = str(PAGE_LIMIT)
        headers["X-Page-Page"] = str(page)
    return requests.get(f"{BASE_URL}{path}", headers=headers, timeout=60)


def get_paginated(path: str) -> Any:
    page = 1
    results: list[Any] = []

    while True:
        resp = request_json(path, page=page)
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list):
            return data

        results.extend(data)
        if len(data) < PAGE_LIMIT:
            return results

        page += 1
        time.sleep(0.2)


def backup_collection(base_dir: pathlib.Path, objects: dict[str, str]) -> None:
    for filename, path in objects.items():
        try:
            data = get_paginated(path)
            save_json(base_dir / filename, data)
            print(f"OK {base_dir}/{filename}")
        except Exception as exc:
            print(f"FEIL {base_dir}/{filename}: {exc}")


def main() -> None:
    org_objects = {
        "org.json": f"/api/v1/orgs/{ORG_ID}",
        "sites.json": f"/api/v1/orgs/{ORG_ID}/sites",
        # Fyll ut videre fra Mist API Reference:
        # "switch-templates.json": f"/api/v1/orgs/{ORG_ID}/switch_templates",
        # "org-webhooks.json": f"/api/v1/orgs/{ORG_ID}/webhooks",
        # "admins.json": f"/api/v1/orgs/{ORG_ID}/admins",
    }

    backup_collection(BACKUP_ROOT / "org", org_objects)

    sites_path = BACKUP_ROOT / "org" / "sites.json"
    if not sites_path.exists():
        print("sites.json mangler, stopper", file=sys.stderr)
        sys.exit(2)

    sites = json.loads(sites_path.read_text(encoding="utf-8"))
    manifest: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": BASE_URL,
        "org_id": ORG_ID,
        "site_count": len(sites),
        "sites": [],
    }

    for site in sites:
        site_id = site["id"]
        site_name = site.get("name", site_id).replace("/", "_")
        site_dir = BACKUP_ROOT / "sites" / site_name
        save_json(site_dir / "site.json", site)

        site_objects = {
            # Fyll ut videre fra Mist API Reference:
            # "devices.json": f"/api/v1/sites/{site_id}/devices",
            # "wlans.json": f"/api/v1/sites/{site_id}/wlans",
            # "switches.json": f"/api/v1/sites/{site_id}/switches",
            # "switch-ports.json": f"/api/v1/sites/{site_id}/switch_ports",
            # "site-webhooks.json": f"/api/v1/sites/{site_id}/webhooks",
            # "setting.json": f"/api/v1/sites/{site_id}/setting",
        }
        backup_collection(site_dir, site_objects)
        manifest["sites"].append({"site_id": site_id, "site_name": site_name})

    save_json(BACKUP_ROOT / "manifest.json", manifest)
    print(f"Backup complete in {BACKUP_ROOT}")


if __name__ == "__main__":
    main()
