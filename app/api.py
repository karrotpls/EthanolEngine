from fastapi import FastAPI
import psycopg2
app = FastAPI()

DB_DSN = "postgresql://user:pass@localhost:5432/mdx"

def conn():
    return psycopg2.connect(DB_DSN)

@app.get("/supply")
def supply():
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT total_supply, circulating_supply, ts FROM supply_snapshots ORDER BY ts DESC LIMIT 1")
    r = cur.fetchone()
    c.close()
    if r:
        return {"total_supply": r[0], "circulating": r[1], "ts": r[2].isoformat()}
    return {"total_supply": None}

@app.get("/holders/top/{n}")
def top_holders(n: int = 20):
    c = conn()
    cur = c.cursor()
    cur.execute("SELECT address, balance FROM holders ORDER BY balance DESC LIMIT %s", (n,))
    rows = cur.fetchall()
    c.close()
    return [{"address": r[0], "balance": str(r[1])} for r in rows]
