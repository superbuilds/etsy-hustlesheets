"""Build the Client CRM + Sales Pipeline Dashboard workbook (xlsx -> Google Sheets).
Usage: python build.py out.xlsx [--today YYYY-MM-DD]  (--today pins 'Today' for screenshots; default is =TODAY())"""
import datetime as dt, sys, random
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.utils import get_column_letter as L

OUT = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "Client-CRM-Sales-Pipeline.xlsx"
PIN = sys.argv[sys.argv.index("--today") + 1] if "--today" in sys.argv else None
YEAR = 2027
F = "Arial"; INK, MUTED = "1F2A37", "6B7280"
BRAND, BRAND_D, BRAND_L = "5B4B8A", "3B2F63", "ECE8F6"
INPUT = "FFF7D6"; WARN, GOOD, AMBER = "C2410C", "15803D", "B45309"
MONEY = '$#,##0;-$#,##0;"-"'
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
    ws.row_dimensions[row].height = 24
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
def dd(ws, f1, rng):
    v = DataValidation(type="list", formula1=f1, allow_blank=True); ws.add_data_validation(v); v.add(rng)

wb = Workbook()
start = wb.active; start.title = "Start Here"
setup = wb.create_sheet("Setup"); dash = wb.create_sheet("Dashboard"); fu = wb.create_sheet("Follow-Ups")
deals = wb.create_sheet("Deals"); clients = wb.create_sheet("Clients"); act = wb.create_sheet("Activities")
for ws in wb.worksheets: ws.sheet_properties.tabColor = BRAND
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# ---------------- Setup ----------------
base(setup, {"B": 24, "C": 14, "D": 13, "E": 3, "F": 22, "G": 3, "H": 22, "I": 3, "J": 26, "K": 14})
title(setup, "Setup", "Step 1 - Your business, pipeline stages and dropdown lists. Yellow cells are yours to edit.")
cell(setup, "B4", "Business Name", bold=True); cell(setup, "C4", "Bright Pixel Studio", inp=True); setup.merge_cells("C4:D4")
cell(setup, "B5", "Dashboard Year", bold=True); cell(setup, "C5", YEAR, "0", inp=True, align="center")
cell(setup, "B6", "Today's Date", bold=True)
cell(setup, "C6", dt.date.fromisoformat(PIN) if PIN else "=TODAY()", "mmm d, yyyy", inp=True, align="center"); setup.merge_cells("C6:D6")
note(setup, "F6", "Leave as =TODAY(). Follow-up reminders and 'days open' count from this date.")
header(setup, 9, 2, ["Pipeline Stage", "Probability", "Stage Type"])
STAGES = [("Lead", .10, "Open"), ("Contacted", .20, "Open"), ("Qualified", .40, "Open"), ("Proposal Sent", .60, "Open"),
          ("Negotiation", .80, "Open"), ("Won", 1, "Won"), ("Lost", 0, "Lost")]
G0, G1 = 10, 19
for i, r in enumerate(range(G0, G1 + 1)):
    v = STAGES[i] if i < len(STAGES) else (None, None, None)
    cell(setup, f"B{r}", v[0], inp=True); cell(setup, f"C{r}", v[1], "0%", inp=True, align="center"); cell(setup, f"D{r}", v[2], inp=True, align="center")
dd(setup, '"Open,Won,Lost"', f"D{G0}:D{G1}")
note(setup, "B20", "Stage Type tells the sheet which stages are still open, won or lost.")
lists = [("F", "Lead Source", ["Referral", "Website", "Instagram", "Google Search", "Networking Event", "Cold Outreach", "Repeat Client"]),
         ("H", "Sales Rep / Owner", ["Alex", "Jordan", "Sam"]),
         ("J", "Service / Product", ["Website Design", "Branding Package", "SEO Retainer", "Social Media Management", "Photography Session"])]
for col, lab, vals in lists:
    header(setup, 9, ord(col) - 64, [lab])
    for i, r in enumerate(range(10, 30)):
        cell(setup, f"{col}{r}", vals[i] if i < len(vals) else None, inp=True)
