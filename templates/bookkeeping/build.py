"""Build the Small Business Bookkeeping + P&L Dashboard workbook (xlsx -> Google Sheets)."""
import datetime as dt, sys, random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.utils import get_column_letter as L

OUT = sys.argv[1] if len(sys.argv) > 1 else "Small-Business-Bookkeeping.xlsx"
YEAR = 2027
F = "Arial"; INK, MUTED = "1F2A37", "6B7280"
BRAND, BRAND_D, BRAND_L = "2F5D8A", "1E3F5E", "E4EDF6"
INPUT = "FFF7D6"; WARN, GOOD = "C2410C", "15803D"
MONEY = '$#,##0;-$#,##0;"-"'; MONEY2 = '$#,##0.00;-$#,##0.00;"-"'
thin = Side(style="thin", color="E5E7EB"); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
def font(**k): return Font(name=F, color=k.pop("color", INK), **k)
def fill(c): return PatternFill("solid", fgColor=c)
def base(ws, widths):
    ws.sheet_view.showGridLines = False; ws.column_dimensions["A"].width = 2
    for col, w in widths.items(): ws.column_dimensions[col].width = w
def title(ws, text, sub):
    ws["B1"] = text; ws["B1"].font = font(size=20, bold=True, color=BRAND_D); ws.row_dimensions[1].height = 32
    ws["B2"] = sub; ws["B2"].font = font(size=10, color=MUTED)
def header(ws, row, col0, labels):
    for i, t in enumerate(labels):
        c = ws.cell(row, col0 + i, t); c.font = font(bold=True, color="FFFFFF", size=10); c.fill = fill(BRAND)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = BOX
    ws.row_dimensions[row].height = 22
def cell(ws, ref, v=None, fmt=None, inp=False, bold=False, color=INK, size=10, align=None, bg=None):
    c = ws[ref]
    if v is not None: c.value = v
    c.font = font(bold=bold, color=color, size=size); c.border = BOX
    if fmt: c.number_format = fmt
    if inp: c.fill = fill(INPUT)
    if bg: c.fill = fill(bg)
    if align: c.alignment = Alignment(horizontal=align, vertical="center")
    return c
def note(ws, ref, text): ws[ref] = text; ws[ref].font = font(size=9, color=MUTED, italic=True)
def bar(ref): return f'REPT("█",MIN(20,ROUND({ref}*20,0)))&REPT("░",MAX(0,20-ROUND({ref}*20,0)))'

wb = Workbook()
start = wb.active; start.title = "Start Here"
setup = wb.create_sheet("Setup"); led = wb.create_sheet("Ledger"); dash = wb.create_sheet("Dashboard")
pl = wb.create_sheet("Profit & Loss"); tax = wb.create_sheet("Tax Summary"); mil = wb.create_sheet("Mileage")
for ws in wb.worksheets: ws.sheet_properties.tabColor = BRAND
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# ---------------- Setup ----------------
base(setup, {"B": 28, "C": 12, "D": 16, "E": 3, "F": 22, "G": 16, "H": 3, "I": 30})
title(setup, "Setup", "Step 1 - Your business details, categories and accounts. Yellow cells are yours to edit.")
for r, (k, v, fmt) in enumerate([("Business Name", "Sunny Day Candle Co.", None), ("Year", YEAR, "0"),
                                  ("Tax Set-Aside Rate", 0.25, "0%"), ("Mileage Rate ($/mile)", 0.70, "$0.000")], start=4):
    cell(setup, f"B{r}", k, bold=True); cell(setup, f"C{r}", v, fmt, inp=True, align="center"); setup.merge_cells(f"C{r}:D{r}")
note(setup, "F6", "Rough % of profit to save for income + self-employment tax. Ask your tax pro.")
note(setup, "F7", "Use the current IRS standard mileage rate (irs.gov).")
header(setup, 10, 2, ["Category", "Type", "Schedule C Line"])
CATS = [("Etsy Sales","Income","1"),("Shopify Sales","Income","1"),("Wholesale Orders","Income","1"),("Other Income","Income","6"),
 ("Refunds & Returns","Returns","2"),
 ("Product Materials","COGS","4"),("Packaging","COGS","4"),
 ("Advertising & Marketing","Expense","8"),("Platform & Payment Fees","Expense","10"),("Contract Labor","Expense","11"),
 ("Insurance","Expense","15"),("Legal & Professional","Expense","17"),("Office Expenses","Expense","18"),("Rent","Expense","20b"),
 ("Repairs & Maintenance","Expense","21"),("Supplies","Expense","22"),("Taxes & Licenses","Expense","23"),("Travel","Expense","24a"),
 ("Meals","Expense","24b"),("Utilities","Expense","25"),("Phone & Internet","Expense","25"),("Shipping & Postage","Expense","27a"),
 ("Software & Subscriptions","Expense","27a"),("Education & Training","Expense","27a"),("Bank Fees","Expense","27a"),
 ("Owner Draw","Transfer Out",""),("Owner Contribution","Transfer In",""),("Transfer Out","Transfer Out",""),("Transfer In","Transfer In","")]
