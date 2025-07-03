"""
Triangular Arbitrage Optimizer using PuLP Linear Programming

This module implements a linear programming solution for optimizing triangular arbitrage
opportunities in cryptocurrency markets, considering liquidity constraints, transaction fees,
minimum holding values, and volume limitations.
"""

import pulp as pl
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ArbitrageOpportunity:
    """Represents a triangular arbitrage opportunity"""

    base_currency: str
    intermediate_currency: str
    quote_currency: str
    exchange_rates: Dict[
        str, float
    ]  # e.g., {'BTC/USD': 50000, 'ETH/BTC': 0.06, 'ETH/USD': 3000}
    liquidity: Dict[str, float]  # Available liquidity for each trading pair
    transaction_fees: Dict[str, float]  # Fee percentage for each trading pair
    expected_profit: float
    confidence_score: float


@dataclass
class PortfolioConstraints:
    """Portfolio and trading constraints"""

    initial_balances: Dict[str, float]  # Current holdings in each currency
    min_holdings: Dict[str, float]  # Minimum required holdings for each currency
    max_position_size: Dict[str, float]  # Maximum position size for each currency
    risk_tolerance: float  # Risk tolerance factor (0-1)


class TriangularArbitrageOptimizer:
    """
    Optimizes triangular arbitrage opportunities using linear programming
    """

    def __init__(self, portfolio_constraints: PortfolioConstraints):
        self.portfolio_constraints = portfolio_constraints
        self.problem = None
        self.variables = {}
        self.solution = {}

    def create_optimization_problem(
        self, opportunities: List[ArbitrageOpportunity]
    ) -> pl.LpProblem:
        """
        Creates the linear programming problem for arbitrage optimization

        Args:
            opportunities: List of available arbitrage opportunities

        Returns:
            PuLP LpProblem instance
        """
        # Create the problem
        self.problem = pl.LpProblem("Triangular_Arbitrage_Optimization", pl.LpMaximize)

        # Decision variables: amount to invest in each arbitrage opportunity
        self.variables = {}
        for i, opp in enumerate(opportunities):
            var_name = f"invest_opp_{i}"
            self.variables[var_name] = pl.LpVariable(
                var_name, lowBound=0, cat="Continuous"
            )

        # Objective function: maximize expected profit adjusted for risk
        objective = pl.lpSum(
            [
                opp.expected_profit
                * opp.confidence_score
                * self.variables[f"invest_opp_{i}"]
                for i, opp in enumerate(opportunities)
            ]
        )
        self.problem += objective

        # Add constraints
        self._add_liquidity_constraints(opportunities)
        self._add_balance_constraints(opportunities)
        self._add_minimum_holding_constraints(opportunities)
        self._add_risk_constraints(opportunities)

        return self.problem

    def _add_liquidity_constraints(self, opportunities: List[ArbitrageOpportunity]):
        """Add liquidity constraints for each trading pair"""
        # Track liquidity usage across all opportunities
        liquidity_usage = {}

        for i, opp in enumerate(opportunities):
            for pair, _ in opp.liquidity.items():
                if pair not in liquidity_usage:
                    liquidity_usage[pair] = []

                # Estimate liquidity consumption based on investment amount
                # This is a simplified model - in practice, you'd need more sophisticated modeling
                consumption_factor = self._estimate_liquidity_consumption(opp, pair)
                liquidity_usage[pair].append(
                    consumption_factor * self.variables[f"invest_opp_{i}"]
                )

        # Add constraints to ensure we don't exceed available liquidity
        for pair, usage_list in liquidity_usage.items():
            max_liquidity = max([opp.liquidity.get(pair, 0) for opp in opportunities])
            if max_liquidity > 0:
                self.problem += pl.lpSum(usage_list) <= max_liquidity

    def _add_balance_constraints(self, opportunities: List[ArbitrageOpportunity]):
        """Add balance constraints to ensure we don't exceed available funds"""
        # Calculate total investment needed for each currency
        currency_investment = {}

        for i, opp in enumerate(opportunities):
            currencies = [
                opp.base_currency,
                opp.intermediate_currency,
                opp.quote_currency,
            ]
            for currency in currencies:
                if currency not in currency_investment:
                    currency_investment[currency] = []

                # Add investment amount (simplified - assumes investment is in base currency)
                if currency == opp.base_currency:
                    currency_investment[currency].append(
                        self.variables[f"invest_opp_{i}"]
                    )

        # Ensure we don't exceed available balances
        for currency, investments in currency_investment.items():
            available_balance = self.portfolio_constraints.initial_balances.get(
                currency, 0
            )
            if available_balance > 0:
                self.problem += pl.lpSum(investments) <= available_balance

    def _add_minimum_holding_constraints(
        self, opportunities: List[ArbitrageOpportunity]
    ):
        """Add minimum holding constraints"""
        for currency, min_holding in self.portfolio_constraints.min_holdings.items():
            # Calculate net change in holdings for this currency
            net_change = []

            for i, opp in enumerate(opportunities):
                if currency in [
                    opp.base_currency,
                    opp.intermediate_currency,
                    opp.quote_currency,
                ]:
                    # Simplified calculation - in practice, you'd model the exact flow
                    if currency == opp.base_currency:
                        net_change.append(-self.variables[f"invest_opp_{i}"])
                    else:
                        # Estimate net gain from the arbitrage
                        estimated_gain = opp.expected_profit * 0.5  # Simplified
                        net_change.append(
                            estimated_gain * self.variables[f"invest_opp_{i}"]
                        )

            current_balance = self.portfolio_constraints.initial_balances.get(
                currency, 0
            )
            if net_change:
                self.problem += current_balance + pl.lpSum(net_change) >= min_holding

    def _add_risk_constraints(self, opportunities: List[ArbitrageOpportunity]):
        """Add risk management constraints"""
        # Maximum position size constraint
        for i, opp in enumerate(opportunities):
            max_position = self.portfolio_constraints.max_position_size.get(
                opp.base_currency, float("inf")
            )
            if max_position < float("inf"):
                self.problem += self.variables[f"invest_opp_{i}"] <= max_position

        # Risk tolerance constraint (limit total exposure)
        total_investment = pl.lpSum(
            [self.variables[f"invest_opp_{i}"] for i in range(len(opportunities))]
        )
        total_portfolio_value = sum(
            self.portfolio_constraints.initial_balances.values()
        )
        max_exposure = total_portfolio_value * self.portfolio_constraints.risk_tolerance
        self.problem += total_investment <= max_exposure

    def _estimate_liquidity_consumption(
        self, opp: ArbitrageOpportunity, pair: str
    ) -> float:
        """
        Estimate how much liquidity is consumed per unit of investment
        This is a simplified model - in practice, you'd use order book data
        """
        # Base consumption factor
        base_factor = 0.1

        # Adjust based on transaction fees (higher fees might indicate lower liquidity)
        fee_adjustment = opp.transaction_fees.get(pair, 0.001) * 10

        return base_factor + fee_adjustment

    def solve(self, opportunities: List[ArbitrageOpportunity]) -> Dict:
        """
        Solve the optimization problem

        Args:
            opportunities: List of arbitrage opportunities

        Returns:
            Dictionary containing optimization results
        """
        if not opportunities:
            logger.warning("No arbitrage opportunities provided")
            return {"status": "No opportunities", "investments": {}}

        # Create and solve the problem
        self.create_optimization_problem(opportunities)

        # Solve using CBC solver (default)
        logger.info("Solving optimization problem...")
        status = self.problem.solve()

        # Extract results
        self.solution = {
            "status": pl.LpStatus[status],
            "objective_value": pl.value(self.problem.objective),
            "investments": {},
            "total_investment": 0,
            "expected_profit": 0,
        }

        if status == pl.LpStatusOptimal:
            for i, opp in enumerate(opportunities):
                var_name = f"invest_opp_{i}"
                investment_amount = pl.value(self.variables[var_name])

                if investment_amount > 0.001:  # Only include significant investments
                    self.solution["investments"][f"opportunity_{i}"] = {
                        "amount": investment_amount,
                        "opportunity": opp,
                        "expected_profit": investment_amount
                        * opp.expected_profit
                        * opp.confidence_score,
                    }
                    self.solution["total_investment"] += investment_amount
                    self.solution["expected_profit"] += (
                        investment_amount * opp.expected_profit * opp.confidence_score
                    )

            logger.info(
                f"Optimization successful. Expected profit: {self.solution['expected_profit']:.4f}"
            )
        else:
            logger.warning(f"Optimization failed with status: {pl.LpStatus[status]}")

        return self.solution

    def get_execution_plan(self) -> List[Dict]:
        """
        Generate a detailed execution plan for the optimized arbitrage trades

        Returns:
            List of trade execution steps
        """
        if not self.solution or self.solution["status"] != "Optimal":
            return []

        execution_plan = []

        for opp_id, investment_data in self.solution["investments"].items():
            opp = investment_data["opportunity"]
            amount = investment_data["amount"]

            # Generate the three trades for triangular arbitrage
            trades = [
                {
                    "step": 1,
                    "action": "buy",
                    "pair": f"{opp.intermediate_currency}/{opp.base_currency}",
                    "amount": amount,
                    "expected_rate": opp.exchange_rates.get(
                        f"{opp.intermediate_currency}/{opp.base_currency}", 0
                    ),
                    "fee": opp.transaction_fees.get(
                        f"{opp.intermediate_currency}/{opp.base_currency}", 0.001
                    ),
                },
                {
                    "step": 2,
                    "action": "buy",
                    "pair": f"{opp.quote_currency}/{opp.intermediate_currency}",
                    "amount": amount
                    * opp.exchange_rates.get(
                        f"{opp.intermediate_currency}/{opp.base_currency}", 1
                    ),
                    "expected_rate": opp.exchange_rates.get(
                        f"{opp.quote_currency}/{opp.intermediate_currency}", 0
                    ),
                    "fee": opp.transaction_fees.get(
                        f"{opp.quote_currency}/{opp.intermediate_currency}", 0.001
                    ),
                },
                {
                    "step": 3,
                    "action": "sell",
                    "pair": f"{opp.quote_currency}/{opp.base_currency}",
                    "amount": "calculated_from_step_2",
                    "expected_rate": opp.exchange_rates.get(
                        f"{opp.quote_currency}/{opp.base_currency}", 0
                    ),
                    "fee": opp.transaction_fees.get(
                        f"{opp.quote_currency}/{opp.base_currency}", 0.001
                    ),
                },
            ]

            execution_plan.append(
                {
                    "opportunity_id": opp_id,
                    "investment_amount": amount,
                    "trades": trades,
                    "expected_profit": investment_data["expected_profit"],
                }
            )

        return execution_plan


def calculate_triangular_arbitrage_profit(
    rate_ab: float,
    rate_bc: float,
    rate_ca: float,
    fees: Tuple[float, float, float] = (0.001, 0.001, 0.001),
) -> float:
    """
    Calculate the expected profit from a triangular arbitrage opportunity

    Args:
        rate_ab: Exchange rate from currency A to B
        rate_bc: Exchange rate from currency B to C
        rate_ca: Exchange rate from currency C to A
        fees: Transaction fees for each trade (default 0.1% each)

    Returns:
        Expected profit percentage
    """
    # Calculate the effective rates after fees
    effective_ab = rate_ab * (1 - fees[0])
    effective_bc = rate_bc * (1 - fees[1])
    effective_ca = rate_ca * (1 - fees[2])

    # Calculate the final amount after the triangular trade
    final_amount = effective_ab * effective_bc * effective_ca

    # Profit is the difference from the initial amount (1 unit)
    profit = final_amount - 1.0

    return profit
