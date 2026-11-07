"""Build the All-in-One Budget Planner workbook (xlsx -> upload to Google Drive, opens as Google Sheets)."""
import datetime as dt, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, LineChart, DoughnutChart, Reference
from openpyxl.utils import get_column_letter as L

OUT = sys.argv[1] if len(sys.argv) > 1 else "All-in-One-Budget-Planner.xlsx"
YEAR = 2027
F = "Arial"
INK, MUTED = "1F2A37", "6B7280"
BRAND, BRAND_D, BRAND_L = "2F7D6D", "1E5A4E", "E3F1EE"
INPUT = "FFF7D6"
WARN, GOOD = "C2410C", "15803D"
MONEY = '$#,##0;-$#,##0;"-"'
MONEY2 = '$#,##0.00;-$#,##0.00;"-"'
thin = Side(style="thin", color="E5E7EB")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)

def font(**k): return Font(name=F, color=k.pop("color", INK), **k)
def fill(c): return PatternFill("solid", fgColor=c)

def base(ws, widths):
    ws.sheet_view.showGridLines = False
    for col, w in widths.items(): ws.column_dimensions[col].width = w
    ws.column_dimensions["A"].width = 2

def title(ws, text, sub):
    ws["B1"] = text; ws["B1"].font = font(size=20, bold=True, color=BRAND_D)
    ws["B2"] = sub; ws["B2"].font = font(size=10, color=MUTED)
    ws.row_dimensions[1].height = 32

def header(ws, row, col0, labels):
    for i, t in enumerate(labels):
        c = ws.cell(row, col0 + i, t)
        c.font = font(bold=True, color="FFFFFF", size=10); c.fill = fill(BRAND)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = BOX
    ws.row_dimensions[row].height = 22

def cell(ws, ref, v=None, fmt=None, inp=False, bold=False, color=INK, size=10, align=None):
    c = ws[ref]
    if v is not None: c.value = v
    c.font = font(bold=bold, color=color, size=size)
    if fmt: c.number_format = fmt
    if inp: c.fill = fill(INPUT)
    c.border = BOX
    if align: c.alignment = Alignment(horizontal=align, vertical="center")
    return c

wb = Workbook()
start = wb.active; start.title = "Start Here"
setup = wb.create_sheet("Setup"); tx = wb.create_sheet("Transactions"); dash = wb.create_sheet("Dashboard")
annual = wb.create_sheet("Annual"); debt = wb.create_sheet("Debt Payoff"); sink = wb.create_sheet("Sinking Funds")
for ws in wb.worksheets: ws.sheet_properties.tabColor = BRAND

# ---------------- Setup ----------------
base(setup, {"B": 26, "C": 14, "D": 18, "E": 3, "F": 30, "G": 16, "H": 12})
title(setup, "Setup", "Step 1 - Enter your budget year, income sources and spending categories. Yellow cells are yours to edit.")
cell(setup, "B4", "Budget Year", bold=True); cell(setup, "C4", YEAR, inp=True, align="center")
header(setup, 6, 2, ["Category", "Type", "Monthly Budget"])
CATS = [("Paycheck", "Income", 4800), ("Side Hustle", "Income", 600),
        ("Rent / Mortgage", "Fixed", 1650), ("Utilities", "Fixed", 220), ("Phone & Internet", "Fixed", 140),
        ("Insurance", "Fixed", 180), ("Car Payment", "Fixed", 385), ("Subscriptions", "Fixed", 45),
        ("Groceries", "Variable", 600), ("Dining Out", "Variable", 200), ("Gas", "Variable", 180),
        ("Shopping", "Variable", 150), ("Entertainment", "Variable", 100), ("Personal Care", "Variable", 60),
        ("Miscellaneous", "Variable", 100),
        ("Emergency Fund", "Savings", 300), ("Vacation", "Savings", 150), ("Christmas Gifts", "Savings", 75),
        ("Car Repairs", "Savings", 50), ("Debt Payments", "Debt", 600)]
C0, C1 = 7, 46  # 40 category rows
for i, r in enumerate(range(C0, C1 + 1)):
    v = CATS[i] if i < len(CATS) else (None, None, None)
    cell(setup, f"B{r}", v[0], inp=True); cell(setup, f"C{r}", v[1], inp=True, align="center")
    cell(setup, f"D{r}", v[2], MONEY, inp=True)
