"""
Clean the NYC DOHMH restaurant inspection export into three Tableau-ready tables
and a SQLite database.

Input : data/raw/restaurant_inspections_raw.csv  (one row per violation cited)
Output: data/clean/inspections.csv      one row per inspection (with restaurant details)
        data/clean/violations.csv       one row per violation cited (inspection_id, code)
        data/clean/violation_codes.csv  lookup: code -> description, critical flag
        data/restaurant_inspections.db  SQLite database with the same three tables

Run from the repository root:  python src/clean_data.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/restaurant_inspections_raw.csv")
CLEAN = Path("data/clean")
DB = Path("data/restaurant_inspections.db")
CLEAN.mkdir(parents=True, exist_ok=True)

BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]

# ---- 1. Load ---------------------------------------------------------------
raw = pd.read_csv(RAW, dtype=str)
print(f"Raw rows: {len(raw):,}")
log = {"raw rows": len(raw)}

# ---- 2. Basic fixes ----------------------------------------------------------
df = raw.drop_duplicates().copy()
log["exact duplicate rows removed"] = len(raw) - len(df)

df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce").dt.normalize()
df = df[df["inspection_date"].dt.year > 1900]      # 1900-01-01 marks "not yet inspected"
df["score"] = pd.to_numeric(df["score"], errors="coerce")
for col in ["latitude", "longitude"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df.loc[df[col] == 0, col] = pd.NA                # 0,0 means "no geocode"
df["zipcode"] = df["zipcode"].str.strip().str.zfill(5)

# Borough "0" = missing. Recover it from the ZIP code where that ZIP belongs to a single borough.
zip_to_boro = (df[df["boro"].isin(BOROUGHS)].groupby("zipcode")["boro"]
               .agg(lambda s: s.mode().iat[0]))
missing = ~df["boro"].isin(BOROUGHS)
df.loc[missing, "boro"] = df.loc[missing, "zipcode"].map(zip_to_boro)
log["rows with missing borough"] = int(missing.sum())
log["  of which recovered from ZIP"] = int(df.loc[missing, "boro"].notna().sum())
df["boro"] = df["boro"].fillna("Unknown")

# Tidy text fields
df["dba"] = df["dba"].str.strip().str.title()
df["cuisine_description"] = (df["cuisine_description"].str.strip()
                             .replace({"Not Listed/Not Applicable": "Other / Not Listed"}))

# ---- 3. Inspection-level table -------------------------------------------
key = ["camis", "inspection_date", "inspection_type"]
df["is_critical"] = (df["critical_flag"] == "Critical").astype(int)
df["is_closure"] = df["action"].str.contains("Closed by DOHMH|re-closed by DOHMH", case=False, na=False).astype(int)
df["has_violation"] = df["violation_code"].notna().astype(int)

insp = (df.groupby(key, as_index=False)
          .agg(score=("score", "max"), grade=("grade", "first"),
               violations=("has_violation", "sum"), critical_violations=("is_critical", "sum"),
               closed=("is_closure", "max")))
insp = insp.sort_values(key).reset_index(drop=True)
insp.insert(0, "inspection_id", insp.index + 1)
insp["program"] = insp["inspection_type"].str.split(" / ").str[0]
insp["visit"] = insp["inspection_type"].str.split(" / ").str[1]
insp["is_initial_cycle"] = (insp["inspection_type"] == "Cycle Inspection / Initial Inspection").astype(int)
insp["has_critical"] = (insp["critical_violations"] > 0).astype(int)
insp["year"] = insp["inspection_date"].dt.year
insp["month"] = insp["inspection_date"].dt.to_period("M").dt.to_timestamp()

# Restaurant attributes: most recent non-missing value per restaurant
rest_cols = ["dba", "boro", "zipcode", "cuisine_description", "latitude", "longitude", "nta"]
rest = (df.sort_values("inspection_date").groupby("camis")[rest_cols].last().reset_index())
insp = insp.merge(rest, on="camis", how="left")
insp = insp.rename(columns={"dba": "restaurant", "boro": "borough", "cuisine_description": "cuisine",
                            "camis": "restaurant_id", "nta": "neighborhood_code"})
insp["inspection_date"] = insp["inspection_date"].dt.date
insp["month"] = insp["month"].dt.date

# ---- 4. Violation tables -----------------------------------------------------
viol = df[df["violation_code"].notna()].merge(insp[["inspection_id", "restaurant_id", "inspection_date", "inspection_type"]]
                                              .assign(inspection_date=lambda d: pd.to_datetime(d["inspection_date"])),
                                              left_on=key, right_on=["restaurant_id", "inspection_date", "inspection_type"])
violations = viol[["inspection_id", "violation_code"]].reset_index(drop=True)
codes = (viol.groupby("violation_code")
             .agg(description=("violation_description", lambda s: s.mode().iat[0]),
                  critical=("critical_flag", lambda s: s.mode().iat[0]))
             .reset_index())

# ---- 5. Save -------------------------------------------------------------------
insp.to_csv(CLEAN / "inspections.csv", index=False)
violations.to_csv(CLEAN / "violations.csv", index=False)
codes.to_csv(CLEAN / "violation_codes.csv", index=False)
with sqlite3.connect(DB) as con:
    insp.to_sql("inspections", con, if_exists="replace", index=False)
    violations.to_sql("violations", con, if_exists="replace", index=False)
    codes.to_sql("violation_codes", con, if_exists="replace", index=False)

log.update({"inspections": len(insp), "restaurants": insp["restaurant_id"].nunique(),
            "violations cited": len(violations), "violation codes": len(codes),
            "date range": f"{insp['inspection_date'].min()} to {insp['inspection_date'].max()}"})
for k, v in log.items():
    print(f"{k}: {v:,}" if isinstance(v, int) else f"{k}: {v}")
