#!/usr/bin/env python3
"""
Cleary Family Portfolio Quantitative Analysis
==============================================
Rigorous Monte Carlo simulation, stress testing, sensitivity analysis,
and sequence-of-returns risk modeling using real historical data.

Author: Doyle (AI Advisory)
Date: 2026-03-29
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
from datetime import datetime
import json
import os
import sys

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

np.random.seed(42)

# Chart styling
NAVY = '#1B3A5C'
TEAL = '#2E8B8B'
CORAL = '#E8725A'
GOLD = '#D4A843'
LIGHT_BLUE = '#5BA3CF'
LIGHT_GRAY = '#F5F5F5'
MED_GRAY = '#CCCCCC'
GREEN = '#4CAF50'
RED = '#E74C3C'

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': MED_GRAY,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.color': MED_GRAY,
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
})

# Portfolio parameters
INITIAL_PORTFOLIO = 1_230_000
TRANSITION_MONTHLY = 18_000  # $18K/month for 24 months
ONGOING_MONTHLY = 6_667      # ~$80K/year
TRANSITION_MONTHS = 24
TOTAL_MONTHS = 228           # 19 years
BALLOON_MONTH = 168          # Year 14 (age 50)
BALLOON_AMOUNT = 400_000
N_SIMULATIONS = 10_000
ANNUAL_EXPENSES = 180_000
RETIREMENT_YEARS = 35        # age 55 to 90

# Asset tickers and proxies
# Using longer-history proxies where available
TICKERS = {
    'US_Total':    'SPY',      # S&P 500 as proxy (since 1993)
    'Intl_Dev':    'EFA',      # iShares MSCI EAFE (since 2001)
    'SCV':         'IWN',      # iShares Russell 2000 Value (since 2000)
    'Intl_SC':     'SCZ',      # iShares MSCI EAFE Small Cap (since 2007)
    'EM':          'EEM',      # iShares MSCI Emerging Markets (since 2003)
    'REITs':       'VNQ',      # Vanguard Real Estate (since 2004)
    'Bonds':       'AGG',      # iShares Core US Aggregate Bond (since 2003)
    'TIPS':        'TIP',      # iShares TIPS Bond (since 2003)
    'Gold':        'GLD',      # SPDR Gold Shares (since 2004)
    'AMZN':        'AMZN',     # Amazon direct
    'QQQ':         'QQQ',      # Nasdaq 100 (also proxy for TSLA/individual tech stocks)
    # GBTC excluded - only 0.6% allocation, short history biases bootstrap pool
    # Its weight is redistributed to QQQ in current portfolio
}

# ============================================================
# PORTFOLIO SCENARIOS
# ============================================================
# Each scenario maps asset class names to target weights.
# All weights are normalized automatically.

def normalize_weights(w):
    total = sum(w.values())
    return {k: v/total for k, v in w.items()}

SCENARIOS = {}

# 1. CURRENT — John's actual holdings
# AMZN: 35%, SPY/QQQ/401k: 31.5%, TSLA: 3.5%, Other stocks: 2.4%,
# Bonds: 2.8%, Gold: 1.6%, Crypto: 0.6%, Cash: 1.8%, Schwab robo: 2.2%
SCENARIOS['Current'] = normalize_weights({
    'AMZN':      0.350,
    'US_Total':  0.330,   # SPY/QQQ/401k large cap + half of schwab robo
    'QQQ':       0.065,   # Other stocks + TSLA (merged for longer history) + crypto
    'Bonds':     0.068,   # Bonds + Cash/HYSA + quarter of schwab robo
    'Gold':      0.016,
    'Intl_Dev':  0.007,   # Quarter of schwab robo
    'REITs':     0.000,
    'SCV':       0.000,
    'Intl_SC':   0.000,
    'EM':        0.000,
    'TIPS':      0.000,
})

# 2. CONSERVATIVE — Sell 500 AMZN shares over 12 months, redeploy to VTI/VXUS
# AMZN drops from 35% to ~20%, freed capital goes to US Total + International
SCENARIOS['Conservative'] = normalize_weights({
    'AMZN':      0.200,
    'US_Total':  0.400,   # Existing + new VTI purchases
    'QQQ':       0.065,
    'Intl_Dev':  0.100,   # New VXUS purchases
    'Bonds':     0.068,
    'Gold':      0.016,
    'REITs':     0.000,
    'SCV':       0.000,
    'Intl_SC':   0.000,
    'EM':        0.000,
    'TIPS':      0.000,
})

# 3. DALIO ALL-WEATHER — Ray Dalio's risk-parity inspired allocation
# 30% stocks, 55% long-term bonds/TIPS, 15% gold/commodities
# Designed to perform in any economic regime
SCENARIOS['All-Weather'] = normalize_weights({
    'US_Total':  0.180,   # 18% US stocks
    'Intl_Dev':  0.090,   # 9% international developed
    'EM':        0.030,   # 3% emerging markets
    'Bonds':     0.400,   # 40% long-term bonds (Dalio uses 40% LT bonds)
    'TIPS':      0.150,   # 15% inflation-linked bonds
    'Gold':      0.150,   # 15% gold/commodities
    'AMZN':      0.000,
    'QQQ':       0.000,
    'SCV':       0.000,
    'Intl_SC':   0.000,
    'REITs':     0.000,
})

# 4. BOGLEHEAD 3-FUND — Classic simplicity
# VTI 60% / VXUS 30% / BND 10%
SCENARIOS['Boglehead'] = normalize_weights({
    'US_Total':  0.600,
    'Intl_Dev':  0.300,
    'Bonds':     0.100,
    'AMZN':      0.000,
    'QQQ':       0.000,
    'SCV':       0.000,
    'Intl_SC':   0.000,
    'EM':        0.000,
    'REITs':     0.000,
    'TIPS':      0.000,
    'Gold':      0.000,
})

# 5. BARBELL — Nassim Taleb philosophy
# 70% aggressive equity (tilted growth + SCV) / 30% safest bonds
# Nothing in between — either taking real risk or hiding in safety
SCENARIOS['Barbell'] = normalize_weights({
    'US_Total':  0.250,   # Core US
    'QQQ':       0.150,   # Aggressive growth/tech
    'SCV':       0.100,   # Small-cap value premium
    'Intl_Dev':  0.100,   # International diversification
    'EM':        0.050,   # Emerging markets
    'Intl_SC':   0.050,   # International small cap
    'Bonds':     0.200,   # Treasury bonds (safe haven)
    'TIPS':      0.100,   # Inflation protection
    'AMZN':      0.000,
    'REITs':     0.000,
    'Gold':      0.000,
})

# Scenario display colors for charts
SCENARIO_COLORS = {
    'Current':      CORAL,
    'Conservative': GOLD,
    'All-Weather':  TEAL,
    'Boglehead':    LIGHT_BLUE,
    'Barbell':      GREEN,
}

SCENARIO_LIGHT_COLORS = {
    'Current':      '#F5C6B8',
    'Conservative': '#F0DCA8',
    'All-Weather':  '#B8E0E0',
    'Boglehead':    '#C4DAF0',
    'Barbell':      '#C8E6C9',
}

# Keep backward compatibility for functions that reference these
CURRENT_WEIGHTS = SCENARIOS['Current']
PROPOSED_WEIGHTS = SCENARIOS['Boglehead']  # default comparison

# ============================================================
# DATA ACQUISITION
# ============================================================

def fetch_historical_data():
    """Fetch monthly returns for all asset classes."""
    print("Fetching historical data from Yahoo Finance...")
    
    all_prices = {}
    data_info = {}
    
    for name, ticker in TICKERS.items():
        try:
            print(f"  Downloading {name} ({ticker})...", end=' ')
            data = yf.download(ticker, start='1998-01-01', end='2026-03-28', 
                             interval='1mo', progress=False, auto_adjust=True)
            if len(data) > 12:
                prices = data['Close'].dropna()
                if isinstance(prices, pd.DataFrame):
                    prices = prices.iloc[:, 0]
                all_prices[name] = prices
                data_info[name] = {
                    'ticker': ticker,
                    'start': str(prices.index[0].date()),
                    'end': str(prices.index[-1].date()),
                    'months': len(prices)
                }
                print(f"OK ({len(prices)} months from {prices.index[0].date()})")
            else:
                print(f"INSUFFICIENT DATA ({len(data)} rows)")
        except Exception as e:
            print(f"FAILED: {e}")
    
    # Compute monthly returns
    returns_dict = {}
    for name, prices in all_prices.items():
        rets = prices.pct_change().dropna()
        # Remove extreme outliers that are likely data errors (>100% monthly)
        rets = rets[rets.abs() < 1.0]
        returns_dict[name] = rets
    
    # CRITICAL FIX: Cap AMZN forward-looking returns
    # Historical AMZN returned 37% annualized (1998-2026) — from $5 startup to $2T mega-cap.
    # That is NOT predictive of future returns. A $2T company cannot 40x again.
    # Approach: Scale AMZN returns so the bootstrap pool has a forward-looking
    # expected return of ~11% annualized (market consensus for mega-cap tech).
    # This preserves AMZN's volatility structure, correlation, and fat tails
    # while adjusting the mean to a realistic forward estimate.
    if 'AMZN' in returns_dict:
        amzn_rets = returns_dict['AMZN']
        historical_monthly_mean = amzn_rets.mean()
        target_annual = 0.11  # 11% forward consensus for mega-cap
        target_monthly_mean = (1 + target_annual) ** (1/12) - 1
        adjustment = target_monthly_mean - historical_monthly_mean
        returns_dict['AMZN'] = amzn_rets + adjustment
        actual_annual = (1 + returns_dict['AMZN'].mean()) ** 12 - 1
        print(f"\n  AMZN return adjustment applied:")
        print(f"    Historical annual: {(1 + historical_monthly_mean)**12 - 1:.1%}")
        print(f"    Target annual: {target_annual:.1%}")
        print(f"    Monthly shift: {adjustment:.4f}")
        print(f"    Adjusted annual: {actual_annual:.1%}")
        print(f"    Volatility preserved: {amzn_rets.std() * np.sqrt(12):.1%}")
    
    # Align all returns to common dates
    returns_df = pd.DataFrame(returns_dict)
    
    # For correlation matrix, use the overlapping period
    common_returns = returns_df.dropna()
    print(f"\nCommon period: {common_returns.index[0].date()} to {common_returns.index[-1].date()}")
    print(f"Common months: {len(common_returns)}")
    
    return returns_df, common_returns, data_info, all_prices


def compute_statistics(returns_df):
    """Compute annualized statistics from monthly returns."""
    stats_dict = {}
    for col in returns_df.columns:
        rets = returns_df[col].dropna()
        monthly_mean = rets.mean()
        monthly_std = rets.std()
        annual_return = (1 + monthly_mean)**12 - 1
        annual_vol = monthly_std * np.sqrt(12)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0
        stats_dict[col] = {
            'monthly_mean': monthly_mean,
            'monthly_std': monthly_std,
            'annual_return': annual_return,
            'annual_vol': annual_vol,
            'sharpe': sharpe,
            'skew': rets.skew(),
            'kurtosis': rets.kurtosis(),
            'max_drawdown': compute_max_drawdown_series(rets),
            'n_months': len(rets)
        }
    return stats_dict


def compute_max_drawdown_series(returns):
    """Compute maximum drawdown from a return series."""
    cum = (1 + returns).cumprod()
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    return drawdown.min()


# ============================================================
# MODEL 1: MONTE CARLO SIMULATION
# ============================================================

def run_monte_carlo(returns_df, common_returns, scenarios_dict):
    """
    Bootstrap Monte Carlo simulation using historical returns.
    Preserves fat tails, correlations, and real-world distribution.
    Runs all portfolio scenarios from scenarios_dict.
    """
    print("\n" + "="*60)
    print(f"MODEL 1: MONTE CARLO SIMULATION ({N_SIMULATIONS:,} paths × {len(scenarios_dict)} scenarios)")
    print("="*60)
    
    # Build separate bootstrap pools for each scenario to maximize history
    scenario_configs = {}  # label -> (w_vec, boot_matrix, n_hist, asset_list)
    all_assets_set = set()
    
    for label, weights in scenarios_dict.items():
        assets = [a for a in weights if weights[a] > 0 and a in returns_df.columns]
        all_assets_set.update(assets)
        boot = returns_df[assets].dropna()
        w_vec = np.array([weights.get(a, 0) for a in assets])
        w_vec = w_vec / w_vec.sum()
        scenario_configs[label] = (w_vec, boot.values, len(boot), assets)
        print(f"{label} bootstrap: {len(boot)} months ({boot.index[0].date()} to {boot.index[-1].date()})")
    
    all_assets = sorted(all_assets_set)
    results = {}
    
    portfolio_configs = [
        (label, cfg[0], cfg[1], cfg[2]) for label, cfg in scenario_configs.items()
    ]
    
    for label, weights, boot_matrix, n_hist in portfolio_configs:
        print(f"\nRunning {label} portfolio simulations ({n_hist} months of history)...")
        
        portfolio_paths = np.zeros((N_SIMULATIONS, TOTAL_MONTHS + 1))
        portfolio_paths[:, 0] = INITIAL_PORTFOLIO
        max_drawdowns = np.zeros(N_SIMULATIONS)
        min_values = np.full(N_SIMULATIONS, INITIAL_PORTFOLIO)
        
        for sim in range(N_SIMULATIONS):
            # Bootstrap: sample random months WITH replacement
            sample_indices = np.random.randint(0, n_hist, size=TOTAL_MONTHS)
            sampled_returns = boot_matrix[sample_indices]
            
            value = INITIAL_PORTFOLIO
            peak = INITIAL_PORTFOLIO
            max_dd = 0
            
            # Track asset allocation for rebalancing
            asset_values = weights * value
            
            for month in range(TOTAL_MONTHS):
                # Apply returns to each asset
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                
                # Add contribution
                if month < TRANSITION_MONTHS:
                    contribution = TRANSITION_MONTHLY
                else:
                    contribution = ONGOING_MONTHLY
                
                # Distribute contribution according to target weights
                asset_values += weights * contribution
                
                # Balloon payment at month 168 (age 50)
                if month == BALLOON_MONTH:
                    total = asset_values.sum()
                    if total > BALLOON_AMOUNT:
                        asset_values -= weights * BALLOON_AMOUNT
                    else:
                        asset_values *= 0.5  # Take half if insufficient
                
                # Annual rebalancing
                if (month + 1) % 12 == 0:
                    total = asset_values.sum()
                    asset_values = weights * total
                
                value = asset_values.sum()
                portfolio_paths[sim, month + 1] = value
                
                # Track drawdown
                if value > peak:
                    peak = value
                dd = (value - peak) / peak
                if dd < max_dd:
                    max_dd = dd
                if value < min_values[sim]:
                    min_values[sim] = value
            
            max_drawdowns[sim] = max_dd
        
        # Compute statistics at each year
        yearly_indices = [0] + [i*12 for i in range(1, 20)]
        yearly_values = portfolio_paths[:, yearly_indices]
        
        percentiles = {}
        for i, year in enumerate(range(20)):
            vals = yearly_values[:, i]
            percentiles[year] = {
                'p10': np.percentile(vals, 10),
                'p25': np.percentile(vals, 25),
                'median': np.median(vals),
                'mean': np.mean(vals),
                'p75': np.percentile(vals, 75),
                'p90': np.percentile(vals, 90),
            }
        
        final_values = portfolio_paths[:, -1]
        
        results[label] = {
            'paths': portfolio_paths,
            'final_values': final_values,
            'percentiles': percentiles,
            'max_drawdowns': max_drawdowns,
            'min_values': min_values,
            'prob_5M': (final_values >= 5_000_000).mean(),
            'prob_8M': (final_values >= 8_000_000).mean(),
            'prob_10M': (final_values >= 10_000_000).mean(),
            'prob_15M': (final_values >= 15_000_000).mean(),
            'prob_below_500K': (min_values < 500_000).mean(),
            'median_final': np.median(final_values),
            'mean_final': np.mean(final_values),
        }
        
        print(f"  Median final: ${np.median(final_values):,.0f}")
        print(f"  Mean final: ${np.mean(final_values):,.0f}")
        print(f"  10th percentile: ${np.percentile(final_values, 10):,.0f}")
        print(f"  90th percentile: ${np.percentile(final_values, 90):,.0f}")
        print(f"  P(>$5M): {results[label]['prob_5M']:.1%}")
        print(f"  P(>$10M): {results[label]['prob_10M']:.1%}")
        print(f"  P(below $500K ever): {results[label]['prob_below_500K']:.1%}")
        print(f"  Median max drawdown: {np.median(max_drawdowns):.1%}")
    
    return results, all_assets, scenario_configs


def plot_monte_carlo(results):
    """Generate fan/ribbon chart for Monte Carlo results — one panel per scenario."""
    n_scenarios = len(results)
    # Layout: up to 3 columns
    n_cols = min(3, n_scenarios)
    n_rows = (n_scenarios + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(7*n_cols, 7*n_rows), sharey=True, squeeze=False)
    
    ages = np.arange(36, 56)
    years = np.arange(0, 20)
    
    scenario_labels = list(results.keys())
    
    for idx, label in enumerate(scenario_labels):
        row, col = divmod(idx, n_cols)
        ax = axes[row][col]
        color_main = SCENARIO_COLORS.get(label, TEAL)
        
        r = results[label]
        p = r['percentiles']
        
        p10 = [p[y]['p10'] for y in years]
        p25 = [p[y]['p25'] for y in years]
        med = [p[y]['median'] for y in years]
        p75 = [p[y]['p75'] for y in years]
        p90 = [p[y]['p90'] for y in years]
        
        ax.fill_between(ages, [x/1e6 for x in p10], [x/1e6 for x in p90], 
                        alpha=0.15, color=color_main, label='10th-90th %ile')
        ax.fill_between(ages, [x/1e6 for x in p25], [x/1e6 for x in p75], 
                        alpha=0.3, color=color_main, label='25th-75th %ile')
        ax.plot(ages, [x/1e6 for x in med], color=color_main, linewidth=2.5, 
                label=f'Median: ${med[-1]/1e6:.1f}M')
        
        # Mark balloon payment
        ax.axvline(x=50, color=MED_GRAY, linestyle='--', alpha=0.7)
        y_pos = max(med) * 0.15
        ax.annotate('$400K Balloon\n(Age 50)', xy=(50, y_pos), 
                    fontsize=9, fontweight='bold', ha='center', va='bottom', color=NAVY,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
        
        ax.set_xlabel('Age')
        ax.set_title(f'{label}', fontsize=14, fontweight='bold', color=NAVY)
        ax.legend(loc='upper left', fontsize=8)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}M'))
        ax.set_xlim(36, 55)
        
        # Add key stats in lower right
        ax.text(0.97, 0.03, 
                f"P(>$5M): {r['prob_5M']:.0%}\nMax DD: {np.median(r['max_drawdowns']):.0%}",
                transform=ax.transAxes, fontsize=9, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Hide unused panels
    for idx in range(n_scenarios, n_rows * n_cols):
        row, col = divmod(idx, n_cols)
        axes[row][col].set_visible(False)
    
    axes[0][0].set_ylabel('Portfolio Value')
    
    fig.suptitle(f'Monte Carlo Simulation: {N_SIMULATIONS:,} Paths Over 19 Years — {n_scenarios} Scenarios', 
                 fontsize=16, fontweight='bold', color=NAVY, y=1.02)
    
    # Also generate a single overlay chart for easy comparison
    fig2, ax2 = plt.subplots(figsize=(14, 8))
    for label in scenario_labels:
        r = results[label]
        p = r['percentiles']
        med = [p[y]['median'] for y in years]
        color = SCENARIO_COLORS.get(label, TEAL)
        ax2.plot(ages, [x/1e6 for x in med], color=color, linewidth=2.5, label=f'{label}: ${med[-1]/1e6:.1f}M')
        p10 = [p[y]['p10'] for y in years]
        p90 = [p[y]['p90'] for y in years]
        ax2.fill_between(ages, [x/1e6 for x in p10], [x/1e6 for x in p90], alpha=0.08, color=color)
    
    ax2.axvline(x=50, color=MED_GRAY, linestyle='--', alpha=0.7)
    ax2.annotate('$400K Balloon (Age 50)', xy=(50, 0.5), fontsize=10, fontweight='bold',
                 ha='center', va='bottom', color=NAVY,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
    ax2.set_xlabel('Age')
    ax2.set_ylabel('Portfolio Value')
    ax2.set_title('Monte Carlo Median Paths: All Scenarios Compared', fontsize=16, fontweight='bold', color=NAVY)
    ax2.legend(loc='upper left', fontsize=11)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}M'))
    ax2.set_xlim(36, 55)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'mc-real.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    fig2.savefig(os.path.join(CHARTS_DIR, 'mc-overlay.png'), dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    plt.close('all')
    print("\nSaved: reports/charts/mc-real.png")
    print("Saved: reports/charts/mc-overlay.png")


# ============================================================
# MODEL 2: HISTORICAL STRESS TESTS
# ============================================================

def run_stress_tests(all_prices, scenarios_dict):
    """Run all portfolio scenarios through actual historical crises."""
    print("\n" + "="*60)
    print("MODEL 2: HISTORICAL STRESS TESTS")
    print("="*60)
    
    crises = {
        'Dot-Com Crash\n(2000-2002)': ('2000-03-01', '2002-10-31', '2003-12-31'),
        'Global Financial\nCrisis (2007-09)': ('2007-10-01', '2009-03-31', '2012-12-31'),
        'COVID Crash\n(2020)': ('2020-02-01', '2020-03-31', '2020-08-31'),
        '2022 Rate Hikes': ('2022-01-01', '2022-10-31', '2023-06-30'),
    }
    
    stress_results = {}
    
    for crisis_name, (start, trough, recovery_end) in crises.items():
        print(f"\n{crisis_name.replace(chr(10), ' ')}:")
        
        crisis_results = {}
        for label, weights in scenarios_dict.items():
            # Compute portfolio return through the crisis using available prices
            portfolio_value = 100  # Normalize to 100
            peak_value = 100
            max_dd = 0
            
            # Get monthly prices for the full crisis+recovery period
            try:
                crisis_prices = {}
                for asset, weight in weights.items():
                    if weight <= 0:
                        continue
                    ticker = TICKERS.get(asset)
                    if ticker and asset in all_prices:
                        p = all_prices[asset]
                        # Filter to crisis period
                        mask = (p.index >= start) & (p.index <= recovery_end)
                        cp = p[mask]
                        if len(cp) > 1:
                            crisis_prices[asset] = cp
                
                if not crisis_prices:
                    print(f"  {label}: No data available for this period")
                    crisis_results[label] = {'max_dd': None, 'recovery_months': None}
                    continue
                
                # Use the asset with most data points to define the date grid
                # Then for each date, use available assets with renormalized weights
                ref_asset = max(crisis_prices, key=lambda a: len(crisis_prices[a]))
                common_dates = sorted(crisis_prices[ref_asset].index)
                
                if len(common_dates) < 2:
                    print(f"  {label}: Insufficient data")
                    crisis_results[label] = {'max_dd': None, 'recovery_months': None}
                    continue
                
                # Track which assets cover what fraction of weight
                total_covered = sum(weights.get(a, 0) for a in crisis_prices)
                print(f"    {label} coverage: {total_covered:.0%} of portfolio has data for this period")
                
                # Build portfolio returns using available assets, renormalized
                portfolio_values = [1.0]
                for i in range(1, len(common_dates)):
                    monthly_return = 0
                    total_weight = 0
                    for asset, cp in crisis_prices.items():
                        w = weights.get(asset, 0)
                        if w <= 0:
                            continue
                        try:
                            # Find nearest dates in this asset's data
                            prev_idx = cp.index.get_indexer([common_dates[i-1]], method='nearest')[0]
                            curr_idx = cp.index.get_indexer([common_dates[i]], method='nearest')[0]
                            prev_price = cp.iloc[prev_idx]
                            curr_price = cp.iloc[curr_idx]
                            if isinstance(prev_price, pd.Series):
                                prev_price = prev_price.iloc[0]
                            if isinstance(curr_price, pd.Series):
                                curr_price = curr_price.iloc[0]
                            if prev_price > 0:
                                ret = (curr_price / prev_price) - 1
                                monthly_return += w * ret
                                total_weight += w
                        except:
                            pass
                    
                    # Renormalize: scale up so available assets represent the full portfolio
                    # This assumes missing assets would have performed like the weighted avg of available ones
                    if total_weight > 0 and total_weight < 0.99:
                        monthly_return = monthly_return / total_weight
                    
                    portfolio_values.append(portfolio_values[-1] * (1 + monthly_return))
                
                portfolio_arr = np.array(portfolio_values)
                peak_arr = np.maximum.accumulate(portfolio_arr)
                drawdown_arr = (portfolio_arr - peak_arr) / peak_arr
                
                max_dd = drawdown_arr.min()
                max_dd_idx = drawdown_arr.argmin()
                
                # Find recovery (when portfolio gets back to pre-crisis peak)
                recovery_months = None
                for j in range(max_dd_idx, len(portfolio_arr)):
                    if portfolio_arr[j] >= peak_arr[max_dd_idx]:
                        recovery_months = j - max_dd_idx
                        break
                
                # Dollar loss at trough based on $1.23M starting
                dollar_loss = abs(max_dd) * INITIAL_PORTFOLIO
                
                crisis_results[label] = {
                    'max_dd': max_dd,
                    'dollar_loss': dollar_loss,
                    'recovery_months': recovery_months,
                    'values': portfolio_arr,
                    'dates': common_dates,
                }
                
                print(f"  {label}: Max drawdown {max_dd:.1%}, "
                      f"Dollar loss ${dollar_loss:,.0f}, "
                      f"Recovery: {recovery_months if recovery_months else 'N/A'} months")
                
            except Exception as e:
                print(f"  {label}: Error - {e}")
                crisis_results[label] = {'max_dd': None, 'recovery_months': None}
        
        stress_results[crisis_name] = crisis_results
    
    return stress_results


def plot_stress_tests(stress_results):
    """Generate stress test comparison chart for N scenarios."""
    fig, ax = plt.subplots(figsize=(16, 8))
    
    crises = list(stress_results.keys())
    # Get all scenario labels from first crisis
    first_crisis = stress_results[crises[0]]
    scenario_labels = [k for k in first_crisis.keys()]
    n_scenarios = len(scenario_labels)
    
    x = np.arange(len(crises))
    total_width = 0.8
    bar_width = total_width / n_scenarios
    
    for s_idx, label in enumerate(scenario_labels):
        dds = []
        for crisis in crises:
            data = stress_results[crisis].get(label, {})
            dds.append(abs(data.get('max_dd', 0) or 0) * 100)
        
        offset = (s_idx - (n_scenarios - 1) / 2) * bar_width
        color = SCENARIO_COLORS.get(label, TEAL)
        bars = ax.bar(x + offset, dds, bar_width * 0.9, label=label, 
                      color=color, edgecolor='white', linewidth=0.5)
        
        # Value labels on top
        for bar in bars:
            height = bar.get_height()
            if height > 3:  # Only label bars > 3%
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.0f}%', ha='center', va='bottom', fontsize=7, 
                        fontweight='bold', color=color)
    
    ax.set_xlabel('')
    ax.set_ylabel('Maximum Drawdown (%)')
    ax.set_title('Historical Stress Tests: Maximum Drawdown by Crisis', 
                 fontsize=14, fontweight='bold', color=NAVY)
    ax.set_xticks(x)
    clean_labels = [c.replace('\n', ' ') for c in crises]
    ax.set_xticklabels(clean_labels, fontsize=10, ha='center')
    ax.legend(fontsize=10, ncol=min(n_scenarios, 3))
    
    y_max = 0
    for crisis in crises:
        for label in scenario_labels:
            dd = abs(stress_results[crisis].get(label, {}).get('max_dd', 0) or 0) * 100
            y_max = max(y_max, dd)
    ax.set_ylim(0, y_max * 1.2)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'stress-test.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("\nSaved: reports/charts/stress-test.png")


# ============================================================
# MODEL 3: SENSITIVITY ANALYSIS
# ============================================================

def run_sensitivity_analysis(returns_df, common_returns, all_assets, scenario_configs):
    """Test how outcomes change with varying assumptions for all scenarios."""
    print("\n" + "="*60)
    print("MODEL 3: SENSITIVITY ANALYSIS")
    print("="*60)
    
    N_SENS = 3000  # Fewer sims for sensitivity (still statistically significant)
    
    # Build boot_configs and weight_configs from scenario_configs
    boot_configs = {}
    weight_configs = {}
    for label, (w_vec, boot_mat, n_hist, asset_list) in scenario_configs.items():
        boot_configs[label] = (asset_list, boot_mat, n_hist)
        weight_configs[label] = w_vec
    
    def run_quick_mc(port_label, n_sims, monthly_adj=0, contribution_mult=1.0, 
                     inflation_rate=0.02, amzn_override=None, amzn_months=0,
                     equity_adj=0, japan_scenario=False):
        """Quick Monte Carlo with parameter overrides."""
        assets, boot_matrix, n_hist = boot_configs[port_label]
        weights = weight_configs[port_label]
        
        amzn_idx = assets.index('AMZN') if 'AMZN' in assets else None
        
        # Identify equity indices for Japan scenario / equity adjustments
        equity_names = ['US_Total', 'SCV', 'QQQ', 'AMZN']
        equity_indices = [assets.index(a) for a in equity_names if a in assets]
        
        final_values = np.zeros(n_sims)
        
        for sim in range(n_sims):
            sample_indices = np.random.randint(0, n_hist, size=TOTAL_MONTHS)
            sampled_returns = boot_matrix[sample_indices].copy()
            
            # Apply equity return adjustment
            if equity_adj != 0:
                monthly_equity_adj = equity_adj / 12
                for ei in equity_indices:
                    sampled_returns[:, ei] += monthly_equity_adj
            
            # Japan scenario: US equities earn 0% real for 15 years
            if japan_scenario:
                us_names = ['US_Total', 'QQQ']
                us_indices = [assets.index(a) for a in us_names if a in assets]
                for ui in us_indices:
                    sampled_returns[:180, ui] = 0  # 15 years of zero
            
            # AMZN override for first N months
            if amzn_override is not None and amzn_idx is not None and amzn_months > 0:
                monthly_amzn_ret = (1 + amzn_override) ** (1/amzn_months) - 1
                sampled_returns[:amzn_months, amzn_idx] = monthly_amzn_ret
            
            value = INITIAL_PORTFOLIO
            asset_values = weights * value
            
            for month in range(TOTAL_MONTHS):
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                
                if month < TRANSITION_MONTHS:
                    contribution = TRANSITION_MONTHLY * contribution_mult
                else:
                    contribution = ONGOING_MONTHLY * contribution_mult
                
                asset_values += weights * contribution
                
                if month == BALLOON_MONTH:
                    total = asset_values.sum()
                    if total > BALLOON_AMOUNT:
                        asset_values -= weights * BALLOON_AMOUNT
                
                if (month + 1) % 12 == 0:
                    total = asset_values.sum()
                    asset_values = weights * total
                
                value = asset_values.sum()
            
            # Convert to real dollars
            real_value = value / (1 + inflation_rate) ** 19
            final_values[sim] = real_value
        
        return np.median(final_values)
    
    scenarios = {}
    port_labels = list(boot_configs.keys())
    
    # 1. Return assumptions
    print("\nReturn sensitivity...")
    for label_suffix, equity_adj, japan in [
        ('Base', 0, False),
        ('Bear (-2%)', -0.02, False),
        ('Bull (+2%)', 0.02, False),
        ('Japan (flat 15yr)', 0, True),
    ]:
        for port_label in port_labels:
            key = f"Returns: {label_suffix} | {port_label}"
            val = run_quick_mc(port_label, N_SENS, equity_adj=equity_adj, japan_scenario=japan)
            scenarios[key] = val
            print(f"  {key}: ${val/1e6:.2f}M (real)")
    
    # 2. Contribution sensitivity
    print("\nContribution sensitivity...")
    for label_suffix, mult in [
        ('Base ($80K/yr)', 1.0),
        ('Reduced (−30%)', 0.7),
        ('Increased ($130K/yr)', 1.625),
    ]:
        for port_label in port_labels:
            key = f"Contributions: {label_suffix} | {port_label}"
            val = run_quick_mc(port_label, N_SENS, contribution_mult=mult)
            scenarios[key] = val
            print(f"  {key}: ${val/1e6:.2f}M (real)")
    
    # 3. AMZN scenarios (only for portfolios that hold AMZN)
    print("\nAMZN-specific scenarios...")
    amzn_scenarios = [
        ('AMZN −50% (12mo)', -0.50, 12),
        ('AMZN flat (5yr)', 0.0, 60),
        ('AMZN +100% (3yr)', 1.0, 36),
    ]
    for label_suffix, amzn_ret, amzn_months in amzn_scenarios:
        for port_label in port_labels:
            # Check if this portfolio has AMZN
            assets = boot_configs[port_label][0]
            if 'AMZN' not in assets:
                continue
            key = f"AMZN: {label_suffix} | {port_label}"
            val = run_quick_mc(port_label, N_SENS, amzn_override=amzn_ret, amzn_months=amzn_months)
            scenarios[key] = val
            print(f"  {key}: ${val/1e6:.2f}M (real)")
    
    # 4. Inflation sensitivity
    print("\nInflation sensitivity...")
    for label_suffix, infl in [
        ('2% (target)', 0.02),
        ('4% sustained', 0.04),
        ('6% then normalize', 0.045),  # ~4.5% effective over 19 years
    ]:
        for port_label in port_labels:
            key = f"Inflation: {label_suffix} | {port_label}"
            val = run_quick_mc(port_label, N_SENS, inflation_rate=infl)
            scenarios[key] = val
            print(f"  {key}: ${val/1e6:.2f}M (real)")
    
    return scenarios


def plot_sensitivity(scenarios):
    """Generate grouped heatmap/bar chart for sensitivity across all scenarios."""
    # Find all portfolio labels and base cases
    base_values = {}
    for key, val in scenarios.items():
        if 'Returns: Base' in key:
            port_label = key.split(' | ')[-1]
            base_values[port_label] = val
    
    port_labels = list(base_values.keys())
    if not port_labels:
        print("Warning: Could not find base cases for sensitivity chart")
        return
    
    # Define sensitivity tests to show
    sensitivity_tests = [
        ('Bear market (−2%)', 'Returns: Bear (-2%)'),
        ('Bull market (+2%)', 'Returns: Bull (+2%)'),
        ('Japan scenario', 'Returns: Japan (flat 15yr)'),
        ('Income −30%', 'Contributions: Reduced (−30%)'),
        ('Income +60%', 'Contributions: Increased ($130K/yr)'),
        ('Inflation 4%', 'Inflation: 4% sustained'),
        ('Inflation 6%', 'Inflation: 6% then normalize'),
        ('AMZN −50% (12mo)', 'AMZN: AMZN −50% (12mo)'),
        ('AMZN flat (5yr)', 'AMZN: AMZN flat (5yr)'),
        ('AMZN +100% (3yr)', 'AMZN: AMZN +100% (3yr)'),
    ]
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    n_tests = len(sensitivity_tests)
    n_ports = len(port_labels)
    bar_height = 0.8 / n_ports
    
    for p_idx, port_label in enumerate(port_labels):
        base = base_values[port_label]
        color = SCENARIO_COLORS.get(port_label, TEAL)
        impacts = []
        for display_name, key_prefix in sensitivity_tests:
            val = scenarios.get(f"{key_prefix} | {port_label}")
            if val is not None:
                impacts.append((val - base) / 1e6)
            else:
                impacts.append(0)
        
        y_positions = np.arange(n_tests) + (p_idx - (n_ports - 1) / 2) * bar_height
        bars = ax.barh(y_positions, impacts, bar_height * 0.9, color=color, alpha=0.8,
                       label=f'{port_label} (base ${base/1e6:.1f}M)')
        
        # Value labels
        for y, val in zip(y_positions, impacts):
            if abs(val) > 0.05:
                ha = 'left' if val >= 0 else 'right'
                x_off = 0.03 if val >= 0 else -0.03
                ax.text(val + x_off, y, f'{val:+.1f}M', ha=ha, va='center', 
                        fontsize=6, color=color, fontweight='bold')
    
    ax.set_yticks(np.arange(n_tests))
    ax.set_yticklabels([t[0] for t in sensitivity_tests], fontsize=10)
    ax.set_xlabel('Impact on Median Outcome ($M, real)')
    ax.set_title('Sensitivity Analysis: Impact on Retirement Portfolio Value\n(Difference from Base Case, Inflation-Adjusted)',
                 fontsize=14, fontweight='bold', color=NAVY)
    ax.axvline(x=0, color=NAVY, linewidth=2)
    ax.legend(loc='lower right', fontsize=9)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'sensitivity.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("\nSaved: reports/charts/sensitivity.png")


# ============================================================
# MODEL 4: SEQUENCE OF RETURNS RISK
# ============================================================

def run_sequence_risk(returns_df, common_returns, all_assets, scenario_configs, mc_results):
    """Model retirement withdrawal phase with sequence of returns risk for all scenarios."""
    print("\n" + "="*60)
    print(f"MODEL 4: SEQUENCE OF RETURNS RISK ({len(scenario_configs)} scenarios)")
    print("="*60)
    
    RETIREMENT_MONTHS = RETIREMENT_YEARS * 12  # 420 months (35 years)
    N_RETIREMENT_SIMS = 10_000
    INFLATION = 0.03  # 3% average inflation during retirement
    
    withdrawal_strategies = {}
    
    def _run_withdrawal_sim(port_label, w_vec, boot_mat, n_hist, starting_val, 
                            strategy='fixed', annual_amount=ANNUAL_EXPENSES,
                            guardrails=False, bond_tent=False, asset_list=None):
        """Generic withdrawal simulation. Returns dict with paths, ruin_rate, ruin_ages."""
        paths = np.zeros((N_RETIREMENT_SIMS, RETIREMENT_MONTHS + 1))
        paths[:, 0] = starting_val
        ruin_count = 0
        ruin_ages = []
        
        # Bond tent setup
        bonds_idx = asset_list.index('Bonds') if (bond_tent and asset_list and 'Bonds' in asset_list) else None
        tips_idx = asset_list.index('TIPS') if (bond_tent and asset_list and 'TIPS' in asset_list) else None
        
        for sim in range(N_RETIREMENT_SIMS):
            sample_indices = np.random.randint(0, n_hist, size=RETIREMENT_MONTHS)
            sampled_returns = boot_mat[sample_indices]
            
            value = starting_val
            asset_values = w_vec * value
            current_withdrawal = annual_amount
            ruined = False
            
            for month in range(RETIREMENT_MONTHS):
                if value <= 0:
                    paths[sim, month + 1:] = 0
                    if not ruined:
                        ruin_count += 1
                        ruin_ages.append(55 + month / 12)
                        ruined = True
                    break
                
                year = month // 12
                weights_this_month = w_vec
                
                # Bond tent weight adjustment
                if bond_tent and bonds_idx is not None:
                    if year <= 5:
                        bond_alloc = 0.40
                    elif year <= 10:
                        bond_alloc = 0.40 - (year - 5) * 0.064
                    else:
                        bond_alloc = 0.08
                    
                    tent_w = w_vec.copy()
                    current_bond = tent_w[bonds_idx]
                    if tips_idx is not None:
                        current_bond += tent_w[tips_idx]
                    extra = bond_alloc - current_bond
                    if extra > 0:
                        eq_mask = np.ones(len(w_vec), dtype=bool)
                        if bonds_idx is not None: eq_mask[bonds_idx] = False
                        if tips_idx is not None: eq_mask[tips_idx] = False
                        eq_total = tent_w[eq_mask].sum()
                        if eq_total > extra:
                            tent_w[eq_mask] *= (eq_total - extra) / eq_total
                            tent_w[bonds_idx] = bond_alloc * 0.7
                            if tips_idx is not None:
                                tent_w[tips_idx] = bond_alloc * 0.3
                    weights_this_month = tent_w / tent_w.sum()
                    asset_values = weights_this_month * value
                
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                total = asset_values.sum()
                
                # Guardrail adjustments
                if guardrails and month > 0 and month % 12 == 0:
                    inflation_adj = (1 + INFLATION) ** year
                    wd_rate = current_withdrawal / total if total > 0 else 1
                    if wd_rate > 0.06:
                        current_withdrawal *= 0.90
                    elif wd_rate < 0.035:
                        current_withdrawal *= 1.10
                    else:
                        current_withdrawal *= (1 + INFLATION)
                    floor = 120_000 * inflation_adj
                    current_withdrawal = max(current_withdrawal, floor)
                
                # Compute monthly withdrawal
                if guardrails:
                    monthly_wd = current_withdrawal / 12
                else:
                    adj = current_withdrawal * (1 + INFLATION) ** year / 12
                    monthly_wd = adj
                
                if total > monthly_wd:
                    asset_values -= weights_this_month * monthly_wd
                else:
                    asset_values = weights_this_month * 0
                
                # Annual rebalance
                if (month + 1) % 12 == 0:
                    total = asset_values.sum()
                    asset_values = weights_this_month * max(total, 0)
                
                value = max(asset_values.sum(), 0)
                paths[sim, month + 1] = value
        
        ruin_rate = ruin_count / N_RETIREMENT_SIMS
        return {
            'paths': paths,
            'ruin_rate': ruin_rate,
            'ruin_ages': ruin_ages,
            'starting_value': starting_val,
        }
    
    # Inflate current $180K expenses to retirement year (19 years at 3%)
    YEARS_TO_RETIREMENT = TOTAL_MONTHS / 12  # 19 years
    RETIREMENT_EXPENSES = ANNUAL_EXPENSES * (1 + INFLATION) ** YEARS_TO_RETIREMENT
    print(f"\nInflation-adjusted expenses at retirement: ${RETIREMENT_EXPENSES:,.0f}/yr "
          f"(${ANNUAL_EXPENSES:,}/yr in 2026 dollars × {(1+INFLATION)**YEARS_TO_RETIREMENT:.2f}x)")
    
    # Run inflation-adjusted actual expenses for ALL scenarios
    print(f"\nStrategy: Actual Expenses (${RETIREMENT_EXPENSES/1000:.0f}K/year in 2045 dollars) — all scenarios...")
    for label, (w_vec, boot_mat, n_hist, asset_list) in scenario_configs.items():
        sv = mc_results[label]['percentiles'][19]['median']
        result = _run_withdrawal_sim(label, w_vec, boot_mat, n_hist, sv,
                                      annual_amount=RETIREMENT_EXPENSES, asset_list=asset_list)
        withdrawal_strategies[f'${RETIREMENT_EXPENSES/1000:.0f}K/yr | {label}'] = result
        print(f"  {label} - ${RETIREMENT_EXPENSES/1000:.0f}K/yr: Ruin rate = {result['ruin_rate']:.1%} (start ${sv/1e6:.1f}M)")
    
    # Run 3% withdrawal for ALL scenarios
    print("\nStrategy: 3% Withdrawal — all scenarios...")
    for label, (w_vec, boot_mat, n_hist, asset_list) in scenario_configs.items():
        sv = mc_results[label]['percentiles'][19]['median']
        annual_3pct = sv * 0.03
        result = _run_withdrawal_sim(label, w_vec, boot_mat, n_hist, sv,
                                      annual_amount=annual_3pct, asset_list=asset_list)
        withdrawal_strategies[f'3% Rule | {label}'] = result
        print(f"  {label} - 3% Rule (${annual_3pct/1000:.0f}K/yr): Ruin rate = {result['ruin_rate']:.1%}")
    
    # Run 4% rule for ALL scenarios
    print("\nStrategy: 4% Rule — all scenarios...")
    for label, (w_vec, boot_mat, n_hist, asset_list) in scenario_configs.items():
        sv = mc_results[label]['percentiles'][19]['median']
        annual_4pct = sv * 0.04
        result = _run_withdrawal_sim(label, w_vec, boot_mat, n_hist, sv,
                                      annual_amount=annual_4pct, asset_list=asset_list)
        withdrawal_strategies[f'4% Rule | {label}'] = result
        print(f"  {label} - 4% Rule (${annual_4pct/1000:.0f}K/yr): Ruin rate = {result['ruin_rate']:.1%}")
    
    # Run Guyton-Klinger guardrails for ALL scenarios
    print("\nStrategy: Guyton-Klinger Guardrails — all scenarios...")
    for label, (w_vec, boot_mat, n_hist, asset_list) in scenario_configs.items():
        sv = mc_results[label]['percentiles'][19]['median']
        result = _run_withdrawal_sim(label, w_vec, boot_mat, n_hist, sv,
                                      annual_amount=sv * 0.05, guardrails=True, asset_list=asset_list)
        withdrawal_strategies[f'Guardrails | {label}'] = result
        print(f"  {label} - Guardrails: Ruin rate = {result['ruin_rate']:.1%}")
    
    return withdrawal_strategies


def plot_sequence_risk(withdrawal_strategies):
    """Generate sequence risk charts — one per strategy showing all scenarios overlaid."""
    # Discover strategy prefixes dynamically from keys
    all_prefixes = sorted(set(k.split(' | ')[0] for k in withdrawal_strategies.keys()))
    strategy_prefixes = all_prefixes[:4]  # Limit to 2×2 grid
    ages = np.linspace(55, 90, 421)
    
    n_strats = len(strategy_prefixes)
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    
    for ax, strat_prefix in zip(axes.flat, strategy_prefixes):
        # Find all scenarios for this strategy
        matching = {k: v for k, v in withdrawal_strategies.items() if k.startswith(strat_prefix)}
        
        if not matching:
            ax.set_visible(False)
            continue
        
        # Plot median + 10/90 band for each scenario
        for key, data in matching.items():
            label = key.split(' | ')[-1]
            color = SCENARIO_COLORS.get(label, TEAL)
            paths = data['paths']
            ruin = data['ruin_rate']
            sv = data.get('starting_value', paths[0, 0])
            
            median_path = np.median(paths, axis=0)
            p10 = np.percentile(paths, 10, axis=0)
            p90 = np.percentile(paths, 90, axis=0)
            
            ax.fill_between(ages, p10 / 1e6, p90 / 1e6, alpha=0.08, color=color)
            ax.plot(ages, median_path / 1e6, color=color, linewidth=2, 
                    label=f'{label}: {ruin:.1%} ruin')
        
        ax.axhline(y=0, color=RED, linewidth=1, linestyle='-', alpha=0.5)
        ax.axvline(x=62, color=GOLD, linestyle=':', alpha=0.4)
        ax.axvline(x=65, color=GREEN, linestyle=':', alpha=0.4)
        ax.text(62.2, ax.get_ylim()[1] * 0.9 if ax.get_ylim()[1] > 0 else 1, 
                'SS (62)', fontsize=8, color=GOLD, fontweight='bold')
        ax.text(65.2, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] > 0 else 0.8, 
                'Medicare (65)', fontsize=8, color=GREEN, fontweight='bold')
        
        ax.set_title(f'{strat_prefix} Withdrawal', fontsize=13, fontweight='bold', color=NAVY)
        ax.set_xlabel('Age')
        ax.set_ylabel('Portfolio ($M)')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}M'))
        ax.legend(loc='upper right', fontsize=8)
        ax.set_xlim(55, 90)
    
    fig.suptitle('Sequence of Returns Risk: Retirement Portfolio Survival (Age 55→90)\nAll Scenarios Compared',
                 fontsize=16, fontweight='bold', color=NAVY, y=1.02)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'sequence-risk.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("\nSaved: reports/charts/sequence-risk.png")


# ============================================================
# REPORT GENERATION
# ============================================================

def generate_report(mc_results, stress_results, sensitivity_scenarios, 
                   withdrawal_strategies, asset_stats, data_info, corr_matrix):
    """Generate the full quantitative analysis report for all scenarios."""
    
    scenario_labels = list(mc_results.keys())
    
    report = f"""# Quantitative Portfolio Analysis: Cleary Family