dv = DataValidation(type="list", formula1='"Income,Fixed,Variable,Savings,Debt"', allow_blank=True)
setup.add_data_validation(dv); dv.add(f"C{C0}:C{C1}")
CAT = f"Setup!$B${C0}:$B${C1}"; TYP = f"Setup!$C${C0}:$C${C1}"; BUD = f"Setup!$D${C0}:$D${C1}"
# Summary
cell(setup, "F6", "Budget Summary (monthly)", bold=True, color="FFFFFF").fill = fill(BRAND); setup["G6"].fill = fill(BRAND)
rows = [("Income", f'=SUMIFS({BUD},{TYP},"Income")'), ("Fixed", f'=SUMIFS({BUD},{TYP},"Fixed")'),
        ("Variable", f'=SUMIFS({BUD},{TYP},"Variable")'), ("Savings", f'=SUMIFS({BUD},{TYP},"Savings")'),
        ("Debt", f'=SUMIFS({BUD},{TYP},"Debt")'), ("Left to assign", "=G7-SUM(G8:G11)")]
for i, (k, f) in enumerate(rows):
    r = 7 + i; cell(setup, f"F{r}", k, bold=(i == 5)); cell(setup, f"G{r}", f, MONEY, bold=(i == 5))
setup["F14"] = "Tip: aim for $0 left to assign - every dollar gets a job."; setup["F14"].font = font(size=9, color=MUTED, italic=True)
setup.conditional_formatting.add("G12", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, bold=True, color=WARN)))
setup.conditional_formatting.add("G12", CellIsRule(operator="greaterThanOrEqual", formula=["0"], font=Font(name=F, bold=True, color=GOOD)))
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
setup["I6"] = "Months"; setup["I6"].font = font(size=8, color=MUTED)
for i, m in enumerate(MONTHS): setup[f"I{7+i}"] = m; setup[f"I{7+i}"].font = font(size=8, color=MUTED)
setup.column_dimensions["I"].hidden = True
setup.freeze_panes = "B7"

# ---------------- Transactions ----------------
base(tx, {"B": 13, "C": 30, "D": 22, "E": 14, "F": 14, "G": 30})
title(tx, "Transactions", "Step 2 - Log every purchase, bill and paycheck. Pick a category from the dropdown; Type fills in automatically.")
tx["B3"] = "Enter amounts as positive numbers. Delete the sample rows when you're ready to start."; tx["B3"].font = font(size=9, color=MUTED, italic=True)
header(tx, 5, 2, ["Date", "Description", "Category", "Amount", "Type", "Notes"])
T0, T1 = 6, 1505
d = lambda m, day: dt.date(YEAR, m, day)
SAMPLE = [(d(1,1),"Rent","Rent / Mortgage",1650),(d(1,2),"Netflix + Spotify","Subscriptions",45),(d(1,3),"Kroger","Groceries",142.18),
 (d(1,4),"Shell","Gas",48.20),(d(1,5),"Electric bill","Utilities",118.40),(d(1,6),"Chipotle","Dining Out",24.75),
 (d(1,7),"Transfer to savings","Emergency Fund",300),(d(1,8),"Car payment","Car Payment",385),(d(1,9),"Target","Shopping",63.12),
 (d(1,10),"Trader Joe's","Groceries",96.44),(d(1,12),"Movie night","Entertainment",32.00),(d(1,14),"Paycheck","Paycheck",2400),
 (d(1,14),"Visa payment","Debt Payments",380),(d(1,15),"Verizon","Phone & Internet",140),(d(1,16),"Water + gas bill","Utilities",76.10),
 (d(1,17),"Kroger","Groceries",131.02),(d(1,18),"Haircut","Personal Care",35),(d(1,19),"Shell","Gas",51.60),
 (d(1,20),"Etsy sales payout","Side Hustle",640),(d(1,21),"Pizza night","Dining Out",38.50),(d(1,22),"Car insurance","Insurance",180),
 (d(1,23),"Vacation fund","Vacation",150),(d(1,24),"Costco","Groceries",188.73),(d(1,25),"Amazon","Shopping",41.99),
 (d(1,26),"Christmas fund","Christmas Gifts",75),(d(1,27),"Car repair fund","Car Repairs",50),(d(1,28),"Paycheck","Paycheck",2400),
 (d(1,28),"Store card + student loan","Debt Payments",220),(d(1,29),"Coffee shop","Dining Out",18.40),(d(1,30),"Shell","Gas",44.90),
 (d(1,31),"Birthday gift","Miscellaneous",45),
 (d(2,1),"Rent","Rent / Mortgage",1650),(d(2,2),"Netflix + Spotify","Subscriptions",45),(d(2,3),"Kroger","Groceries",155.30),
 (d(2,5),"Electric bill","Utilities",124.90),(d(2,7),"Transfer to savings","Emergency Fund",300),(d(2,8),"Car payment","Car Payment",385),
 (d(2,9),"Super Bowl party","Entertainment",85),(d(2,11),"Paycheck","Paycheck",2400),(d(2,11),"Visa payment","Debt Payments",380),
 (d(2,12),"Shell","Gas",46.75),(d(2,14),"Valentine's dinner","Dining Out",96.00),(d(2,15),"Verizon","Phone & Internet",140),
 (d(2,16),"Kroger","Groceries",128.64),(d(2,17),"Water + gas bill","Utilities",81.35),(d(2,18),"Etsy sales payout","Side Hustle",585),
 (d(2,19),"Target","Shopping",72.40),(d(2,20),"Car insurance","Insurance",180),(d(2,21),"Vacation fund","Vacation",150),
 (d(2,22),"Costco","Groceries",201.15),(d(2,23),"Shell","Gas",49.80),(d(2,24),"Christmas fund","Christmas Gifts",75),
 (d(2,24),"Car repair fund","Car Repairs",50),(d(2,25),"Paycheck","Paycheck",2400),(d(2,25),"Store card + student loan","Debt Payments",220),
 (d(2,26),"Nails","Personal Care",45),(d(2,27),"Trader Joe's","Groceries",88.90),(d(2,28),"Taco Tuesday","Dining Out",42.30)]
