import pytest
import asyncio
from web3 import Web3
from app.ethanol_engine import trigger_burn_proposal
from app.vaults import deposit_to_vault, withdraw_from_vault

TESTNET_RPC_URL = "https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID"
MANDALA_ADDRESS = "0xYourMandalaTokenAddress"
DAO_ADDRESS = "0xYourDaoContractAddress"
PRIVATE_KEY = "0xyour_private_key"
ACCOUNT_ADDRESS = "0xyour_account_address"

@pytest.mark.asyncio
async def test_live_integration_with_testnet():
    web3 = Web3(Web3.HTTPProvider(TESTNET_RPC_URL))
    assert web3.isConnected(), "Cannot connect to testnet"

    # Example: Fetch Mandala token balance
    balance = web3.eth.get_balance(ACCOUNT_ADDRESS)
    print(f"Account balance: {balance}")

    # Simulate deposit (mock or send real tx)
    deposit_response = await deposit_to_vault(ACCOUNT_ADDRESS, "MDX", MANDALA_ADDRESS, 100, None)
    assert deposit_response["new_balance"] == "100"

    # Trigger burn proposal on testnet via Ethanol Engine logic
    burn_amount = 50  # Example value
    result = await trigger_burn_proposal(burn_amount, None)  # DAO service should handle real contract calls
    print(f"DAO proposal trigger result: {result}")

    # Add real contract interaction tests here — eg. listen to ProposalCreated events, etc.

    # Optional: wait for events with filters, verify emitted logs
    await asyncio.sleep(10)
