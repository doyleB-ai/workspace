#!/usr/bin/env python3
"""Generate all charts for the Comprehensive Financial Plan."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

# Output directory
CHARTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Consistent style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
})

# ============================================================
# CHART 1: Current Portfolio Allocation (Pie Chart)
# ============================================================
def chart_current_allocation():
    labels = [
        'AMZN (Direct)',
        'S&P 500 / US Large Cap',
        'TSLA',
        'Other Stocks',
        'Bonds / Fixed Income',
        'Gold (GLD)',
        'Crypto (BTC)',
        'Cash / HYSA',
        'Schwab Robo',
        'Other (HSA, misc)',
    ]
    # Calculating remainder for "Other"
    known = 431453 + 389000 + 43372 + 30000 + 35000 + 19373 + 7000 + 21848 + 27583
    total = 1253735
    other = total - known
    
    values = [431453, 389000, 43372, 30000, 35000, 19373, 7000, 21848, 27583, other]
    
    # Colors: AMZN bright red, rest muted professional
    colors = [
        '#DC2626',   # AMZN - bright red
        '#6B7280',   # S&P 500 - gray
        '#9CA3AF',   # TSLA - lighter gray
        '#B0BEC5',   # Other stocks - blue-gray
        '#78909C',   # Bonds - steel
        '#D4A843',   # Gold - muted gold
        '#F59E0B',   # Crypto - amber
        '#A7C4BC',   # Cash - sage
        '#8DA0CB',   # Schwab Robo - periwinkle
        '#CFD8DC',   # Other - light gray
    ]
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    
    # Explode the AMZN slice slightly
    explode = [0.05] + [0] * (len(values) - 1)
    
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='',
        colors=colors, explode=explode,
        startangle=90, pctdistance=0.75,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )
    
    # Add percentage labels manually for readability
    total_val = sum(values)
    legend_labels = []
    for i, (label, val) in enumerate(zip(labels, values)):
        pct = val / total_val * 100
        if pct >= 1.5:
            legend_labels.append(f'{label}: {pct:.1f}%')
        else:
            legend_labels.append(f'{label}: {pct:.1f}%')
    
    ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1.0, 0.5),
              fontsize=9, frameon=False)
    
    ax.set_title('Current Portfolio Allocation', fontsize=16, fontweight='bold', pad=20)
    
    # Add warning annotation
    ax.annotate('35% single-stock\nconcentration in AMZN',
                xy=(0.05, -0.02), fontsize=9, color='#DC2626', fontweight='bold',
                ha='center', va='center')
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'current-allocation.png'))
    plt.close(fig)
    print("✓ current-allocation.png")


# ============================================================
# CHART 2: Recommended Target Allocation (Pie Chart)
# ============================================================
def chart_proposed_allocation():
    labels = [
        'VTI / US Total Market',
        'AMZN (Retained)',
        'VXUS / Int\'l Developed',
        'AVUV / US Small Cap Value',
        'AVDV / Int\'l SCV',
        'VWO / Emerging Markets',
        'VNQ / REITs',
        'BND / US Bonds',
        'SCHP / TIPS',
        'GLDM / Gold',
    ]
    values = [35, 15, 15, 10, 5, 5, 5, 5, 3, 2]
    
    colors = [
        '#2563EB',   # VTI - blue
        '#3B82F6',   # AMZN - moderate blue (not alarming)
        '#10B981',   # VXUS - green
        '#6366F1',   # AVUV - indigo
        '#8B5CF6',   # AVDV - purple
        '#14B8A6',   # VWO - teal
        '#F97316',   # VNQ - orange
        '#64748B',   # BND - slate
        '#94A3B8',   # SCHP - light slate
        '#D4A843',   # GLDM - gold
    ]
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    
    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='',
        colors=colors, startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
    )
    
    legend_labels = [f'{label}: {val}%' for label, val in zip(labels, values)]
    
    ax.legend(wedges, legend_labels, loc='center left', bbox_to_anchor=(1.0, 0.5),
              fontsize=9, frameon=False)
    
    ax.set_title('Recommended Target Allocation', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'proposed-allocation.png'))
    plt.close(fig)
    print("✓ proposed-allocation.png")


# ============================================================
# CHART 3: Monte Carlo Retirement Projections
# ============================================================
def chart_monte_carlo():
    years = np.arange(0, 20)  # 0 to 19
    ages = np.arange(36, 56)
    start_val = 1.23  # $M
    
    # End-point data (year 19)
    # Recommended portfolio
    rec = {
        'p10': 9.2, 'p25': 10.8, 'p50': 12.9, 'p75': 15.3, 'p90': 18.0
    }
    # Current portfolio
    cur = {
        'p10': 6.0, 'p25': 8.0, 'p50': 10.4, 'p75': 13.0, 'p90': 16.0
    }
    
    def log_normal_path(start, end, n_years):
        """Generate a smooth log-normal interpolation."""
        if end <= 0 or start <= 0:
            return np.linspace(start, end, n_years)
        t = np.linspace(0, 1, n_years)
        log_start = np.log(start)
        log_end = np.log(end)
        return np.exp(log_start + (log_end - log_start) * t)
    
    # Generate paths
    n = len(years)
    rec_paths = {k: log_normal_path(start_val, v, n) for k, v in rec.items()}
    cur_paths = {k: log_normal_path(start_val, v, n) for k, v in cur.items()}
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    
    # Current portfolio (red tones) - draw first (behind)
    ax.fill_between(ages, cur_paths['p10'], cur_paths['p90'],
                    alpha=0.10, color='#EF4444', label='Current: 10th–90th percentile')
    ax.fill_between(ages, cur_paths['p25'], cur_paths['p75'],
                    alpha=0.18, color='#EF4444', label='Current: 25th–75th percentile')
    ax.plot(ages, cur_paths['p50'], color='#DC2626', linewidth=2.0,
            linestyle='--', label='Current: Median')
    
    # Recommended portfolio (blue/green tones) - draw on top
    ax.fill_between(ages, rec_paths['p10'], rec_paths['p90'],
                    alpha=0.10, color='#2563EB', label='Recommended: 10th–90th percentile')
    ax.fill_between(ages, rec_paths['p25'], rec_paths['p75'],
                    alpha=0.20, color='#2563EB', label='Recommended: 25th–75th percentile')
    ax.plot(ages, rec_paths['p50'], color='#1D4ED8', linewidth=2.5,
            label='Recommended: Median')
    
    ax.set_title('Portfolio Projection: Current vs. Recommended (19 Years)',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Age', fontsize=12)
    ax.set_ylabel('Portfolio Value ($M)', fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))
    ax.set_xlim(36, 55)
    ax.set_ylim(0, 20)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add end-point annotations
    ax.annotate(f'${rec["p50"]:.1f}M', xy=(55, rec['p50']),
                xytext=(55.3, rec['p50']), fontsize=9, color='#1D4ED8', fontweight='bold',
                va='center')
    ax.annotate(f'${cur["p50"]:.1f}M', xy=(55, cur['p50']),
                xytext=(55.3, cur['p50']), fontsize=9, color='#DC2626', fontweight='bold',
                va='center')
    
    # Compact legend
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'monte-carlo.png'))
    plt.close(fig)
    print("✓ monte-carlo.png")


# ============================================================
# CHART 4: Tax Cost of Selling AMZN (Waterfall)
# ============================================================
def chart_tax_cost():
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    
    categories = ['Gross Proceeds', 'Tax Cost', 'Net Proceeds']
    values = [99670, -4597, 95073]
    
    # Waterfall: stacked bars
    bar_bottoms = [0, 95073, 0]
    bar_heights = [99670, 4597, 95073]
    bar_colors = ['#10B981', '#DC2626', '#2563EB']
    
    bars = ax.bar(categories, bar_heights, bottom=bar_bottoms, color=bar_colors,
                  width=0.5, edgecolor='white', linewidth=1.5)
    
    # Add value labels
    ax.text(0, 99670 / 2, f'${99670:,.0f}', ha='center', va='center',
            fontsize=14, fontweight='bold', color='white')
    ax.text(1, 95073 + 4597 / 2, f'${4597:,.0f}\n(4.6%)', ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')
    ax.text(2, 95073 / 2, f'${95073:,.0f}', ha='center', va='center',
            fontsize=14, fontweight='bold', color='white')
    
    # Add connector line
    ax.plot([0.25, 1.25], [99670, 99670], color='#9CA3AF', linewidth=1, linestyle='--')
    
    ax.set_title('Tax Impact: Selling 500 AMZN Shares', fontsize=14, fontweight='bold')
    ax.set_ylabel('Amount ($)', fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_ylim(0, 115000)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Subtitle annotation
    ax.annotate('You keep 95.4¢ of every dollar sold', xy=(1, -0.12),
                xycoords='axes fraction', ha='center', fontsize=10,
                color='#374151', fontstyle='italic')
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, 'tax-cost.png'))
    plt.close(fig)
    print("✓ tax-cost.png")


# ============================================================
# CHART 5: 529 Plan Projections
# ============================================================
def chart_529_projection():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    
    annual_return = 0.07
    monthly_return = (1 + annual_return) ** (1/12) - 1
    
    def project_529(current_balance, monthly_contrib, years):
        months = years * 12
        balances = [current_balance]
        for m in range(1, months + 1):
            bal = balances[-1] * (1 + monthly_return) + monthly_contrib
            balances.append(bal)
        # Convert to yearly for plotting
        yearly = [balances[y * 12] for y in range(years + 1)]
        return yearly
    
    max_years = 17
    years_range = np.arange(0, max_years + 1)
    
    # Child 1: age 3, 15 years to college
    c1_200 = project_529(17451, 200, 15)
    c1_400 = project_529(17451, 400, 15)
    
    # Child 2: age 1, 17 years to college
    c2_200 = project_529(8619, 200, 17)
    c2_400 = project_529(8619, 400, 17)
    
    # Pad child 1 data with NaN for years 16-17
    c1_200_padded = c1_200 + [np.nan] * 2
    c1_400_padded = c1_400 + [np.nan] * 2
    
    # Plot lines
    ax.plot(years_range, c1_200_padded, color='#DC2626', linewidth=2, linestyle='--',
            label='Child 1 @ $200/mo', marker='o', markersize=0)
    ax.plot(years_range, c1_400_padded, color='#DC2626', linewidth=2.5,
            label='Child 1 @ $400/mo', marker='o', markersize=0)
    ax.plot(years_range, c2_200, color='#2563EB', linewidth=2, linestyle='--',
            label='Child 2 @ $200/mo', marker='o', markersize=0)
    ax.plot(years_range, c2_400, color='#2563EB', linewidth=2.5,
            label='Child 2 @ $400/mo', marker='o', markersize=0)
    
    # College cost bands
    ax.axhspan(120000, 160000, alpha=0.12, color='#10B981',
               label='In-State Public 4-Year ($120K–$160K)')
    ax.axhspan(350000, 450000, alpha=0.08, color='#F59E0B',
               label='Private 4-Year ($350K–$450K)')
    
    # End-point labels
    ax.annotate(f'${c1_200[-1]/1000:.0f}K', xy=(15, c1_200[-1]),
                xytext=(15.3, c1_200[-1]), fontsize=9, color='#DC2626', va='center')
    ax.annotate(f'${c1_400[-1]/1000:.0f}K', xy=(15, c1_400[-1]),
                xytext=(15.3, c1_400[-1]), fontsize=9, color='#DC2626',
                fontweight='bold', va='center')
    ax.annotate(f'${c2_200[-1]/1000:.0f}K', xy=(17, c2_200[-1]),
                xytext=(17.3, c2_200[-1]), fontsize=9, color='#2563EB', va='center')
    ax.annotate(f'${c2_400[-1]/1000:.0f}K', xy=(17, c2_400[-1]),
                xytext=(17.3, c2_400[-1]), fontsize=9, color='#2563EB',
                fontweight='bold', va='center')
    
    ax.set_title('529 Plan Projections: Current vs. Increased Contributions',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Years from Now', fontsize=12)
    ax.set_ylabel('Balance ($)', fontsize=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.0f}K'))
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 500000)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    
    plt.tight_layout()
    fig.savefig(os.path.join(CHARTS_DIR, '529-projection.png'))
    plt.close(fig)
    print("✓ 529-projection.png")


# ============================================================
# Run all charts
# ============================================================
if __name__ == '__main__':
    chart_current_allocation()
    chart_proposed_allocation()
    chart_monte_carlo()
    chart_tax_cost()
    chart_529_projection()
    print("\nAll charts generated successfully!")