C0, C1 = 11, 60
for i, r in enumerate(range(C0, C1 + 1)):
    v = CATS[i] if i < len(CATS) else (None, None, None)
    cell(setup, f"B{r}", v[0], inp=True); cell(setup, f"C{r}", v[1], inp=True, align="center"); cell(setup, f"D{r}", v[2], inp=True, align="center")
    setup[f"K{r}"] = f'=IF(B{r}="","",C{r}&"|"&COUNTIF(C${C0}:C{r},C{r}))'
setup.column_dimensions["K"].hidden = True
dv = DataValidation(type="list", formula1='"Income,Returns,COGS,Expense,Transfer In,Transfer Out"', allow_blank=True); setup.add_data_validation(dv); dv.add(f"C{C0}:C{C1}")
dv = DataValidation(type="list", formula1='"1,2,4,6,8,9,10,11,15,16b,17,18,20a,20b,21,22,23,24a,24b,25,26,27a"', allow_blank=True); setup.add_data_validation(dv); dv.add(f"D{C0}:D{C1}")
CAT, TYP, LINE, KEY = (f"Setup!${c}${C0}:${c}${C1}" for c in "BCDK")
header(setup, 10, 6, ["Account", "Starting Balance"])
ACCTS = [("Business Checking", 4200), ("Business Credit Card", 0), ("PayPal", 350), ("Cash", 100)]
A0, A1 = 11, 18
for i, r in enumerate(range(A0, A1 + 1)):
    v = ACCTS[i] if i < len(ACCTS) else (None, None)
    cell(setup, f"F{r}", v[0], inp=True); cell(setup, f"G{r}", v[1], MONEY2, inp=True)
ACC = f"Setup!$F${A0}:$F${A1}"
types_help = [("How category Types work", None), ("Income", "Sales and other money your business earns"),
 ("Returns", "Refunds you give customers (subtracted from sales)"), ("COGS", "Cost of goods sold - materials that go into what you sell"),
 ("Expense", "Everyday business costs (ads, fees, software...)"), ("Transfer In", "Money into an account that isn't income (owner contribution, card payment received)"), ("Transfer Out", "Money out that isn't an expense (owner pay, paying the credit card)")]
for i, (k, v) in enumerate(types_help):
    r = 21 + i
    setup[f"F{r}"] = k; setup[f"F{r}"].font = font(bold=True, color=BRAND_D if v is None else INK, size=11 if v is None else 10)
    if v: setup[f"G{r}"] = v; setup[f"G{r}"].font = font(size=9, color=MUTED)
note(setup, "F28", "Schedule C lines are a starting point for your tax pro - not tax advice.")
setup.freeze_panes = "B11"
for i, m in enumerate(MONTHS): setup[f"M{11+i}"] = m
setup["M23"] = "Full Year"
setup.column_dimensions["M"].hidden = True

