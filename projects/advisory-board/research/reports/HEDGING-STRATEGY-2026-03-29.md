# Hedging Strategy Report: The Mark Cuban Question

**Date:** March 29, 2026
**Prepared for:** Advisory Board — Fiduciary Review
**Client:** John | Age 36 | MFJ | California Resident | Amazon L5
**Subject:** "Can I hedge my AMZN like Mark Cuban hedged Yahoo?"
**AMZN Price at Analysis:** $199.34

---

## FIDUCIARY NOTICE

This report analyzes hedging strategies for a concentrated AMZN position. The client holds 2,164 vested shares (~$431K), plus ~$354K in unvested RSUs, and is a current Amazon employee. **This analysis is educational and strategic — not trade execution advice. The client should consult with a securities attorney and tax professional before implementing any options strategy.** Options involve significant risk, including the risk of loss of the entire premium paid.

---

## EXECUTIVE SUMMARY

**The short answer: No, you shouldn't do what Cuban did. Your situation is fundamentally different, and a collar adds complexity that isn't justified by your modest embedded gains.**

Mark Cuban used a costless collar because he *had no choice* — he was locked up, couldn't sell, and had $1.4 billion at risk. The collar was the only tool available. It was brilliant for his situation.

Your situation is different in every way that matters:
- **You CAN sell.** No lockup.
- **Your embedded gain is modest.** ~$42/share ($91K total) vs. Cuban's hundreds of millions.
- **The tax cost of selling is tiny.** ~$6,900 per 500 shares (6.9% of proceeds).
- **A collar adds complexity** — constructive sale risk, Amazon Legal preclearance, rolling costs, and tax complications — for marginal benefit.

**Our recommendation:** Sell shares directly. The tax "savings" from a collar vs. selling are ~$6,900 per 500 shares — that's less than one RSU vest. The collar's complexity isn't worth it at your gain levels. However, we detail every strategy below so you can understand the mechanics and make an informed decision.

**One exception where a collar COULD make sense:** If you're very bullish short-term but want crash protection, a 6-12 month collar on a portion of your holdings (say 1,000 shares) while you execute a gradual selling program on the rest could provide psychological comfort during the transition. We detail this hybrid approach in Section 6.

---

## TABLE OF CONTENTS