for i, r in enumerate(range(T0, T1 + 1)):
    s = SAMPLE[i] if i < len(SAMPLE) else (None, None, None, None)
    cell(tx, f"B{r}", s[0], "mmm d, yyyy", inp=True, align="center"); cell(tx, f"C{r}", s[1], inp=True)
    cell(tx, f"D{r}", s[2], inp=True); cell(tx, f"E{r}", s[3], MONEY2, inp=True)
    cell(tx, f"F{r}", f'=IF(D{r}="","",IFERROR(INDEX({TYP},MATCH(D{r},{CAT},0)),"Unknown"))', align="center", color=MUTED)
    cell(tx, f"G{r}", None, inp=True)
dv = DataValidation(type="list", formula1=f"={CAT}", allow_blank=True); tx.add_data_validation(dv); dv.add(f"D{T0}:D{T1}")
dvd = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True); tx.add_data_validation(dvd); dvd.add(f"B{T0}:B{T1}")
tx.conditional_formatting.add(f"F{T0}:F{T1}", CellIsRule(operator="equal", formula=['"Income"'], font=Font(name=F, color=GOOD, bold=True)))
tx.conditional_formatting.add(f"F{T0}:F{T1}", CellIsRule(operator="equal", formula=['"Unknown"'], font=Font(name=F, color=WARN, bold=True)))
tx.freeze_panes = "B6"
TD, TC, TA = f"Transactions!$B${T0}:$B${T1}", f"Transactions!$D${T0}:$D${T1}", f"Transactions!$E${T0}:$E${T1}"

# ---------------- Dashboard ----------------
base(dash, {"B": 24, "C": 12, "D": 15, "E": 15, "F": 15, "G": 11, "H": 24})
title(dash, "Monthly Dashboard", "Pick a month - everything updates from your Transactions.")
cell(dash, "B4", "Month", bold=True); cell(dash, "C4", "January", inp=True, bold=True, align="center")
dash.merge_cells("C4:D4")
dv = DataValidation(type="list", formula1="=Setup!$I$7:$I$18"); dash.add_data_validation(dv); dv.add("C4")
cell(dash, "E4", "Year", bold=True, align="right"); cell(dash, "F4", "=Setup!C4", align="center", bold=True)
dash["J4"] = "=DATE(F4,MATCH(C4,Setup!$I$7:$I$18,0),1)"; dash["J5"] = "=EDATE(J4,1)"
for r in ("J4", "J5"): dash[r].number_format = "yyyy-mm-dd"; dash[r].font = font(size=8, color=MUTED)
dash.column_dimensions["J"].hidden = True
DR = f'{TD},">="&$J$4,{TD},"<"&$J$5'
# KPI tiles row 6-8
kpis = [("B", "INCOME", f'=SUMPRODUCT(SUMIFS({TA},{TC},{CAT},{DR})*({TYP}="Income"))'),
        ("D", "SPENT", f'=SUMPRODUCT(SUMIFS({TA},{TC},{CAT},{DR})*(({TYP}="Fixed")+({TYP}="Variable")+({TYP}="Debt")))'),
        ("E", "SAVED", f'=SUMPRODUCT(SUMIFS({TA},{TC},{CAT},{DR})*({TYP}="Savings"))'),
        ("F", "LEFT OVER", "=B8-D8-E8"), ("G", "SAVINGS RATE", '=IF(B8=0,0,E8/B8)')]