# ---------------- Ledger ----------------
base(led, {"B": 13, "C": 30, "D": 22, "E": 24, "F": 20, "G": 13, "H": 11, "I": 10, "J": 26})
title(led, "Ledger", "Step 2 - Record every sale, expense and transfer. Enter amounts as positive numbers - the Type decides the direction.")
note(led, "B3", "Tip: paste in your bank/Etsy CSV, then pick a category for each row. Delete the sample rows when you start.")
header(led, 5, 2, ["Date", "Description", "Customer / Vendor", "Category", "Account", "Amount", "Type", "Receipt?", "Notes"])
T0, T1 = 6, 2505
random.seed(7)
d = lambda m, day: dt.date(YEAR, m, day)
S = []
for m in (1, 2, 3):
    season = {1: 0.8, 2: 1.15, 3: 0.95}[m]
    for day in (3, 10, 17, 24):
        amt = round(random.uniform(950, 1450) * season, 2); S.append((d(m, day), "Etsy deposit", "Etsy", "Etsy Sales", "Business Checking", amt))
        S.append((d(m, day), "Etsy fees + ads", "Etsy", "Platform & Payment Fees", "Business Checking", round(amt * 0.105, 2)))
    for day in (8, 22):
        amt = round(random.uniform(380, 620) * season, 2); S.append((d(m, day), "Shopify payout", "Shopify", "Shopify Sales", "Business Checking", amt))
        S.append((d(m, day), "Shopify Payments fees", "Shopify", "Platform & Payment Fees", "Business Checking", round(amt * 0.032, 2)))
    S += [(d(m, 15), "Wholesale order", ["Maple & Main Boutique", "The Gift Loft", "Harbor Home Goods"][m - 1], "Wholesale Orders", "Business Checking", [840, 1260, 960][m - 1]),
          (d(m, 2), "Soy wax + wicks", "CandleScience", "Product Materials", "Business Credit Card", round(random.uniform(520, 760), 2)),
          (d(m, 16), "Fragrance oils", "CandleScience", "Product Materials", "Business Credit Card", round(random.uniform(240, 380), 2)),
          (d(m, 5), "Jars + lids", "Uline", "Packaging", "Business Credit Card", round(random.uniform(210, 330), 2)),
          (d(m, 6), "Shipping labels", "Pirate Ship", "Shipping & Postage", "Business Credit Card", round(random.uniform(160, 260), 2)),
          (d(m, 20), "Shipping labels", "Pirate Ship", "Shipping & Postage", "Business Credit Card", round(random.uniform(140, 230), 2)),
          (d(m, 1), "Shopify plan", "Shopify", "Software & Subscriptions", "Business Credit Card", 39),
          (d(m, 1), "Canva Pro", "Canva", "Software & Subscriptions", "Business Credit Card", 15),
          (d(m, 9), "Instagram ads", "Meta", "Advertising & Marketing", "Business Credit Card", round(random.uniform(90, 160), 2)),
          (d(m, 12), "Phone + internet", "Verizon", "Phone & Internet", "Business Checking", 95),
          (d(m, 28), "Owner pay", "", "Owner Draw", "Business Checking", 1500),
          (d(m, 27), "Monthly account fee", "Chase", "Bank Fees", "Business Checking", 15)]
S = [s for s in S if s[5]]
S += [(d(1, 11), "Product liability insurance", "Next Insurance", "Insurance", "Business Checking", 186),
      (d(1, 14), "Business license renewal", "City of Austin", "Taxes & Licenses", "Business Checking", 75),
      (d(1, 19), "Lunch with wholesale buyer", "Café Java", "Meals", "Business Credit Card", 46.80),
      (d(2, 4), "Refund - broken jar", "Etsy customer", "Refunds & Returns", "Business Checking", 32),
      (d(2, 13), "Market booth fee", "Austin Makers Market", "Advertising & Marketing", "Business Checking", 125),
      (d(2, 18), "Product photographer", "Jess Rivera Photo", "Contract Labor", "Business Checking", 350),
      (d(3, 7), "Pricing for makers course", "Teachable", "Education & Training", "Business Credit Card", 97),
      (d(3, 10), "Label printer ink", "Amazon", "Supplies", "Business Credit Card", 64.99),
      (d(3, 21), "CPA consult", "Lopez Tax & Accounting", "Legal & Professional", "Business Checking", 250),
      (d(3, 26), "Refund - lost package", "Etsy customer", "Refunds & Returns", "Business Checking", 28.50)]
for m in (1, 2, 3):
    due = round(sum(x[5] for x in S if x[4] == "Business Credit Card" and x[0].month == m and x[0].day <= 25), 2)
    S += [(d(m, 26), "Credit card payment", "Chase", "Transfer Out", "Business Checking", due),
          (d(m, 26), "Payment received", "Chase", "Transfer In", "Business Credit Card", due)]
S.sort(key=lambda s: s[0])
for i, r in enumerate(range(T0, T1 + 1)):
    s = S[i] if i < len(S) else (None,) * 6
    cell(led, f"B{r}", s[0], "mmm d, yyyy", inp=True, align="center"); cell(led, f"C{r}", s[1], inp=True); cell(led, f"D{r}", s[2] or None, inp=True)
    cell(led, f"E{r}", s[3], inp=True); cell(led, f"F{r}", s[4], inp=True); cell(led, f"G{r}", s[5], MONEY2, inp=True)
    cell(led, f"H{r}", f'=IF(E{r}="","",IFERROR(INDEX({TYP},MATCH(E{r},{CAT},0)),"Unknown"))', align="center", color=MUTED)
    cell(led, f"I{r}", ("Yes" if s[3] not in (None, "Etsy Sales", "Shopify Sales", "Wholesale Orders", "Owner Draw", "Transfer Out", "Transfer In") else None), inp=True, align="center")
    cell(led, f"J{r}", None, inp=True)
