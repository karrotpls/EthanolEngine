import asyncio
from app.chain_listener import listen_mandala_transfers
from app.ethanol_engine import calculate_burn_amount, trigger_burn_proposal

async def periodic_tasks():
    while True:
        # TODO: fetch inflation data, current supply
        inflation_rate = 0.02
        current_supply = 1_000_000
        burn_amount = await calculate_burn_amount(inflation_rate, current_supply)
        await trigger_burn_proposal(burn_amount)
        await asyncio.sleep(300)  # every 5 minutes

async def main():
    await asyncio.gather(
        listen_mandala_transfers(),
        periodic_tasks()
    )

if __name__ == "__main__":
    asyncio.run(main())