for col, lab, f in kpis:
    a = dash[f"{col}7"]; a.value = lab; a.font = font(size=8, bold=True, color=MUTED); a.fill = fill(BRAND_L)
    b = dash[f"{col}8"]; b.value = f; b.font = font(size=16, bold=True, color=BRAND_D); b.fill = fill(BRAND_L)
    b.number_format = "0%" if col == "G" else MONEY
    for c in (a, b): c.alignment = Alignment(horizontal="center", vertical="center")
dash.merge_cells("B7:C7"); dash.merge_cells("B8:C8"); dash.row_dimensions[8].height = 34
dash.conditional_formatting.add("F8", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, size=16, bold=True, color=WARN)))
# Type summary rows 11-15
header(dash, 10, 2, ["By Type", "", "Budget", "Actual", "Remaining", "% Used", "Progress"])
dash.merge_cells("B10:C10")
for i, t in enumerate(["Income", "Fixed", "Variable", "Savings", "Debt"]):
    r = 11 + i
    cell(dash, f"B{r}", t, bold=True); dash.merge_cells(f"B{r}:C{r}")
    cell(dash, f"D{r}", f'=SUMIFS({BUD},{TYP},B{r})', MONEY)
    cell(dash, f"E{r}", f'=SUMPRODUCT(SUMIFS({TA},{TC},{CAT},{DR})*({TYP}=B{r}))', MONEY)
    cell(dash, f"F{r}", f"=D{r}-E{r}", MONEY); cell(dash, f"G{r}", f"=IF(D{r}=0,0,E{r}/D{r})", "0%", align="center")
    cell(dash, f"H{r}", f'=REPT("█",MIN(20,ROUND(G{r}*20,0)))&REPT("░",MAX(0,20-ROUND(G{r}*20,0)))', color=BRAND)
# Category detail rows 18+
header(dash, 17, 2, ["Category", "Type", "Budget", "Actual", "Remaining", "% Used", "Progress"])
for i, sr in enumerate(range(C0, C1 + 1)):
    r = 18 + i
    cell(dash, f"B{r}", f'=IF(Setup!B{sr}="","",Setup!B{sr})'); cell(dash, f"C{r}", f'=IF(B{r}="","",Setup!C{sr})', align="center", color=MUTED)
    cell(dash, f"D{r}", f'=IF(B{r}="","",Setup!D{sr})', MONEY)
    cell(dash, f"E{r}", f'=IF(B{r}="","",SUMIFS({TA},{TC},B{r},{DR}))', MONEY)
    cell(dash, f"F{r}", f'=IF(B{r}="","",D{r}-E{r})', MONEY)
    cell(dash, f"G{r}", f'=IF(B{r}="","",IF(D{r}=0,0,E{r}/D{r}))', "0%", align="center")
    cell(dash, f"H{r}", f'=IF(B{r}="","",REPT("█",MIN(20,ROUND(G{r}*20,0)))&REPT("░",MAX(0,20-ROUND(G{r}*20,0))))', color=BRAND)
DLAST = 18 + (C1 - C0)
dash.conditional_formatting.add(f"F18:F{DLAST}", FormulaRule(formula=[f'AND($C18<>"Income",$C18<>"",F18<0)'], font=Font(name=F, color=WARN, bold=True)))
dash.conditional_formatting.add(f"H18:H{DLAST}", FormulaRule(formula=[f'AND($C18<>"Income",$G18>1)'], font=Font(name=F, color=WARN)))
ch = BarChart(); ch.type = "bar"; ch.title = "Budget vs Actual"; ch.style = 10
ch.add_data(Reference(dash, min_col=4, max_col=5, min_row=10, max_row=15), titles_from_data=True)
ch.set_categories(Reference(dash, min_col=2, min_row=11, max_row=15)); ch.height = 7.5; ch.width = 14
ch.y_axis.numFmt = '$#,##0'; ch.y_axis.majorGridlines = None
dash.add_chart(ch, "J7")
dn = DoughnutChart(); dn.title = "Where the money went"
dn.add_data(Reference(dash, min_col=5, min_row=12, max_row=15)); dn.set_categories(Reference(dash, min_col=2, min_row=12, max_row=15))
dn.height = 7.5; dn.width = 14; dash.add_chart(dn, "J23")
dash.freeze_panes = "B10"

# ---------------- Annual ----------------
base(annual, {"B": 24, "C": 10} | {L(c): 11 for c in range(4, 16)} | {"P": 13, "Q": 12, "R": 13})
title(annual, "Annual Overview", "Your whole year at a glance - actuals by month from Transactions.")
annual["B3"] = "=\"Year: \"&Setup!C4"; annual["B3"].font = font(bold=True, color=BRAND_D)
header(annual, 5, 2, ["", "Type"] + [m[:3] for m in MONTHS] + ["Total", "Avg / Month"])
for i in range(12):
    c = L(4 + i)
    annual[f"{c}3"] = f"=DATE(Setup!$C$4,{i+1},1)"; annual[f"{c}4"] = f"=DATE(Setup!$C$4,{i+2},1)"
    for rr in (3, 4): annual[f"{c}{rr}"].font = font(size=1, color="FFFFFF"); annual[f"{c}{rr}"].number_format = "yyyy-mm-dd"
