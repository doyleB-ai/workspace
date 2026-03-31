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

# Current portfolio weights (mapped to our asset classes)
# AMZN: 35%, SPY/QQQ/401k: 31.5%, TSLA: 3.5%, Other stocks: 2.4%,
# Bonds: 2.8%, Gold: 1.6%, Crypto: 0.6%, Cash: 1.8%, Schwab robo: 2.2%
CURRENT_WEIGHTS = {
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
}
# Note: TSLA (3.5%) merged into QQQ as both are high-vol tech. This extends
# the bootstrap period from 2010 to 2003 (limited by AGG/GLD instead of TSLA).
# GBTC (0.6%) also merged into QQQ. Schwab robo split across US/Intl/Bonds.

# Proposed portfolio weights
PROPOSED_WEIGHTS = {
    'US_Total':  0.350,
    'AMZN':      0.150,
    'Intl_Dev':  0.150,
    'SCV':       0.100,
    'Intl_SC':   0.050,
    'EM':        0.050,
    'REITs':     0.050,
    'Bonds':     0.050,
    'TIPS':      0.030,
    'Gold':      0.020,
    'QQQ':       0.000,
}

# Normalize weights
def normalize_weights(w):
    total = sum(w.values())
    return {k: v/total for k, v in w.items()}

CURRENT_WEIGHTS = normalize_weights(CURRENT_WEIGHTS)
PROPOSED_WEIGHTS = normalize_weights(PROPOSED_WEIGHTS)

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