header(setup, 9, 11, ["Default Price"])
PRICES = [3500, 2200, 900, 1200, 650]
for i, r in enumerate(range(10, 30)): cell(setup, f"K{r}", PRICES[i] if i < len(PRICES) else None, MONEY, inp=True)
for i, m in enumerate(MONTHS): setup[f"M{10+i}"] = m
setup["M22"] = "Full Year"; setup.column_dimensions["M"].hidden = True
ACT_TYPES = '"Call,Email,Meeting,Text/DM,Proposal,Note"'
STG, PROB, STYPE = (f"Setup!${c}${G0}:${c}${G1}" for c in "BCD")
SRC, OWN, SVC = "Setup!$F$10:$F$29", "Setup!$H$10:$H$29", "Setup!$J$10:$J$29"
TODAY = "Setup!$C$6"
setup.freeze_panes = "B10"

# ---------------- sample data ----------------
random.seed(11)
d = lambda m, day: dt.date(YEAR, m, day)
PEOPLE = [("Maria Lopez","Lopez Family Dental"),("Derek Chen","Chen & Co. Realty"),("Priya Shah","Bloom Yoga Studio"),("Tom Becker","Becker Plumbing"),
 ("Alicia Grant","Grant Law Group"),("Marcus Hill","Hill Fitness"),("Hannah Reed","Reed Bakery"),("Omar Haddad","Cedar Grill"),
 ("Lena Novak","Novak Interiors"),("Chris Walsh","Walsh Roofing"),("Nina Patel","Sunrise Pediatrics"),("Ben Ortiz","Ortiz Landscaping"),
 ("Grace Kim","Kim Wellness Spa"),("Ryan Murphy","Murphy Auto Care"),("Sofia Rossi","Rossi Bridal"),("Jake Turner","Turner Coffee Roasters"),
 ("Emma Davis","Davis Pet Grooming"),("Luis Romero","Romero Construction"),("Olivia Brooks","Brooks Boutique"),("Sean Kelly","Kelly Insurance"),
 ("Aisha Bello","Bello Hair Lounge"),("Victor Lin","Lin Accounting")]
SOURCES = lists[0][2]; OWNERS = lists[1][2]; SERVICES = lists[2][2]
CL = []
for i, (n, co) in enumerate(PEOPLE):
    src = random.choice(SOURCES[:6]) if i < 19 else "Repeat Client"
    first = n.split()[0].lower(); dom = co.lower().replace("&", "and").replace(".", "").replace(" ", "")[:18]
    CL.append((n, co, f"{first}@{dom}.com", f"(512) 555-{1000 + i * 37:04d}", src, OWNERS[i % 3], d(random.choice([1, 1, 2, 2, 3]), random.randint(1, 20))))
DL = []
plan = ["Won"] * 9 + ["Lost"] * 5 + ["Negotiation"] * 3 + ["Proposal Sent"] * 4 + ["Qualified"] * 4 + ["Contacted"] * 3 + ["Lead"] * 3
random.shuffle(plan)
NOW = dt.date(YEAR, 3, 24)
for i, stage in enumerate(plan):
    c = CL[i % len(CL)]; svc = random.choice(SERVICES); price = PRICES[SERVICES.index(svc)]
    val = round(price * random.choice([0.9, 1, 1, 1.2, 1.5]) / 50) * 50
    created = c[6] + dt.timedelta(days=random.randint(0, 10))
    created = min(created, NOW - dt.timedelta(days=5))
    closed = fu_ = None; nxt = None
    if stage in ("Won", "Lost"):
        closed = min(created + dt.timedelta(days=random.randint(9, 40)), NOW - dt.timedelta(days=1))
    else:
        fu_ = NOW + dt.timedelta(days=random.choice([-6, -3, -1, 0, 1, 2, 3, 5, 6, 9, 14, 21]))
        nxt = {"Lead": "Intro call", "Contacted": "Send portfolio + book call", "Qualified": "Discovery meeting",
               "Proposal Sent": "Follow up on proposal", "Negotiation": "Finalize scope + contract"}[stage]
    exp = (closed or created + dt.timedelta(days=random.randint(25, 50)))
    DL.append((f"{c[1].split()[0]} - {svc}", c[0], svc, val, stage, c[5], created, exp, closed, fu_, nxt))