annual.row_dimensions[4].hidden = True
summ = [("Income", '"Income"'), ("Spent", None), ("Saved", '"Savings"')]
for i, (lab, t) in enumerate(summ):
    r = 6 + i; cell(annual, f"B{r}", lab, bold=True); cell(annual, f"C{r}", "", align="center")
    for m in range(12):
        c = L(4 + m); rng = f'{TD},">="&{c}$3,{TD},"<"&{c}$4'
        if t: f = f'=SUMPRODUCT(SUMIFS({TA},{TC},{CAT},{rng})*({TYP}={t}))'
        else: f = f'=SUMPRODUCT(SUMIFS({TA},{TC},{CAT},{rng})*(({TYP}="Fixed")+({TYP}="Variable")+({TYP}="Debt")))'
        cell(annual, f"{c}{r}", f, MONEY, bold=True)
    cell(annual, f"P{r}", f"=SUM(D{r}:O{r})", MONEY, bold=True); cell(annual, f"Q{r}", f"=P{r}/12", MONEY)
r = 9; cell(annual, f"B{r}", "Net (Income - Spent - Saved)", bold=True, color=BRAND_D); cell(annual, f"C{r}", "")
for m in range(14):
    c = L(4 + m); cell(annual, f"{c}{r}", f"={c}6-{c}7-{c}8", MONEY, bold=True, color=BRAND_D)
for c in range(2, 18): annual.cell(9, c).fill = fill(BRAND_L)
annual.conditional_formatting.add("D9:Q9", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, bold=True, color=WARN)))
header(annual, 11, 2, ["Category", "Type"] + [m[:3] for m in MONTHS] + ["Total", "Avg / Month"])
for i, sr in enumerate(range(C0, C1 + 1)):
    r = 12 + i
    cell(annual, f"B{r}", f'=IF(Setup!B{sr}="","",Setup!B{sr})'); cell(annual, f"C{r}", f'=IF(B{r}="","",Setup!C{sr})', align="center", color=MUTED)
    for m in range(12):
        c = L(4 + m); cell(annual, f"{c}{r}", f'=IF($B{r}="","",SUMIFS({TA},{TC},$B{r},{TD},">="&{c}$3,{TD},"<"&{c}$4))', MONEY)
    cell(annual, f"P{r}", f'=IF(B{r}="","",SUM(D{r}:O{r}))', MONEY, bold=True); cell(annual, f"Q{r}", f'=IF(B{r}="","",P{r}/12)', MONEY)
# move date helper rows below table
ac = BarChart(); ac.title = "Income vs Spending by Month"; ac.style = 10
ac.add_data(Reference(annual, min_col=3, max_col=15, min_row=6, max_row=8), from_rows=True, titles_from_data=False)
ac.set_categories(Reference(annual, min_col=4, max_col=15, min_row=5))
from openpyxl.chart.series import SeriesLabel
for s, n in zip(ac.series, ["Income", "Spent", "Saved"]): s.tx = SeriesLabel(v=n)
ac.height = 7.5; ac.width = 22; ac.y_axis.numFmt = '$#,##0'; ac.y_axis.majorGridlines = None
annual.add_chart(ac, "B55")
annual.freeze_panes = "D6"

