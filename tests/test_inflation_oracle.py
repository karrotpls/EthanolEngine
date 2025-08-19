import pytest
import asyncio
from unittest.mock import AsyncMock
from app.ethanol_engine import calculate_burn_amount, trigger_burn_proposal, DaoProposalService

class InflationOracle:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    async def push_inflation(self, inflation_rate):
        for cb in self.subscribers:
            await cb(inflation_rate)

@pytest.mark.asyncio
async def test_inflation_oracle_burn_flow():
    mock_dao = DaoProposalService(None, None)
    mock_dao.submit_burn_proposal = AsyncMock(return_value={"status": "mock_submitted"})

    oracle = InflationOracle()

    # Recursive callback to react on inflation updates
    async def on_inflation_update(inflation_rate):
        current_supply = 1_000_000
        burn_amount = await calculate_burn_amount(inflation_rate, current_supply)
        result = await trigger_burn_proposal(burn_amount, mock_dao)
        assert result["status"] == "mock_submitted"
        print(f"Inflation {inflation_rate*100:.2f}%, Burn {burn_amount}")

    oracle.subscribe(on_inflation_update)

    # Simulate inflation input sequence
    inflation_inputs = [0.01, 0.05, 0.02, 0.0, 0.10]  # 1%, 5%, etc.

    for rate in inflation_inputs:
        await oracle.push_inflation(rate)
        await asyncio.sleep(0.05)  # Allow async tasks to run
