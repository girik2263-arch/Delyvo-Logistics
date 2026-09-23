from pathlib import Path
import shutil,py_compile

routes=Path("app/routes")
f=routes/"finance.py"

if f.exists():
    shutil.copy2(f,str(f)+".bak")

f.write_text('''from flask import Blueprint,jsonify
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
''')

reg=routes/"__init__.py"
text=reg.read_text()

if "from app.routes.finance import bp as finance_bp" not in text:
    lines=text.splitlines()
    pos=0
    while pos<len(lines) and lines[pos].startswith("from "):
        pos+=1
    lines.insert(pos,"from app.routes.finance import bp as finance_bp")
    text="\\n".join(lines)+"\\n"

if "app.register_blueprint(finance_bp)" not in text:
    text=text.replace(
        "def register_routes(app):",
        "def register_routes(app):\\n    app.register_blueprint(finance_bp)",
        1
    )

reg.write_text(text)

py_compile.compile(str(f),doraise=True)
py_compile.compile(str(reg),doraise=True)

print("✅ FINANCE API COMPLETE")
print("GET /api/finance/summary")
print("GET /api/finance/collections")
print("No fake data inserted.")