1. [Mark Cuban's Strategy — What He Actually Did](#1-mark-cubans-strategy)
2. [Hedging Strategies Available to John](#2-hedging-strategies)
3. [Critical Tax and Legal Issues](#3-tax-and-legal-issues)
4. [John's Situation vs. Cuban's](#4-comparison)
5. [Practical Implementation](#5-practical-implementation)
6. [Recommendation](#6-recommendation)

---

## 1. MARK CUBAN'S STRATEGY

### The Setup

In April 1999, Yahoo acquired Mark Cuban's company Broadcast.com for $5.7 billion in Yahoo stock. Cuban received approximately **14.6 million shares of Yahoo**, trading at ~$95/share, giving him a position worth roughly **$1.4 billion**.

The critical constraint: Cuban was subject to a **lockup period** and couldn't sell. He also had an essentially **zero cost basis** — as a co-founder of Broadcast.com, his shares had negligible original cost. Selling (if he could) would have triggered an enormous capital gains tax bill — potentially $200-300M+ at the time.

### What He Did: The Costless Collar

Cuban executed what's become one of the most famous hedging trades in history:

**For each 100 shares of Yahoo stock:**
- **Bought 1 put option** at a **$85 strike price** (~11% below market)
- **Sold 1 call option** at a **$205 strike price** (~116% above market)
- **Expiration:** 3 years out
- **Net cost:** $0 (the call premium paid for the put premium — hence "costless")

**In total:** 146,000 put contracts + 146,000 call contracts covering all 14.6 million shares.

### How It Worked Mechanically

| If Yahoo at Expiration... | What Happens | Cuban's Outcome |
|---------------------------|--------------|-----------------|
| Below $85 (e.g., $13) | Put is exercised — shares sold at $85 | Gets $85/share = ~$1.24B (protected) |
| Between $85 and $205 | Both options expire worthless | Keeps shares at market value |
| Above $205 | Call is exercised — shares called away at $205 | Gets $205/share = ~$2.99B (capped) |

### What Actually Happened

Yahoo went on a parabolic run:
- **January 2000:** Yahoo hit **$237/share** — Cuban's position was theoretically worth $3.46B, but his upside was capped at $205. At that moment, the collar "cost" him $460M in paper gains.
- **2000-2002:** The dot-com bubble burst. Yahoo crashed **97%** from peak.
- **Late 2002:** Yahoo hit **$13/share** — his unprotected position would have been worth just $190M.

**Cuban's collar floor of $85 saved him over $1 billion.** While others watched their Yahoo fortunes evaporate, Cuban locked in ~$1.24 billion minimum.

The collar wasn't just smart — it was the *only rational move* given his constraints. He couldn't sell, the position was too large to hedge conventionally, and the downside risk was catastrophic.

### Key Lesson

Cuban's collar worked because:
1. He **couldn't sell** (lockup)
2. The **tax cost of selling was enormous** (near-zero basis → massive capital gains)
3. The **position was so large** that the collar's complexity was trivially small relative to the dollars protected
4. He was hedging against a **binary outcome** in a clearly speculative market

---

## 2. HEDGING STRATEGIES AVAILABLE TO JOHN

### Current Position

| Metric | Value |
|--------|-------|
| Vested shares | 2,164 (1,944 Fidelity TOD + 220 ESPP) |
| Current price | $199.34 |
| Position value | ~$431,453 |
| Average cost basis | ~$157/share |
| Embedded gain | ~$42/share (~$91K total) |
| Contracts needed | 21-22 contracts (100 shares each) |

### Strategy A: Costless Collar (Cuban's Strategy)

**How it works:** Buy protective puts (floor) + sell covered calls (cap) = net cost ≈ $0.

Using live AMZN options data pulled March 28, 2026:

#### 6-Month Collar (September 18, 2026 — 173 days)

| Put Strike | Put Cost | Call Strike | Call Premium | Net/Share | Net Total | Floor | Cap |
|-----------|----------|-------------|-------------|-----------|-----------|-------|-----|
| $175 | $10.73 | $225 | $12.70 | **-$1.97 (credit)** | **+$4,274** | -12% | +13% |
| $180 | $12.23 | $230 | $11.10 | +$1.12 (debit) | -$2,434 | -10% | +15% |
| $175 | $10.73 | $220 | $14.50 | **-$3.78 (credit)** | **+$8,169** | -12% | +10% |
| $170 | $9.28 | $215 | $16.45 | **-$7.17 (credit)** | **+$15,527** | -15% | +8% |

#### 12-Month Collar (March 19, 2027 — 355 days)

| Put Strike | Put Cost | Call Strike | Call Premium | Net/Share | Net Total | Floor | Cap |
|-----------|----------|-------------|-------------|-----------|-----------|-------|-----|
| $180 | $18.03 | $240 | $18.13 | **-$0.10 (credit)** | **+$216** | -10% | +20% |
| $175 | $16.15 | $230 | $21.30 | **-$5.15 (credit)** | **+$11,145** | -12% | +15% |
| $185 | $20.00 | $250 | $15.33 | +$4.68 (debit) | -$10,117 | -7% | +25% |

#### ⭐ Best Costless Collar: 12-Month $180P / $240C

This is the "Mark Cuban" trade adapted for John:

- **Floor:** $180/share (-10% from current)
- **Cap:** $240/share (+20% from current)
- **Net cost:** Essentially $0 (actually a tiny $0.10/share credit)
- **Duration:** 12 months (March 2027)
- **Contracts needed:** 21 (covering 2,100 of 2,164 shares)

**What this means:**

| Scenario | AMZN Price | Unhedged P&L | Collared P&L | Collar Benefit |
|----------|-----------|-------------|-------------|----------------|
| 30% crash | $140 | -$128,418 | -$41,174* | **+$87,244 saved** |
| 20% drop | $160 | -$84,932 | -$41,174* | **+$43,758 saved** |
| 10% drop | $180 | -$41,447 | -$41,174* | Roughly equal |
| Flat | $199 | $0 | $0 | No difference |
| 10% rally | $220 | +$44,671 | +$44,671 | No difference |
| 20% rally | $240 | +$87,899 | +$87,899 | No difference (at cap) |
| 30% rally | $260 | +$131,126 | +$87,899** | **-$43,227 missed** |
| 50% rally | $300 | +$217,580 | +$87,899** | **-$129,681 missed** |

*Floor: Maximum loss capped at ($199.34 - $180) × 2,100 = $40,614
**Cap: Maximum gain capped at ($240 - $199.34) × 2,100 = $85,386

**The collar protects you below $180 but caps you at $240.** In a 2022-style AMZN crash (-50%), this saves you ~$170K. In a big rally, you leave money on the table.

#### Liquidity Considerations

The AMZN options chain is liquid but not *infinitely* liquid at every strike:

| Expiration | Put Strike | Open Interest | Call Strike | Open Interest |
|-----------|-----------|---------------|-------------|---------------|
| Sep 2026 | $180 | 11,524 | $230 | 5,103 |
| Sep 2026 | $175 | 7,307 | $225 | 3,938 |
| Mar 2027 | $180 | 171 | $240 | 114 |

The 6-month options have significantly better liquidity. The 12-month options at $180P/$240C have only ~114-171 open interest — executing 21 contracts would represent ~12-18% of current open interest. This is feasible but you might face wider spreads on entry. Consider:
- Breaking the order into 3-5 lots over a few days
- Using limit orders at the midpoint
- The 6-month collar (Sep) has much better liquidity if you can stomach rolling every 6 months

---

### Strategy B: Protective Puts Only (Insurance)

**How it works:** Buy puts without selling calls. Pure insurance — unlimited upside preserved, but you pay real money.

| Description | Put Price | Total Cost | % of Position | Protected Below |
|------------|----------|-----------|---------------|-----------------|
| 6mo $180P (Sep 2026) | $12.23 | **$26,455** | 6.1% | $180 |
| 6mo $175P (Sep 2026) | $10.73 | **$23,209** | 5.4% | $175 |
| 6mo $170P (Sep 2026) | $9.28 | **$20,071** | 4.7% | $170 |
| 6mo $190P (Sep 2026) | $15.95 | **$34,516** | 8.0% | $190 |
| 12mo $180P (Mar 2027) | $18.03 | **$39,006** | 9.0% | $180 |
| 12mo $175P (Mar 2027) | $16.15 | **$34,949** | 8.1% | $175 |
| 12mo $185P (Mar 2027) | $20.00 | **$43,280** | 10.0% | $185 |

**The math problem:** Protecting 2,164 shares for 12 months at the $180 strike costs **$39,006**. That's 9% of the position value. If AMZN doesn't crash, you lose $39K. If it goes up 20%, you made $86K but spent $39K on insurance, netting only $47K.

**Compare to just selling 500 shares:**
- Tax cost: $6,872 (one-time)
- Permanently reduces risk
- No expiration, no rolling cost

Protective puts are essentially **paying $39K/year for insurance** vs. a **one-time $6,872 "fee" to permanently reduce the position.** The put makes sense only if you're very bullish AND very worried about a short-term crash — a contradictory position.

**When puts make sense:** If you have a specific event risk (e.g., you believe Q1 earnings could cause a 20%+ move but don't want to sell before it), buying puts for 1-2 months around that event can be rational. The cost is much lower for shorter durations.

---

### Strategy C: Prepaid Variable Forward Contract (PVFC)

**How it works:** A more sophisticated version of the collar, typically structured as an OTC contract with an investment bank. You receive cash upfront in exchange for delivering a variable number of shares at a future date.

**Mechanics:**
1. You pledge your shares to a counterparty (investment bank)
2. You receive an upfront cash payment (~80-90% of share value)
3. At settlement (typically 3-5 years), you deliver shares based on a formula:
   - If stock is below the "floor": deliver all pledged shares
   - If stock is between floor and cap: deliver shares worth the upfront payment
   - If stock is above the "cap": deliver fewer shares (keeping the upside above cap)

**Tax treatment:** Per Revenue Ruling 2003-7, a properly structured PVFC is NOT a sale for tax purposes and NOT a constructive sale under IRC §1259, provided:
- The collar band has "significant variation" (typically 20-25%+ spread)
- You retain voting rights and dividends
- You have the legal right to settle in cash or different shares (not economically compelled to deliver pledged shares)

**Who offers it:** Goldman Sachs, Morgan Stanley, JPMorgan, UBS — for positions typically **$5M+**.

**Why it doesn't work for John:**
- **Minimum position size:** Most banks require $5-10M+ for custom PVFCs
- **John's position ($431K) is far too small** — banks won't structure this
- **Fees:** 0.5-1.5% annually on the notional, plus structuring fees
- **Complexity:** Requires specialized tax and legal counsel
- **Duration:** 3-5 year lock-up is longer than a simple sell program

**Verdict: Not applicable.** This is a tool for the ultra-wealthy. Cuban's position ($1.4B) was in the right range. John's ($431K) is not.

---

### Strategy D: Covered Calls Only (Income + Partial Hedge)

**How it works:** Sell call options against your shares. You collect premium income, which provides a small buffer against decline, but you have NO downside floor.

| Description | Premium/Share | Total Income | % of Position | Called Away At |
|------------|--------------|-------------|---------------|---------------|
| 6mo $220C (Sep) | $14.50 | **$31,378** | 7.3% | $220 |
| 6mo $230C (Sep) | $11.10 | **$24,020** | 5.6% | $230 |
| 6mo $240C (Sep) | $8.38 | **$18,124** | 4.2% | $240 |
| 6mo $250C (Sep) | $6.23 | **$13,471** | 3.1% | $250 |
| 12mo $230C (Mar 2027) | $21.30 | **$46,093** | 10.7% | $230 |
| 12mo $240C (Mar 2027) | $18.13 | **$39,222** | 9.1% | $240 |
| 12mo $250C (Mar 2027) | $15.33 | **$33,163** | 7.7% | $250 |

**The appeal:** Selling 12-month $240 calls generates $39K in income. That's real cash.

**The problems:**
1. **No downside protection.** If AMZN drops 30%, you lose $128K minus the $39K premium = net loss of $89K. A collar would have limited your loss to ~$41K.
2. **Upside is capped.** If AMZN rallies to $300, your shares are called away at $240 and you miss $60/share ($126K) in upside.
3. **Tax treatment:** The premium received is short-term capital gain (ordinary income rates) regardless of how long you've held the shares. If the call is exercised, the premium is added to the sale price.
4. **Not really a hedge.** This is an income strategy that works best in flat-to-slightly-up markets. It's the wrong tool if your goal is crash protection.

**When covered calls make sense:** If you've already decided to sell at a certain price and want to get paid while you wait. Selling $240 calls is like saying "I'd happily sell at $240" and getting paid $18/share for that commitment.

---

### Strategy Comparison Matrix

| Factor | Costless Collar | Protective Put | PVFC | Covered Calls | Direct Sale |
|--------|---------------|----------------|------|---------------|-------------|
| Downside protection | ✅ Full below floor | ✅ Full below floor | ✅ Full below floor | ❌ None | ✅ Eliminated |
| Upside participation | ⚠️ Capped | ✅ Unlimited | ⚠️ Capped | ⚠️ Capped | ❌ None |
| Cost | ~$0 | $20-43K/yr | N/A | Generates income | Tax: ~$6,900/500 shares |
| Complexity | Moderate | Low | Very High | Low | Very Low |
| Tax complications | High (§1259 risk) | Low | High | Moderate | Low |
| Ongoing management | Rolling every 6-12mo | Rolling every 6-12mo | None (3-5yr) | Rolling every 6-12mo | None |
| Available to John? | ✅ Yes (with preclearance) | ✅ Yes | ❌ Position too small | ✅ Yes | ✅ Yes |
| Amazon Legal approval needed? | ✅ Yes | ✅ Yes | N/A | ✅ Yes | No (standard sell) |

---

## 3. CRITICAL TAX AND LEGAL ISSUES

### A. Constructive Sale Rules (IRC Section 1259)

**The big risk with collars.** Section 1259 says that if you enter into a transaction that eliminates "substantially all" risk of loss AND opportunity for gain on an appreciated position, it's treated as if you sold the stock — triggering immediate capital gains tax.

**What triggers a constructive sale:**
- Short sale against the box (selling short shares you also own)
- Forward contracts to deliver owned shares at a fixed price
- **A collar that is "too tight"** — where the put and call strikes are so close together that you've essentially locked in a fixed price

**How wide does the collar need to be?**

There is no bright-line statutory test. However:

1. **Revenue Ruling 2003-7** blessed a variable prepaid forward with an embedded collar band of **100-125% of fair market value** (a 25% band). This is the closest thing to IRS guidance on collar width.

2. **New York State Bar Association** proposed a safe harbor where the collar band should be at least **20-25%** of the stock's value. Most practitioners follow this guideline.

3. **Industry practice:** Tax advisors generally recommend the put and call strikes be at least **20% apart** (measured from each other) to safely avoid constructive sale treatment. A wider band (25-30%) provides more comfort.

**Applying this to John's collars:**

| Collar | Put Strike | Call Strike | Spread | % Spread | Constructive Sale Risk |
|--------|-----------|-------------|--------|----------|----------------------|
| $180P / $240C | $180 | $240 | $60 | 33% | ✅ **Safe** — well above 25% threshold |
| $175P / $230C | $175 | $230 | $55 | 31% | ✅ **Safe** |
| $180P / $230C | $180 | $230 | $50 | 28% | ✅ **Safe** (marginally) |
| $185P / $220C | $185 | $220 | $35 | 19% | ⚠️ **Risky** — below 20% threshold |
| $190P / $210C | $190 | $210 | $20 | 10% | ❌ **Almost certainly constructive sale** |
| $195P / $205C | $195 | $205 | $10 | 5% | ❌ **Constructive sale** |

**Bottom line:** The $180P/$240C collar (our recommended structure) has a 33% spread and is clearly safe under current guidance. Do NOT go tighter than a ~25% spread without specific tax counsel.

**What happens if it IS a constructive sale?**
- You'd owe capital gains tax immediately as if you sold the shares on the date you entered the collar
- For John: ~$42/share gain × applicable tax rate × shares collared
- Essentially, the collar would trigger the same tax bill you were trying to avoid

### B. Insider Trading Considerations — Amazon-Specific

This is the section that matters most. We reviewed Amazon's actual Insider Trading Policy (SEC filing, Exhibit 19.1, dated December 31, 2024).

**The critical distinction is by level:**

| Employee Level | Hedging/Collar Allowed? | Trading Window Required? | Preclearance Required? |
|---------------|------------------------|-------------------------|----------------------|
| L11+ / Board / Section 16 | ❌ **PROHIBITED** — no collars, swaps, PVFCs, or exchange funds | Yes | Yes |
| L10 | Allowed with preclearance | Yes | Yes |
| **L5 (John)** | **Allowed with preclearance** | **Only if named in Attachment A** | **Only if named in Attachment B** |

**For John (L5), Amazon's policy specifically permits hedging IF:**

1. ✅ He is **not in possession of material nonpublic information** at the time of entry
2. ✅ He enters the trade **during an open trading window** (if subject to the window — L5 employees typically are not, but Amazon may designate specific groups)
3. ✅ The transaction is **not speculative** and involves a **protective trade on existing investment** (puts/calls on vested shares — NOT on unvested RSUs)
4. ✅ The options **expire or settle at least 6 months** after entry, with no discretion on timing
5. ✅ **Settlement manner is established at entry**

**The process:**
1. Contact Amazon Legal Department to request preclearance
2. Confirm you meet all 5 conditions above
3. Amazon Legal approves or denies
4. If approved, execute during the permitted period (typically 2-5 trading days)
5. You remain subject to trading window + preclearance until the collar settles

**Important: Amazon Legal may deny the request.** The policy says they will "generally consider approving" protective trades, but it's not guaranteed. Some companies discourage hedging even when technically permitted.

**Can John use a collar during blackout periods?**

Not directly — the collar must be entered during an open trading window. However, if John sets up a **Rule 10b5-1 plan** that includes the collar structure:
- The plan is established during an open window when he has no MNPI
- The collar executes automatically per the plan's terms
- The 10b5-1 plan provides legal safe harbor for the timing

Under SEC amendments effective February 2023, new 10b5-1 plans require a **90-day cooling-off period** before the first trade (for non-officers/directors) and a certification that the insider is not aware of MNPI.

### C. Tax Treatment of Collar Outcomes

**Scenario 1: Put is exercised (stock drops below $180)**

If AMZN falls below $180 and John exercises the puts:
- He sells shares at $180/share
- **Capital gain:** $180 - $157 (basis) = $23/share
- **Tax:** ~$23 × 28.1% (LTCG + NIIT + CA) = ~$6.46/share
- **On 2,100 shares:** ~$13,569 in tax
- **Holding period:** The put exercise does NOT change the character of the gain — if shares were held long-term, the gain is still long-term

**Scenario 2: Call is exercised (stock rises above $240)**

If AMZN rises above $240 and the calls are exercised:
- Shares are called away at $240/share
- **Capital gain:** $240 - $157 (basis) = $83/share
- **Tax:** ~$83 × 28.1% = ~$23.32/share
- **On 2,100 shares:** ~$48,972 in tax
- **Net proceeds after tax:** ($240 × 2,100) - $48,972 = $455,028
- **Holding period:** If shares were held >1 year, this is LTCG regardless of when the call was sold

**Scenario 3: Neither exercised (stock stays between $180-$240)**

- Both options expire worthless
- No tax event from the collar itself (if costless)
- The put premium paid is a capital loss; the call premium received is a capital gain — but these net to ~$0 in a costless collar
- Shares retain their original basis and holding period

**Comparison to just selling outright:**

| Action | Tax/Share | Tax on 2,100 Shares | Net Proceeds |
|--------|----------|-------------------|-------------|
| Sell now at $199 | $11.87 | $24,920 | $393,520 |
| Put exercised at $180 | $6.46 | $13,569 | $364,431 |
| Call exercised at $240 | $23.32 | $48,972 | $455,028 |
| Collar expires (no exercise) | $0 | $0 | Still hold shares |

**Key insight:** The collar doesn't save you from taxes — it delays them. If AMZN goes to $240, you pay MORE tax ($49K) than if you'd sold at $199 ($25K) because your gain is larger. The collar is a *hedging* tool, not a *tax-reduction* tool.

---

## 4. JOHN'S SITUATION VS. CUBAN'S

| Factor | Mark Cuban | John | Implication |
|--------|-----------|------|-------------|
| **Position size** | ~$1.4 billion | ~$431K | Cuban's transaction costs were trivial vs. value. John's are meaningful. |
| **Lockup restriction** | Yes — couldn't sell | No — can sell anytime | Cuban HAD to use a collar. John has simpler options. |
| **Cost basis** | Near-zero (founder) | ~$157/share (~79% of market) | Cuban would owe hundreds of millions in tax. John owes ~$6,900/500 shares. |
| **Embedded gain** | ~$95/share (100% of value) | ~$42/share (21% of value) | Cuban's gain was his entire position. John's gain is modest. |
| **Tax cost of selling 25%** | ~$100-200M+ | ~$6,872 | This is the killer comparison. |
| **Position as % of net worth** | ~95%+ | ~35% of liquid portfolio | Both had concentration, but Cuban's was existential. |
| **Ability to execute collar** | Yes (investment bank structured it) | Yes (with Amazon Legal preclearance) | Both can do it, but at different scales. |
| **Income dependence** | Broadcast.com sold — no ongoing | Amazon salary + RSUs + ESPP | John has triple-correlated Amazon risk. Cuban didn't. |
| **Options market liquidity** | Yahoo was extremely liquid | AMZN is extremely liquid | Both have excellent liquidity for collar execution. |

### The Critical Math

**For Cuban:** Selling 25% of his shares would have cost ~$100-200M in taxes. The collar cost $0. The collar saved him hundreds of millions vs. selling.

**For John:** Selling 500 shares costs ~$6,872 in taxes. A collar costs $0 upfront but requires:
- Amazon Legal preclearance (time, effort, uncertainty)
- Ongoing management (rolling every 6-12 months)
- Constructive sale risk monitoring
- Options knowledge and broker approval
- Potential psychological regret if AMZN rallies past the cap

**The collar "saves" John $6,872 in immediate taxes. But:**
- If AMZN stays flat for a year, John still holds the same concentrated position and has to decide again
- If AMZN rallies past $240, the collar forces a sale at $240 with a HIGHER tax bill ($49K vs. $25K at $199)
- If AMZN crashes to $140, the collar limits losses to ~$40K — but selling would have avoided all loss

**Break-even analysis: When does a collar start making more sense than selling?**

The collar's primary benefit is tax deferral. It becomes attractive when the embedded gain is large enough that the tax bill from selling creates significant opportunity cost.

| Cost Basis | Gain/Share | Tax/Share (28.1%) | Tax on 500 Shares | Collar Advantage |
|-----------|-----------|------------------|-------------------|-----------------|
| $157 (John's actual) | $42 | $11.87 | $5,935 | **Low — just sell** |
| $120 | $79 | $22.20 | $11,100 | Moderate |
| $80 | $119 | $33.44 | $16,720 | Starting to make sense |
| $50 | $149 | $41.87 | $20,935 | **Collar is attractive** |
| $20 | $179 | $50.30 | $25,150 | **Collar is strongly preferred** |
| $5 (founder-like) | $194 | $54.51 | $27,255 | **Collar is the only rational choice** |

**Rule of thumb:** A collar starts being worth the complexity when your embedded gain exceeds ~50-60% of the current share price. John's gain is only ~21%. Cuban's was ~100%.

---

## 5. PRACTICAL IMPLEMENTATION

### If John Wants to Execute a Collar

**Step 1: Amazon Legal Preclearance (Required)**
- Submit a preclearance request to Amazon Legal Department via their ticketing system
- Specify: number of shares, put/call strikes, expiration, settlement terms
- Wait for approval (typically a few business days)
- Note: Must not possess MNPI at time of request

**Step 2: Broker Setup**
- John's shares are at Fidelity. Fidelity supports multi-leg options strategies including collars.
- **Options approval required:** John needs at least Level 2 options approval (covered calls + protective puts). Fidelity may require an application.
- If Fidelity's options platform isn't optimal, consider:
  - **Schwab** (John already has an account) — excellent options platform, merged with TD Ameritrade's thinkorswim
  - **Interactive Brokers** — best execution for complex options, lowest commissions
  - Note: Transferring shares just for options execution may not be worth the hassle

**Step 3: Execution**
- Place the collar as a **multi-leg order** (buy put + sell call simultaneously) to ensure balanced execution
- Use limit orders at the net debit/credit target
- For 21 contracts, consider breaking into 3-5 lots over 1-2 days
- Best to execute in the first 2 hours after market open (most liquid)
- Expect to give up ~$0.05-0.15/share on the bid-ask spread (total cost: ~$105-315)

**Step 4: Ongoing Management**
- If options expire (AMZN between $180-$240): Decide whether to roll (establish new collar) or sell
- If put is exercised: Shares are sold at $180 — reinvest proceeds
- If call is exercised: Shares are called away at $240 — reinvest proceeds
- If rolling: Establish the new collar during an open trading window, with preclearance

**Rolling Cost Estimate:**
- Each 6-month roll: Bid-ask spread of ~$0.10-0.30/share × 2,100 shares = $210-630
- Transaction costs: ~$1.30/contract × 42 contracts (21 puts + 21 calls) = ~$55
- Annual cost if rolling every 6 months: ~$530-1,370/year
- This is small but non-zero, and adds up over multi-year holding periods

### Minimum Position Size for Efficient Execution

Options trade in 100-share lots. John's 2,164 shares translate to 21 contracts (covering 2,100 shares, with 64 shares unhedged). This is a reasonable size for a retail collar — not too small to be inefficient, not so large as to move the market.

Below ~500 shares (5 contracts), the fixed costs of execution, monitoring, and rolling make collars inefficient. John's position is well above this threshold.

---

## 6. RECOMMENDATION

### The Bottom Line

**Don't do what Cuban did. Do what Cuban would do if he were in your shoes.**

If Mark Cuban had John's position — 2,164 shares of AMZN with a $157 basis, no lockup, and a tax bill of only $6,900 per 500 shares — he wouldn't bother with a collar. He'd sell. The collar was a tool of *necessity* born from constraints John doesn't have.

### Primary Recommendation: Direct Sale Program (Reiterated)

Stick with the strategy outlined in the Tax Strategy report:

1. **Sell 500 shares over 12 months** (Scenario 2 from the tax report)
2. Tax cost: ~$6,872 (6.9% of proceeds)
3. Net proceeds: ~$92,798 → reinvest into VTI/VXUS
4. Continue selling RSUs as they vest
5. Re-evaluate in 12 months

This is simpler, more tax-efficient (yes, really — the collar doesn't save taxes, it delays them), and more effective at reducing concentration.

### Alternative: Hybrid Approach (If John Wants Some Hedge)

If John is genuinely worried about a near-term crash but doesn't want to sell everything:

**Phase 1 (Immediate):**
- Sell 500 shares per the existing plan (~$92.8K net proceeds)
- This alone drops concentration from ~35% to ~27%

**Phase 2 (If approved by Amazon Legal):**
- Collar 1,000 shares with a 12-month $180P/$240C (costless)
- This protects another ~$200K of exposure for 12 months
- Leaves 664 shares unhedged (for full upside participation)

**Phase 3 (12 months later):**
- If AMZN is between $180-$240: Collar expires, sell the 1,000 shares
- If AMZN is below $180: Put is exercised, shares sold at $180, reassess
- If AMZN is above $240: Shares called away at $240, good outcome

**Total 12-month result of hybrid:**
- 500 shares sold directly ✅
- 1,000 shares either sold via collar exercise or sold at collar expiration ✅
- 664 shares retained for long-term holding
- Total proceeds: ~$290-340K, reinvested into diversified portfolio
- AMZN position reduced to ~$130K (664 shares), or ~12% of portfolio

This gives John the "Cuban hedge" feeling while still executing the rational selling program. The collar provides psychological comfort during the transition period. It's not financially optimal (direct selling is cheaper and simpler), but it may be *behaviorally* optimal if it prevents John from freezing and doing nothing.

### What We'd Tell John Directly

> You asked a great question, and the Cuban story is worth understanding. He was brilliant to use the collar — but he was also trapped. You're not.
>
> Cuban's collar saved him ~$1 billion. A collar on your shares would save you... roughly the same amount as just paying the tax and selling. The machinery is impressive but the payoff doesn't match the complexity for a position with modest embedded gains.
>
> If you do one thing from this report: **start the 500-share selling program.** The tax bill is $6,900 — less than one RSU vest. That's the price of reducing your Amazon concentration from 35% to 27%.
>
> If you want the collar for peace of mind on the remaining shares while you execute the sell program, we can help you structure that. But don't let the search for a perfect hedge delay the simple, effective action of selling.

---

## APPENDIX A: OPTIONS DATA (RAW)

### September 18, 2026 (173 days) — Selected Strikes

**Puts (Downside Protection)**

| Strike | Last | Bid | Ask | Volume | Open Interest | Implied Vol |
|--------|------|-----|-----|--------|---------------|-------------|
| $155 | $5.90 | $5.85 | $6.00 | 61 | 5,572 | 43.8% |
| $160 | $6.82 | $6.85 | $7.00 | 65 | 15,869 | 42.9% |
| $165 | $8.08 | $7.95 | $8.15 | 433 | 4,825 | 42.1% |
| $170 | $9.40 | $9.20 | $9.35 | 177 | 10,103 | 41.1% |
| $175 | $10.80 | $10.65 | $10.80 | 841 | 7,307 | 40.4% |
| $180 | $12.40 | $12.20 | $12.25 | 167 | 11,524 | 39.4% |
| $185 | $14.00 | $13.95 | $14.10 | 294 | 4,339 | 38.8% |
| $190 | $15.85 | $15.85 | $16.05 | 287 | 9,169 | 38.1% |
| $195 | $17.98 | $17.95 | $18.15 | 557 | 5,481 | 37.4% |
| $200 | $20.47 | $20.25 | $20.45 | 174 | 11,428 | 36.7% |

**Calls (Upside Cap)**

| Strike | Last | Bid | Ask | Volume | Open Interest | Implied Vol |
|--------|------|-----|-----|--------|---------------|-------------|
| $210 | $18.59 | $18.45 | $18.70 | 684 | 3,545 | 42.1% |
| $215 | $16.45 | $16.35 | $16.55 | 523 | 1,987 | 41.4% |
| $220 | $14.50 | $14.40 | $14.60 | 121 | 3,351 | 40.9% |
| $225 | $12.80 | $12.60 | $12.80 | 631 | 3,938 | 40.3% |
| $230 | $11.15 | $11.00 | $11.20 | 133 | 5,103 | 39.8% |
| $235 | $9.69 | $9.55 | $9.75 | 271 | 2,372 | 39.3% |
| $240 | $8.60 | $8.30 | $8.45 | 95 | 5,852 | 38.8% |
| $250 | $6.25 | $6.15 | $6.30 | 609 | 4,817 | 38.1% |
| $260 | $4.60 | $4.50 | $4.65 | 163 | 6,914 | 37.5% |

### March 19, 2027 (355 days) — Selected Strikes

**Puts**

| Strike | Last | Bid | Ask | Volume | Open Interest | Implied Vol |
|--------|------|-----|-----|--------|---------------|-------------|
| $165 | $10.80 | $12.60 | $13.00 | 1 | 5 | 37.6% |
| $175 | $16.15 | $16.00 | $16.30 | 43 | 127 | 36.5% |
| $180 | $18.00 | $17.85 | $18.20 | 4 | 171 | 36.0% |
| $185 | $20.05 | $19.85 | $20.15 | 13 | 1,204 | 35.5% |
| $195 | $24.50 | $24.20 | $24.55 | 28 | 84 | 34.5% |
| $200 | $26.90 | $26.55 | $27.00 | 371 | 229 | 34.1% |

**Calls**

| Strike | Last | Bid | Ask | Volume | Open Interest | Implied Vol |
|--------|------|-----|-----|--------|---------------|-------------|
| $210 | $29.19 | $28.90 | $29.45 | 28 | 44 | 43.1% |
| $220 | $25.05 | $24.80 | $25.30 | 44 | 43 | 42.3% |
| $230 | $21.71 | $21.05 | $21.55 | 17 | 47 | 41.4% |
| $240 | $18.40 | $17.90 | $18.35 | 41 | 114 | 40.8% |
| $250 | $15.50 | $15.10 | $15.55 | 84 | 71 | 40.2% |

---

## APPENDIX B: GLOSSARY

| Term | Definition |
|------|-----------|
| **Costless collar** | Buying a put and selling a call at strikes where the premiums offset, costing $0 upfront |
| **Protective put** | Buying a put option to establish a price floor on owned shares |
| **Covered call** | Selling a call option against shares you own |
| **Constructive sale** | An IRS concept (§1259) where a hedging transaction is treated as if you sold the stock, triggering tax |
| **10b5-1 plan** | A pre-arranged trading plan that provides insider trading safe harbor |
| **PVFC** | Prepaid Variable Forward Contract — an OTC hedge typically for $5M+ positions |
| **Rolling** | Closing an expiring options position and opening a new one at a later expiration |
| **NIIT** | Net Investment Income Tax — 3.8% surtax on investment income for high earners |
| **Open interest** | The total number of outstanding option contracts at a given strike/expiration |
| **Implied volatility** | The market's expectation of future price movement, reflected in option prices |

---

## APPENDIX C: REFERENCES

- Amazon.com, Inc. Insider Trading Policy (SEC Exhibit 19.1, filed Feb 2025)
- IRC Section 1259 — Constructive Sales Treatment for Appreciated Financial Positions
- Revenue Ruling 2003-7 (Variable Prepaid Forward Contracts)
- CPA Journal, December 2003: "Revenue Ruling 2003-7: Variable Prepaid Forwards" by Callender & Kaplan
- New York State Bar Association Tax Section: Constructive Sale Safe Harbor Recommendations
- SEC Rule 10b5-1 (as amended February 2023)

---

*This report was prepared for fiduciary advisory purposes. Options trading involves significant risk, including the risk of loss of the entire premium paid. The strategies discussed are educational and should not be implemented without consultation with a qualified financial advisor, tax professional, and securities attorney. The client must verify all tax calculations with a CPA and obtain Amazon Legal preclearance before entering any hedging transaction.*

*Report generated: March 29, 2026*
*Data sources: Yahoo Finance (live options chains), SEC filings, IRS publications, CPA Journal archives*
*Options data as of market close March 28, 2026*