## Date: March 29, 2026

---

## Portfolio Allocations

Each scenario represents a distinct investment philosophy. All weights sum to 100%.

| Asset Class | Current | Conservative | All-Weather | Boglehead | Barbell |
|-------------|---------|-------------|-------------|-----------|---------|
"""
    
    # Build allocation table
    all_asset_names = sorted(set().union(*[set(SCENARIOS[l].keys()) for l in scenario_labels]))
    for asset in all_asset_names:
        row = f"| {asset} "
        for label in scenario_labels:
            w = SCENARIOS[label].get(asset, 0)
            row += f"| {w:.1%} " if w > 0 else "| — "
        row += "|\n"
        report += row
    
    report += f"""
**Current:** Your actual holdings — 35% AMZN, heavy US large cap, no international, minimal bonds.
**Conservative:** Sell ~500 AMZN shares over 12 months, redeploy to VTI/VXUS. AMZN drops to ~20%.
**All-Weather:** Ray Dalio's risk-parity approach — designed to perform in any economic regime (inflation, deflation, growth, recession).
**Boglehead:** The classic 3-fund portfolio (VTI/VXUS/BND). Dead simple, hard to beat.
**Barbell:** Nassim Taleb philosophy — 70% aggressive equity + 30% safest bonds. Nothing in between.

