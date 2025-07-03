"""
Advanced debug script to understand why optimizer selects only one opportunity
"""

from arbitrage_optimizer import TriangularArbitrageOptimizer, PortfolioConstraints
from arbitrage_detector import FakeArbitrageAnalyzer
from market_simulator import CryptoMarketSimulator
import pulp as pl


def debug_optimization_detailed():
    # Initialize components
    analyzer = FakeArbitrageAnalyzer()
    market_sim = CryptoMarketSimulator()

    # Generate portfolio constraints
    base_constraints = market_sim.generate_portfolio_constraints(
        total_portfolio_value=100_000, risk_profile="moderate"
    )

    # Generate opportunities
    opportunities = analyzer.generate_arbitrage_opportunities(5)

    print("=== GENERATED OPPORTUNITIES ===")
    for i, opp in enumerate(opportunities):
        profit_pct = opp.expected_profit * 100
        confidence_pct = opp.confidence_score * 100
        weighted_profit = opp.expected_profit * opp.confidence_score * 100
        print(
            f"{i}: {opp.base_currency}→{opp.intermediate_currency}→{opp.quote_currency}"
        )
        print(
            f"   Profit: {profit_pct:.3f}% | Confidence: {confidence_pct:.1f}% | Weighted: {weighted_profit:.3f}%"
        )

    # Create optimizer
    optimizer = TriangularArbitrageOptimizer(base_constraints)

    # Create the problem
    optimizer.create_optimization_problem(opportunities)

    print(f"\n=== OPTIMIZATION PROBLEM STRUCTURE ===")
    print(f"Variables: {len(optimizer.variables)}")
    print(f"Constraints: {len(optimizer.problem.constraints)}")

    # Solve the problem
    print(f"\n=== SOLVING ===")
    solution = optimizer.solve(opportunities)

    print(f"\n=== SOLUTION ANALYSIS ===")
    print(f"Status: {solution['status']}")
    print(f"Objective Value: {solution.get('objective_value', 0):.6f}")
    print(f"Total Investment: ${solution.get('total_investment', 0):.2f}")
    print(f"Expected Profit: ${solution.get('expected_profit', 0):.6f}")

    # Show variable values
    print(f"\n=== VARIABLE VALUES ===")
    for i, opp in enumerate(opportunities):
        var_name = f"invest_opp_{i}"
        if var_name in optimizer.variables:
            value = pl.value(optimizer.variables[var_name])
            print(f"{var_name}: {value:.6f}")
        else:
            print(f"{var_name}: Not found")

    # Check constraint slack
    print(f"\n=== CONSTRAINT ANALYSIS ===")
    total_portfolio_value = sum(base_constraints.initial_balances.values())
    max_exposure = total_portfolio_value * base_constraints.risk_tolerance
    print(f"Risk tolerance limit: ${max_exposure:.2f}")
    print(f"Actual total investment: ${solution.get('total_investment', 0):.2f}")
    print(
        f"Risk utilization: {(solution.get('total_investment', 0) / max_exposure) * 100:.1f}%"
    )

    # Test manual allocation to multiple opportunities
    print(f"\n=== MANUAL ALLOCATION TEST ===")
    if len(opportunities) >= 2:
        # Try to manually allocate to top 2 opportunities
        top_2_opps = opportunities[:2]
        available_budget = max_exposure / 2  # Split budget

        print(
            f"Testing split allocation: ${available_budget:.2f} each to top 2 opportunities"
        )

        total_manual_profit = 0
        for i, opp in enumerate(top_2_opps):
            manual_profit = (
                available_budget * opp.expected_profit * opp.confidence_score
            )
            total_manual_profit += manual_profit
            print(
                f"  Opp {i}: Investment=${available_budget:.2f}, Profit=${manual_profit:.6f}"
            )

        print(f"Total manual profit: ${total_manual_profit:.6f}")
        print(f"Optimizer profit: ${solution.get('expected_profit', 0):.6f}")
        print(
            f"Manual vs Optimizer: {(total_manual_profit / solution.get('expected_profit', 1)) * 100:.1f}%"
        )


if __name__ == "__main__":
    debug_optimization_detailed()
