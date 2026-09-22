import sqlite3
from werkzeug.security import generate_password_hash

DB = "delyvo.db"

email = "control@delyvo.in"
new_password = input("New Control password: ")

if len(new_password) < 8:
    raise SystemExit("Password minimum 8 characters hona chahiye.")

conn = sqlite3.connect(DB)

user = conn.execute(
    "SELECT id FROM users WHERE email = ?",
    (email,)
).fetchone()

if not user:
    conn.close()
    raise SystemExit("Control user nahi mila.")

conn.execute(
    "UPDATE users SET password_hash = ? WHERE id = ?",
    (generate_password_hash(new_password), user[0])
)

# Purane sessions invalidate
conn.execute(
    "UPDATE auth_sessions SET revoked_at = CURRENT_TIMESTAMP WHERE user_id = ? AND revoked_at IS NULL",
    (user[0],)
)

conn.commit()
conn.close()

print("Control password reset successfully.")
print("Ab isi naye password se login karo.")
