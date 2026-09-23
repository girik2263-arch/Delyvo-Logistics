from pathlib import Path
import shutil,py_compile

f=Path("app/routes/auth.py")
shutil.copy2(f,str(f)+".me-backup")

text=f.read_text()

if '@auth_bp.get("/me")' not in text:
    marker='@auth_bp.post("/logout")'
    block='''@auth_bp.get("/me")
def me():
    token=get_bearer_token()

    if not token:
        return jsonify({"error":"Bearer token is required"}),401

    rows=supabase_request(
        "GET","auth_sessions",
        params={
            "select":"id,user_id,expires_at,revoked_at",
            "token_hash":f"eq.{hash_token(token)}",
            "revoked_at":"is.null",
            "limit":"1"
        }
    ) or []

    if not rows:
        return jsonify({"error":"Invalid session"}),401

    session=rows[0]

    try:
        expiry=datetime.fromisoformat(
            session["expires_at"].replace("Z","+00:00")
        )
        if expiry <= datetime.now(timezone.utc):
            return jsonify({"error":"Session expired"}),401
    except Exception:
        return jsonify({"error":"Invalid session expiry"}),401

    users=supabase_request(
        "GET","users",
        params={
            "select":"id,company_id,name,email,phone,role,status",
            "id":f"eq.{session['user_id']}",
            "limit":"1"
        }
    ) or []

    if not users:
        return jsonify({"error":"User not found"}),404

    user=users[0]

    if user["status"]!="active":
        return jsonify({"error":"User account is not active"}),403

    return jsonify({
        "authenticated":True,
        "user":user_response(user),
        "expires_at":session["expires_at"]
    })


'''
    text=text.replace(marker,block+marker,1)
    f.write_text(text)

py_compile.compile(str(f),doraise=True)

print("OK /api/auth/me added")
print("Existing auth flow preserved")
print("Backup: app/routes/auth.py.me-backup")
