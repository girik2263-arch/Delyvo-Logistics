from pathlib import Path
import shutil,py_compile

f=Path("app/routes/reports.py")
if f.exists(): shutil.copy2(f,str(f)+".bak")

f.write_text('''from flask import Blueprint,jsonify,request
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
''')

reg=Path("app/routes/__init__.py")
shutil.copy2(reg,str(reg)+".reports-backup")

text=reg.read_text()
if "from app.routes.reports import bp as reports_bp" not in text:
    text=text.replace(
        "from app.routes.finance import bp as finance_bp",
        "from app.routes.finance import bp as finance_bp\nfrom app.routes.reports import bp as reports_bp"
    )

if "app.register_blueprint(reports_bp)" not in text:
    text=text.replace(
        "def register_routes(app):",
        "def register_routes(app):\n    app.register_blueprint(reports_bp)",
        1
    )

reg.write_text(text)

py_compile.compile(str(f),doraise=True)
py_compile.compile(str(reg),doraise=True)

print("✅ REPORTS API COMPLETE")
print("GET /api/reports/shipments")
print("GET /api/reports/status")
print("GET /api/reports/collections")
print("GET /api/reports/companies")
print("No fake data inserted.")
