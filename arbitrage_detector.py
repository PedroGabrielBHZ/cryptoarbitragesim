"""
Fake Arbitrage Data Generator

This module generates realistic fake triangular arbitrage opportunities
for testing and demonstration purposes.
"""

import random
import numpy as np
from typing import List, Dict
from arbitrage_optimizer import (
    ArbitrageOpportunity,
    calculate_triangular_arbitrage_profit,
)


class FakeArbitrageAnalyzer:
    """
    Simulates an external arbitrage analyzer that provides triangular arbitrage opportunities
    """

    def __init__(self, seed: int = None):
        """
        Initialize the fake analyzer

        Args:
            seed: Random seed for reproducible results (None for random seed)
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Common crypto trading pairs
        self.currencies = ["BTC", "ETH", "USDT", "ADA", "DOT", "LINK", "XRP", "LTC"]
        self.stable_coins = ["USDT", "USDC", "DAI"]

        # Base exchange rates (simplified for demonstration)
        self.base_rates = {
            "BTC/USDT": 45000 + random.uniform(-5000, 5000),
            "ETH/USDT": 3000 + random.uniform(-500, 500),
            "ADA/USDT": 1.2 + random.uniform(-0.3, 0.3),
            "DOT/USDT": 25 + random.uniform(-5, 5),
            "LINK/USDT": 15 + random.uniform(-3, 3),
            "XRP/USDT": 0.6 + random.uniform(-0.2, 0.2),
            "LTC/USDT": 150 + random.uniform(-30, 30),
            "ETH/BTC": 0.067 + random.uniform(-0.01, 0.01),
            "ADA/BTC": 0.000027 + random.uniform(-0.000005, 0.000005),
            "DOT/BTC": 0.00056 + random.uniform(-0.0001, 0.0001),
        }

    def generate_exchange_rates(
        self, base: str, intermediate: str, quote: str
    ) -> Dict[str, float]:
        """
        Generate exchange rates for a triangular arbitrage opportunity

        Args:
            base: Base currency (e.g., 'USDT')
            intermediate: Intermediate currency (e.g., 'BTC')
            quote: Quote currency (e.g., 'ETH')

        Returns:
            Dictionary of exchange rates with small arbitrage opportunities
        """
        rates = {}

        # Get base rates with some random variation
        rate_variation = 0.002  # 0.2% variation

        # Direct rates
        pair1 = f"{intermediate}/{base}"
        pair2 = f"{quote}/{intermediate}"
        pair3 = f"{quote}/{base}"

        # Generate rates based on base rates with variations
        if pair1 in self.base_rates:
            rates[pair1] = self.base_rates[pair1] * (
                1 + random.uniform(-rate_variation, rate_variation)
            )
        else:
            rates[pair1] = self._generate_synthetic_rate(intermediate, base)

        if pair2 in self.base_rates:
            rates[pair2] = self.base_rates[pair2] * (
                1 + random.uniform(-rate_variation, rate_variation)
            )
        else:
            rates[pair2] = self._generate_synthetic_rate(quote, intermediate)

        # For arbitrage to work: rate1 * rate2 > rate3 (after fees)
        # So we set rate3 to be slightly less than the product
        theoretical_rate3 = rates[pair1] * rates[pair2]

        # Create arbitrage opportunity by making rate3 less than theoretical
        arbitrage_margin = random.uniform(
            0.008, 0.025
        )  # 0.8% to 2.5% arbitrage opportunity
        rates[pair3] = theoretical_rate3 * (
            1 - arbitrage_margin
        )  # Make rate3 LESS to create profit

        return rates

    def _generate_synthetic_rate(self, currency1: str, currency2: str) -> float:
        """Generate a synthetic exchange rate between two currencies"""
        # Simple synthetic rate generation based on market caps (simplified)
        market_caps = {
            "BTC": 800_000_000_000,
            "ETH": 360_000_000_000,
            "USDT": 80_000_000_000,
            "ADA": 35_000_000_000,
            "DOT": 30_000_000_000,
            "LINK": 15_000_000_000,
            "XRP": 40_000_000_000,
            "LTC": 12_000_000_000,
        }

        ratio = market_caps.get(currency1, 1_000_000_000) / market_caps.get(
            currency2, 1_000_000_000
        )
        return ratio * random.uniform(0.8, 1.2)

    def generate_liquidity_data(
        self, base: str, intermediate: str, quote: str
    ) -> Dict[str, float]:
        """
        Generate realistic liquidity data for trading pairs

        Returns:
            Dictionary of liquidity amounts in base currency equivalent
        """
        # Base liquidity amounts (in USD equivalent)
        base_liquidity = {
            "BTC": random.uniform(1_000_000, 10_000_000),  # $1M-$10M
            "ETH": random.uniform(500_000, 5_000_000),  # $500K-$5M
            "USDT": random.uniform(2_000_000, 20_000_000),  # $2M-$20M
            "ADA": random.uniform(100_000, 1_000_000),  # $100K-$1M
            "DOT": random.uniform(150_000, 1_500_000),  # $150K-$1.5M
            "LINK": random.uniform(100_000, 1_000_000),  # $100K-$1M
            "XRP": random.uniform(200_000, 2_000_000),  # $200K-$2M
            "LTC": random.uniform(80_000, 800_000),  # $80K-$800K
        }

        # Convert to base currency units
        liquidity = {}
        pairs = [f"{intermediate}/{base}", f"{quote}/{intermediate}", f"{quote}/{base}"]

        for pair in pairs:
            currency = pair.split("/")[0]
            # Liquidity varies by trading pair popularity
            liquidity_factor = random.uniform(0.5, 1.5)
            liquidity[pair] = base_liquidity.get(currency, 100_000) * liquidity_factor

        return liquidity

    def generate_transaction_fees(self) -> Dict[str, float]:
        """
        Generate realistic transaction fees for different exchanges

        Returns:
            Dictionary of transaction fees (as decimals, e.g., 0.001 = 0.1%)
        """
        # Different exchanges have different fee structures
        fee_tiers = {
            "tier1": random.uniform(0.0005, 0.001),  # 0.05%-0.1% (premium exchanges)
            "tier2": random.uniform(0.001, 0.002),  # 0.1%-0.2% (standard exchanges)
            "tier3": random.uniform(0.002, 0.004),  # 0.2%-0.4% (higher fee exchanges)
        }

        # Randomly assign fee tiers to different pairs
        selected_tier = random.choice(list(fee_tiers.keys()))
        base_fee = fee_tiers[selected_tier]

        # Add some variation
        fees = {}
        for i in range(3):  # For three trading pairs in triangular arbitrage
            fees[f"pair_{i}"] = base_fee * random.uniform(0.8, 1.2)

        return fees

    def generate_arbitrage_opportunities(
        self, num_opportunities: int = 10
    ) -> List[ArbitrageOpportunity]:
        """
        Generate a list of fake triangular arbitrage opportunities

        Args:
            num_opportunities: Number of opportunities to generate

        Returns:
            List of ArbitrageOpportunity objects
        """
        opportunities = []

        for _ in range(num_opportunities):
            # Randomly select three currencies for triangular arbitrage
            base = random.choice(self.stable_coins)  # Usually start with stablecoin
            available_currencies = [c for c in self.currencies if c != base]
            intermediate = random.choice(available_currencies)
            quote_candidates = [c for c in available_currencies if c != intermediate]
            quote = random.choice(quote_candidates)

            # Generate exchange rates
            exchange_rates = self.generate_exchange_rates(base, intermediate, quote)

            # Generate liquidity data
            liquidity = self.generate_liquidity_data(base, intermediate, quote)

            # Generate transaction fees
            transaction_fees = {
                f"{intermediate}/{base}": random.uniform(0.0008, 0.002),  # 0.08%-0.2%
                f"{quote}/{intermediate}": random.uniform(0.0008, 0.002),
                f"{quote}/{base}": random.uniform(0.0008, 0.002),
            }

            # Calculate expected profit
            rate_ab = exchange_rates[f"{intermediate}/{base}"]
            rate_bc = exchange_rates[f"{quote}/{intermediate}"]
            rate_ca = 1.0 / exchange_rates[f"{quote}/{base}"]  # Inverse rate

            fees_tuple = (
                transaction_fees[f"{intermediate}/{base}"],
                transaction_fees[f"{quote}/{intermediate}"],
                transaction_fees[f"{quote}/{base}"],
            )

            expected_profit = calculate_triangular_arbitrage_profit(
                rate_ab, rate_bc, rate_ca, fees_tuple
            )

            # Only include profitable opportunities
            if expected_profit > 0:
                # Generate confidence score based on market conditions
                confidence_score = random.uniform(0.7, 0.95)

                opportunity = ArbitrageOpportunity(
                    base_currency=base,
                    intermediate_currency=intermediate,
                    quote_currency=quote,
                    exchange_rates=exchange_rates,
                    liquidity=liquidity,
                    transaction_fees=transaction_fees,
                    expected_profit=expected_profit,
                    confidence_score=confidence_score,
                )

                opportunities.append(opportunity)

        # Sort by expected profit (descending)
        opportunities.sort(
            key=lambda x: x.expected_profit * x.confidence_score, reverse=True
        )

        return opportunities

    def simulate_market_update(
        self, opportunities: List[ArbitrageOpportunity]
    ) -> List[ArbitrageOpportunity]:
        """
        Simulate market changes that affect existing arbitrage opportunities

        Args:
            opportunities: Existing arbitrage opportunities

        Returns:
            Updated list of opportunities
        """
        updated_opportunities = []

        for opp in opportunities:
            # Simulate market volatility
            volatility = random.uniform(0.995, 1.005)  # ±0.5% change

            # Update exchange rates
            updated_rates = {}
            for pair, rate in opp.exchange_rates.items():
                updated_rates[pair] = rate * volatility * random.uniform(0.998, 1.002)

            # Update liquidity (can increase or decrease)
            updated_liquidity = {}
            for pair, liq in opp.liquidity.items():
                liquidity_change = random.uniform(0.9, 1.1)  # ±10% change
                updated_liquidity[pair] = liq * liquidity_change

            # Recalculate profit with updated rates
            rate_ab = updated_rates[f"{opp.intermediate_currency}/{opp.base_currency}"]
            rate_bc = updated_rates[f"{opp.quote_currency}/{opp.intermediate_currency}"]
            rate_ca = 1.0 / updated_rates[f"{opp.quote_currency}/{opp.base_currency}"]

            fees_tuple = (
                opp.transaction_fees[
                    f"{opp.intermediate_currency}/{opp.base_currency}"
                ],
                opp.transaction_fees[
                    f"{opp.quote_currency}/{opp.intermediate_currency}"
                ],
                opp.transaction_fees[f"{opp.quote_currency}/{opp.base_currency}"],
            )

            updated_profit = calculate_triangular_arbitrage_profit(
                rate_ab, rate_bc, rate_ca, fees_tuple
            )

            # Only keep profitable opportunities
            if updated_profit > 0:
                updated_opp = ArbitrageOpportunity(
                    base_currency=opp.base_currency,
                    intermediate_currency=opp.intermediate_currency,
                    quote_currency=opp.quote_currency,
                    exchange_rates=updated_rates,
                    liquidity=updated_liquidity,
                    transaction_fees=opp.transaction_fees,
                    expected_profit=updated_profit,
                    confidence_score=opp.confidence_score * random.uniform(0.95, 1.05),
                )
                updated_opportunities.append(updated_opp)

        return updated_opportunities