# ---------------- Debt Payoff ----------------
base(debt, {"B": 22, "C": 14, "D": 11, "E": 14, "F": 10, "G": 12, "H": 14, "I": 14})
title(debt, "Debt Payoff Planner", "Snowball (smallest balance first) or Avalanche (highest interest first) - see your debt-free date.")
cell(debt, "B4", "Method", bold=True); cell(debt, "C4", "Snowball", inp=True, bold=True, align="center")
dv = DataValidation(type="list", formula1='"Snowball,Avalanche"'); debt.add_data_validation(dv); dv.add("C4")
cell(debt, "B5", "Monthly debt budget", bold=True); cell(debt, "C5", f'=SUMIFS({BUD},{TYP},"Debt")', MONEY, inp=True)
debt["B8"] = "Monthly debt budget comes from your Setup tab (Debt Payments) - or type your own amount."; debt["B8"].font = font(size=9, color=MUTED, italic=True)
cell(debt, "B6", "Start month", bold=True); cell(debt, "C6", "=DATE(Setup!C4,1,1)", "mmm yyyy", inp=True, align="center")
debt["B7"] = '=IF(C5<SUM(E11:E18),"⚠ Your debt budget is less than your total minimum payments ("&TEXT(SUM(E11:E18),"$#,##0")&")","")'
debt["B7"].font = font(bold=True, color=WARN)
header(debt, 10, 2, ["Debt", "Balance", "APR", "Min Payment", "Pay Order", "Months", "Debt-Free", "Interest Paid"])
DEBTS = [("Visa", 3200, 0.229, 95), ("Store Card", 850, 0.2699, 35), ("Student Loan", 12400, 0.055, 140), ("Medical Bill", 600, 0, 50)]
N = 8; R0 = 11
PA, BA = 4, 4 + N
TOTPAY, TOTBAL = 4 + 2 * N, 5 + 2 * N
OW, MO = 6 + 2 * N, 6 + 3 * N
KC, MC, NC, OC, PC, QC = [L(6 + 4 * N + i) for i in range(6)]
for i in range(N):
    r = R0 + i; v = DEBTS[i] if i < len(DEBTS) else (None, None, None, None)
    cell(debt, f"B{r}", v[0], inp=True); cell(debt, f"C{r}", v[1], MONEY2, inp=True)
    cell(debt, f"D{r}", v[2], "0.00%", inp=True, align="center"); cell(debt, f"E{r}", v[3], MONEY2, inp=True)
    # hidden sort key in K
    debt[f"{KC}{r}"] = f'=IF(N(C{r})>0,IF($C$4="Avalanche",-N(D{r}),N(C{r}))+ROW()/100000,1E+15+ROW())'
    cell(debt, f"F{r}", f'=IF(N(C{r})>0,COUNTIF(${KC}${R0}:${KC}${R0+N-1},"<"&{KC}{r})+1,"")', align="center", bold=True)
# sorted helper M..P (pos, name, bal, apr, min) rows 11-18
for k in range(N):
    r = R0 + k
    debt[f"{MC}{r}"] = k + 1
    debt[f"{NC}{r}"] = f'=IFERROR(INDEX($B${R0}:$B${R0+N-1},MATCH({MC}{r},$F${R0}:$F${R0+N-1},0)),"")'
    debt[f"{OC}{r}"] = f'=IFERROR(INDEX($C${R0}:$C${R0+N-1},MATCH({MC}{r},$F${R0}:$F${R0+N-1},0)),0)'
    debt[f"{PC}{r}"] = f'=IFERROR(INDEX($D${R0}:$D${R0+N-1},MATCH({MC}{r},$F${R0}:$F${R0+N-1},0)),0)'
    debt[f"{QC}{r}"] = f'=IFERROR(INDEX($E${R0}:$E${R0+N-1},MATCH({MC}{r},$F${R0}:$F${R0+N-1},0)),0)'
for c in (KC, MC, NC, OC, PC, QC): debt.column_dimensions[c].hidden = True
# schedule
S_HDR, S0, MONTHS_N = 30, 32, 120
Sstart = S0 + 1; Send = S0 + MONTHS_N
debt[f"B{S_HDR-2}"] = "Payment Schedule"; debt[f"B{S_HDR-2}"].font = font(size=14, bold=True, color=BRAND_D)
debt[f"B{S_HDR-1}"] = "Month-by-month payments in pay order. Hidden columns to the right hold the behind-the-scenes math."; debt[f"B{S_HDR-1}"].font = font(size=9, color=MUTED, italic=True)
hdr = ["#", "Month"] + [f'=IF({NC}{R0+k}="","Pay "&{k+1},"Pay: "&{NC}{R0+k})' for k in range(N)] + [f'=IF({NC}{R0+k}="","Balance "&{k+1},"Bal: "&{NC}{R0+k})' for k in range(N)] + ["Total Paid", "Total Debt"] + [f"Owed {k+1}" for k in range(N)] + [f"Min {k+1}" for k in range(N)]
header(debt, S_HDR, 2, hdr)
for k in range(N):
    for blk in (OW, MO): debt.column_dimensions[L(blk + k)].outlineLevel = 1; debt.column_dimensions[L(blk + k)].hidden = True
    for blk in (PA, BA): debt.column_dimensions[L(blk + k)].width = max(debt.column_dimensions[L(blk + k)].width or 0, 14)
debt.column_dimensions[L(TOTPAY)].width = 13; debt.column_dimensions[L(TOTBAL)].width = 13
# month 0 row
cell(debt, f"B{S0}", "Start", align="center"); cell(debt, f"C{S0}", "", align="center")
for k in range(N):
    cell(debt, f"{L(BA+k)}{S0}", f"={OC}{R0+k}", MONEY)
