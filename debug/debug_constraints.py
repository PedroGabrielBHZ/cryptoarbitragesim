"""
Debug script to analyze why only one arbitrage opportunity is selected
"""

from arbitrage_optimizer import TriangularArbitrageOptimizer, PortfolioConstraints
from arbitrage_detector import FakeArbitrageAnalyzer
from market_simulator import CryptoMarketSimulator
import numpy as np


def debug_constraints():
    # Initialize components
    analyzer = FakeArbitrageAnalyzer()
    market_sim = CryptoMarketSimulator()

    # Generate portfolio constraints
    base_constraints = market_sim.generate_portfolio_constraints(
        total_portfolio_value=100_000, risk_profile="moderate"
    )

    print("=== PORTFOLIO CONSTRAINTS ===")
    print(f"Risk tolerance: {base_constraints.risk_tolerance:.3f}")
    print(
        f"Total portfolio value: ${sum(base_constraints.initial_balances.values()):,.2f}"
    )

    print("\n=== INITIAL BALANCES ===")
    for currency, balance in base_constraints.initial_balances.items():
        print(f"{currency}: {balance:,.4f}")

    print("\n=== MINIMUM HOLDINGS ===")
    for currency, min_hold in base_constraints.min_holdings.items():
        print(f"{currency}: {min_hold:,.4f}")

    print("\n=== MAXIMUM POSITION SIZES ===")
    for currency, max_pos in base_constraints.max_position_size.items():
        print(f"{currency}: ${max_pos:,.2f}")

    # Generate opportunities
    opportunities = analyzer.generate_arbitrage_opportunities(10)

    print(f"\n=== ARBITRAGE OPPORTUNITIES ({len(opportunities)}) ===")
    for i, opp in enumerate(opportunities):
        profit_pct = opp.expected_profit * 100
        confidence_pct = opp.confidence_score * 100
        print(
            f"{i}: {opp.base_currency}→{opp.intermediate_currency}→{opp.quote_currency} "
            f"| Profit: {profit_pct:.3f}% | Confidence: {confidence_pct:.1f}%"
        )

    # Create optimizer and analyze constraints
    optimizer = TriangularArbitrageOptimizer(base_constraints)

    # Calculate maximum possible investment per opportunity
    total_portfolio_value = sum(base_constraints.initial_balances.values())
    max_total_investment = total_portfolio_value * base_constraints.risk_tolerance

    print(f"\n=== RISK ANALYSIS ===")
    print(f"Total portfolio value: ${total_portfolio_value:,.2f}")
    print(f"Risk tolerance: {base_constraints.risk_tolerance:.1%}")
    print(f"Maximum total investment: ${max_total_investment:,.2f}")

    # Check if opportunities share the same base currency
    base_currencies = [opp.base_currency for opp in opportunities]
    unique_bases = set(base_currencies)
    print(f"\n=== CURRENCY OVERLAP ANALYSIS ===")
    print(f"Unique base currencies: {unique_bases}")
    print(
        f"Base currency distribution: {dict(zip(*np.unique(base_currencies, return_counts=True)))}"
    )

    # Check available balance for each base currency
    print(f"\n=== BALANCE CONSTRAINTS ===")
    for currency in unique_bases:
        available = base_constraints.initial_balances.get(currency, 0)
        max_position = base_constraints.max_position_size.get(currency, float("inf"))

        # Count opportunities using this currency
        opp_count = sum(1 for opp in opportunities if opp.base_currency == currency)

        print(f"{currency}:")
        print(f"  Available balance: {available:,.4f}")
        print(f"  Max position size: ${max_position:,.2f}")
        print(f"  Opportunities using this currency: {opp_count}")

        if available > 0:
            max_investment_per_opp = (
                available / opp_count if opp_count > 0 else available
            )
            print(f"  Max investment per opportunity: {max_investment_per_opp:,.4f}")


if __name__ == "__main__":
    debug_constraints()
