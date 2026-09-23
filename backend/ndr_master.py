from pathlib import Path
import py_compile
import shutil
import subprocess
import sys

ROOT = Path(".")
FILE = ROOT / "app/routes/ndr.py"
BACKUP = ROOT / "app/routes/ndr.py.ndr-hardening-backup"

if not FILE.exists():
    print("ERROR: ndr.py not found")
    sys.exit(1)

if not BACKUP.exists():
    shutil.copy2(FILE, BACKUP)
    print("BACKUP:", BACKUP)

code = '''from flask import Blueprint, jsonify, request
from app.services.supabase_client import supabase_request

bp = Blueprint("ndr", __name__)

VALID_ACTIONS = {
    "reattempt": "out_for_delivery",
    "rto": "rto",
    "cancel": "cancelled",
}

@bp.post("/api/shipments/<sid>/ndr")
def create(sid):
    d = request.get_json(silent=True) or {}

    reason = str(d.get("reason") or "").strip()
    notes = d.get("notes")

    if not reason:
        return jsonify({"error": "reason required"}), 400

    payload = {
        "shipment_id": sid,
        "reason": reason,
        "notes": notes,
    }

    r = supabase_request("POST", "ndr", json=payload)

    if r is None:
        return jsonify({"error": "failed to create NDR"}), 502

    return jsonify({
        "message": "NDR created",
        "data": r,
    }), 201


@bp.get("/api/shipments/<sid>/ndr")
def get(sid):
    r = supabase_request(
        "GET",
        "ndr",
        params={
            "shipment_id": f"eq.{sid}",
            "order": "created_at.desc",
        },
    )

    return jsonify(r or [])


@bp.post("/api/shipments/<sid>/ndr/action")
def action(sid):
    d = request.get_json(silent=True) or {}
    action_name = d.get("action")

    status = VALID_ACTIONS.get(action_name)

    if not status:
        return jsonify({
            "error": "invalid action",
            "allowed": list(VALID_ACTIONS.keys()),
        }), 400

    # Only change shipment status here.
    # No NDR row is created by this action endpoint.
    r = supabase_request(
        "PATCH",
        "shipments",
        params={"id": f"eq.{sid}"},
        json={"status": status},
    )

    return jsonify({
        "message": "NDR action applied",
        "status": status,
        "data": r or [],
    })
'''

FILE.write_text(code)

py_compile.compile(str(FILE), doraise=True)

print("PYTHON SYNTAX: OK")

text = FILE.read_text()

required = [
    'POST("/api/shipments/<sid>/ndr")',
    'GET("/api/shipments/<sid>/ndr")',
    'POST("/api/shipments/<sid>/ndr/action")',
    '"reason required"',
    '"reattempt": "out_for_delivery"',
    '"rto": "rto"',
    '"cancel": "cancelled"',
    'supabase_request("POST", "ndr"',
]

for item in required:
    if item not in text:
        print("MISSING:", item)
        sys.exit(1)

print("NDR ROUTE MARKERS: OK")

# If the Flask server is already running, perform safe negative tests.
# These use a deliberately nonexistent UUID and never create real data.
try:
    import requests

    base = "http://127.0.0.1:5000"
    fake = "00000000-0000-0000-0000-000000000000"

    r1 = requests.get(f"{base}/api/shipments/{fake}/ndr", timeout=5)
    print("GET NDR:", r1.status_code)

    r2 = requests.post(
        f"{base}/api/shipments/{fake}/ndr",
        json={},
        timeout=5,
    )
    print("POST NDR empty:", r2.status_code)

    r3 = requests.post(
        f"{base}/api/shipments/{fake}/ndr/action",
        json={"action": "invalid"},
        timeout=5,
    )
    print("NDR invalid action:", r3.status_code)

    if r2.status_code != 400:
        print("WARNING: expected 400 for empty NDR")
    if r3.status_code != 400:
        print("WARNING: expected 400 for invalid action")

except Exception as e:
    print("LIVE SERVER TEST: SKIPPED")
    print("Reason:", str(e))

print("===== NDR HARDENING COMPLETE =====")
