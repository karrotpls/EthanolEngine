import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CreamVault, DaoProposalRecord
from app.ethanol_engine import trigger_burn_proposal
from app.vaults import deposit_to_vault, withdraw_from_vault

@pytest.mark.asyncio
async def test_vault_and_dao_persistence(db_session: AsyncSession):
    user = "0xpersistuser"
    asset_symbol = "MDX"
    asset_address = "0xmandala_address"

    # Deposit to vault
    deposit_resp = await deposit_to_vault(user, asset_symbol, asset_address, 1000, db_session)
    assert deposit_resp["new_balance"] == "1000"

    # Withdraw partial
    withdraw_resp = await withdraw_from_vault(user, asset_symbol, asset_address, 400, db_session)
    assert withdraw_resp["new_balance"] == "600"

    # Record a DAO proposal in DB (mocking submission)
    burn_amount = 200
    proposal = DaoProposalRecord(
        user_address=user,
        proposal_type="burn",
        amount=burn_amount,
        status="pending"
    )
    db_session.add(proposal)
    await db_session.commit()

    # Fetch from DB to verify persistence
    stored = await db_session.get(DaoProposalRecord, proposal.id)
    assert stored is not None
    assert stored.amount == burn_amount
    assert stored.status == "pending"

    # Simulate proposal completion update
    stored.status = "approved"
    await db_session.commit()

    updated = await db_session.get(DaoProposalRecord, proposal.id)
    assert updated.status == "approved"
