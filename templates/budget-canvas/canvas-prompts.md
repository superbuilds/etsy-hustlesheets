# Budget Planner (Canvas Edition) - Gemini Prompt Pack

**Database:** `Budget-Database.xlsx` - 4 tabs: Categories, Transactions, Debts, Goals.
**Canvases:** 2 - "Budget App" (data entry) and "Budget Dashboard".

## Setup
1. Upload `Budget-Database.xlsx` to Google Drive → open → **File → Save as Google Sheets**.
2. **Insert → Create a canvas**, select all 4 tabs as sources, paste **Prompt 1**. Repeat for **Prompt 2**.
3. Test: add, edit and delete a transaction in the Budget App; confirm the Transactions tab and the Dashboard update.
4. Share → **Anyone with the link → Viewer** → send me the link (I'll make the buyer PDF with the "Make a copy" link).

If a canvas comes out wrong, follow up in the same canvas with one short fix at a time.

---

## Prompt 0 - Build the database with Gemini (instead of uploading the .xlsx)

Paste into the Gemini side panel in a **blank** Google Sheet.

```
Set up this spreadsheet as a simple budget database with exactly 4 tabs. Use plain values only - no formulas, no titles, no merged cells. Each tab: bold header row in row 1 (white text on #2F7D6D), data from row 2, freeze row 1.

1. Categories: Category | Group | Monthly Budget
   Group must be one of: Income, Fixed, Variable, Savings, Debt (add a dropdown to the Group column).
   Rows: Paycheck (Income, 4800), Side Hustle (Income, 600), Rent / Mortgage (Fixed, 1650), Utilities (Fixed, 220), Phone & Internet (Fixed, 140), Insurance (Fixed, 180), Car Payment (Fixed, 385), Subscriptions (Fixed, 45), Groceries (Variable, 600), Dining Out (Variable, 200), Gas (Variable, 180), Shopping (Variable, 150), Entertainment (Variable, 100), Personal Care (Variable, 60), Gifts (Variable, 50), Miscellaneous (Variable, 100), Emergency Fund (Savings, 300), Vacation (Savings, 150), Christmas Gifts (Savings, 75), Visa (Debt, 250), Store Card (Debt, 100), Student Loan (Debt, 200), Medical Bill (Debt, 50).

2. Debts: Debt | Starting Balance | APR | Minimum Payment
   Rows: Visa (3200, 22.9%, 95), Store Card (850, 26.99%, 35), Student Loan (12400, 5.5%, 140), Medical Bill (600, 0%, 50). Store APR as a decimal formatted as a percent.

3. Goals: Goal | Target Amount | Target Date | Starting Amount
   Rows: Emergency Fund (10000, Dec 31 next year, 2500), Vacation (3000, Jul 1 next year, 400), Christmas Gifts (900, Dec 1 this year, 450).

4. Transactions: Date | Description | Category | Amount | Notes
   Add a dropdown on Category that pulls from the Categories tab. Fill in realistic sample data for the last 3 full months plus the current month so far (about 100 rows, sorted by date):
   - Paycheck 2400 on the 7th and 21st of each month; a Side Hustle "Etsy payout" of 480-720 once a month.
   - Every Fixed category once a month at its budget amount (Utilities split into an electric bill ~95-140 and a water/gas bill ~60-90).
   - Variable categories spread through the month, mostly under budget: Groceries 3-4 trips of 90-190, Dining Out 4 times 14-52, Gas 3 times 42-58, a couple of Shopping and Entertainment entries, occasional Gifts, Personal Care and Miscellaneous.
   - Each month: Emergency Fund 300, Vacation 150, Christmas Gifts 75, Visa 250, Store Card 100, Student Loan 200, Medical Bill 50.
   - Amounts are always positive numbers with 2 decimals. Every Category value must exactly match a name in the Categories tab.

Format money columns as currency and dates as dates. Size columns to fit.
```

After it runs, spot-check: every Debts and Goals name appears in Categories with the same spelling, and no Transactions row has a category that isn't in Categories.

---

## Prompt 1 - "Budget App" (data entry)

```
Build a budgeting app called "Budget App" that lets me add, edit and delete my budget data with a clean, friendly UI. It reads from and writes to these 4 tabs.

DATA MODEL (every tab: headers in row 1, data from row 2, no formulas; ignore blank rows):
- Categories: Category | Group | Monthly Budget. Group is one of Income, Fixed, Variable, Savings, Debt. Category names are unique.
- Transactions: Date | Description | Category | Amount | Notes. Amount is always positive; whether it is income or spending comes from the Category's Group. Category must match a name in Categories.
- Debts: Debt | Starting Balance | APR | Minimum Payment. APR is a decimal (0.229 = 22.9%). Every debt also exists as a category with Group = Debt, using the same name; a transaction in that category is a payment toward that debt.
- Goals: Goal | Target Amount | Target Date | Starting Amount. Every goal also exists as a category with Group = Savings, using the same name; a transaction in that category is a contribution to that goal.

SCREENS (tabs across the top):
1. Add - a fast entry form front and center: Amount (big input), Description, Category (searchable picker grouped by Group, each with an icon/color per Group), Date (default today), Notes. A toggle at the top for "Spending" vs "Income" that filters the category picker. "Save" appends a new row to Transactions in the first empty row and shows a confirmation; the form clears for the next entry. Show this month's remaining budget for the selected category under the picker.
2. Transactions - searchable, filterable list (by month, category, group), newest first, grouped by day, income in green. Tap a row to edit any field or delete it (with confirm). Edits update that exact row in the Transactions tab.
3. Categories - list grouped by Group with Monthly Budget. Add, rename, change group, change budget, delete. Renaming a category also updates every matching Transactions row (and the matching Debts or Goals row if its Group is Debt or Savings). Block deleting a category that still has transactions, and say why. Show a summary: total monthly Income budget minus all other budgets = "Left to assign" (green if 0 or more, red if negative).
4. Debts - add/edit/delete debts. Adding a debt also adds a Debt-group category with the same name and a Monthly Budget equal to its Minimum Payment. Show each debt's current balance = Starting Balance minus all payments (transactions in its category).
5. Goals - add/edit/delete goals. Adding a goal also adds a Savings-group category with the same name and a Monthly Budget of 0. Show each goal's saved amount = Starting Amount plus contributions, with a progress bar.

RULES: Never write formulas. Never change the header row. Dates written as real dates. Amounts as plain numbers. Validate required fields before saving.

STYLE: Modern mobile-first finance app. White rounded cards on a light warm-gray background, accent #2F7D6D, headings #1E5A4E, Group colors: Income green, Fixed blue, Variable amber, Savings teal, Debt rose. Money shown as $ with 2 decimals in lists. Large tap targets; works on phone and laptop.
```

---

## Prompt 2 - "Budget Dashboard"

```
Build a read-only "Budget Dashboard" from these 4 tabs.

DATA MODEL (every tab: headers in row 1, data from row 2, no formulas; ignore blank rows):
- Categories: Category | Group | Monthly Budget. Group is one of Income, Fixed, Variable, Savings, Debt.
- Transactions: Date | Description | Category | Amount | Notes. Amount is always positive; its meaning comes from the Category's Group.
- Debts: Debt | Starting Balance | APR | Minimum Payment. APR is a decimal. Each debt is also a Debt-group category with the same name; transactions in it are payments.
- Goals: Goal | Target Amount | Target Date | Starting Amount. Each goal is also a Savings-group category with the same name; transactions in it are contributions.

DEFINITIONS (for the selected month):
Income = Income group. Spent = Fixed + Variable + Debt groups. Saved = Savings group. Left Over = Income - Spent - Saved. Savings Rate = Saved / Income. Budget for a category = its Monthly Budget (x number of months for multi-month views).
Debt current balance = Starting Balance - all payments to date (never below 0). Goal saved = Starting Amount + all contributions to date.

CONTROLS: Month selector (default to the latest month that has transactions) with previous/next arrows, plus "Year to date".

SECTIONS (tabs across the top):
1. Overview - KPI cards: Income, Spent, Saved, Left Over (red if negative), Savings Rate. Budget vs actual for every category grouped by Group, with progress bars (green under 90%, amber 90-100%, red over 100%) and group subtotals; Income shows earned vs expected. Donut of spending by Group with total in the center. Top 5 spending categories. Recent 10 transactions.
2. Trends - for the last 12 months: Income vs Spent vs Saved line chart, Left Over bar chart, stacked bars of spending by Group, and a category picker to see one category's monthly trend against its budget.
3. Calendar - month calendar heatmap of daily spending (Fixed + Variable + Debt); tap a day to list its transactions. Cards: average spend per day, biggest expense, no-spend days.
4. Debt Payoff - a toggle for Snowball (smallest balance first) or Avalanche (highest APR first) and an input for monthly debt budget (default = total Monthly Budget of all Debt-group categories). Simulate month by month from current balances: each month add interest (balance x APR / 12), pay every debt its minimum (or its remaining balance), then put all leftover budget on the focus debt in strategy order; when a debt is paid off its payment rolls to the next. Show: debt-free date, total interest, months to go, a card per debt (current balance, APR, minimum, payoff month, "Focus" badge on the current target), a total-debt-over-time area chart, and a comparison line "Snowball vs Avalanche: X months / $Y interest". Warn if the budget is less than the total minimum payments.
5. Goals - card per goal with a progress ring, saved / target, target date, months left, and "Save $X per month to hit your date" (remaining / months left, minimum 1 month). Celebrate goals that are reached.

STYLE: Polished finance dashboard. White rounded cards with soft shadows on a light warm-gray background, accent #2F7D6D, headings #1E5A4E, Group colors: Income green, Fixed blue, Variable amber, Savings teal, Debt rose. Big bold numbers on KPI cards, money as $ with no decimals on cards. Responsive for laptop and phone.
```
