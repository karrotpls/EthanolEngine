import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_deposit_and_withdraw():
    async with AsyncClient(app=app, base_url="http://test") as client:
        deposit_payload = {
            "user_address": "0xabc123",
            "asset_symbol": "cDAI",
            "asset_address": "0xdef456",
            "amount": 100.0
        }
        # Deposit test
        resp = await client.post("/vault/deposit", json=deposit_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["new_balance"] == "100.0"

        # Deposit more
        deposit_payload["amount"] = 50.0
        resp = await client.post("/vault/deposit", json=deposit_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["new_balance"] == "150.0"

        # Withdraw test
        withdraw_payload = deposit_payload.copy()
        withdraw_payload["amount"] = 40.0
        resp = await client.post("/vault/withdraw", json=withdraw_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["new_balance"] == "110.0"

        # Withdraw too much
        withdraw_payload["amount"] = 200.0
        resp = await client.post("/vault/withdraw", json=withdraw_payload)
        assert resp.status_code == 400
