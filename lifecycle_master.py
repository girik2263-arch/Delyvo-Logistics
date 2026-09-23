from pathlib import Path
import shutil,subprocess,sys

R=Path.cwd()
D=R/"backend/app/routes/lifecycle.py"
I=R/"backend/app/routes/__init__.py"

shutil.copy2(I,str(I)+".lifecycle.bak")

D.write_text('''from flask import Blueprint,jsonify,request
from app.services.supabase_client import supabase_request

bp=Blueprint("lifecycle",__name__)
ST=["created","pickup_requested","picked_up","at_hub","dispatched","out_for_delivery","delivered","cancelled","ndr","rto"]

@bp.post("/api/shipments/<sid>/status")
def status(sid):
 d=request.get_json(silent=True) or {}
 s=d.get("status")
 if s not in ST:return jsonify({"error":"invalid status","allowed":ST}),400
 r=supabase_request("PATCH","shipments",params={"id":f"eq.{sid}"},json={"status":s})
 return jsonify({"message":"status updated","status":s,"data":r or []})

@bp.get("/api/shipments/<sid>/tracking")
def tracking(sid):
 r=supabase_request("GET","shipments",params={"select":"*","id":f"eq.{sid}"}) or []
 if not r:return jsonify({"error":"shipment not found"}),404
 s=r[0].get("status") or "created"
 return jsonify({"shipment":r[0],"current_status":s,"timeline":[{"status":x,"completed":i<=ST.index(s) if s in ST else False,"current":x==s} for i,x in enumerate(ST)]})
''')

x=I.read_text()
if "routes.lifecycle" not in x:
 x="from app.routes.lifecycle import bp as lifecycle_bp\n"+x
 x=x.replace("def register_routes(app):","def register_routes(app):\n    app.register_blueprint(lifecycle_bp)")
 I.write_text(x)

for f in [D,I]:
 subprocess.run([sys.executable,"-m","py_compile",str(f)],check=True)

print("✅ LIFECYCLE + TRACKING COMPLETE")
