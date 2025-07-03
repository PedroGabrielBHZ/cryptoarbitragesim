# Triangular Arbitrage Optimizer

A sophisticated cryptocurrency arbitrage optimization system using PuLP linear programming to maximize profits from triangular arbitrage opportunities while considering real-world constraints.

## 🎯 Overview

This system receives fake triangular arbitrage data from an external analyzer and creates a linear programming optimization model that accounts for:

- **Liquidity constraints** - Available trading volume on each exchange
- **Transaction fees** - Exchange fees for each trade
- **Minimum holding requirements** - Portfolio balance constraints  
- **Volume limitations** - Maximum position sizes
- **Risk management** - Portfolio risk tolerance

## 🏗️ System Architecture

### Core Components

1. **ArbitrageOptimizer** (`arbitrage_optimizer.py`)
   - Linear programming optimizer using PuLP
   - Handles portfolio constraints and risk management
   - Generates optimal investment allocation

2. **FakeArbitrageAnalyzer** (`arbitrage_detector.py`)
   - Simulates external arbitrage opportunity detection
   - Generates realistic triangular arbitrage data
   - Models market inefficiencies and opportunities

3. **CryptoMarketSimulator** (`market_simulator.py`)
   - Simulates real market conditions
   - Dynamic constraint adjustment based on market volatility
   - Execution risk assessment

4. **Main Application** (`main.py`)
   - Orchestrates the complete optimization workflow
   - Multi-period analysis capabilities
   - Performance reporting

## 📊 Key Features

### Linear Programming Optimization
- **Objective Function**: Maximize expected profit adjusted for confidence scores
- **Constraints**:
  - Liquidity limitations per trading pair
  - Portfolio balance constraints
  - Minimum holding requirements
  - Maximum position size limits
  - Risk tolerance constraints

### Triangular Arbitrage Modeling
- Three-currency arbitrage chains (e.g., USDT → BTC → ETH → USDT)
- Real-time profit calculation considering transaction fees
- Confidence scoring for opportunity reliability

### Risk Management
- Dynamic risk tolerance adjustment based on market volatility
- Execution probability assessment
- Multi-factor risk scoring

### Market Simulation
- Realistic market condition modeling
- Volatility impact on liquidity and spreads
- Network congestion effects on transaction costs

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

Required packages:
- `pulp` - Linear programming solver
- `numpy` - Numerical computations
- `pandas` - Data manipulation

### Basic Usage

```python
from main import ArbitrageSystem

# Initialize system with $100K portfolio
system = ArbitrageSystem(
    portfolio_value=100_000,
    risk_profile='moderate'
)

# Run optimization
results = system.run_optimization_cycle(num_opportunities=20)

# Generate report
system.print_results_summary(results)
```

### Running the Complete Demo

```bash
python main.py
```

This will:
1. Generate 20 arbitrage opportunities
2. Optimize investment allocation
3. Display comprehensive results
4. Simulate market updates
5. Run multi-period analysis

## 📈 Example Output

### Optimization Results
```
TRIANGULAR ARBITRAGE OPTIMIZATION SUMMARY
============================================================

ARBITRAGE OPPORTUNITIES ANALYZED: 15
  • Average Expected Profit: 0.3234%
  • Maximum Expected Profit: 0.6789%
  • Average Confidence Score: 82.4%

OPTIMIZATION RESULTS:
  • Status: Optimal
  • Total Investment: $25,432.18
  • Expected Profit: $156.78
  • Return on Investment: 0.6167%
  • Number of Opportunities Invested: 5

PORTFOLIO ANALYSIS:
  • Total Portfolio Value: $100,000.00
  • Risk Tolerance: 25.0%
  • Risk Utilization: 25.4%
  • Number of Currencies: 6
```

### Investment Allocation
```
TOP INVESTMENTS:
  1. opportunity_0:
     • Currencies: USDT → BTC → ETH
     • Investment: $8,543.21
     • Expected Profit: $58.234
     • Confidence: 89.2%
     
  2. opportunity_3:
     • Currencies: USDT → ADA → DOT  
     • Investment: $6,234.87
     • Expected Profit: $41.567
     • Confidence: 85.7%
```

## 🔧 Configuration Options

