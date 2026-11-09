# Purchase Order app - Gemini prompts

## Prompt 1 - data tables (Gemini side panel, blank sheet)
```
Set up this spreadsheet as a raw database for a purchase order app. Create exactly 4 tabs with plain data tables only - no formulas, no titles, no merged cells, no charts, no summary rows, no extra formatting. Each tab: header row in row 1 starting in column A, data from row 2, freeze row 1.

1. "Company" - one data row: Company Name | Address | City State ZIP | Phone | Email | Website | Tax Rate | PO Prefix
   Sample: Northwind Supply Co. | 1200 Market Street | Austin, TX 78701 | (512) 555-0142 | orders@northwindsupply.com | northwindsupply.com | 0.0825 | PO-

2. "Vendors": Vendor | Contact Name | Email | Phone | Address | Payment Terms | Notes
   8 realistic sample vendors (office supplies, packaging, raw materials, printing, electronics, cleaning supplies, shipping supplies, furniture). Payment Terms is one of: Due on Receipt, Net 15, Net 30, Net 60.

3. "POs": PO Number | Order Date | Vendor | Status | Expected Delivery | Received Date | Payment Status | Shipping | Notes
   25 sample purchase orders spread over the last 4 months up to today. PO Number format PO-1001, PO-1002... in date order. Vendor must exactly match a name in Vendors. Status is one of: Draft, Sent, Partially Received, Received, Cancelled. Payment Status is one of: Unpaid, Paid. Received Date only filled when Status is Received. Shipping is a number (0-150). Make 3 of the Sent orders have an Expected Delivery date in the past (overdue). Dates as YYYY-MM-DD.

4. "PO Lines": PO Number | Item | Description | Quantity | Unit Price | Received Qty
   2-5 line items for every PO (about 75 rows), realistic for that vendor. PO Number must exactly match a PO in the POs tab. Quantity and Unit Price are numbers. Received Qty equals Quantity for Received orders, is partial for Partially Received orders, and is 0 otherwise.

Add dropdown validation for POs Status, POs Payment Status, POs Vendor (from the Vendors tab) and Vendors Payment Terms.
```

## Prompt 2 - canvas (Insert > Create a canvas, select all 4 tabs)
```
Build a full purchase order app called "Purchase Orders" on top of these 4 tabs. The sheet is only the database - this canvas is the entire user interface, including data entry.

DATA MODEL (every tab: headers in row 1, data from row 2, ignore blank rows; find columns by header name, never by position):
- Company: one row - Company Name, Address, City State ZIP, Phone, Email, Website, Tax Rate (decimal, 0.0825 = 8.25%), PO Prefix.
- Vendors: Vendor (unique name), Contact Name, Email, Phone, Address, Payment Terms, Notes.
- POs: PO Number (unique), Order Date, Vendor, Status (Draft / Sent / Partially Received / Received / Cancelled), Expected Delivery, Received Date, Payment Status (Unpaid / Paid), Shipping, Notes.
- PO Lines: PO Number, Item, Description, Quantity, Unit Price, Received Qty. Each line belongs to the PO with the same PO Number.

CALCULATIONS (always computed in the canvas, never stored):
Line total = Quantity x Unit Price. Subtotal = sum of the PO's line totals. Tax = Subtotal x Company Tax Rate. PO Total = Subtotal + Tax + Shipping. Overdue = Status is Sent or Partially Received and Expected Delivery is before today. Open = Status is Draft, Sent or Partially Received. Cancelled POs are excluded from all spend totals.

SCREENS (tabs across the top):
1. Dashboard - KPI cards: Open POs (count and value), Spend This Month, Unpaid Balance (Received or Partially Received POs with Payment Status Unpaid), Overdue Deliveries. Charts: monthly spend for the last 12 months, spend by vendor (top 8), POs by status. A "Needs attention" list: overdue deliveries and unpaid received POs, each clickable to open the PO.
2. Purchase Orders - searchable table (PO number, date, vendor, status, expected delivery, payment, total) with filters for status, vendor, payment status and date range, sortable columns, colored status badges, red "Overdue" badge. Click a row to open the PO.
3. PO Editor (opens from "+ New PO" or any PO) - header fields (vendor dropdown that shows the vendor's contact and payment terms, order date default today, expected delivery, status, payment status, shipping, notes) and an editable line-items grid (item, description, quantity, unit price, line total, received qty) with "+ Add line" and delete-line buttons, and live subtotal / tax / shipping / total. New POs get the next PO Number automatically (Company PO Prefix + highest existing number + 1). Buttons: Save, Mark as Sent, Mark as Received (sets Status to Received, Received Date to today and every line's Received Qty to its Quantity), Mark as Paid, Print / PDF, Delete (with confirm).
4. Vendors - card or table list with contact info, payment terms, number of POs and total spend per vendor; add / edit / delete vendors (block deleting a vendor that has POs). Click a vendor to see its PO history.
5. Print view - a clean, professional printable purchase order on a white page: company name and contact details at the top left, "PURCHASE ORDER" with PO number, order date and expected delivery at the top right, vendor block, ship-to block (the company address), line-items table, subtotal / tax / shipping / total, notes and a signature line. A "Print / Save as PDF" button that calls window.print(), with print CSS that hides everything except the purchase order.

SAVING RULES:
- Creating a PO: insert one row in POs and one row per line in PO Lines.
- Editing a PO: update only the cells that changed (leave every other cell undefined); update, insert or delete PO Lines rows to match the grid.
- Deleting a PO also deletes all of its PO Lines rows.
- Renaming a vendor also updates the Vendor on every matching PO.
- Write dates as YYYY-MM-DD and numbers as plain numbers. Never write formulas. Never change the header rows.

EVERGREEN RULES (this is sold as a template and used for years, often after the sample data is deleted):
- Never hardcode dates, months, years, vendors, items or statuses lists beyond the ones defined above; "today" is always new Date(). Default the dashboard to the current month.
- Dates may arrive as "YYYY-MM-DD" text, as date serial numbers, or as Date values - handle all three. Numbers may arrive as text - parse safely.
- Every screen needs a friendly empty state (e.g. "No purchase orders yet - create your first one"). Never show NaN, undefined or #ERROR.
- Layout is full-width and fluid: no max-width containers (no max-w-7xl / mx-auto); use w-full with px-6, and stack cleanly on small screens.

STYLE: Clean, modern business software. White rounded cards on a light slate background, accent color #0F766E (teal) with #134E4A for headings, status colors: Draft gray, Sent blue, Partially Received amber, Received green, Cancelled red-gray; Paid green, Unpaid amber. Money as $ with 2 decimals. Inter-style font, generous spacing, large click targets.
```

## If window.print() is blocked
```
Print is blocked - instead make the Print view a full-screen, print-friendly page with instructions to press Ctrl/Cmd+P.
```
