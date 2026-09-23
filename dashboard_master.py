from pathlib import Path
import shutil,subprocess,sys
R=Path.cwd(); F=R/"frontend/index.html"; D=R/"backend/app/routes/control_dashboard.py"; I=R/"backend/app/routes/__init__.py"
shutil.copy2(F,str(F)+".bak"); shutil.copy2(I,str(I)+".bak")
D.write_text('''from flask import Blueprint,jsonify
from app.services.supabase_client import supabase_request
bp=Blueprint("control",__name__)
T={"companies":"companies","hubs":"hubs","pilots":"partners","shipments":"shipments"}
@bp.get("/api/control/<r>")
def get(r):
 t=T.get(r)
 if not t:return jsonify({"error":"unknown resource"}),404
 return jsonify(supabase_request("GET",t,params={"select":"*","limit":"100"}) or [])
''')
x=I.read_text()
if "control_dashboard" not in x:
 x="from app.routes.control_dashboard import bp as control_dashboard_bp\n"+x
 x=x.replace("def register_routes(app):","def register_routes(app):\n    app.register_blueprint(control_dashboard_bp)")
 I.write_text(x)
h=F.read_text()
if "DELYVO_CONTROL_CENTER" not in h:
 u='''<section id="DELYVO_CONTROL_CENTER" style="margin:25px;padding:20px;background:#fff;border-radius:16px"><h2>🚚 Delyvo Control Center</h2><button onclick="dc('companies')">Companies</button> <button onclick="dc('shipments')">Shipments</button> <button onclick="dc('hubs')">Hubs</button> <button onclick="dc('pilots')">Pilots</button><pre id="dcbox">Select</pre></section><script>async function dc(x){let r=await fetch('/api/control/'+x);document.getElementById('dcbox').textContent=JSON.stringify(await r.json(),null,2)}</script>'''
 F.write_text(h.replace("</body>",u+"</body>",1))
for f in [R/"backend/app/__init__.py",I,D]: subprocess.run([sys.executable,"-m","py_compile",str(f)],check=True)
print("✅ DELYVO DASHBOARD COMPLETE")