AC = []
for dl in DL:
    AC.append((dl[6], dl[1], "Call", f"Intro call - interested in {dl[2].lower()}", dl[5]))
    if dl[4] not in ("Lead", "Contacted"):
        AC.append((dl[6] + dt.timedelta(days=4), dl[1], "Meeting", "Discovery meeting - goals, budget, timeline", dl[5]))
    if dl[4] in ("Proposal Sent", "Negotiation", "Won", "Lost"):
        AC.append((dl[6] + dt.timedelta(days=7), dl[1], "Proposal", f"Sent proposal - ${dl[3]:,}", dl[5]))
    if dl[4] == "Won": AC.append((dl[8], dl[1], "Email", "Signed contract + deposit received", dl[5]))
    if dl[4] == "Lost": AC.append((dl[8], dl[1], "Email", random.choice(["Went with a cheaper option", "Postponed - budget", "No response after 3 follow-ups"]), dl[5]))
AC = [a for a in AC if a[0] <= NOW]; AC.sort(key=lambda a: a[0])

# ---------------- Clients ----------------
base(clients, {"B": 20, "C": 24, "D": 28, "E": 16, "F": 17, "G": 11, "H": 13, "I": 8, "J": 13, "K": 13, "L": 13, "M": 12, "N": 28})
title(clients, "Clients", "Step 2 - Your contacts. Deals, revenue, last contact and status fill in automatically.")
header(clients, 5, 2, ["Name", "Company", "Email", "Phone", "Lead Source", "Owner", "First Contact", "Deals", "Lifetime Revenue", "Open Pipeline", "Last Contact", "Status", "Notes"])
K0, K1 = 6, 505
for i, r in enumerate(range(K0, K1 + 1)):
    c = CL[i] if i < len(CL) else (None,) * 7
    for col, v, fmt in zip("BCDEFGH", c, [None] * 6 + ["mmm d, yyyy"]):
        cell(clients, f"{col}{r}", v, fmt, inp=True, align="center" if col in "GH" else None)
    cell(clients, f"I{r}", f'=IF(B{r}="","",COUNTIF(Deals!$C$6:$C$1005,B{r}))', align="center")
    cell(clients, f"J{r}", f'=IF(B{r}="","",SUMIFS(Deals!$E$6:$E$1005,Deals!$C$6:$C$1005,B{r},Deals!$R$6:$R$1005,"Won"))', MONEY, bold=True)
    cell(clients, f"K{r}", f'=IF(B{r}="","",SUMIFS(Deals!$E$6:$E$1005,Deals!$C$6:$C$1005,B{r},Deals!$R$6:$R$1005,"Open"))', MONEY)
    cell(clients, f"L{r}", f'=IF(B{r}="","",IF(COUNTIF(Activities!$C$6:$C$2005,B{r})=0,"",_xlfn.MAXIFS(Activities!$B$6:$B$2005,Activities!$C$6:$C$2005,B{r})))', "mmm d", align="center")
    cell(clients, f"M{r}", f'=IF(B{r}="","",IF(J{r}>0,IF(K{r}>0,"Active","Customer"),IF(K{r}>0,"Prospect",IF(I{r}=0,"New Lead","Lost"))))', align="center", bold=True)
    cell(clients, f"N{r}", None, inp=True)
dd(clients, f"={SRC}", f"F{K0}:F{K1}"); dd(clients, f"={OWN}", f"G{K0}:G{K1}")
for val, col in (("Customer", GOOD), ("Active", GOOD), ("Prospect", BRAND), ("Lost", MUTED)):
    clients.conditional_formatting.add(f"M{K0}:M{K1}", CellIsRule(operator="equal", formula=[f'"{val}"'], font=Font(name=F, bold=True, color=col)))
clients.freeze_panes = "C6"
CLN, CLS = f"Clients!$B${K0}:$B${K1}", f"Clients!$F${K0}:$F${K1}"

# ---------------- Deals ----------------
base(deals, {"B": 30, "C": 18, "D": 22, "E": 12, "F": 15, "G": 11, "H": 12, "I": 12, "J": 12, "K": 13, "L": 28, "M": 9, "N": 12, "O": 16, "P": 9, "Q": 16})
title(deals, "Deals", "Step 3 - Your sales pipeline. Move deals through the stages and set a next follow-up date.")
note(deals, "B3", "Columns M-Q fill in automatically. When a deal is Won or Lost, enter the Closed Date.")
header(deals, 5, 2, ["Deal", "Client", "Service", "Value", "Stage", "Owner", "Created", "Expected Close", "Closed Date", "Next Follow-Up", "Next Step",
                     "Prob.", "Weighted", "Lead Source", "Days Open", "Follow-Up Status"])
