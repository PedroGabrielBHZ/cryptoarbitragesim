"""
Test the solution extraction directly
"""

from arbitrage_optimizer import TriangularArbitrageOptimizer, PortfolioConstraints
from arbitrage_detector import FakeArbitrageAnalyzer
from market_simulator import CryptoMarketSimulator


def test_solution_extraction():
    # Initialize components
    analyzer = FakeArbitrageAnalyzer()
    market_sim = CryptoMarketSimulator()

    # Generate portfolio constraints
    base_constraints = market_sim.generate_portfolio_constraints(
        total_portfolio_value=100_000, risk_profile="moderate"
    )

    # Generate opportunities
    opportunities = analyzer.generate_arbitrage_opportunities(5)

    # Create optimizer and solve
    optimizer = TriangularArbitrageOptimizer(base_constraints)
    solution = optimizer.solve(opportunities)

    print("=== SOLUTION EXTRACTION TEST ===")
    print(f"Solution status: {solution['status']}")
    print(f"Number of investments: {len(solution.get('investments', {}))}")
    print(f"Total investment: ${solution.get('total_investment', 0):.2f}")
    print(f"Expected profit: ${solution.get('expected_profit', 0):.6f}")

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
        print(f"  Profit %: {opp.expected_profit*100:.3f}%")
        print(f"  Confidence: {opp.confidence_score*100:.1f}%")
        print()


if __name__ == "__main__":
    test_solution_extraction()
