# Deal Analysis Feature - Implementation Summary

## Overview
The "Analyse a Potential Investment" feature has been enhanced to match the comprehensive analysis capabilities of the portfolio property detail view.

## Key Enhancements

### 1. Advanced Financial Metrics
**Added 8 Key Performance Indicators:**

- **NRAT (Net Return After Tax)** - Primary headline metric showing Year 1 after-tax return as % of total cash deployed
- **ROI (Return on Investment)** - Year 1 pre-tax return as % of cash invested
- **Monthly/Annual Net Income** - Cash flow metrics before tax
- **Gross Annual Yield** - Rental income / Market value %
- **Net Annual Yield** - Net operating income / Market value %
- **DSCR (Debt Service Coverage Ratio)** - Measures mortgage payment coverage (color-coded: green ≥1.25, yellow ≥1.0, red <1.0)
- **Opex Load** - Operating expense ratio (color-coded: green ≤30%, yellow ≤40%, red >40%)

### 2. 10-Year Cashflow Projection
**Comprehensive year-by-year financial modeling including:**

- Projected rental income with **3.71% annual growth**
- Projected expenses with **2.8% annual inflation**
- Mortgage amortization schedule (both P&I and interest-only)
- Remaining mortgage balance tracking
- Net Operating Income (NOI) calculation
- Pre-tax cash flow
- Tax calculations with loss carryforward
- **After-tax cash flow** (final metric)

### 3. Tax Calculations
**Sophisticated tax modeling based on ownership structure:**

- **UK Limited Company**: Corporation tax on taxable profit
- **Individual Onshore**: Personal income tax with 20% mortgage interest relief
- **Individual Offshore**: Offshore tax rates with 20% mortgage interest relief

**Tax Loss Carryforward "Corkscrew" Logic:**
- Tracks losses generated in negative years
- Automatically applies losses to offset future tax liabilities
- Shows beginning balance, generated, utilized, and ending balance per year

### 4. SDLT Calculation & Total Cash Deployed
**Accurate stamp duty calculation:**
- Automatically calculates SDLT based on purchase price and buyer type
- Always treats as Buy-to-Let (BTL) property
- Includes SDLT in total cash deployed for NRAT calculation
- **Total Cash Deployed = Deposit + SDLT + Acquisition Costs**

### 5. Enhanced Results Template
**Professional presentation with:**

- **8 Metric Cards** in 2 rows showing all KPIs
- **10-Year Cashflow Table** with color-coded values
  - Green for income/positive values
  - Red for expenses/taxes
  - Blue highlight for after-tax cash flow column
  - Yellow highlight for Year 1 (NRAT basis)
- **Expandable Tax Details** section showing full tax corkscrew
- **SDLT breakdown** in financial summary
- **Enhanced assumptions** section with methodology notes

## Technical Implementation

### Backend (views.py)
**Location:** `user_home/views.py` - `analyse_deal` function (lines 427-747)

**Key Components:**
1. Form data extraction and validation
2. Vacancy (3.85%) and maintenance (3.5%) rate application
3. Advanced metrics calculation (yields, DSCR, opex load)
4. 10-year projection loop with compound growth rates
5. Mortgage amortization with fixed payment calculation
6. Tax calculator integration (corp_tax, income_tax, offshore_tax)
7. Tax loss carryforward mechanics
8. SDLT calculation via sdlt_calculator
9. NRAT calculation using Year 1 after-tax cash flow

### Frontend (deal_analysis_result.html)
**Location:** `user_home/templates/user_home/deal_analysis_result.html`

**Structure:**
1. Header with deal name
2. Two rows of 4 metric cards each
3. 10-year cashflow projection table with expandable tax details
4. Property details grid
5. Enhanced financial summary with SDLT
6. Updated assumptions section
7. Action buttons (Analyse Another Deal, Print)

## Calculation Constants
- **Vacancy Rate:** 3.85%
- **Maintenance Rate:** 3.5%
- **Rental Growth Rate:** 3.71% annually
- **Inflation Rate:** 2.8% annually
- **Mortgage Interest Relief:** 20% (for individuals)

## Data Flow
1. User submits deal analysis form
2. Backend extracts 29 form fields
3. Calculates 8 immediate KPIs
4. Runs 10-year projection loop (Years 1-10)
5. For each year:
   - Projects rent with growth
   - Projects expenses with inflation
   - Calculates mortgage payments with amortization
   - Determines applicable tax based on ownership
   - Applies tax loss carryforward
   - Calculates after-tax cash flow
6. Calculates SDLT and NRAT from Year 1
7. Passes all data to template
8. Template displays comprehensive analysis

## User Benefits
- **Complete investment analysis** matching professional property analysis tools
- **Multi-year visibility** into cash flow and tax implications
- **Tax optimization** through loss carryforward tracking
- **Accurate SDLT** included in cash deployment calculations
- **NRAT metric** provides true after-tax return on cash deployed
- **Professional presentation** suitable for investor reports

## Color Coding System
- **Yellow:** NRAT card (primary metric), Year 1 row (NRAT basis)
- **Green:** Positive cash flows, income, good DSCR/opex load
- **Red:** Expenses, taxes, poor DSCR/opex load
- **Blue:** ROI card, after-tax cash flow column (final metric)
- **Purple:** Net Annual Yield
- **Orange:** Opex Load
- **Indigo:** DSCR

## Expansion vs. Property Detail View
The deal analysis now matches property_detail in:
- ✅ All KPIs (NRAT, yields, DSCR, opex load)
- ✅ 10-year cashflow projection structure
- ✅ Tax calculations with loss carryforward
- ✅ Mortgage amortization
- ✅ SDLT calculation

Differences (intentional):
- Deal analysis uses form inputs instead of Property model
- No capital growth calculations (purchase analysis only)
- No CGT calculations (exit analysis not needed for deal evaluation)

## Future Enhancement Opportunities
1. Export to PDF functionality
2. Side-by-side deal comparison
3. Sensitivity analysis (varying rent/expenses/rates)
4. Break-even analysis
5. IRR calculation
6. Deal scoring/rating system

---

**Last Updated:** January 11, 2025
**Feature Status:** ✅ Complete and Production-Ready