D0, D1 = 6, 1005
for i, r in enumerate(range(D0, D1 + 1)):
    v = DL[i] if i < len(DL) else (None,) * 11
    fm = [None, None, None, MONEY, None, None, "mmm d", "mmm d", "mmm d", "mmm d", None]
    for col, val, f in zip("BCDEFGHIJKL", v, fm):
        cell(deals, f"{col}{r}", val, f, inp=True, align="center" if col in "FGHIJK" else None)
    cell(deals, f"M{r}", f'=IF(F{r}="","",IFERROR(INDEX({PROB},MATCH(F{r},{STG},0)),0))', "0%", align="center", color=MUTED)
    cell(deals, f"N{r}", f'=IF(F{r}="","",N(E{r})*M{r})', MONEY, color=MUTED)
    cell(deals, f"O{r}", f'=IF(C{r}="","",IFERROR(INDEX({CLS},MATCH(C{r},{CLN},0)),""))', align="center", color=MUTED)
    cell(deals, f"P{r}", f'=IF(H{r}="","",IF(J{r}<>"",J{r},{TODAY})-H{r})', "0", align="center", color=MUTED)
    deals[f"R{r}"] = f'=IF(F{r}="","",IFERROR(INDEX({STYPE},MATCH(F{r},{STG},0)),"Open"))'
    cell(deals, f"Q{r}", f'=IF(B{r}="","",IF(R{r}<>"Open",R{r},IF(K{r}="","No follow-up set",IF(K{r}<{TODAY},"Overdue",IF(K{r}<={TODAY}+7,"Due this week","On track")))))', align="center", bold=True)
    deals[f"S{r}"] = f'=IF(AND(R{r}="Open",K{r}<>""),IF(K{r}<={TODAY}+7,K{r}+ROW()/1000000,""),"")'
deals.column_dimensions["R"].hidden = True; deals.column_dimensions["S"].hidden = True
dd(deals, f"={CLN}", f"C{D0}:C{D1}"); dd(deals, f"={SVC}", f"D{D0}:D{D1}"); dd(deals, f"={STG}", f"F{D0}:F{D1}"); dd(deals, f"={OWN}", f"G{D0}:G{D1}")
for val, col in (("Overdue", WARN), ("Due this week", AMBER), ("Won", GOOD), ("On track", BRAND), ("Lost", MUTED), ("No follow-up set", MUTED)):
    deals.conditional_formatting.add(f"Q{D0}:Q{D1}", CellIsRule(operator="equal", formula=[f'"{val}"'], font=Font(name=F, bold=True, color=col)))
deals.conditional_formatting.add(f"B{D0}:Q{D1}", FormulaRule(formula=[f'$R{D0}="Won"'], fill=fill("EAF7EE")))
deals.freeze_panes = "C6"
DV, DS, DO, DC, DJ, DH, DT, DN, DSRC, DP, DCL = (f"Deals!${c}${D0}:${c}${D1}" for c in "EFGJJHRNOPC")

# ---------------- Activities ----------------
base(act, {"B": 13, "C": 20, "D": 12, "E": 50, "F": 12})
title(act, "Activities", "Log every call, email and meeting. Each client's Last Contact updates automatically.")
header(act, 5, 2, ["Date", "Client", "Type", "Summary", "Owner"])
for i, r in enumerate(range(6, 2006)):
    a = AC[i] if i < len(AC) else (None,) * 5
    cell(act, f"B{r}", a[0], "mmm d, yyyy", inp=True, align="center"); cell(act, f"C{r}", a[1], inp=True)
    cell(act, f"D{r}", a[2], inp=True, align="center"); cell(act, f"E{r}", a[3], inp=True); cell(act, f"F{r}", a[4], inp=True, align="center")
dd(act, f"={CLN}", "C6:C2005"); dd(act, ACT_TYPES, "D6:D2005"); dd(act, f"={OWN}", "F6:F2005")
act.freeze_panes = "B6"