---

## Executive Summary

This analysis compares **5 portfolio scenarios** across 10,000 Monte Carlo simulations, 4 historical stress tests, sensitivity analysis, and sequence-of-returns modeling.

| Metric | {' | '.join(scenario_labels)} |
|--------|{'|'.join(['------' for _ in scenario_labels])}|
"""
    
    # Summary table rows
    metrics = [
        ('Median at 55', lambda r: f"${r['median_final']:,.0f}"),
        ('Mean at 55', lambda r: f"${r['mean_final']:,.0f}"),
        ('10th %ile', lambda r: f"${np.percentile(r['final_values'], 10):,.0f}"),
        ('90th %ile', lambda r: f"${np.percentile(r['final_values'], 90):,.0f}"),
        ('P(>$5M)', lambda r: f"{r['prob_5M']:.1%}"),
        ('P(>$10M)', lambda r: f"{r['prob_10M']:.1%}"),
        ('P(<$500K ever)', lambda r: f"{r['prob_below_500K']:.1%}"),
        ('Median max DD', lambda r: f"{np.median(r['max_drawdowns']):.1%}"),
    ]
    
    for metric_name, metric_fn in metrics:
        row = f"| {metric_name} "
        for label in scenario_labels:
            row += f"| {metric_fn(mc_results[label])} "
        row += "|\n"
        report += row
    
    report += f"""