cell(debt, f"{L(TOTBAL)}{S0}", f"=SUM({L(BA)}{S0}:{L(BA+N-1)}{S0})", MONEY, bold=True)
for r in range(Sstart, Send + 1):
    cell(debt, f"B{r}", f"=N(B{r-1})+1", align="center"); cell(debt, f"C{r}", "=C6" if r == Sstart else f"=EDATE(C{r-1},1)", "mmm yyyy", align="center")
    for k in range(N):
        cell(debt, f"{L(OW+k)}{r}", f"=ROUND({L(BA+k)}{r-1}*(1+${PC}${R0+k}/12),2)", MONEY2)
        cell(debt, f"{L(MO+k)}{r}", f"=MIN({L(OW+k)}{r},${QC}${R0+k})", MONEY2)
        before = f"SUM({L(PA)}{r}:{L(PA+k-1)}{r})" if k > 0 else "0"
        after = f"SUM({L(MO+k+1)}{r}:{L(MO+N-1)}{r})" if k < N - 1 else "0"
        cell(debt, f"{L(PA+k)}{r}", f"=MAX(0,MIN({L(OW+k)}{r},$C$5-{before}-{after}))", MONEY)
        cell(debt, f"{L(BA+k)}{r}", f"=ROUND({L(OW+k)}{r}-{L(PA+k)}{r},2)", MONEY)
    cell(debt, f"{L(TOTPAY)}{r}", f"=SUM({L(PA)}{r}:{L(PA+N-1)}{r})", MONEY, bold=True)
    cell(debt, f"{L(TOTBAL)}{r}", f"=SUM({L(BA)}{r}:{L(BA+N-1)}{r})", MONEY, bold=True)
debt.conditional_formatting.add(f"{L(PA)}{Sstart}:{L(BA+N-1)}{Send}", CellIsRule(operator="equal", formula=["0"], font=Font(name=F, color="D1D5DB")))
# per-debt results (original order) via its pay order
for i in range(N):
    r = R0 + i; k = f"F{r}"
    bal_col = lambda kk: f"INDEX(${L(BA)}${Sstart}:${L(BA+N-1)}${Send},0,{kk})"
    cell(debt, f"G{r}", f'=IF({k}="","",IF(COUNTIF({bal_col(k)},">0.004")>={MONTHS_N},"10+ yrs",COUNTIF({bal_col(k)},">0.004")+1))', align="center")
    cell(debt, f"H{r}", f'=IF(OR({k}="",G{r}="10+ yrs"),"",EDATE($C$6,G{r}-1))', "mmm yyyy", align="center", bold=True, color=GOOD)
    cell(debt, f"I{r}", f'=IF({k}="","",SUM(INDEX(${L(PA)}${Sstart}:${L(PA+N-1)}${Send},0,{k}))+INDEX(${L(BA)}${Send}:${L(BA+N-1)}${Send},1,{k})-C{r})', MONEY2)
# headline
cell(debt, "E4", "DEBT-FREE DATE", bold=True, color=MUTED, size=8, align="center"); debt.merge_cells("E4:F4")
cell(debt, "E5", f'=IF(COUNT(C{R0}:C{R0+N-1})=0,"",IF(COUNTIF(G{R0}:G{R0+N-1},"10+ yrs")>0,"10+ years",EDATE(C6,MAX(G{R0}:G{R0+N-1})-1)))', "mmm yyyy", bold=True, size=16, color=BRAND_D, align="center")
debt.merge_cells("E5:F6")
cell(debt, "G4", "TOTAL INTEREST", bold=True, color=MUTED, size=8, align="center"); debt.merge_cells("G4:H4")
cell(debt, "G5", f"=SUM(I{R0}:I{R0+N-1})", MONEY, bold=True, size=16, color=BRAND_D, align="center"); debt.merge_cells("G5:H6")
for ref in ("E4", "F4", "G4", "H4", "E5", "G5"): debt[ref].fill = fill(BRAND_L)
lc = LineChart(); lc.title = "Total Debt Over Time"; lc.style = 12
lc.add_data(Reference(debt, min_col=TOTBAL, min_row=Sstart, max_row=S0 + 60), titles_from_data=False)
lc.set_categories(Reference(debt, min_col=3, min_row=Sstart, max_row=S0 + 60)); lc.height = 7.5; lc.width = 16
lc.y_axis.numFmt = '$#,##0'; lc.x_axis.number_format = "mmm yy"; lc.legend = None
debt.add_chart(lc, "K4")
debt.freeze_panes = f"D{S_HDR+1}" if False else None

