"""
Test with manually created opportunities to force multiple investments
"""

from arbitrage_optimizer import (
    TriangularArbitrageOptimizer,
    PortfolioConstraints,
    ArbitrageOpportunity,
)
from market_simulator import CryptoMarketSimulator


def test_forced_multiple_investments():
    # Initialize market simulator
    market_sim = CryptoMarketSimulator()

    # Generate portfolio constraints
    base_constraints = market_sim.generate_portfolio_constraints(
        total_portfolio_value=100_000, risk_profile="moderate"
    )

    print("=== PORTFOLIO BALANCES ===")
    for currency, balance in base_constraints.initial_balances.items():
        print(f"{currency}: {balance:.2f}")

    print(f"\nRisk tolerance: {base_constraints.risk_tolerance:.1%}")
    max_investment = (
        sum(base_constraints.initial_balances.values())
        * base_constraints.risk_tolerance
    )
    print(f"Max total investment: ${max_investment:.2f}")

    # Create 3 opportunities with DIFFERENT base currencies to avoid currency conflicts
    opportunities = [
        ArbitrageOpportunity(
            base_currency="USDT",
            intermediate_currency="BTC",
            quote_currency="ETH",
            exchange_rates={"BTC/USDT": 0.00002, "ETH/BTC": 15.0, "ETH/USDT": 0.00035},
            liquidity={"BTC/USDT": 1000000, "ETH/BTC": 1000000, "ETH/USDT": 1000000},
            transaction_fees={"BTC/USDT": 0.001, "ETH/BTC": 0.001, "ETH/USDT": 0.001},
            expected_profit=0.015,  # 1.5% profit
            confidence_score=0.85,  # 85% confidence
        ),
        ArbitrageOpportunity(
            base_currency="USDC",
            intermediate_currency="ADA",
            quote_currency="DOT",
            exchange_rates={"ADA/USDC": 1.2, "DOT/ADA": 20.0, "DOT/USDC": 25.0},
            liquidity={"ADA/USDC": 500000, "DOT/ADA": 500000, "DOT/USDC": 500000},
            transaction_fees={"ADA/USDC": 0.001, "DOT/ADA": 0.001, "DOT/USDC": 0.001},
            expected_profit=0.018,  # 1.8% profit
            confidence_score=0.90,  # 90% confidence
        ),
        ArbitrageOpportunity(
            base_currency="DAI",
            intermediate_currency="LINK",
            quote_currency="LTC",
            exchange_rates={"LINK/DAI": 15.0, "LTC/LINK": 10.0, "LTC/DAI": 152.0},
            liquidity={"LINK/DAI": 300000, "LTC/LINK": 300000, "LTC/DAI": 300000},
            transaction_fees={"LINK/DAI": 0.001, "LTC/LINK": 0.001, "LTC/DAI": 0.001},
            expected_profit=0.012,  # 1.2% profit
            confidence_score=0.80,  # 80% confidence
        ),
    ]

    print("\n=== CREATED OPPORTUNITIES ===")
    for i, opp in enumerate(opportunities):
        weighted_profit = opp.expected_profit * opp.confidence_score * 100
        print(
            f"{i}: {opp.base_currency}→{opp.intermediate_currency}→{opp.quote_currency}"
        )
        print(
            f"   Profit: {opp.expected_profit*100:.1f}% | Confidence: {opp.confidence_score*100:.0f}% | Weighted: {weighted_profit:.2f}%"
        )

    # Create optimizer and solve
    optimizer = TriangularArbitrageOptimizer(base_constraints)
    solution = optimizer.solve(opportunities)

    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Status: {solution['status']}")
    print(f"Number of investments: {len(solution.get('investments', {}))}")
    print(f"Total investment: ${solution.get('total_investment', 0):.2f}")
    print(f"Expected profit: ${solution.get('expected_profit', 0):.6f}")

    print(
        f"\nRisk utilization: {(solution.get('total_investment', 0) / max_investment) * 100:.1f}%"
    )

    print("\n=== INDIVIDUAL INVESTMENTS ===")
    investments = solution.get("investments", {})
    for opp_id, inv_data in investments.items():
        opp = inv_data["opportunity"]
        amount = inv_data["amount"]
        profit = inv_data["expected_profit"]

        print(f"{opp_id}:")
        print(
            f"  Currencies: {opp.base_currency} → {opp.intermediate_currency} → {opp.quote_currency}"
        )
        print(f"  Investment: ${amount:.2f}")
        print(f"  Expected Profit: ${profit:.6f}")


if __name__ == "__main__":
    test_forced_multiple_investments()
