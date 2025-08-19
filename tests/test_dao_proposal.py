import pytest
import asyncio
from unittest.mock import AsyncMock
from app.ethanol_engine import trigger_burn_proposal, DaoProposalService

class MockDaoProposalService:
    async def submit_burn_proposal(self, amount: float):
        # Simulate network delay
        await asyncio.sleep(0.01)
        # Return mocked success response
        return {"status": "mock_submitted", "amount": amount}

@pytest.mark.asyncio
async def test_trigger_burn_proposal_with_mock():
    burn_amount = 5000.0
    mock_service = MockDaoProposalService()

    result = await trigger_burn_proposal(burn_amount, mock_service)
    assert result["status"] == "mock_submitted"
    assert result["amount"] == burn_amount