# ---------------- Sinking Funds ----------------
base(sink, {"B": 22, "C": 13, "D": 14, "E": 14, "F": 14, "G": 13, "H": 13, "I": 10, "J": 14, "K": 10, "L": 24})
title(sink, "Sinking Funds", "Save a little each month for big expenses you know are coming.")
sink["B3"] = "Contributions add up automatically from Transactions - just log transfers using the fund's name as the category."
sink["B3"].font = font(size=9, color=MUTED, italic=True)
header(sink, 5, 2, ["Fund", "Goal", "Target Date", "Starting Balance", "Contributions", "Saved", "Still Needed", "Months Left", "Save / Month", "Progress", ""])
sink.merge_cells("K5:L5")
FUNDS = [("Emergency Fund", 10000, dt.date(YEAR, 12, 31), 2500), ("Vacation", 3000, dt.date(YEAR, 7, 1), 400),
         ("Christmas Gifts", 900, dt.date(YEAR, 12, 1), 0), ("Car Repairs", 1200, dt.date(YEAR, 12, 31), 300)]
for i in range(12):
    r = 6 + i; v = FUNDS[i] if i < len(FUNDS) else (None, None, None, None)
    cell(sink, f"B{r}", v[0], inp=True); cell(sink, f"C{r}", v[1], MONEY, inp=True)
    cell(sink, f"D{r}", v[2], "mmm d, yyyy", inp=True, align="center"); cell(sink, f"E{r}", v[3], MONEY, inp=True)
    cell(sink, f"F{r}", f'=IF(B{r}="","",SUMIFS({TA},{TC},B{r}))', MONEY)
    cell(sink, f"G{r}", f'=IF(B{r}="","",N(E{r})+F{r})', MONEY, bold=True)
    cell(sink, f"H{r}", f'=IF(B{r}="","",MAX(0,N(C{r})-G{r}))', MONEY)
    cell(sink, f"I{r}", f'=IF(OR(B{r}="",D{r}=""),"",MAX(1,(YEAR(D{r})-YEAR(TODAY()))*12+MONTH(D{r})-MONTH(TODAY())))', align="center")
    cell(sink, f"J{r}", f'=IF(OR(B{r}="",I{r}=""),"",H{r}/I{r})', MONEY, bold=True, color=BRAND_D)
    cell(sink, f"K{r}", f'=IF(OR(B{r}="",N(C{r})=0),"",MIN(1,G{r}/C{r}))', "0%", align="center")
    cell(sink, f"L{r}", f'=IF(K{r}="","",REPT("█",ROUND(K{r}*20,0))&REPT("░",20-ROUND(K{r}*20,0)))', color=BRAND)
cell(sink, "B19", "Total", bold=True)
for c in "CEFGHJ": cell(sink, f"{c}19", f"=SUM({c}6:{c}17)", MONEY, bold=True)
for c in range(2, 13): sink.cell(19, c).fill = fill(BRAND_L)
sink.conditional_formatting.add("K6:K17", CellIsRule(operator="greaterThanOrEqual", formula=["1"], font=Font(name=F, bold=True, color=GOOD)))
sink.freeze_panes = "B6"

# ---------------- Start Here ----------------
base(start, {"B": 4, "C": 90})
start["B1"] = "All-in-One Budget Planner"; start["B1"].font = font(size=24, bold=True, color=BRAND_D); start.row_dimensions[1].height = 40
start["B2"] = "Budget, track spending, pay off debt and save for big goals - all in one Google Sheet."; start["B2"].font = font(size=11, color=MUTED)
lines = [("h", "Get started in 5 minutes"),
 ("1", "Setup - enter your budget year, your income sources and your monthly budget for each category."),
 ("2", "Transactions - log each paycheck, bill and purchase. Choose the category from the dropdown."),
 ("3", "Dashboard - pick a month to see budget vs actual, what's left, and your savings rate."),
 ("4", "Annual - see every month of the year side by side."),
 ("5", "Debt Payoff - list your debts, choose Snowball or Avalanche, and see your debt-free date."),
 ("6", "Sinking Funds - set goals for big expenses; progress updates from your transactions."),
 ("", ""),
 ("h", "How the colors work"),
 ("in", "Yellow cells are yours to type in. Everything else calculates automatically."),
 ("", ""),
 ("h", "Tips"),
 ("•", "The sample data shows how it works - delete the sample transactions (and edit the categories) when you're ready."),
 ("•", "Saving to a sinking fund? Add the fund name as a 'Savings' category in Setup, then log transfers to it."),
 ("•", "Debt payments: log them under your 'Debt' category so they count toward your spending."),
 ("•", "Starting a new year? Make a fresh copy and change the Budget Year on the Setup tab."),
 ("", ""),
 ("h", "Questions?"),
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
wb.save(OUT); print("saved", OUT)