for f1, rng in ((f"={CAT}", f"E{T0}:E{T1}"), (f"={ACC}", f"F{T0}:F{T1}"), ('"Yes,No"', f"I{T0}:I{T1}")):
    dv = DataValidation(type="list", formula1=f1, allow_blank=True); led.add_data_validation(dv); dv.add(rng)
led.conditional_formatting.add(f"H{T0}:H{T1}", CellIsRule(operator="equal", formula=['"Income"'], font=Font(name=F, color=GOOD, bold=True)))
led.conditional_formatting.add(f"H{T0}:H{T1}", CellIsRule(operator="equal", formula=['"Unknown"'], font=Font(name=F, color=WARN, bold=True)))
led.conditional_formatting.add(f"I{T0}:I{T1}", FormulaRule(formula=[f'AND(OR($H{T0}="Expense",$H{T0}="COGS"),$I{T0}<>"Yes")'], fill=fill("FDE7DC")))
led.freeze_panes = "B6"
LD, LC, LA, LAM = (f"Ledger!${c}${T0}:${c}${T1}" for c in "BEFG")

def per(cat_or_range, d0, d1, extra=""):
    return f'SUMIFS({LAM},{LC},{cat_or_range},{LD},">="&{d0},{LD},"<"&{d1}{extra})'
def by_type(t, d0, d1):
    return f'SUMPRODUCT(SUMIFS({LAM},{LC},{CAT},{LD},">="&{d0},{LD},"<"&{d1})*({TYP}="{t}"))'

# ---------------- Profit & Loss ----------------
base(pl, {"B": 28} | {L(c): 11 for c in range(3, 15)} | {"O": 13, "P": 11})
title(pl, "Profit & Loss", "Monthly P&L built automatically from your Ledger.")
pl["B3"] = '=Setup!C4&"  |  "&Setup!C5'; pl["B3"].font = font(bold=True, color=BRAND_D)
for i in range(12):
    c = L(3 + i); pl[f"{c}4"] = f"=DATE(Setup!$C$5,{i+1},1)"; pl[f"{c}5"] = f"=DATE(Setup!$C$5,{i+2},1)"
    for rr in (4, 5): pl[f"{c}{rr}"].font = font(size=1, color="FFFFFF"); pl[f"{c}{rr}"].number_format = "yyyy-mm-dd"
pl.row_dimensions[4].hidden = True; pl.row_dimensions[5].hidden = True
header(pl, 6, 2, [""] + [m[:3] for m in MONTHS] + ["Total", "% of Sales"])
row = 7
SECTIONS = [("Income", "INCOME", 6), ("Returns", "RETURNS & REFUNDS", 3), ("COGS", "COST OF GOODS SOLD", 6), ("Expense", "OPERATING EXPENSES", 25)]
TOTAL_LABEL = {"Income": "Total Income", "Returns": "Total Returns", "COGS": "Total COGS", "Expense": "Total Expenses"}
tot = {}
def section_header(r, text):
    pl[f"B{r}"] = text; pl[f"B{r}"].font = font(bold=True, color=BRAND_D, size=10)
    for c in range(2, 17): pl.cell(r, c).fill = fill(BRAND_L)
def total_row(r, label, formula_fn, bold=True, color=INK, pct=True, bg=None):
    cell(pl, f"B{r}", label, bold=bold, color=color, bg=bg)
    for i in range(13):
        c = L(3 + i); cell(pl, f"{c}{r}", formula_fn(c), MONEY, bold=bold, color=color, bg=bg)
    cell(pl, f"P{r}", f"=IF($O$NETSALES=0,0,O{r}/$O$NETSALES)" if pct else "", "0.0%", color=MUTED, bg=bg)
for t, label, n in SECTIONS:
    section_header(row, label); row += 1; first = row
    for k in range(1, n + 1):
        r = row
        cell(pl, f"B{r}", f'=IFERROR(INDEX({CAT},MATCH("{t}|{k}",{KEY},0)),"")')
        for i in range(12):
            c = L(3 + i); cell(pl, f"{c}{r}", f'=IF($B{r}="","",SUMIFS({LAM},{LC},$B{r},{LD},">="&{c}$4,{LD},"<"&{c}$5))', MONEY)
        cell(pl, f"O{r}", f'=IF($B{r}="","",SUM(C{r}:N{r}))', MONEY, bold=True)
        cell(pl, f"P{r}", f'=IF(OR($B{r}="",$O$NETSALES=0),"",O{r}/$O$NETSALES)', "0.0%", color=MUTED)
        row += 1
    tot[t] = row
    total_row(row, TOTAL_LABEL[t], lambda c, a=first, b=row - 1: f"=SUM({c}{a}:{c}{b})", bg=None)
    pl[f"Z{row}"] = f'=IF(COUNTIF({TYP},"{t}")>{n},"More {t} categories than rows - only the first {n} show here","")'
    row += 1
    if t == "Returns":
        total_row(row, "NET SALES", lambda c: f"={c}{tot['Income']}-{c}{tot['Returns']}", color=BRAND_D, bg=BRAND_L); tot["Net"] = row; row += 1
    if t == "COGS":
        total_row(row, "GROSS PROFIT", lambda c: f"={c}{tot['Net']}-{c}{tot['COGS']}", color=BRAND_D, bg=BRAND_L); tot["Gross"] = row; row += 1
    row += 1
