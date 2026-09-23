from flask import Blueprint,jsonify
from app.services.supabase_client import supabase_request

bp=Blueprint("finance",__name__)

@bp.get("/api/finance/summary")
def summary():
    rows=supabase_request(
        "GET","collections",
        params={"select":"amount,status,company_id,created_at",
                "limit":"10000"}
    ) or []

    totals={
        "total":0,
        "pending":0,
        "collected":0,
        "remitted":0,
        "failed":0,
        "cancelled":0
    }

    for r in rows:
        amount=float(r.get("amount") or 0)
        totals["total"]+=amount
        status=r.get("status")
        if status in totals:
            totals[status]+=amount

    totals={k:round(v,2) for k,v in totals.items()}

    return jsonify({
        "currency":"INR",
        "collection_count":len(rows),
        "totals":totals
    })

@bp.get("/api/finance/collections")
def collections():
    rows=supabase_request(
        "GET","collections",
        params={
            "select":"*,shipments(awb,order_id,customer_name)",
            "order":"created_at.desc",
            "limit":"100"
        }
    ) or []
    return jsonify(rows)
