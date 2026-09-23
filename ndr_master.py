from pathlib import Path
import shutil,subprocess,sys

R=Path.cwd(); D=R/"backend/app/routes/ndr.py"; I=R/"backend/app/routes/__init__.py"
shutil.copy2(I,str(I)+".ndr.bak")

D.write_text('''from flask import Blueprint,jsonify,request
from app.services.supabase_client import supabase_request
bp=Blueprint("ndr",__name__)

@bp.post("/api/shipments/<sid>/ndr")
def create(sid):
 d=request.get_json(silent=True) or {}
 d["shipment_id"]=sid
 r=supabase_request("POST","ndr",json=d)
 return jsonify({"message":"NDR created","data":r or []}),201

@bp.get("/api/shipments/<sid>/ndr")
def get(sid):
 r=supabase_request("GET","ndr",params={"shipment_id":f"eq.{sid}","order":"created_at.desc"}) or []
 return jsonify(r)

@bp.post("/api/shipments/<sid>/ndr/action")
def action(sid):
 d=request.get_json(silent=True) or {}; a=d.get("action")
 status={"reattempt":"out_for_delivery","rto":"rto","cancel":"cancelled"}.get(a)
 if not status:return jsonify({"error":"invalid action"}),400
 r=supabase_request("PATCH","shipments",params={"id":f"eq.{sid}"},json={"status":status})
 return jsonify({"message":"NDR action applied","status":status,"data":r or []})
''')

x=I.read_text()
if "routes.ndr" not in x:
 x="from app.routes.ndr import bp as ndr_bp\n"+x
 x=x.replace("def register_routes(app):","def register_routes(app):\n    app.register_blueprint(ndr_bp)")
 I.write_text(x)

for f in [D,I]: subprocess.run([sys.executable,"-m","py_compile",str(f)],check=True)
print("✅ NDR + RTO COMPLETE")
