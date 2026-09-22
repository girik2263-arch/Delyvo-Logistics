import sqlite3

from flask import Blueprint, jsonify, request

from app.services.auth_service import (
    create_token,
    hash_password,
    hash_token,
    session_expiry,
    verify_password,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

DB_PATH = "delyvo.db"

VALID_ROLES = {"control", "company", "hub", "pilot"}


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    role = str(data.get("role", "")).strip().lower()
    company_id = data.get("company_id")

    if not name or not email or not password or not role:
        return jsonify({
            "error": "name, email, password and role are required"
        }), 400

    if role not in VALID_ROLES:
        return jsonify({"error": "invalid role"}), 400

    if len(password) < 8:
        return jsonify({
            "error": "password must be at least 8 characters"
        }), 400

    # Company users must belong to a company.
    if role == "company" and company_id is None:
        return jsonify({
            "error": "company_id is required for company users"
        }), 400

    db = get_db()

    try:
        if company_id is not None:
            company = db.execute(
                "SELECT id FROM companies WHERE id = ? AND status = 'active'",
                (company_id,)
            ).fetchone()

            if not company:
                return jsonify({"error": "company not found"}), 404

        password_hash = hash_password(password)

        cursor = db.execute(
            """
            INSERT INTO users
                (company_id, name, email, password_hash, role)
            VALUES
                (?, ?, ?, ?, ?)
            """,
            (company_id, name, email, password_hash, role)
        )

        db.commit()

        return jsonify({
            "message": "user created",
            "user": {
                "id": cursor.lastrowid,
                "name": name,
                "email": email,
                "role": role,
                "company_id": company_id,
            }
        }), 201

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({
            "error": "email already registered"
        }), 409

    finally:
        db.close()


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({
            "error": "email and password are required"
        }), 400

    db = get_db()

    try:
        user = db.execute(
            """
            SELECT
                id,
                company_id,
                name,
                email,
                password_hash,
                role,
                status
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if not user or not user["password_hash"]:
            return jsonify({"error": "invalid credentials"}), 401

        if user["status"] != "active":
            return jsonify({"error": "account is not active"}), 403

        if not verify_password(user["password_hash"], password):
            return jsonify({"error": "invalid credentials"}), 401

        token = create_token()
        token_hash = hash_token(token)
        expires_at = session_expiry()

        db.execute(
            """
            INSERT INTO auth_sessions
                (user_id, token_hash, expires_at)
            VALUES
                (?, ?, ?)
            """,
            (user["id"], token_hash, expires_at)
        )

        db.commit()

        return jsonify({
            "message": "login successful",
            "token": token,
            "expires_at": expires_at,
            "user": {
                "id": user["id"],
                "company_id": user["company_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            }
        })

    finally:
        db.close()


@auth_bp.post("/logout")
def logout():
    auth = request.headers.get("Authorization", "")

    if not auth.startswith("Bearer "):
        return jsonify({"error": "bearer token required"}), 401

    token = auth[7:].strip()

    if not token:
        return jsonify({"error": "invalid token"}), 401

    token_hash = hash_token(token)

    db = get_db()

    try:
        db.execute(
            """
            UPDATE auth_sessions
            SET revoked_at = CURRENT_TIMESTAMP
            WHERE token_hash = ?
              AND revoked_at IS NULL
            """,
            (token_hash,)
        )

        db.commit()

        return jsonify({"message": "logout successful"})

    finally:
        db.close()


# =========================
# MOBILE OTP AUTHENTICATION
# =========================

from app.services.messagecentral import send_otp as mc_send_otp
from app.services.messagecentral import verify_otp as mc_verify_otp
from app.services.otp_service import otp_expiry
import re


def normalize_phone(phone):
    phone = re.sub(r"\D", "", phone or "")

    if phone.startswith("91") and len(phone) == 12:
        phone = phone[2:]

    if len(phone) != 10:
        return None

    if not phone.startswith(("6", "7", "8", "9")):
        return None

    return phone


@auth_bp.post("/send-otp")
def send_mobile_otp():
    data = request.get_json(silent=True) or {}

    phone = normalize_phone(data.get("phone"))

    if not phone:
        return jsonify({"error": "valid Indian mobile number required"}), 400

    db = get_db()

    user = db.execute(
        """
        SELECT id, name, role, status
        FROM users
        WHERE phone = ?
        LIMIT 1
        """,
        (phone,),
    ).fetchone()

    if not user:
        return jsonify({"error": "mobile number not registered"}), 404

    if user["status"] != "active":
        return jsonify({"error": "user account is inactive"}), 403

    # Control login is OTP-only.
    if user["role"] != "control":
        return jsonify({"error": "OTP login is currently for control only"}), 403

    try:
        result = mc_send_otp(phone)
    except Exception:
        return jsonify({"error": "unable to send OTP"}), 502

    db.execute(
        """
        INSERT INTO messagecentral_verifications
        (user_id, phone, verification_id, status, expires_at)
        VALUES (?, ?, ?, 'pending', ?)
        """,
        (
            user["id"],
            phone,
            result["verification_id"],
            otp_expiry(),
        ),
    )

    db.commit()

    return jsonify({
        "message": "OTP sent",
        "verification_id": result["verification_id"],
        "expires_in_minutes": 5,
    }), 200


@auth_bp.post("/verify-otp")
def verify_mobile_otp():
    data = request.get_json(silent=True) or {}

    verification_id = str(data.get("verification_id") or "").strip()
    otp = str(data.get("otp") or "").strip()

    if not verification_id or not otp:
        return jsonify({
            "error": "verification_id and otp are required"
        }), 400

    if not re.fullmatch(r"\d{4,8}", otp):
        return jsonify({"error": "invalid OTP format"}), 400

    db = get_db()

    verification = db.execute(
        """
        SELECT
            mcv.id,
            mcv.user_id,
            mcv.phone,
            mcv.verification_id,
            u.name,
            u.email,
            u.role,
            u.status
        FROM messagecentral_verifications mcv
        JOIN users u ON u.id = mcv.user_id
        WHERE mcv.verification_id = ?
        ORDER BY mcv.id DESC
        LIMIT 1
        """,
        (verification_id,),
    ).fetchone()

    if not verification:
        return jsonify({"error": "verification not found"}), 404

    if verification["status"] == "verified":
        return jsonify({"error": "OTP already used"}), 400

    if verification["status"] != "pending":
        return jsonify({"error": "OTP verification unavailable"}), 400

    if verification["status"] == "expired":
        return jsonify({"error": "OTP expired"}), 400

    if verification["role"] != "control":
        return jsonify({"error": "OTP login is currently for control only"}), 403

    if verification["status"] != "pending":
        return jsonify({"error": "invalid verification state"}), 400

    try:
        result = mc_verify_otp(
            verification["verification_id"],
            otp,
        )
    except Exception:
        return jsonify({"error": "OTP verification failed"}), 502

    if not result["verified"]:
        return jsonify({"error": "invalid OTP"}), 401

    db.execute(
        """
        UPDATE messagecentral_verifications
        SET status = 'verified',
            verified_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (verification["id"],),
    )

    token = create_token()

    token_hash = hash_token(token)

    db.execute(
        """
        INSERT INTO auth_sessions
        (user_id, token_hash, expires_at)
        VALUES (?, ?, ?)
        """,
        (
            verification["user_id"],
            token_hash,
            session_expiry(),
        ),
    )

    db.commit()

    return jsonify({
        "message": "login successful",
        "token": token,
        "expires_at": session_expiry(),
        "user": {
            "id": verification["user_id"],
            "name": verification["name"],
            "email": verification["email"],
            "phone": verification["phone"],
            "role": verification["role"],
        },
    }), 200
