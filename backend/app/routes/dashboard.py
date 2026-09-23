from flask import Blueprint, jsonify
from app.services.supabase_client import supabase_request

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/api/dashboard")
def dashboard():
    companies = supabase_request(
        "GET", "companies",
        params={"select": "id"}
    ) or []

    hubs = supabase_request(
        "GET", "hubs",
        params={"select": "id"}
    ) or []

    partners = supabase_request(
        "GET", "partners",
        params={"select": "id,status"}
    ) or []

    all_shipments = supabase_request(
        "GET", "shipments",
        params={
            "select": "id,status"
        }
    ) or []

    recent_shipments = supabase_request(
        "GET", "shipments",
        params={
            "select": "id,awb,company_id,delivery_city,status,created_at",
            "order": "created_at.desc",
            "limit": "10"
        }
    ) or []

    active_pilots = sum(
        1 for partner in partners
        if partner.get("status") == "active"
    )

    in_transit = sum(
        1 for shipment in all_shipments
        if shipment.get("status") in [
            "pickup_requested",
            "picked_up",
            "at_hub",
            "out_for_delivery"
        ]
    )

    delivered = sum(
        1 for shipment in all_shipments
        if shipment.get("status") == "delivered"
    )

    return jsonify({
        "stats": {
            "companies": len(companies),
            "hubs": len(hubs),
            "active_pilots": active_pilots,
            "total_shipments": len(all_shipments),
            "in_transit": in_transit,
            "delivered": delivered
        },
        "recent_shipments": recent_shipments
    })
