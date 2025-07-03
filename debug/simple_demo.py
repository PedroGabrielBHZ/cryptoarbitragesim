"""
Simple Demo Script for Triangular Arbitrage Optimizer

This script demonstrates the key features of the arbitrage optimization system
in a simplified format for easy understanding.
"""

from arbitrage_optimizer import TriangularArbitrageOptimizer, PortfolioConstraints
from arbitrage_detector import FakeArbitrageAnalyzer
from market_simulator import CryptoMarketSimulator
import pandas as pd


def simple_demo():
    """Run a simplified demonstration of the arbitrage optimizer"""

    print("🚀 TRIANGULAR ARBITRAGE OPTIMIZER DEMO")
    print("=" * 50)

    # 1. Initialize components
    print("\n1. Initializing system components...")
    analyzer = FakeArbitrageAnalyzer(seed=123)
    market_sim = CryptoMarketSimulator(seed=123)

    # 2. Generate portfolio constraints
    print("\n2. Setting up portfolio...")
    portfolio_value = 50_000  # $50K portfolio
    constraints = market_sim.generate_portfolio_constraints(
        total_portfolio_value=portfolio_value, risk_profile="moderate"
    )

    print(f"   💰 Portfolio Value: ${portfolio_value:,}")
    print(f"   📊 Risk Tolerance: {constraints.risk_tolerance:.1%}")
    print(f"   🏦 Currencies: {len(constraints.initial_balances)}")

    # Show portfolio composition
    print("\n   Portfolio Composition:")
    for currency, amount in constraints.initial_balances.items():
        percentage = (amount / sum(constraints.initial_balances.values())) * 100
        print(f"     • {currency}: {amount:,.2f} ({percentage:.1f}%)")

    # 3. Generate arbitrage opportunities
    print("\n3. Generating arbitrage opportunities...")
    opportunities = analyzer.generate_arbitrage_opportunities(10)

    print(f"   🎯 Found {len(opportunities)} profitable opportunities")

    # Show top opportunities
    print("\n   Top 5 Opportunities:")
    for i, opp in enumerate(opportunities[:5], 1):
        profit_pct = opp.expected_profit * 100
        confidence_pct = opp.confidence_score * 100
        print(
            f"     {i}. {opp.base_currency}→{opp.intermediate_currency}→{opp.quote_currency}: "
            f"{profit_pct:.3f}% profit (confidence: {confidence_pct:.1f}%)"
        )

    # 4. Optimize investment allocation
    print("\n4. Optimizing investment allocation...")
    optimizer = TriangularArbitrageOptimizer(constraints)
    solution = optimizer.solve(opportunities)

    print(f"   ✅ Status: {solution['status']}")
    print(f"   💵 Total Investment: ${solution['total_investment']:,.2f}")
    print(f"   📈 Expected Profit: ${solution['expected_profit']:.4f}")

    if solution["total_investment"] > 0:
        roi = (solution["expected_profit"] / solution["total_investment"]) * 100
        print(f"   🎯 ROI: {roi:.4f}%")

    # 5. Show investment details
    if solution.get("investments"):
        print(
            f"\n   📋 Investment Breakdown ({len(solution['investments'])} opportunities):"
        )

        for opp_id, inv_data in solution["investments"].items():
            opp = inv_data["opportunity"]
            amount = inv_data["amount"]
            profit = inv_data["expected_profit"]

            print(
                f"     • {opp.base_currency}→{opp.intermediate_currency}→{opp.quote_currency}: "
                f"${amount:,.2f} → ${profit:.4f} profit"
            )

    # 6. Generate execution plan
    print("\n5. Generating execution plan...")
    execution_plan = optimizer.get_execution_plan()

    if execution_plan:
        plan = execution_plan[0]  # Show first plan
        print(f"   📝 Execution Plan for {plan['opportunity_id']}:")
        print(f"      Investment: ${plan['investment_amount']:,.2f}")

        for step in plan["trades"]:
            action = step["action"].title()
            pair = step["pair"]
            fee = step["fee"] * 100
            print(f"      Step {step['step']}: {action} {pair} (fee: {fee:.3f}%)")

    # 7. Risk assessment
    print("\n6. Risk Assessment:")
    market_conditions = market_sim.market_conditions
    print(f"   📊 Market Sentiment: {market_conditions.market_sentiment.title()}")
    print(f"   📈 Volatility Index: {market_conditions.volatility_index:.3f}")
    print(f"   💧 Liquidity Factor: {market_conditions.liquidity_factor:.3f}")

    # Calculate portfolio utilization
    portfolio_utilization = (solution["total_investment"] / portfolio_value) * 100
    print(f"   💼 Portfolio Utilization: {portfolio_utilization:.1f}%")
    print(
        f"   ⚠️  Risk Level: {'Low' if portfolio_utilization < 15 else 'Medium' if portfolio_utilization < 30 else 'High'}"
    )

    print("\n" + "=" * 50)
    print("✨ Demo completed successfully!")

    return {
        "opportunities": opportunities,
        "solution": solution,
        "execution_plan": execution_plan,
        "constraints": constraints,
    }


def show_comparison():
    """Show a comparison of different risk profiles"""

    print("\n🔍 RISK PROFILE COMPARISON")
    print("=" * 50)

    profiles = ["conservative", "moderate", "aggressive"]
    results = {}

    for profile in profiles:
        print(f"\n📊 {profile.title()} Profile:")

        # Generate constraints for this profile
        market_sim = CryptoMarketSimulator(seed=456)
        constraints = market_sim.generate_portfolio_constraints(
            total_portfolio_value=100_000, risk_profile=profile
        )

        # Generate opportunities
        analyzer = FakeArbitrageAnalyzer(seed=456)
        opportunities = analyzer.generate_arbitrage_opportunities(15)

        # Optimize
        optimizer = TriangularArbitrageOptimizer(constraints)
        solution = optimizer.solve(opportunities)

        # Store results
        results[profile] = {
            "risk_tolerance": constraints.risk_tolerance,
            "investment": solution.get("total_investment", 0),
            "profit": solution.get("expected_profit", 0),
            "num_opportunities": len(solution.get("investments", {})),
        }

        print(f"   Risk Tolerance: {constraints.risk_tolerance:.1%}")
        print(f"   Investment: ${solution.get('total_investment', 0):,.2f}")
        print(f"   Expected Profit: ${solution.get('expected_profit', 0):.4f}")
        print(f"   Opportunities: {len(solution.get('investments', {}))}")

        if solution.get("total_investment", 0) > 0:
            roi = (
                solution.get("expected_profit", 0) / solution.get("total_investment", 1)
            ) * 100
            print(f"   ROI: {roi:.4f}%")

    # Summary table
    print("\n📋 Summary Comparison:")
    print("-" * 60)
    print(
        f"{'Profile':<12} {'Risk Tol.':<10} {'Investment':<12} {'Profit':<10} {'ROI':<8}"
    )
    print("-" * 60)

    for profile, data in results.items():
        investment = data["investment"]
        profit = data["profit"]
        roi = (profit / investment * 100) if investment > 0 else 0

        print(
            f"{profile.title():<12} {data['risk_tolerance']:<9.1%} ${investment:<11,.0f} ${profit:<9.4f} {roi:<7.3f}%"
        )


if __name__ == "__main__":
    # Run the simple demo
    demo_results = simple_demo()

    # Show risk profile comparison
    show_comparison()

    print("\n🎉 All demonstrations completed!")
