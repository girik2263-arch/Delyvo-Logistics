from flask import Blueprint, jsonify, request
from app.services.supabase_client import supabase_request

shipments_bp = Blueprint("shipments", __name__)


@shipments_bp.get("/api/shipments")
def list_shipments():
    rows = supabase_request(
        "GET",
        "shipments",
        params={
            "select": "*",
            "order": "created_at.desc",
            "limit": "100"
        }
    ) or []

    return jsonify(rows)


@shipments_bp.post("/api/shipments")
def create_shipment():
    data = request.get_json(silent=True) or {}

    required = [
        "company_id",
        "delivery_city",
    ]

    missing = [
        field for field in required
        if not data.get(field)
    ]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "fields": missing
        }), 400

    payload = {
        key: value
        for key, value in data.items()
        if value not in (None, "")
    }

    rows = supabase_request(
        "POST",
        "shipments",
        json=payload
    )

    if rows is None:
        return jsonify({
            "error": "Unable to create shipment"
        }), 500

    return jsonify({
        "message": "Shipment created successfully",
        "shipment": rows[0] if isinstance(rows, list) and rows else rows
    }), 201


@shipments_bp.get("/api/shipments/<shipment_id>")
def get_shipment(shipment_id):
    rows = supabase_request(
        "GET",
        "shipments",
        params={
            "select": "*",
            "id": f"eq.{shipment_id}"
        }
    ) or []

    if not rows:
        return jsonify({
            "error": "Shipment not found"
        }), 404

    return jsonify(rows[0])
