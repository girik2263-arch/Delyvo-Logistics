from flask import Blueprint, jsonify, request
from app.services.supabase_client import supabase_request

bp=Blueprint("collections",__name__)

@bp.get("/api/collections")
def list_collections():
    r=supabase_request(
        "GET","collections",
        params={"select":"*","order":"created_at.desc","limit":"100"}
    )
    return jsonify(r or [])

@bp.post("/api/collections")
def create_collection():
    d=request.get_json(silent=True) or {}
    sid=d.get("shipment_id")
    if not sid:
        return jsonify({"error":"shipment_id required"}),400

    s=supabase_request(
        "GET","shipments",
        params={"select":"id,company_id,partner_id,payment_mode,cod_amount,status",
                "id":f"eq.{sid}"}
    ) or []

    if not s:
        return jsonify({"error":"shipment not found"}),404

    shipment=s[0]

    if shipment.get("payment_mode")!="cod":
        return jsonify({"error":"shipment is not COD"}),400

    amount=d.get("amount",shipment.get("cod_amount",0))
    payload={
        "shipment_id":sid,
        "company_id":shipment["company_id"],
        "partner_id":d.get("partner_id",shipment.get("partner_id")),
        "amount":amount,
        "status":d.get("status","pending"),
        "payment_method":d.get("payment_method"),
        "transaction_ref":d.get("transaction_ref"),
        "notes":d.get("notes")
    }

    r=supabase_request("POST","collections",json=payload)
    return jsonify({"message":"collection created","data":r or []}),201

@bp.patch("/api/collections/<cid>")
def update_collection(cid):
    d=request.get_json(silent=True) or {}
    allowed={"status","payment_method","transaction_ref",
             "collected_at","remitted_at","notes","amount"}
    payload={k:v for k,v in d.items() if k in allowed}

    if not payload:
        return jsonify({"error":"no valid fields"}),400

    r=supabase_request(
        "PATCH","collections",
        params={"id":f"eq.{cid}"},
        json=payload
    )
    return jsonify({"message":"collection updated","data":r or []})