# ---------------- Follow-Ups ----------------
base(fu, {"B": 14, "C": 30, "D": 18, "E": 15, "F": 12, "G": 11, "H": 30, "I": 15})
title(fu, "Follow-Ups", "Overdue and upcoming follow-ups for the next 7 days - updates automatically from Deals.")
cell(fu, "B4", "OVERDUE", bold=True, size=8, color=MUTED, align="center", bg=BRAND_L)
cell(fu, "B5", f'=COUNTIF(Deals!$Q${D0}:$Q${D1},"Overdue")', "0", bold=True, size=18, color=WARN, align="center", bg=BRAND_L)
cell(fu, "C4", "DUE THIS WEEK", bold=True, size=8, color=MUTED, align="center", bg=BRAND_L)
cell(fu, "C5", f'=COUNTIF(Deals!$Q${D0}:$Q${D1},"Due this week")', "0", bold=True, size=18, color=AMBER, align="center", bg=BRAND_L)
cell(fu, "D4", "NO FOLLOW-UP SET", bold=True, size=8, color=MUTED, align="center", bg=BRAND_L)
cell(fu, "D5", f'=COUNTIF(Deals!$Q${D0}:$Q${D1},"No follow-up set")', "0", bold=True, size=18, color=MUTED, align="center", bg=BRAND_L)
fu.row_dimensions[5].height = 30
header(fu, 7, 2, ["Follow-Up", "Deal", "Client", "Stage", "Value", "Owner", "Next Step", "Status"])
for k in range(1, 41):
    r = 7 + k
    fu[f"K{r}"] = f'=IFERROR(MATCH(SMALL(Deals!$S${D0}:$S${D1},{k}),Deals!$S${D0}:$S${D1},0),"")'
    def g(col): return f'=IF($K{r}="","",INDEX(Deals!${col}${D0}:${col}${D1},$K{r}))'
    cell(fu, f"B{r}", g("K"), "ddd, mmm d", align="center", bold=True)
    cell(fu, f"C{r}", g("B")); cell(fu, f"D{r}", g("C")); cell(fu, f"E{r}", g("F"), align="center")
    cell(fu, f"F{r}", g("E"), MONEY); cell(fu, f"G{r}", g("G"), align="center"); cell(fu, f"H{r}", g("L")); cell(fu, f"I{r}", g("Q"), align="center", bold=True)
fu.column_dimensions["K"].hidden = True
for val, col in (("Overdue", WARN), ("Due this week", AMBER)):
    fu.conditional_formatting.add("I8:I47", CellIsRule(operator="equal", formula=[f'"{val}"'], font=Font(name=F, bold=True, color=col)))
fu.conditional_formatting.add("B8:I47", FormulaRule(formula=['$I8="Overdue"'], fill=fill("FDEDE7")))
fu.freeze_panes = "B8"

# ---------------- Dashboard ----------------
base(dash, {"B": 22, "C": 11, "D": 13, "E": 13, "F": 13, "G": 11, "H": 30})
title(dash, "Sales Dashboard", "Pick a month or Full Year. Won revenue and win rate use each deal's Closed Date.")
dash["B3"] = "=Setup!C4"; dash["B3"].font = font(bold=True, color=BRAND_D, size=12)
cell(dash, "B4", "Period", bold=True); cell(dash, "C4", "Full Year", inp=True, bold=True, align="center"); dash.merge_cells("C4:D4")
dd(dash, "=Setup!$M$10:$M$22", "C4")
cell(dash, "E4", "Year", bold=True, align="right"); cell(dash, "F4", "=Setup!C5", "0", bold=True, align="center")
dash["P4"] = '=IF(C4="Full Year",DATE(F4,1,1),DATE(F4,MATCH(C4,Setup!$M$10:$M$21,0),1))'
dash["P5"] = '=IF(C4="Full Year",DATE(F4+1,1,1),EDATE(P4,1))'
for r in ("P4", "P5"): dash[r].number_format = "yyyy-mm-dd"
dash.column_dimensions["P"].hidden = True
PER = f'{DJ},">="&$P$4,{DJ},"<"&$P$5'
CRE = f'{DH},">="&$P$4,{DH},"<"&$P$5'
K = [("B", "WON REVENUE", f'=SUMIFS({DV},{DT},"Won",{PER})', MONEY), ("D", "OPEN PIPELINE", f'=SUMIFS({DV},{DT},"Open")', MONEY),
     ("E", "WEIGHTED FORECAST", f'=SUMIFS({DN},{DT},"Open")', MONEY), ("F", "WIN RATE", f'=IFERROR(COUNTIFS({DT},"Won",{PER})/(COUNTIFS({DT},"Won",{PER})+COUNTIFS({DT},"Lost",{PER})),0)', "0%"),
     ("G", "AVG DEAL", f'=IFERROR(B8/COUNTIFS({DT},"Won",{PER}),0)', MONEY), ("H", "AVG DAYS TO CLOSE", f'=IFERROR(AVERAGEIFS({DP},{DT},"Won",{PER}),0)', "0")]
