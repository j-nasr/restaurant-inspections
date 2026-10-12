# Tableau Build Guide: NYC Restaurant Inspection Dashboard

This guide walks through building the dashboard in **Tableau Public** (free) from the cleaned files in `data/clean/`. It takes about 2-3 hours the first time.

**Colors used throughout** (to match the README charts): teal `#1F6F8B` (good / main), red `#B04A5A` (bad / critical), grey `#9AA7AF` (neutral), dark text `#17262F`.

**Reminder:** inspection **scores work like golf**. Lower is better. A = 0-13 points, B = 14-27, C = 28+.

---

## Step 1. Install and connect

1. Download **Tableau Public** (desktop app) from public.tableau.com and sign in with a free account.
2. On the start screen choose **Connect → To a File → Text file** and open `data/clean/inspections.csv`.
3. On the Data Source page, drag `violations.csv` onto the canvas next to `inspections`. When Tableau asks how to relate them, set **Inspection Id = Inspection Id**.
4. Drag `violation_codes.csv` onto the canvas next to `violations` and relate **Violation Code = Violation Code**.
5. Check data types in the preview grid:
   - `Inspection Date` and `Month` → **Date**
   - `Latitude` / `Longitude` → number, with geographic role Latitude / Longitude (Tableau usually detects this)
   - `Zipcode` → **String**, then right-click → Geographic Role → **ZIP Code/Postcode**
   - `Restaurant Id`, `Inspection Id`, `Year` → right-click → **Convert to Dimension** (they are IDs, not quantities)

## Step 2. Create calculated fields

Right-click in the Data pane → **Create Calculated Field**. Create each of these:

| Name | Formula |
|---|---|
| `Initial Score` | `IF [Is Initial Cycle] = 1 THEN [Score] END` |
| `Avg Initial Score` | `AVG([Initial Score])` |
| `Restaurants` | `COUNTD([Restaurant Id])` |
| `Inspections` | `COUNTD([Inspection Id])` |
| `Closures` | `SUM([Closed])` |
| `Closure Rate` | `SUM([Closed]) / COUNTD([Inspection Id])` (format as percentage, 1 decimal) |
| `% Initial in A Range` | `AVG(IF [Is Initial Cycle] = 1 AND NOT ISNULL([Score]) THEN IIF([Score] <= 13, 1, 0) END)` (format as percentage) |
| `Score Band` | `IF [Score] <= 13 THEN "A range (0-13)" ELSEIF [Score] <= 27 THEN "B range (14-27)" ELSEIF [Score] >= 28 THEN "C range (28+)" END` |
| `Initial Inspections` | `COUNTD(IF [Is Initial Cycle] = 1 THEN [Inspection Id] END)` |

## Step 3. Build the sheets

Create one worksheet per item below (click the **New Worksheet** tab at the bottom). Name each sheet as shown.

### Sheet "KPI - Restaurants" (repeat for the other KPIs)
1. Drag `Restaurants` to **Text** on the Marks card.
2. Marks type: **Text**. Click Text → format the number large (28-36 pt, bold, teal) and add a small label line above it, e.g. "Restaurants inspected".
3. Duplicate the sheet (right-click tab → Duplicate) and swap the measure to make: **Inspections**, **Avg Initial Score** (1 decimal), **% Initial in A Range**, and **Closures**.

### Sheet "Map - Score by ZIP"
1. Double-click `Zipcode`. Tableau draws a map.
2. Change Marks type to **Map** (filled).
3. Drag `Avg Initial Score` to **Color**. Edit colors → Sequential, custom from light grey to red `#B04A5A`, so worse ZIP codes are darker.
4. Drag `Initial Inspections` to **Tooltip**, and filter ZIP codes with fewer than 20 initial inspections (drag `Initial Inspections` to Filters → At least 20), so tiny samples don't dominate.
5. Map → Map Layers: set style to **Light** and turn off extra layers for a clean look.

### Sheet "Trend - Monthly Score"
1. Drag `Month` to **Columns**; right-click it → choose the **continuous** Month (green pill).
2. Drag `Avg Initial Score` to **Rows**. Marks type: **Line**, color teal.
3. Drag `Month` to Filters → Range of dates → start **2024-01-01** (earlier months have far fewer records; see the README).
4. Optional: drag `Closures` to Rows as a second sheet beneath it (don't use a dual axis).

### Sheet "Cuisine - Worst to Best"
1. Drag `Cuisine` to **Rows**, `Avg Initial Score` to **Columns**.
2. Drag `Initial Inspections` to **Filters** → At least **300** (keeps only cuisines with enough data).
3. Sort descending (toolbar sort button). Color bars grey, then select the top 6 and bottom 6 and color them red and teal.
4. Add a reference line at 13 (Analytics pane → Reference Line → Constant 13, label "A-grade cutoff").

### Sheet "Top Violations"
1. Drag `Violation Code` and `Description` (from violation_codes) to **Rows**.
2. Drag `violations (Count)` to **Columns** (it appears under the violations table as the record count).
3. Drag `Critical` to **Color** (Critical = red, Not Critical = grey).
4. Right-click `Violation Code` → Filter → **Top** → By field → Top 10 by `violations (Count)`. Sort descending.
5. Format: shrink the Description column width and wrap text, or keep only the code and show the description in the tooltip.

### Sheet "Borough Comparison"
1. Drag `Borough` to **Rows**, `Avg Initial Score` to **Columns**; exclude "Unknown".
2. Add `% Initial in A Range` and `Closure Rate` to **Tooltip**. Sort descending.

## Step 4. Assemble the dashboard

1. Click **New Dashboard**. Size: **Fixed, 1200 x 900** (Automatic can look broken on Tableau Public).
2. Layout (top to bottom):
   - Title text: **"NYC Restaurant Inspections, 2023-2026: Where and When Kitchens Fall Short"**
   - Row 1: the five KPI sheets in a horizontal container.
   - Row 2: Map (left, about 60% width) and Borough Comparison (right).
   - Row 3: Cuisine (left) and Top Violations (right).
   - Row 4: Trend across the full width.
3. Add filters: on any sheet, right-click a field → Show Filter for **Borough**, **Cuisine** and **Year**. On each filter, click the dropdown → **Apply to Worksheets → All Using This Data Source**.
4. Add an interaction: Dashboard → Actions → Add Action → **Filter**, source = Map and Cuisine sheets, run on **Select**, targets = all other sheets. Clicking a ZIP code or cuisine then filters everything else.
5. Add a short note at the bottom: "Lower scores are better (A = 0-13). Source: NYC DOHMH via NYC Open Data. Scores use initial cycle inspections only."

## Step 5. Publish and capture

1. **File → Save to Tableau Public**, name it "NYC Restaurant Inspections".
2. When it opens in your browser, copy the URL.
3. Take a screenshot of the full dashboard, save it as `figures/dashboard.png`, and paste the URL into the README where it says "add your Tableau Public link".

## Common problems

- **Numbers look too big after adding the violations table:** use `COUNTD([Inspection Id])` rather than `COUNT`, which is why the calculated fields above use `COUNTD`.
- **ZIP map is blank:** check that `Zipcode` is a String with the ZIP Code geographic role, and click "Unknown" in the lower-right of the map to see unmatched ZIPs.
- **Dashboard looks cramped online:** keep the fixed 1200 x 900 size and avoid more than 6-7 sheets.
