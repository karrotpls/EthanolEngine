import pytest
import asyncio
from app.chain_listener import handle_transfer_event

@pytest.mark.asyncio
async def test_handle_transfer_event():
    mock_event = {
        "args": {
            "from": "0xabc123",
            "to": "0xdef456",
            "value": 1000
        }
    }
    # Just check it runs without error
    await handle_transfer_event(mock_event)
