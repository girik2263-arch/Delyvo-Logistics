from flask import Blueprint,jsonify,request
from app.services.supabase_client import supabase_request

bp=Blueprint("reports",__name__)

@bp.get("/api/reports/shipments")
def shipments_report():
    rows=supabase_request(
        "GET","shipments",
        params={"select":"id,awb,company_id,partner_id,status,payment_mode,cod_amount,delivery_city,created_at",
                "order":"created_at.desc","limit":"10000"}
    ) or []
    return jsonify({"count":len(rows),"data":rows})

@bp.get("/api/reports/status")
def status_report():
    rows=supabase_request(
        "GET","shipments",
        params={"select":"status","limit":"10000"}
    ) or []
    counts={}
    for r in rows:
        s=r.get("status") or "unknown"
        counts[s]=counts.get(s,0)+1
    return jsonify({"total":len(rows),"by_status":counts})

@bp.get("/api/reports/collections")
def collections_report():
    rows=supabase_request(
        "GET","collections",
        params={"select":"amount,status,company_id,partner_id,created_at",
                "limit":"10000"}
    ) or []
    totals={}
    for r in rows:
        s=r.get("status") or "unknown"
        totals[s]=round(totals.get(s,0)+float(r.get("amount") or 0),2)
    return jsonify({"count":len(rows),"currency":"INR","by_status":totals})

@bp.get("/api/reports/companies")
def companies_report():
    companies=supabase_request(
        "GET","companies",
        params={"select":"id,name,status,city,state,created_at",
                "order":"created_at.desc","limit":"1000"}
    ) or []
    shipments=supabase_request(
        "GET","shipments",
        params={"select":"company_id,status","limit":"10000"}
    ) or []

    summary={}
    for c in companies:
        summary[str(c["id"])]={
            "company":c,
            "shipment_count":0,
            "delivered":0,
            "in_transit":0
        }

    for s in shipments:
        cid=str(s.get("company_id"))
        if cid in summary:
            summary[cid]["shipment_count"]+=1
            if s.get("status")=="delivered":
                summary[cid]["delivered"]+=1
            elif s.get("status") not in ("created","cancelled","delivered"):
                summary[cid]["in_transit"]+=1

    return jsonify(list(summary.values()))