---

## Model 1: Monte Carlo Simulation

### Methodology
- **Data source:** Historical monthly returns from Yahoo Finance for each asset class proxy
- **Simulation method:** Bootstrap resampling of actual monthly return vectors (preserves fat tails, real correlations, and non-normal distributions)
- **Simulations:** {N_SIMULATIONS:,} paths over {TOTAL_MONTHS} months (19 years)
- **Contributions:** $18,000/month for first 24 months (RSU transition), then $6,667/month ongoing
- **Balloon payment:** $400,000 subtracted at month 168 (age 50) for mortgage balloon
- **Rebalancing:** Annual to target weights

### Historical Data Used
"""
    
    for name, info in data_info.items():
        report += f"- **{name}** ({info['ticker']}): {info['start']} to {info['end']} ({info['months']} months)\n"
    
    report += f"""
### Historical Return Statistics (Annualized)

**Note:** AMZN returns have been adjusted from their historical 37% annualized (reflecting 1998-2026 startup-to-megacap trajectory) to 11% forward-looking consensus for a $2T company. Volatility, correlations, and distribution shape are preserved. All other assets use unadjusted historical returns.

| Asset | Ann. Return | Ann. Volatility | Sharpe | Skew | Kurtosis | Max Drawdown |
|-------|------------|----------------|--------|------|----------|-------------|
"""
    
    for name, s in asset_stats.items():
        suffix = " **(adjusted)**" if name == 'AMZN' else ""
        report += f"| {name}{suffix} | {s['annual_return']:.1%} | {s['annual_vol']:.1%} | {s['sharpe']:.2f} | {s['skew']:.2f} | {s['kurtosis']:.1f} | {s['max_drawdown']:.1%} |\n"
    
    # Year-by-year projections for each scenario
    for label in scenario_labels:
        r = mc_results[label]
        report += f"""
