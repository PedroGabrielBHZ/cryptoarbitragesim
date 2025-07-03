"""
Market Simulator for Cryptocurrency Trading

This module simulates market conditions and provides realistic constraints
for the arbitrage optimization system.
"""

import random
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from arbitrage_optimizer import PortfolioConstraints


@dataclass
class MarketConditions:
    """Current market conditions affecting trading"""

    volatility_index: float  # 0-1, higher means more volatile
    liquidity_factor: float  # 0-2, affects available liquidity
    spread_factor: float  # 0-2, affects bid-ask spreads
    network_congestion: float  # 0-1, affects transaction fees
    market_sentiment: str  # 'bullish', 'bearish', 'neutral'


class CryptoMarketSimulator:
    """
    Simulates cryptocurrency market conditions and portfolio constraints
    """

    def __init__(self, seed: int = None):
        """
        Initialize the market simulator

        Args:
            seed: Random seed for reproducible results (None for random seed)
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Define cryptocurrencies and their characteristics
        self.currencies = {
            "BTC": {
                "volatility": 0.4,
                "market_cap_rank": 1,
                "avg_volume": 30_000_000_000,
            },
            "ETH": {
                "volatility": 0.5,
                "market_cap_rank": 2,
                "avg_volume": 15_000_000_000,
            },
            "USDT": {
                "volatility": 0.01,
                "market_cap_rank": 3,
                "avg_volume": 50_000_000_000,
            },
            "ADA": {
                "volatility": 0.6,
                "market_cap_rank": 5,
                "avg_volume": 1_000_000_000,
            },
            "DOT": {"volatility": 0.7, "market_cap_rank": 8, "avg_volume": 800_000_000},
            "LINK": {
                "volatility": 0.6,
                "market_cap_rank": 15,
                "avg_volume": 600_000_000,
            },
            "XRP": {
                "volatility": 0.5,
                "market_cap_rank": 6,
                "avg_volume": 2_000_000_000,
            },
            "LTC": {
                "volatility": 0.5,
                "market_cap_rank": 12,
                "avg_volume": 3_000_000_000,
            },
        }

        # Current market conditions
        self.market_conditions = self.generate_market_conditions()

    def generate_market_conditions(self) -> MarketConditions:
        """Generate current market conditions"""

        # Market sentiment affects other factors
        sentiments = ["bullish", "bearish", "neutral"]
        sentiment = random.choice(sentiments)

        if sentiment == "bullish":
            volatility = random.uniform(0.2, 0.6)
            liquidity_factor = random.uniform(1.1, 1.5)
            spread_factor = random.uniform(0.8, 1.0)
        elif sentiment == "bearish":
            volatility = random.uniform(0.6, 0.9)
            liquidity_factor = random.uniform(0.6, 0.9)
            spread_factor = random.uniform(1.2, 1.8)
        else:  # neutral
            volatility = random.uniform(0.3, 0.5)
            liquidity_factor = random.uniform(0.9, 1.1)
            spread_factor = random.uniform(0.9, 1.1)

        network_congestion = random.uniform(0.1, 0.8)

        return MarketConditions(
            volatility_index=volatility,
            liquidity_factor=liquidity_factor,
            spread_factor=spread_factor,
            network_congestion=network_congestion,
            market_sentiment=sentiment,
        )

    def generate_portfolio_constraints(
        self, total_portfolio_value: float = 100_000, risk_profile: str = "moderate"
    ) -> PortfolioConstraints:
        """
        Generate realistic portfolio constraints

        Args:
            total_portfolio_value: Total portfolio value in USD
            risk_profile: 'conservative', 'moderate', or 'aggressive'

        Returns:
            PortfolioConstraints object
        """

        # Risk tolerance based on profile
        risk_tolerances = {
            "conservative": random.uniform(0.05, 0.15),
            "moderate": random.uniform(0.15, 0.35),
            "aggressive": random.uniform(0.35, 0.60),
        }
        risk_tolerance = risk_tolerances.get(risk_profile, 0.25)

        # Generate initial balances
        initial_balances = self._generate_initial_balances(total_portfolio_value)

        # Generate minimum holdings (usually 5-20% of current holdings)
        min_holdings = {}
        for currency, balance in initial_balances.items():
            if currency in ["USDT", "USDC", "DAI"]:  # Stablecoins
                min_ratio = random.uniform(0.1, 0.3)  # Keep more stablecoins
            else:
                min_ratio = random.uniform(0.05, 0.2)
            min_holdings[currency] = balance * min_ratio

        # Generate maximum position sizes
        max_position_size = {}
        for currency in initial_balances.keys():
            if currency in ["USDT", "USDC", "DAI"]:  # Stablecoins
                max_ratio = random.uniform(0.4, 0.8)
            else:
                max_ratio = random.uniform(0.2, 0.5)
            max_position_size[currency] = total_portfolio_value * max_ratio

        return PortfolioConstraints(
            initial_balances=initial_balances,
            min_holdings=min_holdings,
            max_position_size=max_position_size,
            risk_tolerance=risk_tolerance,
        )

    def _generate_initial_balances(self, total_value: float) -> Dict[str, float]:
        """
        Generate initial cryptocurrency balances for a portfolio

        Args:
            total_value: Total portfolio value in USD

        Returns:
            Dictionary of currency balances
        """
        balances = {}

        # Typical portfolio allocation weights
        allocation_weights = {
            "USDT": random.uniform(0.15, 0.25),  # 15-25% USDT
            "USDC": random.uniform(0.10, 0.20),  # 10-20% USDC
            "DAI": random.uniform(0.05, 0.15),  # 5-15% DAI
            "BTC": random.uniform(0.25, 0.35),  # 25-35% Bitcoin
            "ETH": random.uniform(0.15, 0.25),  # 15-25% Ethereum
        }

        # Normalize weights to sum to 1
        total_weight = sum(allocation_weights.values())
        remaining_weight = 1.0 - total_weight

        # Add smaller allocations for other currencies
        other_currencies = ["ADA", "DOT", "LINK", "XRP", "LTC"]
        num_others = random.randint(1, 3)
        selected_others = random.sample(other_currencies, num_others)

        other_weight = remaining_weight / len(selected_others) if selected_others else 0
        for currency in selected_others:
            allocation_weights[currency] = other_weight

        # Convert to actual balances
        # Using simplified USD values (in reality you'd use current market prices)
        estimated_prices = {
            "USDT": 1.0,
            "USDC": 1.0,  # Added USDC
            "DAI": 1.0,  # Added DAI
            "BTC": 45000,
            "ETH": 3000,
            "ADA": 1.2,
            "DOT": 25,
            "LINK": 15,
            "XRP": 0.6,
            "LTC": 150,
        }

        for currency, weight in allocation_weights.items():
            usd_allocation = total_value * weight
            price = estimated_prices.get(currency, 1.0)
            balances[currency] = usd_allocation / price

        return balances

    def update_market_conditions(self):
        """Update market conditions to simulate changing market"""

        # Gradual changes to market conditions
        volatility_change = random.uniform(-0.1, 0.1)
        self.market_conditions.volatility_index = np.clip(
            self.market_conditions.volatility_index + volatility_change, 0.1, 0.9
        )

        liquidity_change = random.uniform(-0.2, 0.2)
        self.market_conditions.liquidity_factor = np.clip(
            self.market_conditions.liquidity_factor + liquidity_change, 0.5, 2.0
        )

        spread_change = random.uniform(-0.1, 0.1)
        self.market_conditions.spread_factor = np.clip(
            self.market_conditions.spread_factor + spread_change, 0.5, 2.0
        )

        congestion_change = random.uniform(-0.1, 0.1)
        self.market_conditions.network_congestion = np.clip(
            self.market_conditions.network_congestion + congestion_change, 0.0, 1.0
        )

        # Occasionally change market sentiment
        if random.random() < 0.1:  # 10% chance
            sentiments = ["bullish", "bearish", "neutral"]
            self.market_conditions.market_sentiment = random.choice(sentiments)

    def get_dynamic_constraints(
        self, base_constraints: PortfolioConstraints
    ) -> PortfolioConstraints:
        """
        Adjust portfolio constraints based on current market conditions

        Args:
            base_constraints: Base portfolio constraints

        Returns:
            Adjusted constraints based on market conditions
        """

        # Adjust risk tolerance based on market volatility
        volatility_adjustment = 1.0 - (self.market_conditions.volatility_index * 0.3)
        adjusted_risk_tolerance = (
            base_constraints.risk_tolerance * volatility_adjustment
        )

        # Adjust maximum position sizes based on liquidity
        adjusted_max_positions = {}
        for currency, max_pos in base_constraints.max_position_size.items():
            liquidity_adjustment = self.market_conditions.liquidity_factor
            adjusted_max_positions[currency] = max_pos * liquidity_adjustment

        # Increase minimum holdings in volatile markets
        adjusted_min_holdings = {}
        for currency, min_hold in base_constraints.min_holdings.items():
            if currency in [
                "USDT",
                "USDC",
                "DAI",
            ]:  # Increase stablecoin minimums in volatile markets
                volatility_buffer = 1.0 + (
                    self.market_conditions.volatility_index * 0.5
                )
            else:
                volatility_buffer = 1.0 + (
                    self.market_conditions.volatility_index * 0.2
                )
            adjusted_min_holdings[currency] = min_hold * volatility_buffer

        return PortfolioConstraints(
            initial_balances=base_constraints.initial_balances,
            min_holdings=adjusted_min_holdings,
            max_position_size=adjusted_max_positions,
            risk_tolerance=adjusted_risk_tolerance,
        )

    def calculate_execution_costs(
        self, trade_amount: float, currency_pair: str
    ) -> Dict[str, float]:
        """
        Calculate realistic execution costs based on market conditions

        Args:
            trade_amount: Amount to trade
            currency_pair: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Dictionary with cost breakdown
        """

        # Base transaction fee
        base_fee_rate = 0.001  # 0.1%

        # Adjust fee based on network congestion
        congestion_multiplier = 1.0 + (self.market_conditions.network_congestion * 2.0)

        # Adjust fee based on market volatility (higher volatility = higher spreads)
        volatility_multiplier = 1.0 + (self.market_conditions.volatility_index * 0.5)

        # Calculate components
        transaction_fee = trade_amount * base_fee_rate * congestion_multiplier
        spread_cost = (
            trade_amount * 0.0005 * self.market_conditions.spread_factor
        )  # 0.05% base spread
        slippage_cost = (
            trade_amount * 0.0002 * volatility_multiplier
        )  # Slippage due to market impact

        return {
            "transaction_fee": transaction_fee,
            "spread_cost": spread_cost,
            "slippage_cost": slippage_cost,
            "total_cost": transaction_fee + spread_cost + slippage_cost,
            "effective_fee_rate": (transaction_fee + spread_cost + slippage_cost)
            / trade_amount,
        }

    def simulate_execution_risk(self, execution_plan: List[Dict]) -> Dict[str, float]:
        """
        Simulate execution risks for an arbitrage execution plan

        Args:
            execution_plan: List of trades to execute

        Returns:
            Risk assessment metrics
        """

        total_risk_score = 0.0
        execution_probability = 1.0

        for trade in execution_plan:
            # Risk factors
            market_risk = self.market_conditions.volatility_index * 0.3
            liquidity_risk = (2.0 - self.market_conditions.liquidity_factor) * 0.2
            execution_risk = self.market_conditions.network_congestion * 0.1

            trade_risk = market_risk + liquidity_risk + execution_risk
            total_risk_score += trade_risk

            # Probability that trade executes as planned
            trade_success_prob = 1.0 - trade_risk
            execution_probability *= trade_success_prob

        return {
            "total_risk_score": total_risk_score,
            "execution_probability": execution_probability,
            "average_trade_risk": (
                total_risk_score / len(execution_plan) if execution_plan else 0
            ),
            "risk_level": (
                "high"
                if total_risk_score > 0.6
                else "medium" if total_risk_score > 0.3 else "low"
            ),
        }
