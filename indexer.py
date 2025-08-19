import os, time
from decimal import Decimal
from web3 import Web3
import psycopg2
from psycopg2.extras import execute_values

RPC_URL = os.getenv("RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")
TOKEN_ADDRESS = Web3.toChecksumAddress(os.getenv("TOKEN_ADDRESS", "0xYourMandalaTokenAddress"))
DB_DSN = os.getenv("DB_DSN", "postgresql://user:pass@localhost:5432/mdx")

# Minimal ERC20 ABI with totalSupply and Transfer event
ERC20_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"},
        ],
        "name": "Transfer",
        "type": "event",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
token = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

BATCH_BLOCKS = 5000  # tune as needed

def pg_conn():
    return psycopg2.connect(DB_DSN)

def init_meta(conn):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO metadata (key, value) VALUES (%s,%s) ON CONFLICT (key) DO NOTHING",
        ("last_block", "0"),
    )
    conn.commit()

def get_last_block(conn):
    cur = conn.cursor()
    cur.execute("SELECT value FROM metadata WHERE key='last_block'")
    r = cur.fetchone()
    return int(r[0]) if r else 0

def set_last_block(conn, blk):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO metadata (key, value) VALUES (%s,%s) ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value, updated_at=now()",
        ("last_block", str(blk)),
    )
    conn.commit()

def snapshot_supply(conn, total_supply, circulating):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO supply_snapshots (ts, total_supply, circulating_supply) VALUES (now(), %s, %s)",
        (str(total_supply), str(circulating)),
    )
    conn.commit()

def update_holder_balances(conn, balances):
    # balances: list of (address, balance)
    cur = conn.cursor()
    execute_values(
        cur,
        "INSERT INTO holders (address, balance, last_updated) VALUES %s ON CONFLICT (address) DO UPDATE SET balance=EXCLUDED.balance, last_updated=EXCLUDED.last_updated",
        [(a, str(b)) for a, b in balances],
    )
    conn.commit()

def compute_circulating(conn, total_supply):
    # Placeholder - can subtract locked addresses balances if needed
    return total_supply

def scan_transfer_events(from_block, to_block):
    Transfer = token.events.Transfer()
    logs = Transfer.get_logs(fromBlock=from_block, toBlock=to_block)
    deltas = {}
    for ev in logs:
        frm = ev["args"]["from"]
        to = ev["args"]["to"]
        val = Decimal(ev["args"]["value"])
        if frm != "0x0000000000000000000000000000000000000000":
            deltas[frm] = deltas.get(frm, Decimal(0)) - val
        if to != "0x0000000000000000000000000000000000000000":
            deltas[to] = deltas.get(to, Decimal(0)) + val
    return deltas

def bulk_apply_deltas(conn, deltas):
    addresses = list(deltas.keys())
    cur = conn.cursor()
    cur.execute("SELECT address, balance FROM holders WHERE address = ANY(%s)", (addresses,))
    rows = dict(cur.fetchall())
    new_balances = []
    for addr in addresses:
        cur_bal = Decimal(rows.get(addr, 0))
        new_bal = cur_bal + deltas[addr]
        if new_bal < 0:
            new_bal = Decimal(0)
        new_balances.append((addr, new_bal))
    update_holder_balances(conn, new_balances)

def main_loop():
    conn = pg_conn()
    init_meta(conn)
    last_block = get_last_block(conn)
    if last_block == 0:
        last_block = w3.eth.block_number - BATCH_BLOCKS
    while True:
        latest = w3.eth.block_number
        if latest <= last_block:
            time.sleep(5)
            continue
        to_block = min(latest, last_block + BATCH_BLOCKS)
        print(f"Scanning blocks {last_block+1} to {to_block}")
        deltas = scan_transfer_events(last_block + 1, to_block)
        if deltas:
            bulk_apply_deltas(conn, deltas)
        total_supply = Decimal(token.functions.totalSupply().call())
        circulating = compute_circulating(conn, total_supply)
        snapshot_supply(conn, total_supply, circulating)
        set_last_block(conn, to_block)
        last_block = to_block

if __name__ == "__main__":
    main_loop()
