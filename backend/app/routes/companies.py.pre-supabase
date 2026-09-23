import sqlite3

from flask import Blueprint, jsonify, request

from app.routes.auth import get_db

companies_bp = Blueprint(
    "companies",
    __name__,
    url_prefix="/api/companies"
)


def get_current_user():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return None

    token = auth[7:].strip()

    if not token:
        return None

    db = get_db()

    try:
        return db.execute(
            """
            SELECT
                u.id,
                u.company_id,
                u.name,
                u.email,
                u.role,
                u.status
            FROM auth_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token_hash = ?
              AND s.revoked_at IS NULL
              AND datetime(s.expires_at) > datetime('now')
              AND u.status = 'active'
            """,
            (__import__("hashlib").sha256(
                token.encode("utf-8")
            ).hexdigest(),)
        ).fetchone()
    finally:
        db.close()


def require_user(roles=None):
    user = get_current_user()

    if not user:
        return None, (
            jsonify({"error": "authentication required"}),
            401
        )

    if roles and user["role"] not in roles:
        return None, (
            jsonify({"error": "permission denied"}),
            403
        )

    return user, None


@companies_bp.post("")
def create_company():
    user, error = require_user({"control"})

    if error:
        return error

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    company_code = str(data.get("company_code", "")).strip().upper()

    if not name or not company_code:
        return jsonify({
            "error": "name and company_code are required"
        }), 400

    db = get_db()

    try:
        cursor = db.execute(
            """
            INSERT INTO companies (
                company_code,
                name,
                email,
                phone,
                address,
                city,
                state,
                pincode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_code,
                name,
                data.get("email"),
                data.get("phone"),
                data.get("address"),
                data.get("city"),
                data.get("state"),
                data.get("pincode"),
            )
        )

        db.commit()

        company = db.execute(
            """
            SELECT *
            FROM companies
            WHERE id = ?
            """,
            (cursor.lastrowid,)
        ).fetchone()

        return jsonify({
            "message": "company created",
            "company": dict(company)
        }), 201

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({
            "error": "company code or email already exists"
        }), 409

    finally:
        db.close()


@companies_bp.get("")
def list_companies():
    user, error = require_user({"control"})

    if error:
        return error

    db = get_db()

    try:
        rows = db.execute(
            """
            SELECT
                id,
                company_code,
                name,
                email,
                phone,
                city,
                state,
                pincode,
                status,
                created_at,
                updated_at
            FROM companies
            ORDER BY id DESC
            """
        ).fetchall()

        return jsonify({
            "count": len(rows),
            "companies": [dict(row) for row in rows]
        })

    finally:
        db.close()


@companies_bp.get("/me")
def company_me():
    user, error = require_user({"company"})

    if error:
        return error

    db = get_db()

    try:
        company = db.execute(
            """
            SELECT *
            FROM companies
            WHERE id = ?
            """,
            (user["company_id"],)
        ).fetchone()

        if not company:
            return jsonify({"error": "company not found"}), 404

        return jsonify({
            "company": dict(company)
        })

    finally:
        db.close()


@companies_bp.get("/<int:company_id>")
def get_company(company_id):
    user, error = require_user({"control", "company"})

    if error:
        return error

    if user["role"] == "company" and user["company_id"] != company_id:
        return jsonify({"error": "permission denied"}), 403

    db = get_db()

    try:
        company = db.execute(
            """
            SELECT *
            FROM companies
            WHERE id = ?
            """,
            (company_id,)
        ).fetchone()

        if not company:
            return jsonify({"error": "company not found"}), 404

        return jsonify({
            "company": dict(company)
        })

    finally:
        db.close()


@companies_bp.patch("/<int:company_id>")
def update_company(company_id):
    user, error = require_user({"control"})

    if error:
        return error

    data = request.get_json(silent=True) or {}

    allowed = {
        "name",
        "email",
        "phone",
        "address",
        "city",
        "state",
        "pincode",
        "status",
    }

    updates = {
        key: data[key]
        for key in allowed
        if key in data
    }

    if not updates:
        return jsonify({
            "error": "no valid fields supplied"
        }), 400

    if "status" in updates and updates["status"] not in {
        "active",
        "inactive",
        "suspended",
    }:
        return jsonify({
            "error": "invalid company status"
        }), 400

    set_clause = ", ".join(
        f"{key} = ?"
        for key in updates
    )

    values = list(updates.values())
    values.append(company_id)

    db = get_db()

    try:
        exists = db.execute(
            "SELECT id FROM companies WHERE id = ?",
            (company_id,)
        ).fetchone()

        if not exists:
            return jsonify({
                "error": "company not found"
            }), 404

        db.execute(
            f"""
            UPDATE companies
            SET {set_clause},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            values
        )

        db.commit()

        company = db.execute(
            "SELECT * FROM companies WHERE id = ?",
            (company_id,)
        ).fetchone()

        return jsonify({
            "message": "company updated",
            "company": dict(company)
        })

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({
            "error": "email already exists"
        }), 409

    finally:
        db.close()


@companies_bp.post("/<int:company_id>/users")
def create_company_user(company_id):
    user, error = require_user({"control"})

    if error:
        return error

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({
            "error": "name, email and password are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "password must be at least 8 characters"
        }), 400

    db = get_db()

    try:
        company = db.execute(
            """
            SELECT id
            FROM companies
            WHERE id = ?
              AND status = 'active'
            """,
            (company_id,)
        ).fetchone()

        if not company:
            return jsonify({
                "error": "company not found"
            }), 404

        from werkzeug.security import generate_password_hash

        password_hash = generate_password_hash(password)

        cursor = db.execute(
            """
            INSERT INTO users (
                company_id,
                name,
                email,
                password_hash,
                role
            )
            VALUES (?, ?, ?, ?, 'company')
            """,
            (
                company_id,
                name,
                email,
                password_hash,
            )
        )

        db.commit()

        return jsonify({
            "message": "company user created",
            "user": {
                "id": cursor.lastrowid,
                "company_id": company_id,
                "name": name,
                "email": email,
                "role": "company",
            }
        }), 201

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({
            "error": "email already registered"
        }), 409

    finally:
        db.close()


@companies_bp.get("/<int:company_id>/users")
def list_company_users(company_id):
    user, error = require_user({"control", "company"})

    if error:
        return error

    if user["role"] == "company" and user["company_id"] != company_id:
        return jsonify({"error": "permission denied"}), 403

    db = get_db()

    try:
        company = db.execute(
            "SELECT id FROM companies WHERE id = ?",
            (company_id,)
        ).fetchone()

        if not company:
            return jsonify({
                "error": "company not found"
            }), 404

        rows = db.execute(
            """
            SELECT
                id,
                company_id,
                name,
                email,
                phone,
                role,
                status,
                created_at
            FROM users
            WHERE company_id = ?
            ORDER BY id DESC
            """,
            (company_id,)
        ).fetchall()

        return jsonify({
            "count": len(rows),
            "users": [dict(row) for row in rows]
        })

    finally:
        db.close()