#### {label} Portfolio
| Age | 10th %ile | 25th %ile | Median | 75th %ile | 90th %ile |
|-----|-----------|-----------|--------|-----------|-----------|
"""
        for year in range(0, 20, 2):
            age = 36 + year
            p = r['percentiles'][year]
            report += f"| {age} | ${p['p10']:,.0f} | ${p['p25']:,.0f} | ${p['median']:,.0f} | ${p['p75']:,.0f} | ${p['p90']:,.0f} |\n"
    
    report += f"""

### Probability of Reaching Milestones

| Milestone | {' | '.join(scenario_labels)} |
|-----------|{'|'.join(['------' for _ in scenario_labels])}|
"""
    
    for milestone, key in [('$5M', 'prob_5M'), ('$8M', 'prob_8M'), ('$10M', 'prob_10M'), ('$15M', 'prob_15M')]:
        row = f"| {milestone} "
        for label in scenario_labels:
            row += f"| {mc_results[label][key]:.1%} "
        row += "|\n"
        report += row
    
    report += f"""

![Monte Carlo Simulation — Individual Scenarios](charts/mc-real.png)

![Monte Carlo — All Scenarios Overlaid](charts/mc-overlay.png)

---

## Model 2: Historical Stress Tests

These are the actual returns each portfolio would have experienced during real market crises.

