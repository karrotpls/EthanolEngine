import asyncio
from web3 import AsyncWeb3
from web3.providers.async_rpc import AsyncHTTPProvider
from app.config import RPC_URL, MANDALA_ADDRESS, MANDALA_ABI

w3 = AsyncWeb3(AsyncHTTPProvider(RPC_URL))
mandala_contract = w3.eth.contract(address=MANDALA_ADDRESS, abi=MANDALA_ABI)

async def handle_transfer_event(event):
    # Parse and handle Mandala token transfers, supply changes
    print(f"Detected Transfer: {event}")

async def listen_mandala_transfers():
    event_filter = mandala_contract.events.Transfer.createFilter(fromBlock='latest')
    while True:
        for event in await event_filter.get_new_entries():
            await handle_transfer_event(event)
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(listen_mandala_transfers())