total_row(row, "NET PROFIT", lambda c: f"={c}{tot['Gross']}-{c}{tot['Expense']}", color="FFFFFF", bg=BRAND_D); tot["NetP"] = row
pl.row_dimensions[row].height = 22; row += 1
cell(pl, f"B{row}", "Net Profit Margin", color=MUTED)
for i in range(13):
    c = L(3 + i); cell(pl, f"{c}{row}", f"=IF({c}{tot['Net']}=0,0,{c}{tot['NetP']}/{c}{tot['Net']})", "0.0%", color=MUTED)
tot["Margin"] = row
for r in range(7, row + 1):
    v = pl[f"P{r}"].value
    if isinstance(v, str): pl[f"P{r}"].value = v.replace("$O$NETSALES", f"$O${tot['Net']}")
    for c in range(3, 16):
        v = pl.cell(r, c).value
        if isinstance(v, str) and "NETSALES" in v: pl.cell(r, c).value = v.replace("$O$NETSALES", f"$O${tot['Net']}")
pl.conditional_formatting.add(f"C{tot['NetP']}:O{tot['NetP']}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, bold=True, color="FCA5A5")))
for t in tot.values(): pl[f"Z{t}"].font = font(bold=True, color=WARN)
pl.freeze_panes = "C7"
NETP_ROW, NET_ROW, EXP_ROW = tot["NetP"], tot["Net"], tot["Expense"]

# ---------------- Dashboard ----------------
base(dash, {"B": 26, "C": 13, "D": 13, "E": 13, "F": 13, "G": 13, "H": 24})
title(dash, "Business Dashboard", "Choose a month or Full Year - everything updates from your Ledger.")
dash["B3"] = "=Setup!C4"; dash["B3"].font = font(bold=True, color=BRAND_D, size=12)
cell(dash, "B4", "Period", bold=True); cell(dash, "C4", "Full Year", inp=True, bold=True, align="center"); dash.merge_cells("C4:D4")
dv = DataValidation(type="list", formula1="=Setup!$M$11:$M$23"); dash.add_data_validation(dv); dv.add("C4")
cell(dash, "E4", "Year", bold=True, align="right"); cell(dash, "F4", "=Setup!C5", "0", bold=True, align="center")
dash["K4"] = '=IF(C4="Full Year",DATE(F4,1,1),DATE(F4,MATCH(C4,Setup!$M$11:$M$22,0),1))'
dash["K5"] = '=IF(C4="Full Year",DATE(F4+1,1,1),EDATE(K4,1))'
for r in ("K4", "K5"): dash[r].number_format = "yyyy-mm-dd"
D0, D1 = "$K$4", "$K$5"
K = [("B", "NET SALES", f"={by_type('Income', D0, D1)}-{by_type('Returns', D0, D1)}", MONEY),
     ("D", "GROSS PROFIT", f"=B8-{by_type('COGS', D0, D1)}", MONEY),
     ("E", "EXPENSES", f"={by_type('Expense', D0, D1)}", MONEY),
     ("F", "NET PROFIT", "=D8-E8", MONEY),
     ("G", "PROFIT MARGIN", "=IF(B8=0,0,F8/B8)", "0%"),
     ("H", "SET ASIDE FOR TAX", "=MAX(0,F8)*Setup!C6", MONEY)]
for col, lab, f, fmt in K:
    a = dash[f"{col}7"]; a.value = lab; a.font = font(size=8, bold=True, color=MUTED); a.fill = fill(BRAND_L)
    b = dash[f"{col}8"]; b.value = f; b.font = font(size=16, bold=True, color=BRAND_D); b.fill = fill(BRAND_L); b.number_format = fmt
    for c in (a, b): c.alignment = Alignment(horizontal="center", vertical="center")
dash.merge_cells("B7:C7"); dash.merge_cells("B8:C8"); dash.row_dimensions[8].height = 34
dash.conditional_formatting.add("F8", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, size=16, bold=True, color=WARN)))
# Top expenses
header(dash, 11, 2, ["Top Expenses", "", "Amount", "% of Sales", "Share", "", ""])
dash.merge_cells("B11:C11"); dash.merge_cells("F11:H11")
for i, sr in enumerate(range(C0, C1 + 1)):
    dash[f"M{11+i}"] = f'=IF(OR(Setup!B{sr}="",AND(Setup!C{sr}<>"Expense",Setup!C{sr}<>"COGS")),-1,{per(f"Setup!B{sr}", D0, D1)})+ROW()/10000000'
