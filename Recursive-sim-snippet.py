def simulate_arb(wbtc_amount, cost_usd, slippage_pct, price_wbtc=30000):
    initial_value = wbtc_amount * price_wbtc
    slippage_loss = initial_value * (slippage_pct / 100)
    total_cost = cost_usd + slippage_loss
    final_value = initial_value - total_cost
    profit = final_value - initial_value
    return profit

arb_profit = simulate_arb(1, 55, 1)
print(f"Simulated Arb Profit (USD): {arb_profit:.2f}")
