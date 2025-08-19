CREATE TABLE metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE holders (
  address TEXT PRIMARY KEY,
  balance NUMERIC,
  last_updated TIMESTAMP DEFAULT now()
);

CREATE TABLE supply_snapshots (
  ts TIMESTAMP PRIMARY KEY,
  total_supply NUMERIC,
  circulating_supply NUMERIC
);
