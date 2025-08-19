CREATE TABLE cream_vaults (
  vault_id SERIAL PRIMARY KEY,
  user_address TEXT NOT NULL,
  asset_symbol TEXT NOT NULL,
  asset_address TEXT NOT NULL,
  balance NUMERIC DEFAULT 0,
  collateral_ratio NUMERIC DEFAULT 1.5, -- e.g. 150%
  last_updated TIMESTAMP DEFAULT now()
);

CREATE TABLE vault_events (
  event_id SERIAL PRIMARY KEY,
  vault_id INT REFERENCES cream_vaults(vault_id),
  event_type TEXT, -- deposit, withdraw, rebalance, burn_trigger
  amount NUMERIC,
  event_ts TIMESTAMP DEFAULT now()
);
