PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    password_hash TEXT,
    role TEXT NOT NULL
        CHECK (role IN ('control', 'company', 'hub', 'pilot')),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'blocked')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS hubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hub_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT,
    pincode TEXT,
    phone TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partner_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    hub_id INTEGER,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'blocked')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hub_id) REFERENCES hubs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_code TEXT NOT NULL UNIQUE,
    awb_number TEXT NOT NULL UNIQUE,
    company_id INTEGER NOT NULL,
    origin_hub_id INTEGER,
    destination_hub_id INTEGER,
    assigned_partner_id INTEGER,

    sender_name TEXT NOT NULL,
    sender_phone TEXT NOT NULL,
    sender_address TEXT NOT NULL,

    receiver_name TEXT NOT NULL,
    receiver_phone TEXT NOT NULL,
    receiver_address TEXT NOT NULL,
    receiver_city TEXT,
    receiver_state TEXT,
    receiver_pincode TEXT,

    payment_mode TEXT NOT NULL DEFAULT 'prepaid'
        CHECK (payment_mode IN ('prepaid', 'cod')),

    cod_amount REAL NOT NULL DEFAULT 0,
    declared_value REAL NOT NULL DEFAULT 0,
    weight_kg REAL NOT NULL DEFAULT 0,

    status TEXT NOT NULL DEFAULT 'booked'
        CHECK (
            status IN (
                'booked',
                'pickup_requested',
                'assigned',
                'picked_up',
                'at_hub',
                'in_transit',
                'out_for_delivery',
                'delivered',
                'ndr',
                'rto',
                'returned',
                'cancelled'
            )
        ),

    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE RESTRICT,
    FOREIGN KEY (origin_hub_id) REFERENCES hubs(id) ON DELETE SET NULL,
    FOREIGN KEY (destination_hub_id) REFERENCES hubs(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_partner_id) REFERENCES partners(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS shipment_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    location TEXT,
    remarks TEXT,
    performed_by_user_id INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (shipment_id) REFERENCES shipments(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_users_company
    ON users(company_id);

CREATE INDEX IF NOT EXISTS idx_users_role
    ON users(role);

CREATE INDEX IF NOT EXISTS idx_partners_hub
    ON partners(hub_id);

CREATE INDEX IF NOT EXISTS idx_shipments_company
    ON shipments(company_id);

CREATE INDEX IF NOT EXISTS idx_shipments_status
    ON shipments(status);

CREATE INDEX IF NOT EXISTS idx_shipments_partner
    ON shipments(assigned_partner_id);

CREATE INDEX IF NOT EXISTS idx_shipment_events_shipment
    ON shipment_events(shipment_id);

CREATE INDEX IF NOT EXISTS idx_shipment_events_created
    ON shipment_events(created_at);