for col, lab, f, fmt in K:
    a = dash[f"{col}7"]; a.value = lab; a.font = font(size=8, bold=True, color=MUTED); a.fill = fill(BRAND_L)
    b = dash[f"{col}8"]; b.value = f; b.font = font(size=16, bold=True, color=BRAND_D); b.fill = fill(BRAND_L); b.number_format = fmt
    for c in (a, b): c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
dash.merge_cells("B7:C7"); dash.merge_cells("B8:C8"); dash.row_dimensions[8].height = 34; dash.row_dimensions[7].height = 24
dash["B9"] = f'="New deals this period: "&COUNTIFS({CRE})&"   |   Overdue follow-ups: "&COUNTIF(Deals!$Q${D0}:$Q${D1},"Overdue")'
dash["B9"].font = font(size=9, bold=True, color=BRAND_D)
# Pipeline by stage
header(dash, 11, 2, ["Pipeline by Stage", "Deals", "Value", "Weighted", "% of Value", "", "Funnel"])
dash.merge_cells("F11:G11")
for i, sr in enumerate(range(G0, G1 + 1)):
    r = 12 + i
    cell(dash, f"B{r}", f'=IF(Setup!B{sr}="","",Setup!B{sr})', bold=True)
    cell(dash, f"C{r}", f'=IF(B{r}="","",COUNTIF({DS},B{r}))', align="center")
    cell(dash, f"D{r}", f'=IF(B{r}="","",SUMIFS({DV},{DS},B{r}))', MONEY)
    cell(dash, f"E{r}", f'=IF(B{r}="","",SUMIFS({DN},{DS},B{r}))', MONEY)
    cell(dash, f"F{r}", f'=IF(OR(B{r}="",SUM($D$12:$D$21)=0),"",D{r}/SUM($D$12:$D$21))', "0%", align="center")
    cell(dash, f"G{r}", ""); cell(dash, f"H{r}", f'=IF(OR(B{r}="",MAX($D$12:$D$21)=0),"",{bar(f"D{r}/MAX($D$12:$D$21)")})', color=BRAND)
note(dash, "B22", "Pipeline counts all deals, whatever the period.")
# By lead source
header(dash, 24, 2, ["Lead Source", "New Deals", "Won", "Revenue", "Win Rate", "", "Revenue Share"])
dash.merge_cells("F24:G24")
for i in range(10):
    r = 25 + i; sr = 10 + i
    cell(dash, f"B{r}", f'=IF(Setup!F{sr}="","",Setup!F{sr})', bold=True)
    cell(dash, f"C{r}", f'=IF(B{r}="","",COUNTIFS({DSRC},B{r},{CRE}))', align="center")
    cell(dash, f"D{r}", f'=IF(B{r}="","",COUNTIFS({DSRC},B{r},{DT},"Won",{PER}))', align="center")
    cell(dash, f"E{r}", f'=IF(B{r}="","",SUMIFS({DV},{DSRC},B{r},{DT},"Won",{PER}))', MONEY)
    cell(dash, f"F{r}", f'=IF(B{r}="","",IFERROR(D{r}/(D{r}+COUNTIFS({DSRC},B{r},{DT},"Lost",{PER})),""))', "0%", align="center")
    cell(dash, f"G{r}", ""); cell(dash, f"H{r}", f'=IF(OR(B{r}="",$B$8=0),"",{bar(f"E{r}/$B$8")})', color=BRAND)
# By owner
header(dash, 36, 2, ["Sales Rep", "Open Deals", "Pipeline", "Won Revenue", "Win Rate", "", "Overdue"])
dash.merge_cells("F36:G36")
for i in range(6):
    r = 37 + i; sr = 10 + i
    cell(dash, f"B{r}", f'=IF(Setup!H{sr}="","",Setup!H{sr})', bold=True)
    cell(dash, f"C{r}", f'=IF(B{r}="","",COUNTIFS({DO},B{r},{DT},"Open"))', align="center")
    cell(dash, f"D{r}", f'=IF(B{r}="","",SUMIFS({DV},{DO},B{r},{DT},"Open"))', MONEY)
    cell(dash, f"E{r}", f'=IF(B{r}="","",SUMIFS({DV},{DO},B{r},{DT},"Won",{PER}))', MONEY)
    cell(dash, f"F{r}", f'=IF(B{r}="","",IFERROR(COUNTIFS({DO},B{r},{DT},"Won",{PER})/(COUNTIFS({DO},B{r},{DT},"Won",{PER})+COUNTIFS({DO},B{r},{DT},"Lost",{PER})),""))', "0%", align="center")
    cell(dash, f"G{r}", ""); cell(dash, f"H{r}", f'=IF(B{r}="","",COUNTIFS({DO},B{r},Deals!$Q${D0}:$Q${D1},"Overdue"))', align="center", bold=True, color=WARN)
