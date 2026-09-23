from flask import Blueprint, jsonify, request
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
