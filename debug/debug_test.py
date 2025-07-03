"""
Test script to debug the arbitrage opportunity generation
"""

from arbitrage_detector import (
    FakeArbitrageAnalyzer,
    calculate_triangular_arbitrage_profit,
)
import random

# Initialize analyzer
analyzer = FakeArbitrageAnalyzer(seed=42)

# Test profit calculation directly
print("Testing profit calculation:")

# Test case 1: Manual profitable rates
rate_ab = 1.5  # Buy 1.5 units of intermediate for 1 unit of base
rate_bc = 2.0  # Buy 2.0 units of quote for 1 unit of intermediate
rate_ca = 0.25  # Convert 1 unit of quote back to 0.25 units of base (inverse of 4.0)

fees = (0.001, 0.001, 0.001)  # 0.1% fees
profit = calculate_triangular_arbitrage_profit(rate_ab, rate_bc, rate_ca, fees)
print(f"Test case 1: rate_ab={rate_ab}, rate_bc={rate_bc}, rate_ca={rate_ca}")
print(f"Expected final amount: {rate_ab * rate_bc * rate_ca}")
print(f"Calculated profit: {profit:.6f}")
print()

# Test case 2: Generate a few opportunities manually
print("Testing opportunity generation:")
for i in range(5):
    base = "USDT"
    intermediate = "BTC"
    quote = "ETH"

    # Generate rates with bigger arbitrage margins
    rates = analyzer.generate_exchange_rates(base, intermediate, quote)

    rate_ab = rates[f"{intermediate}/{base}"]
    rate_bc = rates[f"{quote}/{intermediate}"]
    rate_ca = 1.0 / rates[f"{quote}/{base}"]

    fees_tuple = (0.001, 0.001, 0.001)

    profit = calculate_triangular_arbitrage_profit(
        rate_ab, rate_bc, rate_ca, fees_tuple
    )

    print(f"Opportunity {i+1}:")
    print(
        f"  Rates: {rate_ab:.6f} * {rate_bc:.6f} * {rate_ca:.6f} = {rate_ab * rate_bc * rate_ca:.6f}"
    )
    print(f"  Profit: {profit:.6f} ({profit*100:.4f}%)")
    print(f"  Profitable: {profit > 0}")
    print()

# Generate opportunities using the full method
print("Testing full opportunity generation:")
opportunities = analyzer.generate_arbitrage_opportunities(10)
print(f"Generated {len(opportunities)} profitable opportunities")

for i, opp in enumerate(opportunities):
    print(
        f"Opportunity {i+1}: {opp.expected_profit:.6f} ({opp.expected_profit*100:.4f}%)"
    )
