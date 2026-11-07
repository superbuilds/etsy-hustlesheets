# Budget Planner - Sheets Canvas Prompt Pack

Make these in your **master copy** only. Buyers who copy the file can use the canvases but can't edit them.

## Setup (once)
1. Upload `All-in-One-Budget-Planner.xlsx` to Google Drive → open it → **File → Save as Google Sheets**.
2. Delete the original .xlsx from Drive so you don't mix them up.
3. For each canvas below: **Insert → Create a canvas** (or Tools → Create canvas), pick the source tab named in the heading, paste the prompt.
4. Test it: add a transaction through the canvas, check it lands in the next empty row of the Transactions tab and the Dashboard tab updates.
5. Share → General access: **Anyone with the link → Viewer**. Send me the link and I'll make the buyer PDF with the "Make a copy" link.

Each prompt explains the table layout so Gemini reads the right rows. If something comes out wrong, follow up in the same canvas with a short fix ("make the cards smaller", "the month picker should default to the latest month").

---

## Canvas 1 - "Budget Dashboard" (source tab: Transactions)

```
Build an interactive monthly budget dashboard called "My Budget" from this Transactions tab.

DATA: The table header is in row 5, starting in column B: Date, Description, Category, Amount, Type, Notes, Month, Monthly Budget. Data starts in row 6. Ignore any row where Date is blank. Amount is always a positive number. Type is one of Income, Fixed, Variable, Savings, Debt. Month is the first day of the transaction's month. Monthly Budget is that category's budget for ONE month (the same value repeats on every row of that category).

CONTROLS: A month selector at the top (default to the most recent month that has data) plus a "Full Year" option, and a search box for transactions.

KPI CARDS (for the selected period): Income (Type = Income), Spent (Fixed + Variable + Debt), Saved (Savings), Left Over (Income - Spent - Saved, red if negative), Savings Rate (Saved / Income).

BUDGET VS ACTUAL: For each category used in the period, show actual spending vs Monthly Budget (x number of months for Full Year) with a progress bar. Bar is green under 90%, amber 90-100%, red over 100%. Group by Type with a subtotal per group. For Income show "earned vs expected".

CHARTS: (1) Donut of spending by Type (Fixed, Variable, Savings, Debt) with the total in the center. (2) Horizontal bar chart of the top 8 spending categories. (3) Line chart of monthly Income vs Spent vs Saved for the whole year.

TRANSACTIONS: A recent transactions list (newest first) with category filter chips, showing date, description, category, amount (income in green).

ADD TRANSACTION: An "+ Add Transaction" button that opens a form with Date (default today), Description, Category (dropdown of the existing categories), Amount and Notes. Save it into the FIRST row (row 6 or below) where the Date cell is blank, writing only columns B, C, D, E and G. Never write to the Type, Month or Monthly Budget columns - they are formulas.

STYLE: Clean modern finance app look. White rounded cards on a light warm-gray background, accent color #2F7D6D (dark green) with #1E5A4E for headings, soft shadows, Inter-style font. Money as $ with no decimals on cards and 2 decimals in the transaction list. Works well on laptop and phone widths.
```

## Canvas 2 - "Spending Insights" (source tab: Transactions)

```
Build a "Spending Insights" canvas from this Transactions tab.

DATA: Header in row 5 starting in column B: Date, Description, Category, Amount, Type, Notes, Month, Monthly Budget. Data starts in row 6; ignore rows with a blank Date. Spending means Type is Fixed, Variable or Debt (exclude Income and Savings).

CONTROLS: Month selector (default to the most recent month with data) and a Type filter (All, Fixed, Variable, Debt).

SHOW:
1. A calendar heatmap for the selected month - each day shaded by total spending, hover/tap a day to list that day's transactions.
2. Insight cards: Total spent, Average per day, Biggest single expense (with description), Number of no-spend days, Most-used category.
3. "Where it went" - a treemap or bar chart of spending by category.
4. Month-over-month comparison: each category's spending this month vs last month with up/down arrows and % change.
5. Top 5 places/descriptions by total spend.

Read-only canvas (no editing). Same style as a modern finance app: white rounded cards, light warm-gray background, accent #2F7D6D, headings #1E5A4E.
```

## Canvas 3 - "Savings Goals" (source tab: Sinking Funds)

```
Build a "Savings Goals" canvas from this Sinking Funds tab.

DATA: Header in row 5 starting in column B: Fund, Goal, Target Date, Starting Balance, Contributions, Saved, Still Needed, Months Left, Save / Month, Progress. Data rows are 6-17; ignore rows where Fund is blank. Row 19 is a Total row - ignore it. Progress is a fraction (0.31 = 31%).

SHOW:
1. Summary cards: Total saved, Total goal, Overall progress %, Total to save per month.
2. One card per fund with a circular progress ring, Saved / Goal, target date, months left and "Save $X / month". Show a "Goal reached 🎉" badge when Progress is 100%.
3. A horizontal bar chart comparing Saved vs Goal for every fund.

Read-only (the numbers come from formulas). Style: white rounded cards, light warm-gray background, accent #2F7D6D, headings #1E5A4E, friendly and motivating.
```

## Canvas 4 - "Debt Payoff" (source tab: Debt Payoff)

```
Build a "Debt-Free Plan" canvas from this Debt Payoff tab.

DATA: Top area: C4 = Method (Snowball or Avalanche), C5 = Monthly debt budget, E5 = Debt-free date, G5 = Total interest.
Debt table header is in row 10 starting in column B: Debt, Balance, APR, Min Payment, Pay Order, Months, Debt-Free, Interest Paid. Data rows are 11-18; ignore rows where Debt is blank. APR is a fraction (0.229 = 22.9%).
Further down, the payment schedule header is in row 30 and month rows start in row 33: column C = month, columns D-K = payment to each debt, columns L-S = remaining balance of each debt, column T = Total Paid, column U = Total Debt (remaining total debt that month).

SHOW:
1. Hero card: "Debt-free by <E5>" with total interest (G5), the method (C4) and the monthly budget (C5).
2. Debt cards in Pay Order: name, balance, APR, minimum payment, payoff date, a "Focus debt" badge on Pay Order 1.
3. Area chart of Total Debt over time from the schedule (stop when it reaches $0), with a marker on each debt's payoff month.
4. A milestone timeline listing each debt's payoff month in order.

Read-only. Style: white rounded cards, light warm-gray background, accent #2F7D6D, headings #1E5A4E, celebratory feel when debts reach zero.
```
