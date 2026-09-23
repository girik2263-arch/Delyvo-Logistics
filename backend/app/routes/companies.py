from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from app.services.supabase_client import supabase_request


companies_bp = Blueprint(
    "companies",
    __name__,
    url_prefix="/api/companies",
)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_company(company_id):
    rows = supabase_request(
        "GET",
        "companies",
        params={
            "select": "*",
            "id": f"eq.{company_id}",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


@companies_bp.get("")
def list_companies():
    rows = supabase_request(
        "GET",
        "companies",
        params={
            "select": "*",
            "order": "created_at.desc",
        },
    )

    return jsonify({
        "companies": rows or [],
        "count": len(rows or []),
    })


@companies_bp.get("/<company_id>")
def company_detail(company_id):
    company = get_company(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    return jsonify({"company": company})


@companies_bp.post("")
def create_company():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    company_code = str(data.get("company_code", "")).strip().upper()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    address = str(data.get("address", "")).strip()
    city = str(data.get("city", "")).strip()
    state = str(data.get("state", "")).strip()
    pincode = str(data.get("pincode", "")).strip()

    if not name:
        return jsonify({"error": "Company name is required"}), 400

    if not company_code:
        return jsonify({"error": "Company code is required"}), 400

    filters = {
        "company_code": f"eq.{company_code}",
    }

    if email:
        existing_code = supabase_request(
            "GET",
            "companies",
            params={
                "select": "id",
                "company_code": f"eq.{company_code}",
                "limit": "1",
            },
        )

        existing_email = supabase_request(
            "GET",
            "companies",
            params={
                "select": "id",
                "email": f"eq.{email}",
                "limit": "1",
            },
        )

        if existing_code or existing_email:
            return jsonify({
                "error": "Company code or email already exists"
            }), 409
    else:
        existing_code = supabase_request(
            "GET",
            "companies",
            params={
                "select": "id",
                "company_code": f"eq.{company_code}",
                "limit": "1",
            },
        )

        if existing_code:
            return jsonify({
                "error": "Company code already exists"
            }), 409

    timestamp = now_iso()

    payload = {
        "name": name,
        "company_code": company_code,
        "phone": phone or None,
        "email": email or None,
        "address": address or None,
        "city": city or None,
        "state": state or None,
        "pincode": pincode or None,
        "status": "active",
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    try:
        created = supabase_request(
            "POST",
            "companies",
            params={"select": "*"},
            json=payload,
        )
    except Exception as exc:
        message = str(exc)

        if "23505" in message or "duplicate" in message.lower():
            return jsonify({
                "error": "Company code or email already exists"
            }), 409

        return jsonify({
            "error": "Company creation failed"
        }), 500

    if not created:
        return jsonify({"error": "Company creation failed"}), 500

    return jsonify({
        "message": "Company created successfully",
        "company": created[0],
    }), 201


@companies_bp.patch("/<company_id>")
def update_company(company_id):
    company = get_company(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    data = request.get_json(silent=True) or {}

    allowed = {
        "name",
        "company_code",
        "phone",
        "email",
        "address",
        "city",
        "state",
        "pincode",
        "status",
    }

    payload = {
        key: data[key]
        for key in allowed
        if key in data
    }

    if "name" in payload:
        payload["name"] = str(payload["name"]).strip()

    if "company_code" in payload:
        payload["company_code"] = (
            str(payload["company_code"]).strip().upper()
        )

    if "email" in payload and payload["email"]:
        payload["email"] = str(payload["email"]).strip().lower()

    if "status" in payload:
        if payload["status"] not in {"active", "inactive"}:
            return jsonify({"error": "Invalid company status"}), 400

    if not payload:
        return jsonify({"error": "No fields to update"}), 400

    payload["updated_at"] = now_iso()

    try:
        updated = supabase_request(
            "PATCH",
            "companies",
            params={
                "id": f"eq.{company_id}",
                "select": "*",
            },
            json=payload,
        )
    except Exception as exc:
        if "duplicate" in str(exc).lower():
            return jsonify({
                "error": "Company code or email already exists"
            }), 409

        return jsonify({"error": "Company update failed"}), 500

    if not updated:
        return jsonify({"error": "Company update failed"}), 500

    return jsonify({
        "message": "Company updated successfully",
        "company": updated[0],
    })


@companies_bp.delete("/<company_id>")
def delete_company(company_id):
    company = get_company(company_id)

    if not company:
        return jsonify({"error": "Company not found"}), 404

    updated = supabase_request(
        "PATCH",
        "companies",
        params={
            "id": f"eq.{company_id}",
            "select": "*",
        },
        json={
            "status": "inactive",
            "updated_at": now_iso(),
        },
    )

    return jsonify({
        "message": "Company deactivated successfully",
        "company": updated[0] if updated else None,
    })
