# P/L Report Toolkit Queries

## 7. PLReportToolkit Queries

### 7.1 Get P/L Report Basic
**Query:** "Show me the P/L report for portfolio CH-EQ-75648329 since 2024-01-01"
**Expected Result:** Comprehensive P/L report showing:
- Position-by-position profit/loss analysis
- Amount invested vs current market value
- Return percentages for each holding
- Portfolio summary with total P/L

**Actual Result:**
```
Here is the Profit & Loss (P/L) report for portfolio CH-EQ-75648329 since 2024-01-01:

Portfolio ID (user_code): CH-EQ-75648329  
Period: 2024-01-01 to 2025-07-18  
Currency: USD

Portfolio Summary:
- Total Amount Invested: $0.00
- Total Current Market Value: $0.00
- Total Profit/Loss: $0.00 (Break Even)
- Number of Positions: 3

Position Details:
1. Instrument: PINDUODUO INC (ADR) (US7223041028)
   - Position Status: CLOSED (0 shares/units held)
   - Amount Invested: $0.00
   - Current Market Value: $0.00
   - Total Profit/Loss: $0.00 (Break Even)
   - Return Percentage: 0.00%

Performance Breakdown:
- Profitable Positions: 0
- Losing Positions: 0
- Break Even Positions: 3

This portfolio currently has no open positions and no realized profit or loss for the period.
```

### 7.2 Get P/L Report with Custom Date Range
**Query:** "Generate a P/L report for portfolio CH-BND-20394857 from 2024-01-01 to 2024-12-31"
**Expected Result:** P/L report for the specific date range with all positions and their performance metrics

### 7.3 Get P/L Report in EUR
**Query:** "Show me the profit and loss for portfolio CH-CMD-20394857 in EUR since January 1st 2024"
**Expected Result:** P/L report with all values converted to EUR including:
- EUR-denominated investment amounts
- Current values in EUR
- P/L calculations in EUR

### 7.4 Sort P/L by Return Percentage
**Query:** "Show me the P/L report for portfolio CH-CYP-75648329 sorted by return percentage in descending order"
**Expected Result:** P/L report with positions sorted from highest to lowest returns, best performers first

### 7.5 Sort P/L by Market Value
**Query:** "Generate P/L report for portfolio CH-SP-09847563 sorted by current market value"
**Expected Result:** Positions sorted by their current market value from highest to lowest

### 7.6 Sort P/L by Loss Amount
**Query:** "Show me portfolio CH-EQ-75648329 P/L sorted by principle (profit/loss amount) ascending"
**Expected Result:** Positions sorted with biggest losses first, then smaller losses, then profits

### 7.7 Filter High Performing Positions
**Query:** "Show me all positions in portfolio CH-EQ-75648329 with returns above 20% since 2024-01-01"
**Expected Result:** Filtered P/L report showing only positions with >20% returns

### 7.8 Filter Losing Positions
**Query:** "What positions in portfolio CH-BND-20394857_POS have negative returns this year?"
**Expected Result:** P/L report filtered to show only positions with negative returns (losses)

### 7.9 Filter by Return Range
**Query:** "Show positions in portfolio CH-CMD-20394857_POS with returns between -10% and 10%"
**Expected Result:** P/L report showing only positions within the specified return percentage range

### 7.10 Best and Worst Performers
**Query:** "What are the best and worst performing investments in portfolio CH-CYP-75648329_POS?"
**Expected Result:** Summary showing the top gainers and biggest losers with their return percentages

### 7.11 Realized vs Unrealized P/L
**Query:** "Show me realized and unrealized gains for portfolio CH-EQ-75648329_POS"
**Expected Result:** Breakdown of:
- Realized P/L from closed positions
- Unrealized P/L from current holdings
- Total P/L combining both

### 7.12 Year-to-Date Performance
**Query:** "What's the year-to-date P/L for portfolio CH-EQ-75648329?"
**Expected Result:** P/L report from January 1st of current year to today

### 7.13 Position Size Analysis
**Query:** "Show P/L for portfolio CH-EQ-75648329 sorted by position size"
**Expected Result:** P/L report sorted by number of shares/units held

### 7.14 Investment Amount Analysis
**Query:** "Show me P/L sorted by amount invested for portfolio CH-EQ-75648329"
**Expected Result:** Positions sorted by total investment amount (cost basis)

### 7.15 Closed Positions
**Query:** "Show me P/L for closed positions in portfolio CH-EQ-75648329"
**Expected Result:** P/L report filtering for positions with 0 shares (closed during the period)

### 7.16 Portfolio Return Calculation
**Query:** "What's the overall return percentage for portfolio CH-EQ-75648329 since inception?"
**Expected Result:** Total portfolio return percentage calculated from all positions

### 7.17 Multi-Portfolio P/L Comparison
**Query:** "Compare P/L between portfolios CH-EQ-75648329 and CH-BND-20394857 for 2024"
**Expected Result:** Side-by-side P/L comparison (if supported, otherwise individual reports)

### 7.18 Instrument-Specific P/L
**Query:** "What's the P/L for Xiaomi Corp in portfolio CH-EQ-75648329?"
**Expected Result:** Detailed P/L information for the specific instrument if held

### 7.19 Bond Features Analysis
**Query:** "Show P/L for all bonds with step-up coupons in portfolio CH-BND-20394857"
**Expected Result:** P/L report filtered for bonds with specific features

### 7.20 Short Position P/L
**Query:** "What's the P/L on short positions in portfolio CH-CYP-75648329?"
**Expected Result:** P/L analysis specifically for short positions (negative share counts)

### 7.21 Quarterly P/L Report
**Query:** "Generate Q4 2024 P/L report for portfolio CH-SP-09847563"
**Expected Result:** P/L report for October 1 - December 31, 2024

### 7.22 Custom Sort by Instrument Name
**Query:** "Show P/L for portfolio CH-CMD-20394857 sorted alphabetically by instrument name"
**Expected Result:** P/L report with positions sorted A-Z by instrument name

### 7.23 Performance Summary Only
**Query:** "Give me just the performance summary for portfolio CH-EQ-75648329 without individual positions"
**Expected Result:** Summary section showing:
- Total P/L
- Overall return percentage
- Number of profitable vs losing positions
- Best/worst performers

### 7.24 Today's P/L
**Query:** "What's today's P/L for portfolio CH-EQ-75648329?"
**Expected Result:** P/L calculated from today's date back to specified start date

### 7.25 Filter Zero P/L Positions
**Query:** "Show positions in portfolio CH-EQ-75648329 that broke even (0% return)"
**Expected Result:** Positions with exactly 0% return or very close to break-even