### Portfolio Settings
```python
# Conservative portfolio
system = ArbitrageSystem(
    portfolio_value=50_000,
    risk_profile='conservative'  # 5-15% risk tolerance
)

# Aggressive portfolio  
system = ArbitrageSystem(
    portfolio_value=500_000,
    risk_profile='aggressive'    # 35-60% risk tolerance
)
```

### Market Conditions
```python
# Access market simulator
market = system.market_simulator

# Current conditions
print(f"Volatility: {market.market_conditions.volatility_index:.3f}")
print(f"Sentiment: {market.market_conditions.market_sentiment}")
print(f"Liquidity Factor: {market.market_conditions.liquidity_factor:.3f}")
```

## 🧮 Mathematical Model

### Objective Function
```
Maximize: Σ(i=1 to n) profit_i × confidence_i × investment_i
```

### Constraints

1. **Liquidity Constraints**:
   ```
   Σ(consumption_factor_i × investment_i) ≤ available_liquidity_pair
   ```

2. **Balance Constraints**:
   ```
   Σ(investment_i) ≤ available_balance_currency
   ```

3. **Minimum Holdings**:
   ```
   current_balance + net_change ≥ minimum_holding
   ```

4. **Risk Constraint**:
   ```
   Σ(investment_i) ≤ total_portfolio × risk_tolerance
   ```

### Profit Calculation
```python
def calculate_triangular_profit(rate_ab, rate_bc, rate_ca, fees):
    effective_ab = rate_ab * (1 - fees[0])
    effective_bc = rate_bc * (1 - fees[1]) 
    effective_ca = rate_ca * (1 - fees[2])
    final_amount = effective_ab * effective_bc * effective_ca
    return final_amount - 1.0
```

## 📊 Visualization Features

The system provides text-based summaries and reports showing:

### 1. Opportunity Analysis
- Profit percentage and confidence scores
- Investment allocation summaries
- Risk assessment metrics

### 2. Portfolio Analysis  
- Investment allocation breakdown
- Constraint utilization analysis
- Risk exposure summary
- Currency composition details

### 3. Execution Planning
- Trade sequence details
- Fee analysis by trading pair
- Execution timeline information
- Risk assessment results

## 🔄 Multi-Period Analysis

The system supports dynamic multi-period optimization:

```python
# Run 5-period analysis
results = system.run_multi_period_analysis(num_periods=5)

# Analyze performance trends
for period, result in enumerate(results, 1):
    profit = result['solution']['expected_profit']
    investment = result['solution']['total_investment']
    print(f"Period {period}: {profit/investment*100:.4f}% ROI")
```

## ⚠️ Important Notes

### Simulation vs. Reality
- This system uses **simulated data** for demonstration
- Real implementation requires:
  - Live exchange API integration
  - Real-time order book data
  - Actual execution infrastructure
  - Latency optimization

### Risk Considerations
- Cryptocurrency markets are highly volatile
- Arbitrage opportunities can disappear quickly
- Transaction costs and slippage can eliminate profits
- Regulatory compliance may be required

### Performance Optimization
- Use faster solvers (CPLEX, Gurobi) for large problems
- Implement parallel processing for multiple opportunities
- Add real-time data caching
- Optimize constraint generation

## 🛠️ Extension Ideas

1. **Multi-Exchange Arbitrage**
   - Expand beyond triangular to include cross-exchange opportunities
   - Model withdrawal/deposit delays

2. **Real-Time Integration**
   - WebSocket feeds from major exchanges
   - Sub-second execution capabilities

3. **Advanced Risk Models**
   - VaR (Value at Risk) calculations
   - Correlation-based portfolio optimization
   - Dynamic hedging strategies

4. **Machine Learning Enhancement**
   - Opportunity prediction models
   - Execution success probability estimation
   - Market condition classification

## 📚 References

- [PuLP Documentation](https://coin-or.github.io/pulp/)
- [Cryptocurrency Arbitrage Research](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3066643)
- [Linear Programming in Finance](https://web.mit.edu/15.053/www/)

## 📄 License

This project is for educational and demonstration purposes. Use at your own risk for actual trading.

---

**Disclaimer**: This software is for educational purposes only. Cryptocurrency trading involves substantial risk of loss. The authors are not responsible for any financial losses incurred through the use of this software.