dash.column_dimensions["M"].hidden = True; dash.column_dimensions["K"].hidden = True
MH = f"$M$11:$M${11 + C1 - C0}"
for k in range(1, 9):
    r = 11 + k
    dash[f"N{r}"] = f"=LARGE({MH},{k})"
    cell(dash, f"B{r}", f'=IF(N{r}<0.5,"",INDEX({CAT},MATCH(N{r},{MH},0)))'); dash.merge_cells(f"B{r}:C{r}")
    cell(dash, f"D{r}", f'=IF(B{r}="","",ROUND(N{r},2))', MONEY)
    cell(dash, f"E{r}", f'=IF(OR(B{r}="",$B$8=0),"",D{r}/$B$8)', "0%", align="center")
    cell(dash, f"F{r}", f'=IF(B{r}="","",{bar(f"D{r}/MAX($D$12:$D$19)")})', color=BRAND); dash.merge_cells(f"F{r}:H{r}")
dash.column_dimensions["N"].hidden = True
# Accounts
header(dash, 22, 2, ["Account", "", "Starting", "Money In", "Money Out", "Balance", ""])
dash.merge_cells("B22:C22")
for i, ar in enumerate(range(A0, A1 + 1)):
    r = 23 + i
    cell(dash, f"B{r}", f'=IF(Setup!F{ar}="","",Setup!F{ar})'); dash.merge_cells(f"B{r}:C{r}")
    cell(dash, f"D{r}", f'=IF(B{r}="","",Setup!G{ar})', MONEY)
    inn = f'SUMPRODUCT(SUMIFS({LAM},{LA},B{r},{LC},{CAT})*(({TYP}="Income")+({TYP}="Transfer In")))'
    out = f'SUMPRODUCT(SUMIFS({LAM},{LA},B{r},{LC},{CAT})*(({TYP}="Returns")+({TYP}="COGS")+({TYP}="Expense")+({TYP}="Transfer Out")))'
    cell(dash, f"E{r}", f'=IF(B{r}="","",{inn})', MONEY); cell(dash, f"F{r}", f'=IF(B{r}="","",{out})', MONEY)
    cell(dash, f"G{r}", f'=IF(B{r}="","",D{r}+E{r}-F{r})', MONEY, bold=True)
note(dash, "B32", "Account balances use all Ledger entries (not just the selected period). Credit card balances show as negative = owed.")
ch = BarChart(); ch.title = "Sales vs Expenses by Month"; ch.style = 10
for rr, nm in ((NET_ROW, "Net Sales"), (EXP_ROW, "Expenses")):
    ch.add_data(Reference(pl, min_col=3, max_col=14, min_row=rr), from_rows=True, titles_from_data=False)
for s, nm in zip(ch.series, ["Net Sales", "Expenses"]): s.tx = SeriesLabel(v=nm)
ch.set_categories(Reference(pl, min_col=3, max_col=14, min_row=6)); ch.height = 7.5; ch.width = 16
ch.y_axis.numFmt = '$#,##0'; ch.y_axis.majorGridlines = None
dash.add_chart(ch, "J7")
lc = BarChart(); lc.title = "Net Profit by Month"; lc.style = 10
lc.add_data(Reference(pl, min_col=3, max_col=14, min_row=NETP_ROW), from_rows=True, titles_from_data=False)
lc.set_categories(Reference(pl, min_col=3, max_col=14, min_row=6)); lc.height = 7.5; lc.width = 16; lc.legend = None
lc.y_axis.numFmt = '$#,##0'; lc.y_axis.majorGridlines = None
dash.add_chart(lc, "J23")

