"""Build the simple 4-tab budget database (Categories, Transactions, Debts, Goals) for a Sheets canvas app.
Plain data tables: headers in row 1, no formulas, dropdowns for Group and Category."""
import datetime as dt, random, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation

OUT = sys.argv[1] if len(sys.argv) > 1 else "Budget-Database.xlsx"
F = "Arial"; HDR = PatternFill("solid", fgColor="2F7D6D")
CATS = [("Paycheck","Income",4800),("Side Hustle","Income",600),
 ("Rent / Mortgage","Fixed",1650),("Utilities","Fixed",220),("Phone & Internet","Fixed",140),("Insurance","Fixed",180),
 ("Car Payment","Fixed",385),("Subscriptions","Fixed",45),
 ("Groceries","Variable",600),("Dining Out","Variable",200),("Gas","Variable",180),("Shopping","Variable",150),
 ("Entertainment","Variable",100),("Personal Care","Variable",60),("Gifts","Variable",50),("Miscellaneous","Variable",100),
 ("Emergency Fund","Savings",300),("Vacation","Savings",150),("Christmas Gifts","Savings",75),
 ("Visa","Debt",250),("Store Card","Debt",100),("Student Loan","Debt",200),("Medical Bill","Debt",50)]
DEBTS = [("Visa",3200,0.229,95),("Store Card",850,0.2699,35),("Student Loan",12400,0.055,140),("Medical Bill",600,0,50)]
GOALS = [("Emergency Fund",10000,dt.date(2027,12,31),2500),("Vacation",3000,dt.date(2027,7,1),400),("Christmas Gifts",900,dt.date(2026,12,1),450)]

random.seed(3); T = []
def add(d, desc, cat, amt, note=None): T.append((d, desc, cat, round(amt, 2), note))
for y, m, last in ((2026, 8, 31), (2026, 9, 30), (2026, 10, 31), (2026, 11, 6)):
    D = lambda day: dt.date(y, m, day)
    if last < 6: pass
    full = last >= 28
    add(D(1), "Rent", "Rent / Mortgage", 1650); add(D(1), "Netflix + Spotify", "Subscriptions", 45)
    add(D(2), "Kroger", "Groceries", random.uniform(110, 160))
    if full:
        add(D(5), "Electric bill", "Utilities", random.uniform(95, 140)); add(D(8), "Car payment", "Car Payment", 385)
        add(D(7), "Transfer to savings", "Emergency Fund", 300)
        for day in (9, 16, 23): add(D(day), random.choice(["Kroger", "Trader Joe's", "Costco"]), "Groceries", random.uniform(90, 190))
        for day in (6, 13, 20, 27): add(D(day), random.choice(["Chipotle", "Pizza night", "Coffee shop", "Thai takeout"]), "Dining Out", random.uniform(14, 52))
        for day in (4, 14, 25): add(D(day), "Shell", "Gas", random.uniform(42, 58))
        add(D(10), random.choice(["Target", "Amazon"]), "Shopping", random.uniform(35, 90)); add(D(19), "Amazon", "Shopping", random.uniform(20, 60))
        add(D(12), random.choice(["Movie night", "Concert tickets", "Bowling"]), "Entertainment", random.uniform(25, 80))
        add(D(15), "Verizon", "Phone & Internet", 140); add(D(16), "Water + gas bill", "Utilities", random.uniform(60, 90))
        add(D(18), "Haircut", "Personal Care", 35); add(D(20), "Etsy payout", "Side Hustle", random.uniform(480, 720))
        add(D(22), "Car insurance", "Insurance", 180); add(D(23), "Vacation fund", "Vacation", 150); add(D(24), "Christmas fund", "Christmas Gifts", 75)
        add(D(26), "Visa payment", "Visa", 250); add(D(26), "Store card payment", "Store Card", 100)
        add(D(26), "Student loan payment", "Student Loan", 200); add(D(26), "Medical bill payment", "Medical Bill", 50)
        if random.random() < .6: add(D(21), "Birthday gift", "Gifts", random.uniform(25, 60))
        add(D(28), random.choice(["Hardware store", "Pharmacy", "Pet supplies"]), "Miscellaneous", random.uniform(20, 70))
    for day in (1, 15) if m != 11 else (1,):
        pass
    for day in [d for d in (7, 21) if d <= last] if (y, m) != (2026, 11) else []: add(D(day), "Paycheck", "Paycheck", 2400)
T += [(dt.date(2026, 11, 6), "Paycheck", "Paycheck", 2400, None), (dt.date(2026, 11, 4), "Shell", "Gas", 47.85, None),
      (dt.date(2026, 11, 5), "Coffee shop", "Dining Out", 6.75, None)]
T.sort(key=lambda t: t[0])

wb = Workbook(); wb.remove(wb.active)
def table(name, headers, rows, widths, fmts):
    ws = wb.create_sheet(name)
    for i, h in enumerate(headers, 1):
        c = ws.cell(1, i, h); c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HDR; c.alignment = Alignment(horizontal="center")
    for r, row in enumerate(rows, 2):
        for i, v in enumerate(row, 1):
            c = ws.cell(r, i, v); c.font = Font(name=F)
            if fmts[i - 1]: c.number_format = fmts[i - 1]
    for i, w in enumerate(widths): ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = "A2"; return ws
cat = table("Categories", ["Category", "Group", "Monthly Budget"], CATS, [24, 12, 16], [None, None, "$#,##0.00"])
tx = table("Transactions", ["Date", "Description", "Category", "Amount", "Notes"], T, [13, 28, 22, 13, 30], ["yyyy-mm-dd", None, None, "$#,##0.00", None])
db = table("Debts", ["Debt", "Starting Balance", "APR", "Minimum Payment"], DEBTS, [20, 17, 10, 18], [None, "$#,##0.00", "0.00%", "$#,##0.00"])
gl = table("Goals", ["Goal", "Target Amount", "Target Date", "Starting Amount"], GOALS, [20, 15, 14, 16], [None, "$#,##0.00", "yyyy-mm-dd", "$#,##0.00"])
v = DataValidation(type="list", formula1='"Income,Fixed,Variable,Savings,Debt"', allow_blank=True); cat.add_data_validation(v); v.add("B2:B500")
v = DataValidation(type="list", formula1="=Categories!$A$2:$A$500", allow_blank=True); tx.add_data_validation(v); v.add("C2:C10000")
wb.save(OUT)
# consistency checks
names = {c[0]: c[1] for c in CATS}
assert all(t[2] in names for t in T), "unknown category"
assert all(names.get(d[0]) == "Debt" for d in DEBTS) and all(names.get(g[0]) == "Savings" for g in GOALS)
print("saved", OUT, "| categories", len(CATS), "transactions", len(T), "debts", len(DEBTS), "goals", len(GOALS), "| range", T[0][0], "->", T[-1][0])