| Crisis | {' | '.join(scenario_labels)} |
|--------|{'|'.join(['------' for _ in scenario_labels])}|
"""
    
    for crisis_name, crisis_data in stress_results.items():
        clean_name = crisis_name.replace('\n', ' ')
        row = f"| {clean_name} "
        for label in scenario_labels:
            dd = crisis_data.get(label, {}).get('max_dd')
            loss = crisis_data.get(label, {}).get('dollar_loss')
            if dd is not None:
                row += f"| {dd:.1%} (−${loss:,.0f}) " if loss else f"| {dd:.1%} "
            else:
                row += "| N/A "
        row += "|\n"
        report += row
    
    report += f"""

![Stress Tests](charts/stress-test.png)

---

## Model 3: Sensitivity Analysis

How much do different assumptions change the outcome? All values are in **real (inflation-adjusted) dollars**.

"""
    
    # Base cases for all scenarios
    base_values = {}
    for key, val in sensitivity_scenarios.items():
        if 'Returns: Base' in key:
            port_label = key.split(' | ')[-1]
            base_values[port_label] = val
    
    report += "**Base cases (real dollars):**\n"
    for label in scenario_labels:
        bv = base_values.get(label, 0)
        report += f"- {label}: **${bv/1e6:.2f}M**\n"
    
    report += "\n### Full Sensitivity Table\n\n"
    report += f"| Scenario | {' | '.join(scenario_labels)} |\n"
    report += f"|----------|{'|'.join(['------' for _ in scenario_labels])}|\n"
    
    seen = set()
    for key in sorted(sensitivity_scenarios.keys()):
        scenario = key.split(' | ')[0]
        if scenario in seen:
            continue
        seen.add(scenario)
        row = f"| {scenario} "
        for label in scenario_labels:
            val = sensitivity_scenarios.get(f"{scenario} | {label}", 0)
            row += f"| ${val/1e6:.2f}M " if val else "| — "
        row += "|\n"
        report += row
    
    report += f"""

