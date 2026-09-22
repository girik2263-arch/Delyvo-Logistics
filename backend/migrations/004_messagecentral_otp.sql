CREATE TABLE IF NOT EXISTS messagecentral_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    phone TEXT NOT NULL,
    verification_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    expires_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_mc_verification_id
ON messagecentral_verifications(verification_id);

CREATE INDEX IF NOT EXISTS idx_mc_phone
ON messagecentral_verifications(phone);
