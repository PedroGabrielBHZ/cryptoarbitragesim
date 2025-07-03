"""
Main Application for Triangular Arbitrage Optimization

This is the main entry point that demonstrates the complete arbitrage optimization system
using PuLP linear programming with fake data from an external analyzer.
"""

import numpy as np
import logging
from typing import Dict, List
from arbitrage_optimizer import TriangularArbitrageOptimizer, PortfolioConstraints
from arbitrage_detector import FakeArbitrageAnalyzer
from market_simulator import CryptoMarketSimulator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ArbitrageSystem:
    """
    Main arbitrage optimization system that coordinates all components
    """

    def __init__(
        self, portfolio_value: float = 100_000, risk_profile: str = "moderate"
    ):
        """
        Initialize the arbitrage system

        Args:
            portfolio_value: Total portfolio value in USD
            risk_profile: Risk profile ('conservative', 'moderate', 'aggressive')
        """
        self.portfolio_value = portfolio_value
        self.risk_profile = risk_profile

        # Initialize components
        self.analyzer = FakeArbitrageAnalyzer()  # No fixed seed for dynamic results
        self.market_simulator = (
            CryptoMarketSimulator()
        )  # No fixed seed for dynamic results

        # Generate portfolio constraints
        self.base_constraints = self.market_simulator.generate_portfolio_constraints(
            total_portfolio_value=portfolio_value, risk_profile=risk_profile
        )

        # Initialize optimizer
        self.optimizer = TriangularArbitrageOptimizer(self.base_constraints)

        logger.info(
            f"Initialized arbitrage system with ${portfolio_value:,.2f} portfolio"
        )
        logger.info(f"Risk profile: {risk_profile}")
        logger.info(f"Risk tolerance: {self.base_constraints.risk_tolerance:.2%}")

    def run_optimization_cycle(self, num_opportunities: int = 15) -> Dict:
        """
        Run a complete optimization cycle

        Args:
            num_opportunities: Number of arbitrage opportunities to generate

        Returns:
            Dictionary containing all results
        """
        logger.info("=" * 60)
        logger.info("STARTING ARBITRAGE OPTIMIZATION CYCLE")
        logger.info("=" * 60)

        # Step 1: Generate arbitrage opportunities
        logger.info(f"Generating {num_opportunities} arbitrage opportunities...")
        opportunities = self.analyzer.generate_arbitrage_opportunities(
            num_opportunities
        )

        if not opportunities:
            logger.warning("No profitable arbitrage opportunities found!")
            return {"status": "no_opportunities"}

        logger.info(f"Found {len(opportunities)} profitable opportunities")

        # Step 2: Get current market-adjusted constraints
        logger.info("Adjusting constraints based on market conditions...")
        market_conditions = self.market_simulator.market_conditions
        current_constraints = self.market_simulator.get_dynamic_constraints(
            self.base_constraints
        )

        logger.info(f"Market sentiment: {market_conditions.market_sentiment}")
        logger.info(f"Volatility index: {market_conditions.volatility_index:.3f}")
        logger.info(
            f"Adjusted risk tolerance: {current_constraints.risk_tolerance:.2%}"
        )

        # Step 3: Update optimizer with current constraints
        self.optimizer = TriangularArbitrageOptimizer(current_constraints)

        # Step 4: Solve optimization problem
        logger.info("Solving optimization problem...")
        solution = self.optimizer.solve(opportunities)

        # Step 5: Generate execution plan
        execution_plan = self.optimizer.get_execution_plan()

        # Step 6: Calculate execution risks
        risk_assessment = self.market_simulator.simulate_execution_risk(execution_plan)

        # Compile results
        results = {
            "opportunities": opportunities,
            "solution": solution,
            "execution_plan": execution_plan,
            "risk_assessment": risk_assessment,
            "market_conditions": market_conditions,
            "constraints": current_constraints,
            "status": "completed",
        }

        # Log summary
        self._log_results_summary(results)

        return results

    def _log_results_summary(self, results: Dict):
        """Log a summary of the optimization results"""
        solution = results["solution"]
        risk_assessment = results["risk_assessment"]

        logger.info("=" * 60)
        logger.info("OPTIMIZATION RESULTS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {solution.get('status', 'Unknown')}")
        logger.info(f"Total Investment: ${solution.get('total_investment', 0):,.2f}")
        logger.info(f"Expected Profit: ${solution.get('expected_profit', 0):.6f}")

        if solution.get("total_investment", 0) > 0:
            roi = (
                solution.get("expected_profit", 0) / solution.get("total_investment", 1)
            ) * 100
            logger.info(f"ROI: {roi:.4f}%")

        logger.info(f"Opportunities Invested: {len(solution.get('investments', {}))}")
        logger.info(
            f"Execution Probability: {risk_assessment.get('execution_probability', 0):.2%}"
        )
        logger.info(f"Risk Level: {risk_assessment.get('risk_level', 'unknown')}")
        logger.info("=" * 60)

    def print_results_summary(self, results: Dict):
        """
        Print a text summary of the results to console

        Args:
            results: Results dictionary from optimization cycle
        """
        if results["status"] != "completed":
            print("Cannot display summary for incomplete results")
            return

        opportunities = results["opportunities"]
        solution = results["solution"]
        constraints = results["constraints"]

        print("\n" + "=" * 60)
        print("TRIANGULAR ARBITRAGE OPTIMIZATION SUMMARY")
        print("=" * 60)

        # Opportunities summary
        print(f"ARBITRAGE OPPORTUNITIES ANALYZED: {len(opportunities)}")
        if opportunities:
            import numpy as np

            avg_profit = np.mean([opp.expected_profit for opp in opportunities]) * 100
            max_profit = max([opp.expected_profit for opp in opportunities]) * 100
            avg_confidence = (
                np.mean([opp.confidence_score for opp in opportunities]) * 100
            )

            print(f"  • Average Expected Profit: {avg_profit:.4f}%")
            print(f"  • Maximum Expected Profit: {max_profit:.4f}%")
            print(f"  • Average Confidence Score: {avg_confidence:.2f}%")

        # Optimization results
        print("\nOPTIMIZATION RESULTS:")
        print(f"  • Status: {solution.get('status', 'Unknown')}")
        print(f"  • Total Investment: ${solution.get('total_investment', 0):.2f}")
        print(f"  • Expected Profit: ${solution.get('expected_profit', 0):.6f}")

        if solution.get("total_investment", 0) > 0:
            roi = (
                solution.get("expected_profit", 0) / solution.get("total_investment", 1)
            ) * 100
            print(f"  • Return on Investment: {roi:.4f}%")

        num_investments = len(solution.get("investments", {}))
        print(f"  • Number of Opportunities Invested: {num_investments}")

        # Portfolio analysis
        total_portfolio_value = sum(constraints.initial_balances.values())
        risk_utilization = (
            (solution.get("total_investment", 0) / total_portfolio_value) * 100
            if total_portfolio_value > 0
            else 0
        )

        print("\nPORTFOLIO ANALYSIS:")
        print(f"  • Total Portfolio Value: ${total_portfolio_value:.2f}")
        print(f"  • Risk Tolerance: {constraints.risk_tolerance * 100:.1f}%")
        print(f"  • Risk Utilization: {risk_utilization:.2f}%")
        print(f"  • Number of Currencies: {len(constraints.initial_balances)}")

        # Top investments
        if solution.get("investments"):
            print("\nTOP INVESTMENTS:")
            sorted_investments = sorted(
                solution["investments"].items(),
                key=lambda x: x[1]["expected_profit"],
                reverse=True,
            )

            for i, (opp_id, inv_data) in enumerate(sorted_investments[:5], 1):
                opp = inv_data["opportunity"]
                print(f"  {i}. {opp_id}:")
                print(
                    f"     • Currencies: {opp.base_currency} → {opp.intermediate_currency} → {opp.quote_currency}"
                )
                print(f"     • Investment: ${inv_data['amount']:.2f}")
                print(f"     • Expected Profit: ${inv_data['expected_profit']:.6f}")
                print(f"     • Confidence: {opp.confidence_score * 100:.1f}%")

        print("=" * 60)

    def simulate_market_update(self, results: Dict) -> Dict:
        """
        Simulate market changes and update opportunities

        Args:
            results: Current results

        Returns:
            Updated results after market changes
        """
        logger.info("Simulating market update...")

        # Update market conditions
        self.market_simulator.update_market_conditions()

        # Update opportunities based on new market conditions
        updated_opportunities = self.analyzer.simulate_market_update(
            results["opportunities"]
        )

        # Re-run optimization with updated data
        if updated_opportunities:
            logger.info(f"Updated opportunities: {len(updated_opportunities)}")
            return self.run_optimization_cycle()
        else:
            logger.warning("No profitable opportunities after market update")
            return {"status": "no_opportunities_after_update"}

    def run_multi_period_analysis(self, num_periods: int = 5) -> List[Dict]:
        """
        Run multiple optimization periods to simulate dynamic trading

        Args:
            num_periods: Number of periods to simulate

        Returns:
            List of results for each period
        """
        logger.info(f"Running {num_periods}-period analysis...")

        all_results = []

        for period in range(num_periods):
            logger.info(f"\n--- PERIOD {period + 1}/{num_periods} ---")

            # Run optimization cycle
            results = self.run_optimization_cycle()
            results["period"] = period + 1
            all_results.append(results)

            # Update market conditions for next period (except last)
            if period < num_periods - 1:
                self.market_simulator.update_market_conditions()

        # Analyze multi-period performance
        self._analyze_multi_period_performance(all_results)

        return all_results

    def _analyze_multi_period_performance(self, all_results: List[Dict]):
        """Analyze performance across multiple periods"""
        logger.info("\n" + "=" * 60)
        logger.info("MULTI-PERIOD PERFORMANCE ANALYSIS")
        logger.info("=" * 60)

        # Filter out unsuccessful results
        successful_results = [
            r
            for r in all_results
            if r.get("solution") and r["solution"].get("investments")
        ]

        if not successful_results:
            logger.info("No successful periods found.")
            return

        total_investment = sum(
            r["solution"].get("total_investment", 0) for r in successful_results
        )
        total_profit = sum(
            r["solution"].get("expected_profit", 0) for r in successful_results
        )

        successful_periods = len(successful_results)

        logger.info(f"Successful periods: {successful_periods}/{len(all_results)}")
        logger.info(f"Total investment: ${total_investment:,.2f}")
        logger.info(f"Total expected profit: ${total_profit:.6f}")

        if total_investment > 0:
            overall_roi = (total_profit / total_investment) * 100
            logger.info(f"Overall ROI: {overall_roi:.4f}%")

        # Period-by-period summary
        for i, results in enumerate(all_results, 1):
            if results.get("solution"):
                solution = results["solution"]
                investment = solution.get("total_investment", 0)
                profit = solution.get("expected_profit", 0)
                num_opps = len(solution.get("investments", {}))

                logger.info(
                    f"Period {i}: ${investment:.2f} invested, ${profit:.6f} profit, {num_opps} opportunities"
                )
            else:
                logger.info(f"Period {i}: No opportunities found")


def main():
    """Main function to demonstrate the arbitrage optimization system"""

    # Configuration
    PORTFOLIO_VALUE = 100_000  # $100K portfolio
    RISK_PROFILE = "moderate"  # moderate risk tolerance
    NUM_OPPORTUNITIES = 20  # analyze 20 opportunities

    try:
        # Initialize the system
        print("Initializing Triangular Arbitrage Optimization System...")
        system = ArbitrageSystem(
            portfolio_value=PORTFOLIO_VALUE, risk_profile=RISK_PROFILE
        )

        # Run single optimization cycle
        print("\nRunning optimization cycle...")
        results = system.run_optimization_cycle(num_opportunities=NUM_OPPORTUNITIES)

        # Generate and print report
        if results["status"] == "completed":
            system.print_results_summary(results)

            # Demonstrate market update
            print("\nSimulating market update...")
            updated_results = system.simulate_market_update(results)

            if updated_results["status"] == "completed":
                print("\nMarket update completed. New optimization results:")
                system.print_results_summary(updated_results)

        # Demonstrate multi-period analysis
        print("\nRunning multi-period analysis...")
        multi_period_results = system.run_multi_period_analysis(num_periods=3)

        print("\nArbitrage optimization system demonstration completed successfully!")

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()