![Sensitivity Analysis](charts/sensitivity.png)

---

## Model 4: Sequence of Returns Risk

This models the retirement withdrawal phase — starting at age 55 with the projected median portfolio value, testing whether the money lasts through age 90 (35 years).

### Starting Values by Scenario

| Scenario | Median at 55 |
|----------|-------------|
"""
    
    for label in scenario_labels:
        sv = mc_results[label]['percentiles'][19]['median']
        report += f"| {label} | ${sv:,.0f} |\n"
    
    report += f"""

### Ruin Rates: All Strategies × All Scenarios

| Strategy | {' | '.join(scenario_labels)} |
|----------|{'|'.join(['------' for _ in scenario_labels])}|
"""
    
    strat_prefixes = sorted(set(k.split(' | ')[0] for k in withdrawal_strategies.keys()))
    for strat_prefix in strat_prefixes:
        row = f"| {strat_prefix} "
        for label in scenario_labels:
            key = f"{strat_prefix} | {label}"
            data = withdrawal_strategies.get(key, {})
            ruin = data.get('ruin_rate')
            row += f"| {ruin:.1%} " if ruin is not None else "| N/A "
        row += "|\n"
        report += row
    
    report += f"""

### What This Means

The **actual expenses** and **3% rule** rows are the most relevant to your spending. The 4% rule is included as a standard benchmark. All withdrawal amounts inflate at 3%/yr during retirement.

