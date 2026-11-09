# Purchase Order Generator & Tracker (redo of listing 734935569)

Old listing: "Purchase Order Form Template" - 165 sales lifetime ($1,648), declining (1 sale in 2026). Keep the same listing ID when relaunching.

Market (Nov 2026): "purchase order template" 3,868 listings, median $4.99 (printables race to bottom);
"purchase order tracker" 1,682 listings, median $12, p90 $34 -> reposition as tracker app. Target price $14.97-$19.97.

Architecture: Sheet = raw database (Company, Vendors, POs, PO Lines). Canvas = entire UI (dashboard, PO list, PO editor, vendors, print view).
Prompts: see gemini-prompts.md (Prompt 1 builds tables in the Gemini side panel; Prompt 2 builds the canvas over all 4 tabs).