# monthly helper rows 46-48 (cols C..N)
dash["B46"] = "Month"; dash["B47"] = "Won Revenue"; dash["B48"] = "New Deals"
for i in range(12):
    c = L(3 + i)
    dash[f"{c}45"] = f"=DATE($F$4,{i+1},1)"; dash[f"{c}45"].number_format = "yyyy-mm-dd"
    dash[f"{c}46"] = MONTHS[i][:3]
    dash[f"{c}47"] = f'=SUMIFS({DV},{DT},"Won",{DJ},">="&{c}45,{DJ},"<"&EDATE({c}45,1))'; dash[f"{c}47"].number_format = MONEY
    dash[f"{c}48"] = f'=COUNTIFS({DH},">="&{c}45,{DH},"<"&EDATE({c}45,1))'
for r in range(45, 49):
    for c in range(2, 15): dash.cell(r, c).font = font(size=9, color=MUTED)
dash.row_dimensions[45].hidden = True
note(dash, "B44", "Monthly data for the charts")
ch = BarChart(); ch.title = "Won Revenue by Month"; ch.style = 10
ch.add_data(Reference(dash, min_col=3, max_col=14, min_row=47), from_rows=True, titles_from_data=False)
ch.series[0].tx = SeriesLabel(v="Won Revenue"); ch.set_categories(Reference(dash, min_col=3, max_col=14, min_row=46))
ch.height = 7.5; ch.width = 16; ch.legend = None; ch.y_axis.numFmt = '$#,##0'; ch.y_axis.majorGridlines = None
dash.add_chart(ch, "J7")
pc = BarChart(); pc.type = "bar"; pc.title = "Deal Value by Stage"; pc.style = 10
pc.add_data(Reference(dash, min_col=4, min_row=12, max_row=12 + len(STAGES) - 1)); pc.set_categories(Reference(dash, min_col=2, min_row=12, max_row=12 + len(STAGES) - 1))
pc.height = 7.5; pc.width = 16; pc.legend = None; pc.x_axis.scaling.orientation = "maxMin"; pc.y_axis.numFmt = '$#,##0'; pc.y_axis.majorGridlines = None
dash.add_chart(pc, "J24")

# ---------------- Start Here ----------------
base(start, {"B": 4, "C": 92})
start["B1"] = "Client CRM + Sales Pipeline Dashboard"; start["B1"].font = font(size=24, bold=True, color=BRAND_D); start.row_dimensions[1].height = 40
start["B2"] = "Track every client and deal, never miss a follow-up, and see what's coming in - all in one Google Sheet."; start["B2"].font = font(size=11, color=MUTED)
lines = [("h", "Get started in 10 minutes"),
 ("1", "Setup - add your business name, pipeline stages, lead sources, sales reps and services."),
 ("2", "Clients - add your contacts. Deals, lifetime revenue, last contact and status fill in automatically."),
 ("3", "Deals - add each opportunity, move it through the stages, and set a Next Follow-Up date."),
 ("4", "Activities - log calls, emails and meetings."),
 ("5", "Follow-Ups - your to-do list: overdue and upcoming follow-ups for the next 7 days."),
 ("6", "Dashboard - won revenue, pipeline, forecast, win rate, and results by lead source and sales rep."),
 ("", ""), ("h", "How the colors work"),
 ("in", "Yellow cells are yours to type in. Everything else calculates automatically."),
 ("", ""), ("h", "Tips"),
 ("•", "Sample data for a small creative agency shows how it works - delete the sample rows when you're ready."),
 ("•", "When a deal is Won or Lost, enter its Closed Date so revenue and win rate land in the right month."),
 ("•", "Rename stages or change probabilities on the Setup tab - set each stage's Type to Open, Won or Lost."),
 ("•", "Weighted forecast = deal value x stage probability. It's a realistic view of what's likely to close."),
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
wb.save(OUT); print("saved", OUT, "| clients", len(CL), "deals", len(DL), "activities", len(AC))