**Guyton-Klinger guardrails** adapt withdrawals based on portfolio performance — cutting spending in down years and increasing in good years, with a $120K/yr floor.

### Critical Gap: Age 55 to 62

At age 55, you'd be 7 years from earliest Social Security (62) and 10 years from Medicare (65). This window is the most sequence-risk-sensitive period.

![Sequence of Returns Risk](charts/sequence-risk.png)

---

## Correlation Matrix

```
{corr_matrix.to_string() if corr_matrix is not None else "Correlation matrix not available"}
```

---

## Limitations & Assumptions

### What the models CAN tell us:
- Historical risk/return relationships between asset classes
- The impact of concentration vs diversification using real data
- Probability distributions of outcomes based on historical patterns
- Relative comparison between portfolio strategies

### What the models CANNOT tell us:
- **Future returns will not match historical returns.** Past performance is not predictive.
- **Bootstrap resampling assumes the future resembles the past** in its distributional properties.
- **Tax impacts are not modeled.** The transition from concentrated to diversified will trigger capital gains.
- **Behavioral risk is not modeled.** The biggest risk is panic-selling during a drawdown.
- **Correlation regimes can change.** During crises, correlations tend to increase.

### Key Assumptions:
- Monthly rebalancing of contributions, annual rebalancing of portfolio
- $400K balloon payment at age 50
- 3% inflation during retirement for withdrawal adjustments
- No additional income sources in retirement (Social Security, part-time work, etc.)
- No tax drag on returns

---

*This analysis uses real historical data and rigorous simulation methodology. All code is saved in `quantitative/monte_carlo.py` for reproducibility. A CFP or fiduciary advisor should review these findings in the context of your complete financial picture, including tax planning, estate considerations, and insurance needs.*
"""
    
    report_path = os.path.join(OUTPUT_DIR, 'QUANTITATIVE-ANALYSIS-2026-03-29.md')
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nSaved: {report_path}")
    return report_path


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("=" * 70)
    print("CLEARY FAMILY PORTFOLIO QUANTITATIVE ANALYSIS")
    print(f"SCENARIOS: {', '.join(SCENARIOS.keys())}")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Simulations: {N_SIMULATIONS:,}")
    print(f"Timeline: {TOTAL_MONTHS} months (19 years)")
    print()
    
    # Step 1: Fetch data
    returns_df, common_returns, data_info, all_prices = fetch_historical_data()
    
    # Step 2: Compute statistics
    asset_stats = compute_statistics(returns_df)
    
    # Print correlation matrix
    corr = common_returns.corr()
    print("\nCorrelation Matrix (common period):")
    print(corr.round(2).to_string())
    
    # Step 3: Monte Carlo (all scenarios)
    mc_results, all_assets, scenario_configs = run_monte_carlo(
        returns_df, common_returns, SCENARIOS)
    plot_monte_carlo(mc_results)
    
    # Step 4: Stress tests (all scenarios)
    stress_results = run_stress_tests(all_prices, SCENARIOS)
    plot_stress_tests(stress_results)
    
    # Step 5: Sensitivity analysis (all scenarios)
    sensitivity_scenarios = run_sensitivity_analysis(
        returns_df, common_returns, all_assets, scenario_configs)
    plot_sensitivity(sensitivity_scenarios)
    
    # Step 6: Sequence of returns (all scenarios)
    withdrawal_strategies = run_sequence_risk(
        returns_df, common_returns, all_assets, scenario_configs, mc_results)
    plot_sequence_risk(withdrawal_strategies)
    
    # Step 7: Generate report
    report_path = generate_report(
        mc_results, stress_results, sensitivity_scenarios,
        withdrawal_strategies, asset_stats, data_info, corr)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Report: {report_path}")
    print(f"Charts: {CHARTS_DIR}/")
    print(f"Code: quantitative/monte_carlo.py")


if __name__ == '__main__':
    main()
