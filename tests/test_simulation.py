import pytest
import asyncio
from unittest.mock import AsyncMock
from app.vaults import deposit_to_vault, withdraw_from_vault  # Assuming these exist
from app.ethanol_engine import calculate_burn_amount, trigger_burn_proposal, DaoProposalService
from app.chain_listener import handle_transfer_event
from app.models import CreamVault
from app.db import get_db

@pytest.mark.asyncio
async def test_full_simulation(monkeypatch):
    # Step 0: Setup mock DAO service
    class MockDaoProposalService:
        async def submit_burn_proposal(self, amount: float):
            await asyncio.sleep(0.01)
            return {"status": "mock_submitted", "amount": amount}

    mock_dao = MockDaoProposalService()

    # Step 1: Simulate on-chain Mandala transfer event (increase supply)
    transfer_event = {
        "args": {
            "from": "0x0000000000000000000000000000000000000000",
            "to": "0xuser1",
            "value": 100000
        }
    }
    await handle_transfer_event(transfer_event)

    # Step 2: Deposit assets into Cream Vault for user '0xuser1'
    deposit_response = await deposit_to_vault(
        user_address="0xuser1",
        asset_symbol="MDX",
        asset_address="0xmandala_address",
        amount=100000
    )
    assert deposit_response["new_balance"] == "100000"

    # Step 3: Run Ethanol Engine burn calculation
    inflation_rate = 0.03  # 3%
    current_supply = 1_000_000
    burn_amount = await calculate_burn_amount(inflation_rate, current_supply)
    assert burn_amount > 0

    # Step 4: Submit mock DAO burn proposal
    proposal_result = await trigger_burn_proposal(burn_amount, mock_dao)
    assert proposal_result["status"] == "mock_submitted"
    assert proposal_result["amount"] == burn_amount

    # Step 5: Withdraw some assets to simulate vault activity
    withdraw_response = await withdraw_from_vault(
        user_address="0xuser1",
        asset_symbol="MDX",
        asset_address="0xmandala_address",
        amount=50000
    )
    assert withdraw_response["new_balance"] == "50000"
