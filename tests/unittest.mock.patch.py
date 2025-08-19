from unittest.mock import patch

@pytest.mark.asyncio
@patch("app.ethanol_engine.DaoProposalService.submit_burn_proposal", new_callable=AsyncMock)
async def test_trigger_burn_proposal_patch(mock_submit):
    mock_submit.return_value = {"status": "patched", "amount": 10000.0}
    dao_service = DaoProposalService(None, None)
    result = await trigger_burn_proposal(10000.0, dao_service)
    assert result["status"] == "patched"
    assert result["amount"] == 10000.0
