#!/usr/bin/env python3
"""
AI Timeline Analysis for Amazon (AMZN)
Analyzing when the AI bet will pay off with specific monitoring points
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
import pandas as pd

def analyze_amzn_ai_timeline():
    print("=== AMAZON AI BET TIMELINE ANALYSIS ===")
    print("Analysis Date:", datetime.now().strftime("%Y-%m-%d"))
    
    # Get latest AMZN data
    amzn = yf.Ticker("AMZN")
    info = amzn.info
    hist = amzn.history(period="2y")
    financials = amzn.financials
    cashflow = amzn.cashflow
    quarterly_financials = amzn.quarterly_financials
    quarterly_cashflow = amzn.quarterly_cashflow

    print("\n=== CURRENT FINANCIAL POSITION ===")
    current_price = info.get('currentPrice', 'N/A')
    market_cap = info.get('marketCap', 0)
    print(f"Current Price: ${current_price}")
    if market_cap:
        print(f"Market Cap: ${market_cap/1e12:.2f}T")
    print(f"Forward P/E: {info.get('forwardPE', 'N/A')}")
    
    total_revenue = info.get('totalRevenue', 0)
    if total_revenue:
        print(f"Revenue TTM: ${total_revenue/1e9:.1f}B")

    print("\n=== RECENT QUARTERLY TRENDS ===")
    if not quarterly_financials.empty and 'Total Revenue' in quarterly_financials.index:
        revenue_data = quarterly_financials.loc['Total Revenue'].dropna()
        print("Quarterly Revenue:")
        for date, revenue in revenue_data.head(8).items():
            quarter = ((date.month - 1) // 3) + 1
            print(f"  {date.year}-Q{quarter}: ${revenue/1e9:.1f}B")

    print("\n=== CAPEX INVESTMENT CYCLE ===")
    if not quarterly_cashflow.empty and 'Capital Expenditure' in quarterly_cashflow.index:
        capex_data = quarterly_cashflow.loc['Capital Expenditure'].dropna()
        print("Quarterly CapEx (AI-heavy period):")
        for date, capex in capex_data.head(8).items():
            quarter = ((date.month - 1) // 3) + 1
            print(f"  {date.year}-Q{quarter}: ${abs(capex)/1e9:.1f}B")

    print("\n=== FREE CASH FLOW PRESSURE ===")
    if not quarterly_cashflow.empty and 'Free Cash Flow' in quarterly_cashflow.index:
        fcf_data = quarterly_cashflow.loc['Free Cash Flow'].dropna()
        print("Quarterly FCF:")
        for date, fcf in fcf_data.head(8).items():
            quarter = ((date.month - 1) // 3) + 1
            print(f"  {date.year}-Q{quarter}: ${fcf/1e9:.1f}B")

    # Calculate key ratios
    print("\n=== AI INVESTMENT IMPACT ANALYSIS ===")
    if not quarterly_financials.empty and not quarterly_cashflow.empty:
        try:
            # Get most recent quarter data
            latest_revenue = quarterly_financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in quarterly_financials.index else None
            latest_capex = quarterly_cashflow.loc['Capital Expenditure'].iloc[0] if 'Capital Expenditure' in quarterly_cashflow.index else None
            latest_fcf = quarterly_cashflow.loc['Free Cash Flow'].iloc[0] if 'Free Cash Flow' in quarterly_cashflow.index else None
            
            if latest_revenue and latest_capex:
                capex_as_pct_revenue = abs(latest_capex) / latest_revenue * 100
                print(f"Latest Quarter CapEx as % of Revenue: {capex_as_pct_revenue:.1f}%")
            
            if latest_fcf:
                print(f"Latest Quarter FCF: ${latest_fcf/1e9:.1f}B")
                
        except Exception as e:
            print(f"Error calculating ratios: {e}")

    print("\n=== HISTORICAL PRECEDENT: AWS INVESTMENT CYCLE ===")
    print("AWS was launched in 2006, became profitable by 2014 (8-year cycle)")
    print("Key milestones:")
    print("  2006-2010: Heavy investment, minimal revenue")
    print("  2011-2013: Revenue acceleration, margin pressure")
    print("  2014-2016: Profitability breakthrough, margin expansion")
    print("  2017+: Sustained high-margin growth")
    
    return {
        'current_price': current_price,
        'market_cap': market_cap,
        'analysis_date': datetime.now().isoformat()
    }

if __name__ == "__main__":
    result = analyze_amzn_ai_timeline()
    print(f"\nAnalysis completed: {result}")