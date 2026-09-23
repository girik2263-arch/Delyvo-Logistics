from flask import Blueprint,jsonify,request
from app.services.supabase_client import supabase_request
bp=Blueprint("pilot_assignment",__name__)

@bp.post("/api/shipments/<sid>/assign-pilot")
def assign(sid):
 d=request.get_json(silent=True) or {}; pid=d.get("pilot_id")
 if not pid:return jsonify({"error":"pilot_id required"}),400
 r=supabase_request("PATCH","shipments",params={"id":f"eq.{sid}"},json={"partner_id":pid})
 return jsonify({"message":"pilot assigned","data":r or []})

@bp.get("/api/shipments/<sid>/pilot")
def get_pilot(sid):
 r=supabase_request("GET","shipments",params={"select":"partner_id","id":f"eq.{sid}"}) or []
 if not r:return jsonify({"error":"shipment not found"}),404
 return jsonify(r[0])