# ---------------- Tax Summary ----------------
base(tax, {"B": 10, "C": 34, "D": 15, "E": 12, "F": 15, "G": 3, "H": 22, "I": 14, "J": 14, "K": 15, "L": 14})
title(tax, "Tax Summary", "Year-to-date totals by Schedule C line, plus quarterly estimated tax set-asides.")
note(tax, "B3", "Estimates to share with your tax preparer - not tax advice. Meals are counted at 50%.")
tax["N4"] = "=DATE(Setup!C5,1,1)"; tax["N5"] = "=DATE(Setup!C5+1,1,1)"; tax.column_dimensions["N"].hidden = True
header(tax, 5, 2, ["Line", "Description", "Amount", "Deductible %", "Tax Amount"])
LINES = [("1", "Gross receipts or sales"), ("2", "Returns and allowances"), ("4", "Cost of goods sold"), ("6", "Other income"),
 ("8", "Advertising"), ("9", "Car and truck expenses (incl. mileage)"), ("10", "Commissions and fees"), ("11", "Contract labor"),
 ("15", "Insurance (other than health)"), ("16b", "Interest (other)"), ("17", "Legal and professional services"), ("18", "Office expense"),
 ("20a", "Rent - vehicles, machinery, equipment"), ("20b", "Rent - other business property"), ("21", "Repairs and maintenance"),
 ("22", "Supplies"), ("23", "Taxes and licenses"), ("24a", "Travel"), ("24b", "Deductible meals"), ("25", "Utilities"),
 ("26", "Wages"), ("27a", "Other expenses")]
X0 = 6
for i, (ln, desc) in enumerate(LINES):
    r = X0 + i
    cell(tax, f"B{r}", ln, align="center", bold=True); cell(tax, f"C{r}", desc)
    f = f'SUMPRODUCT(SUMIFS({LAM},{LC},{CAT},{LD},">="&$N$4,{LD},"<"&$N$5)*({LINE}=B{r}))'
    if ln == "9": f += "+Mileage!$G$4"
    cell(tax, f"D{r}", "=" + f, MONEY2)
    cell(tax, f"E{r}", 0.5 if ln == "24b" else 1, "0%", align="center", inp=(ln == "24b"))
    cell(tax, f"F{r}", f"=D{r}*E{r}", MONEY2, bold=True)
XL = X0 + len(LINES) - 1
rr = XL + 2
summary = [("Gross income (1 - 2 - 4 + 6)", f"=F{X0}-F{X0+1}-F{X0+2}+F{X0+3}"), ("Total expenses (8 - 27a)", f"=SUM(F{X0+4}:F{XL})"),
           ("Estimated net profit", f"=D{rr}-D{rr+1}"), ("Tax set-aside (" + "rate on Setup)", f"=MAX(0,D{rr+2})*Setup!C6")]
for i, (lab, f) in enumerate(summary):
    r = rr + i; cell(tax, f"C{r}", lab, bold=True, bg=BRAND_L if i == 2 else None); cell(tax, f"D{r}", f, MONEY2, bold=True, bg=BRAND_L if i == 2 else None)
header(tax, 5, 8, ["Estimated Tax", "Period Start", "Period End", "Net Profit", "Set Aside"])
Q = [("Q1 (due Apr 15)", (1, 1), (4, 1)), ("Q2 (due Jun 15)", (4, 1), (6, 1)), ("Q3 (due Sep 15)", (6, 1), (9, 1)), ("Q4 (due Jan 15)", (9, 1), (13, 1))]
for i, (lab, a, b) in enumerate(Q):
    r = 6 + i
    cell(tax, f"H{r}", lab, bold=True)
    cell(tax, f"I{r}", f"=DATE(Setup!$C$5,{a[0]},{a[1]})", "mmm d", align="center")
    cell(tax, f"J{r}", f"=DATE(Setup!$C$5,{b[0]},{b[1]})-1", "mmm d", align="center")
    i1 = f'SUMPRODUCT(SUMIFS({LAM},{LC},{CAT},{LD},">="&I{r},{LD},"<="&J{r})*(({TYP}="Income")-({TYP}="Returns")-({TYP}="COGS")-({TYP}="Expense")))'
    cell(tax, f"K{r}", "=" + i1, MONEY)
    cell(tax, f"L{r}", f"=MAX(0,K{r})*Setup!$C$6", MONEY, bold=True, color=BRAND_D)
cell(tax, "H10", "Total", bold=True, bg=BRAND_L)
for c in "IJ": cell(tax, f"{c}10", "", bg=BRAND_L)
cell(tax, "K10", "=SUM(K6:K9)", MONEY, bold=True, bg=BRAND_L); cell(tax, "L10", "=SUM(L6:L9)", MONEY, bold=True, bg=BRAND_L)
note(tax, "H11", "IRS estimated-tax periods. Due dates move to the next business day on weekends/holidays.")
note(tax, "H12", "Quarterly profit excludes mileage and the 50% meals limit - see the Schedule C table for those.")
tax.freeze_panes = "B6"