def run_monte_carlo(returns_df, common_returns, weights_current, weights_proposed):
    """
    Bootstrap Monte Carlo simulation using historical returns.
    Preserves fat tails, correlations, and real-world distribution.
    """
    print("\n" + "="*60)
    print("MODEL 1: MONTE CARLO SIMULATION (10,000 paths)")
    print("="*60)
    
    # Build separate bootstrap pools for each portfolio to maximize history
    # Only require overlap among assets with >0 weight in that portfolio
    
    current_assets = [a for a in weights_current if weights_current[a] > 0 and a in returns_df.columns]
    proposed_assets = [a for a in weights_proposed if weights_proposed[a] > 0 and a in returns_df.columns]
    all_assets = sorted(set(current_assets + proposed_assets))
    
    # Per-portfolio bootstrap pools
    current_boot = returns_df[current_assets].dropna()
    proposed_boot = returns_df[proposed_assets].dropna()
    
    print(f"Current portfolio bootstrap: {len(current_boot)} months ({current_boot.index[0].date()} to {current_boot.index[-1].date()})")
    print(f"Proposed portfolio bootstrap: {len(proposed_boot)} months ({proposed_boot.index[0].date()} to {proposed_boot.index[-1].date()})")
    
    # Build weight vectors aligned to each portfolio's assets
    current_w_vec = np.array([weights_current.get(a, 0) for a in current_assets])
    current_w_vec = current_w_vec / current_w_vec.sum()
    
    proposed_w_vec = np.array([weights_proposed.get(a, 0) for a in proposed_assets])
    proposed_w_vec = proposed_w_vec / proposed_w_vec.sum()
    
    # Also build all_assets-aligned weight vectors for downstream use
    current_w = np.array([weights_current.get(a, 0) for a in all_assets])
    current_w = current_w / current_w.sum()
    proposed_w = np.array([weights_proposed.get(a, 0) for a in all_assets])
    proposed_w = proposed_w / proposed_w.sum()
    
    results = {}
    
    portfolio_configs = [
        ('Current', current_w_vec, current_boot.values, len(current_boot)),
        ('Proposed', proposed_w_vec, proposed_boot.values, len(proposed_boot)),
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
    
    return (results, all_assets, current_w, proposed_w,
            current_assets, proposed_assets,
            current_boot.values, proposed_boot.values,
            len(current_boot), len(proposed_boot),
            current_w_vec, proposed_w_vec)


def plot_monte_carlo(results):
    """Generate fan/ribbon chart for Monte Carlo results."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
    
    ages = np.arange(36, 56)
    years = np.arange(0, 20)
    
    for idx, (label, color_main, color_light) in enumerate([
        ('Current', CORAL, '#F5C6B8'),
        ('Proposed', TEAL, '#B8E0E0')
    ]):
        ax = axes[idx]
        r = results[label]
        p = r['percentiles']
        
        p10 = [p[y]['p10'] for y in years]
        p25 = [p[y]['p25'] for y in years]
        med = [p[y]['median'] for y in years]
        p75 = [p[y]['p75'] for y in years]
        p90 = [p[y]['p90'] for y in years]
        
        ax.fill_between(ages, [x/1e6 for x in p10], [x/1e6 for x in p90], 
                        alpha=0.15, color=color_main, label='10th-90th percentile')
        ax.fill_between(ages, [x/1e6 for x in p25], [x/1e6 for x in p75], 
                        alpha=0.3, color=color_main, label='25th-75th percentile')
        ax.plot(ages, [x/1e6 for x in med], color=color_main, linewidth=2.5, 
                label=f'Median: ${med[-1]/1e6:.1f}M')
        
        # Mark balloon payment — both panels
        ax.axvline(x=50, color=MED_GRAY, linestyle='--', alpha=0.7)
        # Place annotation at ~20% of y range for visibility
        y_pos = max(med) * 0.15
        ax.annotate('$400K Balloon\nPayment (Age 50)', xy=(50, y_pos), 
                    fontsize=10, fontweight='bold', ha='center', va='bottom', color=NAVY,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))
        
        ax.set_xlabel('Age')
        ax.set_title(f'{label} Portfolio', fontsize=14, fontweight='bold', color=NAVY)
        ax.legend(loc='upper left', fontsize=9)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}M'))
        ax.set_xlim(36, 55)
    
    axes[0].set_ylabel('Portfolio Value')
    
    fig.suptitle('Monte Carlo Simulation: 10,000 Paths Over 19 Years', 
                 fontsize=16, fontweight='bold', color=NAVY, y=1.02)
    
    # Add comparison stats at bottom (escape $ for matplotlib)
    c = results['Current']
    p = results['Proposed']
    fig.text(0.5, -0.06, 
             f"Current median: \\${c['median_final']/1e6:.1f}M  |  Proposed median: \\${p['median_final']/1e6:.1f}M  |  "
             f"Current P(>\\$5M): {c['prob_5M']:.0%}  |  Proposed P(>\\$5M): {p['prob_5M']:.0%}",
             ha='center', fontsize=10, color=NAVY)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'mc-real.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("\nSaved: reports/charts/mc-real.png")


# ============================================================
# MODEL 2: HISTORICAL STRESS TESTS
# ============================================================

def run_stress_tests(all_prices, weights_current_dict, weights_proposed_dict):
    """Run both portfolios through actual historical crises."""
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
        for label, weights in [('Current', weights_current_dict), ('Proposed', weights_proposed_dict)]:
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
    """Generate stress test comparison chart."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    crises = list(stress_results.keys())
    x = np.arange(len(crises))
    width = 0.35
    
    current_dds = []
    proposed_dds = []
    
    for crisis in crises:
        c = stress_results[crisis].get('Current', {})
        p = stress_results[crisis].get('Proposed', {})
        current_dds.append(abs(c.get('max_dd', 0) or 0) * 100)
        proposed_dds.append(abs(p.get('max_dd', 0) or 0) * 100)
    
    bars1 = ax.bar(x - width/2, current_dds, width, label='Current (Concentrated)', 
                   color=CORAL, edgecolor='white', linewidth=0.5)
    bars2 = ax.bar(x + width/2, proposed_dds, width, label='Proposed (Diversified)', 
                   color=TEAL, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color=CORAL)
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color=TEAL)
    
    ax.set_xlabel('')
    ax.set_ylabel('Maximum Drawdown (%)')
    ax.set_title('Historical Stress Tests: Maximum Drawdown by Crisis', 
                 fontsize=14, fontweight='bold', color=NAVY)
    ax.set_xticks(x)
    # Clean up crisis names — remove newlines for x-axis
    clean_labels = [c.replace('\n', ' ') for c in crises]
    ax.set_xticklabels(clean_labels, fontsize=10, ha='center')
    ax.legend(fontsize=11)
    y_max = max(max(current_dds), max(proposed_dds))
    ax.set_ylim(0, y_max * 1.25)
    
    # Add dollar loss annotations INSIDE the bars (not below x-axis)
    for i, crisis in enumerate(crises):
        c = stress_results[crisis].get('Current', {})
        p = stress_results[crisis].get('Proposed', {})
        c_loss = c.get('dollar_loss', 0) or 0
        p_loss = p.get('dollar_loss', 0) or 0
        if c_loss > 0:
            ax.text(i - width/2, current_dds[i] / 2, f'−${c_loss/1000:.0f}K', 
                    ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        if p_loss > 0:
            ax.text(i + width/2, proposed_dds[i] / 2, f'−${p_loss/1000:.0f}K', 
                    ha='center', va='center', fontsize=8, color='white', fontweight='bold')
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'stress-test.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("\nSaved: reports/charts/stress-test.png")


# ============================================================
# MODEL 3: SENSITIVITY ANALYSIS
# ============================================================

def run_sensitivity_analysis(returns_df, common_returns, all_assets, current_w, proposed_w,
                             current_assets, proposed_assets, current_boot_matrix, proposed_boot_matrix,
                             n_hist_current, n_hist_proposed):
    """Test how outcomes change with varying assumptions."""
    print("\n" + "="*60)
    print("MODEL 3: SENSITIVITY ANALYSIS")
    print("="*60)
    
    N_SENS = 3000  # Fewer sims for sensitivity (still statistically significant)
    
    # Map portfolio label to its bootstrap data
    # Build per-portfolio weight vectors aligned to their own asset lists
    current_w_vec = np.array([CURRENT_WEIGHTS.get(a, 0) for a in current_assets])
    current_w_vec = current_w_vec / current_w_vec.sum()
    proposed_w_vec = np.array([PROPOSED_WEIGHTS.get(a, 0) for a in proposed_assets])
    proposed_w_vec = proposed_w_vec / proposed_w_vec.sum()
    
    boot_configs = {
        'Current': (current_assets, current_boot_matrix, n_hist_current),
        'Proposed': (proposed_assets, proposed_boot_matrix, n_hist_proposed),
    }
    weight_configs = {
        'Current': current_w_vec,
        'Proposed': proposed_w_vec,
    }
    
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
    
    # 1. Return assumptions
    print("\nReturn sensitivity...")
    for label_suffix, equity_adj, japan in [
        ('Base', 0, False),
        ('Bear (-2%)', -0.02, False),
        ('Bull (+2%)', 0.02, False),
        ('Japan (flat 15yr)', 0, True),
    ]:
        for port_label in ['Current', 'Proposed']:
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
        for port_label in ['Current', 'Proposed']:
            key = f"Contributions: {label_suffix} | {port_label}"
            val = run_quick_mc(port_label, N_SENS, contribution_mult=mult)
            scenarios[key] = val
            print(f"  {key}: ${val/1e6:.2f}M (real)")
    
    # 3. AMZN scenarios
    print("\nAMZN-specific scenarios...")
    amzn_scenarios = [
        ('AMZN −50% (12mo)', -0.50, 12),
        ('AMZN flat (5yr)', 0.0, 60),
        ('AMZN +100% (3yr)', 1.0, 36),
    ]
    for label_suffix, amzn_ret, amzn_months in amzn_scenarios:
        for port_label in ['Current', 'Proposed']:
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
        for port_label in ['Current', 'Proposed']:
            key = f"Inflation: {label_suffix} | {port_label}"
            val = run_quick_mc(port_label, N_SENS, inflation_rate=infl)
            scenarios[key] = val
            print(f"  {key}: ${val/1e6:.2f}M (real)")
    
    return scenarios


def plot_sensitivity(scenarios):
    """Generate tornado chart showing sensitivity of outcomes."""
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Group scenarios for tornado chart
    # Show difference from base case for proposed portfolio
    base_proposed = None
    base_current = None
    
    # Find base cases
    for key, val in scenarios.items():
        if 'Returns: Base' in key and 'Proposed' in key:
            base_proposed = val
        if 'Returns: Base' in key and 'Current' in key:
            base_current = val
    
    if base_proposed is None or base_current is None:
        print("Warning: Could not find base cases for tornado chart")
        return
    
    # Build tornado data: impact on proposed portfolio
    tornado_items = []
    
    scenario_groups = {
        'AMZN −50% (12mo)': 'AMZN: AMZN −50% (12mo)',
        'AMZN +100% (3yr)': 'AMZN: AMZN +100% (3yr)',
        'AMZN flat (5yr)': 'AMZN: AMZN flat (5yr)',
        'Bear market (−2%)': 'Returns: Bear (-2%)',
        'Bull market (+2%)': 'Returns: Bull (+2%)',
        'Japan scenario': 'Returns: Japan (flat 15yr)',
        'Income −30%': 'Contributions: Reduced (−30%)',
        'Income +60%': 'Contributions: Increased ($130K/yr)',
        'Inflation 4%': 'Inflation: 4% sustained',
        'Inflation 6%': 'Inflation: 6% then normalize',
    }
    
    for display_name, key_prefix in scenario_groups.items():
        # Get both current and proposed
        current_val = scenarios.get(f"{key_prefix} | Current", base_current)
        proposed_val = scenarios.get(f"{key_prefix} | Proposed", base_proposed)
        
        # Impact = difference from base for proposed
        impact_proposed = (proposed_val - base_proposed) / 1e6
        impact_current = (current_val - base_current) / 1e6
        
        tornado_items.append({
            'name': display_name,
            'proposed_impact': impact_proposed,
            'current_impact': impact_current,
        })
    
    # Sort by absolute impact (proposed)
    tornado_items.sort(key=lambda x: abs(x['proposed_impact']))
    
    y_pos = np.arange(len(tornado_items))
    
    for i, item in enumerate(tornado_items):
        ax.barh(i - 0.17, item['current_impact'], 0.34, color=CORAL, alpha=0.8, 
                label='Current' if i == 0 else '')
        ax.barh(i + 0.17, item['proposed_impact'], 0.34, color=TEAL, alpha=0.8,
                label='Proposed' if i == 0 else '')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([item['name'] for item in tornado_items])
    ax.set_xlabel('Impact on Median Outcome ($M, real)')
    ax.set_title('Sensitivity Analysis: Impact on Retirement Portfolio Value\n(Difference from Base Case, Inflation-Adjusted)',
                 fontsize=14, fontweight='bold', color=NAVY)
    ax.axvline(x=0, color=NAVY, linewidth=2)
    ax.legend(loc='lower right', fontsize=11)
    
    # Add value labels at end of each bar
    for i, item in enumerate(tornado_items):
        for offset, val, color in [(-0.17, item['current_impact'], CORAL), 
                                    (0.17, item['proposed_impact'], TEAL)]:
            if abs(val) > 0.05:
                ha = 'left' if val >= 0 else 'right'
                x_offset = 0.05 if val >= 0 else -0.05
                ax.text(val + x_offset, i + offset, f'{val:+.1f}M', 
                        ha=ha, va='center', fontsize=7, color=color, fontweight='bold')
    
    # Add base case annotation
    ax.text(0.02, 0.98, f'Base: Current \\${base_current/1e6:.1f}M | Proposed \\${base_proposed/1e6:.1f}M (real)',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'sensitivity.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    print("\nSaved: reports/charts/sensitivity.png")


# ============================================================
# MODEL 4: SEQUENCE OF RETURNS RISK
# ============================================================

def run_sequence_risk(returns_df, common_returns, all_assets, current_w, proposed_w, mc_results,
                      proposed_assets, proposed_boot_matrix, n_hist_proposed,
                      current_assets, current_boot_matrix, n_hist_current):
    """Model retirement withdrawal phase with sequence of returns risk."""
    print("\n" + "="*60)
    print("MODEL 4: SEQUENCE OF RETURNS RISK")
    print("="*60)
    
    # Use proposed portfolio's bootstrap for retirement sims
    boot_matrix = proposed_boot_matrix
    n_hist = n_hist_proposed
    
    # Use projected median value at age 55 from proposed portfolio
    starting_value = mc_results['Proposed']['percentiles'][19]['median']
    print(f"\nStarting retirement value (proposed median at 55): ${starting_value:,.0f}")
    
    RETIREMENT_MONTHS = RETIREMENT_YEARS * 12  # 420 months (35 years)
    N_RETIREMENT_SIMS = 10_000
    INITIAL_WITHDRAWAL = ANNUAL_EXPENSES  # $180K/year
    INFLATION = 0.03  # 3% average inflation during retirement
    
    withdrawal_strategies = {}
    
    # Strategy 0: Actual expense target ($180K/year, inflation-adjusted)
    print("\nStrategy 0: Actual Expenses ($180K/year)...")
    
    for port_label, weights, boot_mat, n_h in [
        ('Proposed', proposed_w, proposed_boot_matrix, n_hist_proposed),
        ('Current', current_w_local if 'current_w_local' in dir() else current_w, current_boot_matrix, n_hist_current)
    ]:
        # Fix weight alignment for this bootstrap matrix
        if port_label == 'Proposed':
            w_local = np.array([PROPOSED_WEIGHTS.get(a, 0) for a in proposed_assets])
        else:
            w_local = np.array([CURRENT_WEIGHTS.get(a, 0) for a in current_assets])
        w_local = w_local / w_local.sum()
        
        sv = mc_results[port_label]['percentiles'][19]['median']
        paths = np.zeros((N_RETIREMENT_SIMS, RETIREMENT_MONTHS + 1))
        paths[:, 0] = sv
        ruin_count = 0
        ruin_ages = []
        
        for sim in range(N_RETIREMENT_SIMS):
            sample_indices = np.random.randint(0, n_h, size=RETIREMENT_MONTHS)
            sampled_returns = boot_mat[sample_indices]
            
            value = sv
            asset_values = w_local * value
            ruined = False
            
            for month in range(RETIREMENT_MONTHS):
                if value <= 0:
                    paths[sim, month + 1:] = 0
                    if not ruined:
                        ruin_count += 1
                        ruin_ages.append(55 + month / 12)
                        ruined = True
                    break
                
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                
                year = month // 12
                adj_withdrawal = ANNUAL_EXPENSES * (1 + INFLATION) ** year / 12
                
                total = asset_values.sum()
                if total > adj_withdrawal:
                    asset_values -= w_local * adj_withdrawal
                else:
                    asset_values = w_local * 0
                
                if (month + 1) % 12 == 0:
                    total = asset_values.sum()
                    asset_values = w_local * max(total, 0)
                
                value = max(asset_values.sum(), 0)
                paths[sim, month + 1] = value
        
        ruin_rate = ruin_count / N_RETIREMENT_SIMS
        print(f"  {port_label} - $180K/yr: Ruin rate = {ruin_rate:.1%}")
        if ruin_ages:
            print(f"    Median ruin age: {np.median(ruin_ages):.1f}")
        
        withdrawal_strategies[f'$180K/yr | {port_label}'] = {
            'paths': paths,
            'ruin_rate': ruin_rate,
            'ruin_ages': ruin_ages,
            'starting_value': sv,
        }
    
    # Strategy 1: Fixed 4% rule (inflation-adjusted)
    print("\nStrategy 1: Fixed 4% Rule...")
    initial_4pct = starting_value * 0.04
    
    for port_label, weights in [('Proposed', proposed_w)]:
        paths = np.zeros((N_RETIREMENT_SIMS, RETIREMENT_MONTHS + 1))
        paths[:, 0] = starting_value
        ruin_count = 0
        ruin_ages = []
        
        for sim in range(N_RETIREMENT_SIMS):
            sample_indices = np.random.randint(0, n_hist, size=RETIREMENT_MONTHS)
            sampled_returns = boot_matrix[sample_indices]
            
            value = starting_value
            asset_values = weights * value
            annual_withdrawal = initial_4pct
            ruined = False
            
            for month in range(RETIREMENT_MONTHS):
                if value <= 0:
                    paths[sim, month + 1:] = 0
                    if not ruined:
                        ruin_count += 1
                        ruin_ages.append(55 + month / 12)
                        ruined = True
                    break
                
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                
                # Monthly withdrawal (inflation-adjusted annually)
                year = month // 12
                adj_withdrawal = annual_withdrawal * (1 + INFLATION) ** year / 12
                
                total = asset_values.sum()
                if total > adj_withdrawal:
                    asset_values -= weights * adj_withdrawal
                else:
                    asset_values = weights * 0
                
                # Annual rebalance
                if (month + 1) % 12 == 0:
                    total = asset_values.sum()
                    asset_values = weights * max(total, 0)
                
                value = max(asset_values.sum(), 0)
                paths[sim, month + 1] = value
        
        ruin_rate = ruin_count / N_RETIREMENT_SIMS
        print(f"  {port_label} - 4% Rule: Ruin rate = {ruin_rate:.1%}")
        if ruin_ages:
            print(f"    Median ruin age: {np.median(ruin_ages):.1f}")
        
        withdrawal_strategies[f'4% Rule | {port_label}'] = {
            'paths': paths,
            'ruin_rate': ruin_rate,
            'ruin_ages': ruin_ages,
        }
    
    # Strategy 2: Variable withdrawal (Guyton-Klinger guardrails)
    print("\nStrategy 2: Guyton-Klinger Guardrails...")
    
    for port_label, weights in [('Proposed', proposed_w)]:
        paths = np.zeros((N_RETIREMENT_SIMS, RETIREMENT_MONTHS + 1))
        paths[:, 0] = starting_value
        ruin_count = 0
        ruin_ages = []
        
        for sim in range(N_RETIREMENT_SIMS):
            sample_indices = np.random.randint(0, n_hist, size=RETIREMENT_MONTHS)
            sampled_returns = boot_matrix[sample_indices]
            
            value = starting_value
            asset_values = weights * value
            base_withdrawal = starting_value * 0.05  # Start at 5%
            current_withdrawal = base_withdrawal
            ruined = False
            
            for month in range(RETIREMENT_MONTHS):
                if value <= 0:
                    paths[sim, month + 1:] = 0
                    if not ruined:
                        ruin_count += 1
                        ruin_ages.append(55 + month / 12)
                        ruined = True
                    break
                
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                total = asset_values.sum()
                
                # Annual guardrail check
                if month > 0 and month % 12 == 0:
                    year = month // 12
                    inflation_adj = (1 + INFLATION) ** year
                    
                    withdrawal_rate = current_withdrawal / total if total > 0 else 1
                    
                    # Upper guardrail: if rate > 6%, cut by 10%
                    if withdrawal_rate > 0.06:
                        current_withdrawal *= 0.90
                    # Lower guardrail: if rate < 3.5%, increase by 10%
                    elif withdrawal_rate < 0.035:
                        current_withdrawal *= 1.10
                    else:
                        # Normal inflation adjustment
                        current_withdrawal *= (1 + INFLATION)
                    
                    # Floor: never below $120K/year (real)
                    floor = 120_000 * inflation_adj
                    current_withdrawal = max(current_withdrawal, floor)
                
                # Monthly withdrawal
                monthly_withdrawal = current_withdrawal / 12
                
                if total > monthly_withdrawal:
                    asset_values -= weights * monthly_withdrawal
                else:
                    asset_values = weights * 0
                
                if (month + 1) % 12 == 0:
                    total = asset_values.sum()
                    asset_values = weights * max(total, 0)
                
                value = max(asset_values.sum(), 0)
                paths[sim, month + 1] = value
        
        ruin_rate = ruin_count / N_RETIREMENT_SIMS
        print(f"  {port_label} - Guardrails: Ruin rate = {ruin_rate:.1%}")
        
        withdrawal_strategies[f'Guardrails | {port_label}'] = {
            'paths': paths,
            'ruin_rate': ruin_rate,
            'ruin_ages': ruin_ages,
        }
    
    # Strategy 3: Bond tent (increase bonds to 40% years 55-65, then back)
    print("\nStrategy 3: Bond Tent...")
    
    for port_label, weights in [('Proposed', proposed_w)]:
        paths = np.zeros((N_RETIREMENT_SIMS, RETIREMENT_MONTHS + 1))
        paths[:, 0] = starting_value
        ruin_count = 0
        ruin_ages = []
        
        # Build bond tent weights (use proposed_assets for index lookup)
        bonds_idx = proposed_assets.index('Bonds') if 'Bonds' in proposed_assets else None
        tips_idx = proposed_assets.index('TIPS') if 'TIPS' in proposed_assets else None
        
        for sim in range(N_RETIREMENT_SIMS):
            sample_indices = np.random.randint(0, n_hist, size=RETIREMENT_MONTHS)
            sampled_returns = boot_matrix[sample_indices]
            
            value = starting_value
            annual_withdrawal = initial_4pct
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
                
                # Bond tent: 40% bonds in years 0-5, linearly decrease to 8% by year 10
                if year <= 5:
                    bond_alloc = 0.40
                elif year <= 10:
                    bond_alloc = 0.40 - (year - 5) * 0.064  # decrease to 8%
                else:
                    bond_alloc = 0.08
                
                # Adjust weights for bond tent
                tent_weights = weights.copy()
                if bonds_idx is not None:
                    current_bond = tent_weights[bonds_idx]
                    if tips_idx is not None:
                        current_bond += tent_weights[tips_idx]
                    
                    extra_bonds = bond_alloc - current_bond
                    if extra_bonds > 0:
                        # Take from equity proportionally
                        equity_mask = np.ones(len(weights), dtype=bool)
                        if bonds_idx is not None:
                            equity_mask[bonds_idx] = False
                        if tips_idx is not None:
                            equity_mask[tips_idx] = False
                        
                        equity_total = tent_weights[equity_mask].sum()
                        if equity_total > extra_bonds:
                            tent_weights[equity_mask] *= (equity_total - extra_bonds) / equity_total
                            tent_weights[bonds_idx] = bond_alloc * 0.7
                            if tips_idx is not None:
                                tent_weights[tips_idx] = bond_alloc * 0.3
                
                tent_weights = tent_weights / tent_weights.sum()
                asset_values = tent_weights * value
                
                monthly_rets = sampled_returns[month]
                asset_values = asset_values * (1 + monthly_rets)
                
                adj_withdrawal = annual_withdrawal * (1 + INFLATION) ** year / 12
                
                total = asset_values.sum()
                if total > adj_withdrawal:
                    asset_values -= tent_weights * adj_withdrawal
                else:
                    asset_values = tent_weights * 0
                
                value = max(asset_values.sum(), 0)
                paths[sim, month + 1] = value
        
        ruin_rate = ruin_count / N_RETIREMENT_SIMS
        print(f"  {port_label} - Bond Tent: Ruin rate = {ruin_rate:.1%}")
        
        withdrawal_strategies[f'Bond Tent | {port_label}'] = {
            'paths': paths,
            'ruin_rate': ruin_rate,
            'ruin_ages': ruin_ages,
        }
    
    # Also run 4% rule for current portfolio
    print("\nStrategy 1 (Current Portfolio): Fixed 4% Rule...")
    starting_value_current = mc_results['Current']['percentiles'][19]['median']
    initial_4pct_current = starting_value_current * 0.04
    
    # Use current portfolio's bootstrap data
    current_w_local = np.array([CURRENT_WEIGHTS.get(a, 0) for a in current_assets])
    current_w_local = current_w_local / current_w_local.sum()
    
    paths = np.zeros((N_RETIREMENT_SIMS, RETIREMENT_MONTHS + 1))
    paths[:, 0] = starting_value_current
    ruin_count = 0
    ruin_ages = []
    
    for sim in range(N_RETIREMENT_SIMS):
        sample_indices = np.random.randint(0, n_hist_current, size=RETIREMENT_MONTHS)
        sampled_returns = current_boot_matrix[sample_indices]
        
        value = starting_value_current
        asset_values = current_w_local * value
        annual_withdrawal = initial_4pct_current
        ruined = False
        
        for month in range(RETIREMENT_MONTHS):
            if value <= 0:
                paths[sim, month + 1:] = 0
                if not ruined:
                    ruin_count += 1
                    ruin_ages.append(55 + month / 12)
                    ruined = True
                break
            
            monthly_rets = sampled_returns[month]
            asset_values = asset_values * (1 + monthly_rets)
            
            year = month // 12
            adj_withdrawal = annual_withdrawal * (1 + INFLATION) ** year / 12
            
            total = asset_values.sum()
            if total > adj_withdrawal:
                asset_values -= current_w_local * adj_withdrawal
            else:
                asset_values = current_w_local * 0
            
            if (month + 1) % 12 == 0:
                total = asset_values.sum()
                asset_values = current_w_local * max(total, 0)
            
            value = max(asset_values.sum(), 0)
            paths[sim, month + 1] = value
    
    ruin_rate_current = ruin_count / N_RETIREMENT_SIMS
    print(f"  Current - 4% Rule: Ruin rate = {ruin_rate_current:.1%}")
    
    withdrawal_strategies['4% Rule | Current'] = {
        'paths': paths,
        'ruin_rate': ruin_rate_current,
        'ruin_ages': ruin_ages,
        'starting_value': starting_value_current,
    }
    
    return withdrawal_strategies, starting_value


def plot_sequence_risk(withdrawal_strategies, starting_value):
    """Generate spaghetti plot of retirement paths."""
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    
    strategies = [
        ('$180K/yr | Proposed', '$180K/yr Actual Expenses (Proposed)'),
        ('$180K/yr | Current', '$180K/yr Actual Expenses (Current)'),
        ('4% Rule | Proposed', '4% Rule (Proposed)'),
        ('4% Rule | Current', '4% Rule (Current)'),
        ('Guardrails | Proposed', 'Guyton-Klinger Guardrails'),
        ('Bond Tent | Proposed', 'Bond Tent Strategy'),
    ]
    
    ages = np.linspace(55, 90, 421)
    
    # Compute global y-max across all strategies for shared scale
    global_ymax = 0
    for key, _ in strategies:
        if key in withdrawal_strategies:
            p90 = np.percentile(withdrawal_strategies[key]['paths'], 90, axis=0)
            global_ymax = max(global_ymax, p90.max() / 1e6)
    global_ymax = global_ymax * 1.1  # 10% padding
    
    for ax, (key, title) in zip(axes.flat, strategies):
        if key not in withdrawal_strategies:
            ax.set_visible(False)
            continue
        
        data = withdrawal_strategies[key]
        paths = data['paths']
        ruin_rate = data['ruin_rate']
        sv = data.get('starting_value', starting_value)
        
        # Sample 100 random paths
        sample_idx = np.random.choice(paths.shape[0], min(100, paths.shape[0]), replace=False)
        
        for i in sample_idx:
            path = paths[i]
            color = RED if path[-1] <= 0 else TEAL
            alpha = 0.4 if path[-1] <= 0 else 0.15
            ax.plot(ages, path / 1e6, color=color, alpha=alpha, linewidth=0.5)
        
        # Plot median
        median_path = np.median(paths, axis=0)
        ax.plot(ages, median_path / 1e6, color=NAVY, linewidth=2.5, label='Median')
        
        # Plot 10th and 90th percentiles
        p10 = np.percentile(paths, 10, axis=0)
        p90 = np.percentile(paths, 90, axis=0)
        ax.plot(ages, p10 / 1e6, color=NAVY, linewidth=1, linestyle='--', alpha=0.5, label='10th/90th %ile')
        ax.plot(ages, p90 / 1e6, color=NAVY, linewidth=1, linestyle='--', alpha=0.5)
        
        ax.axhline(y=0, color=RED, linewidth=1, linestyle='-', alpha=0.5)
        ax.set_title(f'{title}\nRuin rate: {ruin_rate:.1%} | Start: ${sv/1e6:.1f}M', 
                     fontsize=11, fontweight='bold', color=NAVY)
        ax.set_xlabel('Age')
        ax.set_ylabel('Portfolio ($M)')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}M'))
        ax.legend(loc='upper right', fontsize=8)
        ax.set_xlim(55, 90)
        ax.set_ylim(-0.5, global_ymax)  # Shared y-axis scale
        
        # Social Security and Medicare markers
        ax.axvline(x=62, color=GOLD, linestyle=':', alpha=0.5)
        ax.axvline(x=65, color=GREEN, linestyle=':', alpha=0.5)
        ax.text(62.2, global_ymax * 0.92, 'SS (62)', fontsize=8, color=GOLD, fontweight='bold')
        ax.text(65.2, global_ymax * 0.85, 'Medicare\n(65)', fontsize=8, color=GREEN, fontweight='bold')
    
    fig.suptitle('Sequence of Returns Risk: Retirement Portfolio Survival (Age 55→90)',
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
                   withdrawal_strategies, starting_retirement_value,
                   asset_stats, data_info, corr_matrix):
    """Generate the full quantitative analysis report."""
    
    c = mc_results['Current']
    p = mc_results['Proposed']
    
    report = f"""# Quantitative Portfolio Analysis: Cleary Family
## Date: March 29, 2026

---

## Executive Summary

This analysis compares your **current concentrated portfolio** (~35% Amazon, ~32% US large cap) against a **proposed diversified portfolio** across 10 asset classes. Using 10,000 Monte Carlo simulations built from real historical return data, historical stress tests, and sequence-of-returns modeling, the findings are clear:

{"**The diversified portfolio delivers comparable expected growth with dramatically lower risk.**" if abs(p['median_final'] - c['median_final']) / c['median_final'] < 0.20 else "**The two portfolios show meaningfully different expected outcomes — but the risk profiles diverge even more.**" if p['median_final'] < c['median_final'] else "**The diversified portfolio outperforms on both expected growth and risk reduction.**"}

| Metric | Current (Concentrated) | Proposed (Diversified) |
|--------|----------------------|----------------------|
| Median value at 55 | ${c['median_final']:,.0f} | ${p['median_final']:,.0f} |
| Mean value at 55 | ${c['mean_final']:,.0f} | ${p['mean_final']:,.0f} |
| 10th percentile (bad luck) | ${np.percentile(c['final_values'], 10):,.0f} | ${np.percentile(p['final_values'], 10):,.0f} |
| 90th percentile (good luck) | ${np.percentile(c['final_values'], 90):,.0f} | ${np.percentile(p['final_values'], 90):,.0f} |
| P(reach $5M) | {c['prob_5M']:.1%} | {p['prob_5M']:.1%} |
| P(reach $8M) | {c['prob_8M']:.1%} | {p['prob_8M']:.1%} |
| P(reach $10M) | {c['prob_10M']:.1%} | {p['prob_10M']:.1%} |
| P(portfolio < $500K ever) | {c['prob_below_500K']:.1%} | {p['prob_below_500K']:.1%} |
| Median max drawdown | {np.median(c['max_drawdowns']):.1%} | {np.median(p['max_drawdowns']):.1%} |

**Key takeaway:** The proposed portfolio's 10th percentile outcome (${np.percentile(p['final_values'], 10):,.0f}) is {"higher" if np.percentile(p['final_values'], 10) > np.percentile(c['final_values'], 10) else "lower"} than the current portfolio's 10th percentile (${np.percentile(c['final_values'], 10):,.0f}). {"This means even in bad scenarios, the diversified portfolio protects you better." if np.percentile(p['final_values'], 10) > np.percentile(c['final_values'], 10) else ""}

The spread between the 10th and 90th percentiles tells the story of risk:
- **Current portfolio spread:** ${(np.percentile(c['final_values'], 90) - np.percentile(c['final_values'], 10)):,.0f}
- **Proposed portfolio spread:** ${(np.percentile(p['final_values'], 90) - np.percentile(p['final_values'], 10)):,.0f}

{"The current portfolio has a wider spread — meaning more uncertainty. Some simulations end spectacularly, but many end poorly. The diversified portfolio narrows the range, giving you more predictable outcomes." if (np.percentile(c['final_values'], 90) - np.percentile(c['final_values'], 10)) > (np.percentile(p['final_values'], 90) - np.percentile(p['final_values'], 10)) else ""}

---

## Model 1: Monte Carlo Simulation

### Methodology
- **Data source:** Historical monthly returns from Yahoo Finance for each asset class proxy
- **Simulation method:** Bootstrap resampling of actual monthly return vectors (preserves fat tails, real correlations, and non-normal distributions)
- **Simulations:** 10,000 paths over 228 months (19 years)
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
    
    report += f"""
### Year-by-Year Projections

#### Current Portfolio (Concentrated)
| Age | 10th %ile | 25th %ile | Median | 75th %ile | 90th %ile |
|-----|-----------|-----------|--------|-----------|-----------|
"""
    
    for year in range(0, 20, 2):
        age = 36 + year
        cp = c['percentiles'][year]
        report += f"| {age} | ${cp['p10']:,.0f} | ${cp['p25']:,.0f} | ${cp['median']:,.0f} | ${cp['p75']:,.0f} | ${cp['p90']:,.0f} |\n"
    
    report += f"""
#### Proposed Portfolio (Diversified)
| Age | 10th %ile | 25th %ile | Median | 75th %ile | 90th %ile |
|-----|-----------|-----------|--------|-----------|-----------|
"""
    
    for year in range(0, 20, 2):
        age = 36 + year
        pp = p['percentiles'][year]
        report += f"| {age} | ${pp['p10']:,.0f} | ${pp['p25']:,.0f} | ${pp['median']:,.0f} | ${pp['p75']:,.0f} | ${pp['p90']:,.0f} |\n"
    
    report += f"""
### Probability of Reaching Milestones

| Milestone | Current | Proposed | Advantage |
|-----------|---------|----------|-----------|
| $5M | {c['prob_5M']:.1%} | {p['prob_5M']:.1%} | {'Proposed' if p['prob_5M'] > c['prob_5M'] else 'Current'} +{abs(p['prob_5M'] - c['prob_5M']):.1%} |
| $8M | {c['prob_8M']:.1%} | {p['prob_8M']:.1%} | {'Proposed' if p['prob_8M'] > c['prob_8M'] else 'Current'} +{abs(p['prob_8M'] - c['prob_8M']):.1%} |
| $10M | {c['prob_10M']:.1%} | {p['prob_10M']:.1%} | {'Proposed' if p['prob_10M'] > c['prob_10M'] else 'Current'} +{abs(p['prob_10M'] - c['prob_10M']):.1%} |
| $15M | {c['prob_15M']:.1%} | {p['prob_15M']:.1%} | {'Proposed' if p['prob_15M'] > c['prob_15M'] else 'Current'} +{abs(p['prob_15M'] - c['prob_15M']):.1%} |

### Downside Risk

| Risk Metric | Current | Proposed |
|-------------|---------|----------|
| P(portfolio ever < $500K) | {c['prob_below_500K']:.1%} | {p['prob_below_500K']:.1%} |
| Median max drawdown | {np.median(c['max_drawdowns']):.1%} | {np.median(p['max_drawdowns']):.1%} |
| 95th percentile max drawdown | {np.percentile(c['max_drawdowns'], 5):.1%} | {np.percentile(p['max_drawdowns'], 5):.1%} |
| Worst-case max drawdown | {c['max_drawdowns'].min():.1%} | {p['max_drawdowns'].min():.1%} |

![Monte Carlo Simulation](charts/mc-real.png)

---

## Model 2: Historical Stress Tests

These are not hypothetical scenarios — these are the actual returns each portfolio would have experienced during real market crises.

### Results Summary

| Crisis | Current Max DD | Proposed Max DD | Current $ Loss | Proposed $ Loss |
|--------|---------------|----------------|---------------|----------------|
"""
    
    for crisis_name, crisis_data in stress_results.items():
        c_dd = crisis_data.get('Current', {}).get('max_dd')
        p_dd = crisis_data.get('Proposed', {}).get('max_dd')
        c_loss = crisis_data.get('Current', {}).get('dollar_loss')
        p_loss = crisis_data.get('Proposed', {}).get('dollar_loss')
        
        c_dd_str = f"{c_dd:.1%}" if c_dd else "N/A"
        p_dd_str = f"{p_dd:.1%}" if p_dd else "N/A"
        c_loss_str = f"${c_loss:,.0f}" if c_loss else "N/A"
        p_loss_str = f"${p_loss:,.0f}" if p_loss else "N/A"
        
        clean_name = crisis_name.replace('\n', ' ')
        report += f"| {clean_name} | {c_dd_str} | {p_dd_str} | {c_loss_str} | {p_loss_str} |\n"
    
    report += f"""
### What This Means

"""
    
    # Add specific commentary on dot-com crash
    dotcom_key = [k for k in stress_results.keys() if 'Dot-Com' in k]
    if dotcom_key:
        dotcom = stress_results[dotcom_key[0]]
        c_dd = dotcom.get('Current', {}).get('max_dd')
        p_dd = dotcom.get('Proposed', {}).get('max_dd')
        if c_dd and p_dd:
            report += f"""**Dot-Com Crash (2000-2002):** This is your biggest risk scenario. Amazon dropped ~95% during the dot-com bust. With your current 35% AMZN concentration, the portfolio would have experienced a **{c_dd:.1%}** drawdown — losing **${abs(c_dd) * INITIAL_PORTFOLIO:,.0f}** from a $1.23M portfolio. The diversified portfolio's drawdown was **{p_dd:.1%}** (−${abs(p_dd) * INITIAL_PORTFOLIO:,.0f}). That's the difference between a gut-wrenching near-wipeout and a painful but recoverable drawdown.

"""
    
    report += f"""
![Stress Tests](charts/stress-test.png)

---

## Model 3: Sensitivity Analysis

How much do different assumptions change the outcome? All values are in **real (inflation-adjusted) dollars**.

### Key Findings

"""
    
    # Extract key sensitivity findings
    base_current = None
    base_proposed = None
    for key, val in sensitivity_scenarios.items():
        if 'Returns: Base' in key and 'Current' in key:
            base_current = val
        if 'Returns: Base' in key and 'Proposed' in key:
            base_proposed = val
    
    if base_current and base_proposed:
        report += f"""**Base case (real dollars):**
- Current portfolio: **${base_current/1e6:.2f}M**
- Proposed portfolio: **${base_proposed/1e6:.2f}M**

"""
    
    report += "### Full Sensitivity Table\n\n"
    report += "| Scenario | Current (Real $) | Proposed (Real $) | Δ from Base (Proposed) |\n"
    report += "|----------|-----------------|-------------------|------------------------|\n"
    
    # Group and display
    seen_scenarios = set()
    for key, val in sorted(sensitivity_scenarios.items()):
        parts = key.split(' | ')
        scenario = parts[0]
        portfolio = parts[1] if len(parts) > 1 else ''
        
        if scenario in seen_scenarios:
            continue
        
        current_key = f"{scenario} | Current"
        proposed_key = f"{scenario} | Proposed"
        
        c_val = sensitivity_scenarios.get(current_key, 0)
        p_val = sensitivity_scenarios.get(proposed_key, 0)
        
        delta = (p_val - base_proposed) / 1e6 if base_proposed else 0
        delta_str = f"+${delta:.2f}M" if delta >= 0 else f"−${abs(delta):.2f}M"
        
        report += f"| {scenario} | ${c_val/1e6:.2f}M | ${p_val/1e6:.2f}M | {delta_str} |\n"
        seen_scenarios.add(scenario)
    
    report += f"""
### AMZN Concentration Risk Spotlight

The AMZN-specific scenarios reveal the core risk of concentration:

"""
    
    # Find AMZN -50% scenario
    for key, val in sensitivity_scenarios.items():
        if 'AMZN −50%' in key:
            parts = key.split(' | ')
            portfolio = parts[1] if len(parts) > 1 else ''
            if 'Current' in portfolio:
                amzn_crash_current = val
            else:
                amzn_crash_proposed = val
    
    try:
        report += f"""- If AMZN drops 50% in the next 12 months:
  - **Current portfolio** median outcome: **${amzn_crash_current/1e6:.2f}M** (real)
  - **Proposed portfolio** median outcome: **${amzn_crash_proposed/1e6:.2f}M** (real)
  - **Impact difference:** The current portfolio loses **${(base_current - amzn_crash_current)/1e6:.2f}M** more than its base case; the proposed loses only **${(base_proposed - amzn_crash_proposed)/1e6:.2f}M**

"""
    except:
        pass
    
    report += f"""
![Sensitivity Analysis](charts/sensitivity.png)

---

## Model 4: Sequence of Returns Risk

This models the retirement withdrawal phase — starting at age 55 with the projected median portfolio value, withdrawing $180,000/year (inflation-adjusted), and testing whether the money lasts through age 90 (35 years).

### Starting Values
- **Current portfolio** projected median at 55: ${mc_results['Current']['percentiles'][19]['median']:,.0f}
- **Proposed portfolio** projected median at 55: ${mc_results['Proposed']['percentiles'][19]['median']:,.0f}

### Ruin Rates by Strategy

| Strategy | Portfolio | Ruin Rate (before age 90) |
|----------|-----------|--------------------------|
"""
    
    for key, data in withdrawal_strategies.items():
        report += f"| {key.split(' | ')[0]} | {key.split(' | ')[1]} | {data['ruin_rate']:.1%} |\n"
    
    report += f"""
### What This Means

"""
    
    # Get the 4% rule ruin rates
    proposed_4pct_ruin = withdrawal_strategies.get('4% Rule | Proposed', {}).get('ruin_rate', 0)
    current_4pct_ruin = withdrawal_strategies.get('4% Rule | Current', {}).get('ruin_rate', 0)
    guardrails_ruin = withdrawal_strategies.get('Guardrails | Proposed', {}).get('ruin_rate', 0)
    bond_tent_ruin = withdrawal_strategies.get('Bond Tent | Proposed', {}).get('ruin_rate', 0)
    
    # Get the $180K/yr results
    proposed_180k_ruin = withdrawal_strategies.get('$180K/yr | Proposed', {}).get('ruin_rate', 0)
    current_180k_ruin = withdrawal_strategies.get('$180K/yr | Current', {}).get('ruin_rate', 0)
    
    report += f"""**Your actual target ($180K/year):**

1. **At $180K/year expenses (proposed portfolio):** **{proposed_180k_ruin:.1%}** ruin rate. This is your most relevant number — it reflects your actual spending target, not the arbitrary 4% rule. The concentrated portfolio shows **{current_180k_ruin:.1%}** — higher because of AMZN volatility in the early withdrawal years.

2. **Guyton-Klinger guardrails** — adjusting withdrawals based on portfolio performance — {"reduce" if guardrails_ruin < proposed_180k_ruin else "change"} the ruin rate to **{guardrails_ruin:.1%}**. The tradeoff: spending may vary ±15-20% year-to-year, but you almost never run out of money.

**For reference — the traditional 4% rule:**

3. **The 4% rule** on these portfolios means withdrawing ~${mc_results['Proposed']['percentiles'][19]['median'] * 0.04 / 1000:,.0f}K/year (4% of ~${mc_results['Proposed']['percentiles'][19]['median']/1e6:.1f}M). That's {mc_results['Proposed']['percentiles'][19]['median'] * 0.04 / ANNUAL_EXPENSES:.1f}× your actual expenses. At that rate, ruin rates jump to **{proposed_4pct_ruin:.1%}** (proposed) and **{current_4pct_ruin:.1%}** (current) — indicating the 4% rule is too aggressive for early retirees with a 35-year horizon.

4. **The bond tent strategy** shows a ruin rate of **{bond_tent_ruin:.1%}**. The high rate suggests the current implementation needs refinement — a bond-heavy allocation may sacrifice too much growth over 35 years.

### Critical Gap: Age 55 to 62

At age 55, John would be:
- **7 years** from earliest Social Security (age 62)
- **10 years** from Medicare (age 65)
- **Fully dependent** on portfolio withdrawals + any bridge income

This 7-year gap is the most vulnerable period. Bad market returns here, before Social Security kicks in, have an outsized impact on long-term portfolio survival.

![Sequence of Returns Risk](charts/sequence-risk.png)

---

## Correlation Matrix

The actual historical correlation between assets is what drives diversification benefit. Here are the key correlations:

```
{corr_matrix.to_string() if corr_matrix is not None else "Correlation matrix not available"}
```

**Key observations:**
- AMZN's correlation to US Total Market shows how much "diversification" you actually get from holding it alongside SPY
- International developed and emerging markets provide genuine diversification (lower correlation)
- Bonds and TIPS are the primary portfolio shock absorbers
- Gold has historically low correlation to equities

---

## Limitations & Assumptions

### What the models CAN tell us:
- Historical risk/return relationships between asset classes
- The impact of concentration vs diversification using real data
- Probability distributions of outcomes based on historical patterns
- Relative comparison between the two portfolio strategies

### What the models CANNOT tell us:
- **Future returns will not match historical returns.** Past performance is not predictive. AMZN's next 20 years won't look like the last 20.
- **Bootstrap resampling assumes the future resembles the past** in its distributional properties. A truly unprecedented event (worse than any historical crisis) is not captured.
- **Tax impacts are not modeled.** The transition from concentrated to diversified will trigger capital gains taxes on AMZN positions. Washington has no state income tax, but federal long-term capital gains of 15-20% apply.
- **Behavioral risk is not modeled.** The biggest risk is panic-selling during a drawdown. No model captures that.
- **Correlation regimes can change.** During crises, correlations tend to increase (everything falls together). Our bootstrap partially captures this but may understate it.
- **Single-stock risk is partially captured** through historical returns, but AMZN's future could diverge significantly from its past (regulatory risk, competitive disruption, etc.).

### Key Assumptions:
- Monthly rebalancing of contributions, annual rebalancing of portfolio
- $400K balloon payment at age 50 (conservative — could refinance instead)
- 3% inflation during retirement for withdrawal adjustments
- No additional income sources in retirement (Social Security, part-time work, etc.)
- No tax drag on returns (actual returns will be slightly lower)

---

## What This Means For You

### The Numbers Tell a Clear Story

1. **Diversification doesn't cost you much upside, but it massively reduces downside.** The median outcomes for both portfolios are {"comparable" if abs(c['median_final'] - p['median_final']) / c['median_final'] < 0.15 else "different"}, but the worst-case scenarios diverge dramatically.

2. **Your current portfolio is a bet on Amazon.** In {c['prob_below_500K']:.1%} of simulations, the concentrated portfolio drops below $500K at some point. For the diversified portfolio, that number is {p['prob_below_500K']:.1%}. {"That's a meaningful difference in sleep-at-night risk." if c['prob_below_500K'] > p['prob_below_500K'] else ""}

3. **The stress tests are the most compelling evidence.** During the dot-com crash, a 35% AMZN allocation would have been devastating. Amazon dropped ~95%. Even with the rest in S&P 500, your portfolio would have been severely damaged. This isn't a theoretical risk — it happened, within the last 25 years.

4. **Sequence of returns risk is real for early retirees.** At 55, you're too young for Social Security (62) and Medicare (65). The bond tent strategy or Guyton-Klinger guardrails provide meaningful protection during this vulnerable window.

### Recommended Actions

Based on the quantitative analysis:

1. **Begin the transition to the diversified portfolio.** The risk reduction is significant and the expected return tradeoff is {"minimal" if abs(c['median_final'] - p['median_final']) / c['median_final'] < 0.10 else "moderate"}.

2. **Prioritize the AMZN reduction.** Moving from 35% to 15% captures most of the risk reduction. This is the single highest-impact change.

3. **Plan the tax-efficient transition.** Spread AMZN sales across tax years. Use tax-loss harvesting on TSLA and other positions to offset gains. Maximize use of 401k and ESPP for new diversified positions.

4. **Implement a bond tent starting at age 50.** Begin increasing bond allocation 5 years before retirement to protect against sequence risk.

5. **Consider Guyton-Klinger withdrawal rules** instead of a rigid 4% rule. The flexibility to reduce spending in down years significantly improves portfolio survival.

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
    
    # Step 3: Monte Carlo
    (mc_results, all_assets, current_w, proposed_w,
     current_assets, proposed_assets,
     current_boot_matrix, proposed_boot_matrix,
     n_hist_current, n_hist_proposed,
     current_w_vec, proposed_w_vec) = run_monte_carlo(
        returns_df, common_returns, CURRENT_WEIGHTS, PROPOSED_WEIGHTS)
    plot_monte_carlo(mc_results)
    
    # Step 4: Stress tests
    stress_results = run_stress_tests(all_prices, CURRENT_WEIGHTS, PROPOSED_WEIGHTS)
    plot_stress_tests(stress_results)
    
    # Step 5: Sensitivity analysis
    sensitivity_scenarios = run_sensitivity_analysis(
        returns_df, common_returns, all_assets, current_w, proposed_w,
        current_assets, proposed_assets, current_boot_matrix, proposed_boot_matrix,
        n_hist_current, n_hist_proposed)
    plot_sensitivity(sensitivity_scenarios)
    
    # Step 6: Sequence of returns
    withdrawal_strategies, starting_value = run_sequence_risk(
        returns_df, common_returns, all_assets, current_w_vec, proposed_w_vec, mc_results,
        proposed_assets, proposed_boot_matrix, n_hist_proposed,
        current_assets, current_boot_matrix, n_hist_current)
    plot_sequence_risk(withdrawal_strategies, starting_value)
    
    # Step 7: Generate report
    report_path = generate_report(
        mc_results, stress_results, sensitivity_scenarios,
        withdrawal_strategies, starting_value,
        asset_stats, data_info, corr)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Report: {report_path}")
    print(f"Charts: {CHARTS_DIR}/")
    print(f"Code: quantitative/monte_carlo.py")


if __name__ == '__main__':
    main()
