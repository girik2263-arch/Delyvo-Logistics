from flask import Blueprint,jsonify
from app.services.supabase_client import supabase_request
bp=Blueprint("control",__name__)
T={"companies":"companies","hubs":"hubs","pilots":"partners","shipments":"shipments","collections":"collections"}
@bp.get("/api/control/<r>")
def get(r):
 t=T.get(r)
 if not t:return jsonify({"error":"unknown resource"}),404
 return jsonify(supabase_request("GET",t,params={"select":"*","limit":"100"}) or [])