# ---------------- Mileage ----------------
base(mil, {"B": 13, "C": 32, "D": 20, "E": 20, "F": 10, "G": 14})
title(mil, "Mileage Log", "Log business trips - the deduction flows to Schedule C line 9 on the Tax Summary.")
cell(mil, "B4", "Total miles", bold=True); cell(mil, "C4", "=SUM(F7:F506)", "#,##0.0", bold=True)
cell(mil, "F4", "Deduction", bold=True, align="right"); cell(mil, "G4", "=SUMPRODUCT((YEAR(B7:B506)=Setup!C5)*(F7:F506))*Setup!C7", MONEY2, bold=True, color=BRAND_D)
header(mil, 6, 2, ["Date", "Purpose", "From", "To", "Miles", "Deduction"])
TRIPS = [(d(1, 15), "Deliver wholesale order", "Studio", "Maple & Main Boutique", 18.4), (d(1, 27), "Supply pickup", "Studio", "Hobby Lobby", 9.2),
         (d(2, 13), "Makers market booth", "Studio", "Austin Makers Market", 22.6), (d(2, 15), "Deliver wholesale order", "Studio", "The Gift Loft", 31.0),
         (d(3, 15), "Deliver wholesale order", "Studio", "Harbor Home Goods", 26.8), (d(3, 21), "CPA meeting", "Studio", "Lopez Tax & Accounting", 12.5)]
for i, r in enumerate(range(7, 507)):
    t = TRIPS[i] if i < len(TRIPS) else (None,) * 5
    cell(mil, f"B{r}", t[0], "mmm d, yyyy", inp=True, align="center"); cell(mil, f"C{r}", t[1], inp=True)
    cell(mil, f"D{r}", t[2], inp=True); cell(mil, f"E{r}", t[3], inp=True); cell(mil, f"F{r}", t[4], "#,##0.0", inp=True, align="center")
    cell(mil, f"G{r}", f'=IF(F{r}="","",F{r}*Setup!$C$7)', MONEY2)
mil.freeze_panes = "B7"

# ---------------- Start Here ----------------
base(start, {"B": 4, "C": 92})
start["B1"] = "Small Business Bookkeeping + P&L Dashboard"; start["B1"].font = font(size=24, bold=True, color=BRAND_D); start.row_dimensions[1].height = 40
start["B2"] = "Track sales and expenses, see your profit, and be ready for tax time - all in one Google Sheet."; start["B2"].font = font(size=11, color=MUTED)
lines = [("h", "Get started in 10 minutes"),
 ("1", "Setup - add your business name, year, tax set-aside %, categories and accounts (bank, credit card, PayPal...)."),
 ("2", "Ledger - record every sale and expense. Pick a category and account from the dropdowns."),
 ("3", "Dashboard - choose a month or Full Year to see sales, profit, margin, top expenses and account balances."),
 ("4", "Profit & Loss - your monthly P&L statement builds itself."),
 ("5", "Tax Summary - totals by Schedule C line and how much to set aside each quarter."),
 ("6", "Mileage - log business drives; the deduction flows to the Tax Summary."),
 ("", ""), ("h", "How the colors work"),
 ("in", "Yellow cells are yours to type in. Everything else calculates automatically."),
 ("•", "In the Ledger, expense rows without a receipt are highlighted so nothing slips through."),
 ("", ""), ("h", "Tips"),
 ("•", "Sample data for a small candle shop shows how it works - delete the sample rows when you're ready."),
 ("•", "Enter every amount as a positive number. The category's Type (Income, Returns, COGS, Expense, Equity) decides the direction."),
 ("•", "Paying yourself? Use 'Owner Draw' - it lowers your bank balance but isn't a business expense."),
 ("•", "Moving money between accounts (like paying the credit card)? Add two rows: Transfer Out from one account, Transfer In to the other."),
 ("•", "Schedule C lines are a helpful starting point - always confirm with your tax professional."),
 ("", ""), ("h", "Questions?"),
 ("", "Send me a message on Etsy - I'm happy to help. Thank you for your purchase!")]
r = 4
for k, t in lines:
    if k == "h": start[f"B{r}"] = t; start[f"B{r}"].font = font(size=13, bold=True, color=BRAND_D)
    else:
        start[f"B{r}"] = "" if k == "in" else k; start[f"B{r}"].font = font(bold=True, color=BRAND); start[f"B{r}"].alignment = Alignment(vertical="top")
        if k == "in": start[f"B{r}"].fill = fill(INPUT)
        start[f"C{r}"] = t; start[f"C{r}"].font = font(size=11); start[f"C{r}"].alignment = Alignment(wrap_text=True, vertical="top")
    r += 1

wb.active = wb.worksheets.index(dash)
wb.save(OUT); print("saved", OUT, "| ledger rows", len(S))
