from pathlib import Path
import shutil

root=Path(".")
routes=root/"app/routes"
routes.mkdir(parents=True,exist_ok=True)

f=routes/"collections.py"
if f.exists():
    shutil.copy2(f,str(f)+".bak")

f.write_text('''from flask import Blueprint, jsonify, request
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
''')

reg=routes/"__init__.py"
text=reg.read_text()

if "from app.routes.collections import bp as collections_bp" not in text:
    lines=text.splitlines()
    pos=0
    while pos<len(lines) and lines[pos].startswith("from "):
        pos+=1
    lines.insert(pos,"from app.routes.collections import bp as collections_bp")
    text="\n".join(lines)+"\n"

if "app.register_blueprint(collections_bp)" not in text:
    marker="def register_routes(app):"
    if marker in text:
        text=text.replace(marker,marker+"\n    app.register_blueprint(collections_bp)",1)

reg.write_text(text)

# Add collections to Control Center resource map if present
c=routes/"control_dashboard.py"
if c.exists():
    ct=c.read_text()
    ct=ct.replace(
        '"shipments":"shipments"',
        '"shipments":"shipments","collections":"collections"'
    )
    c.write_text(ct)

import py_compile
py_compile.compile(str(f),doraise=True)
py_compile.compile(str(reg),doraise=True)

print("✅ COD COLLECTIONS API COMPLETE")
print("GET   /api/collections")
print("POST  /api/collections")
print("PATCH /api/collections/<id>")
print("No fake data inserted.")
