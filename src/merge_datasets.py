"""
merge_datasets.py

Downloads Opportunity Insights Mobility Report Card data and merges it
with the College Scorecard CSV to produce data/who_gets_in_top100.csv.

Run from the who-gets-in folder:
    python3 src/merge_datasets.py

OUTPUT COLUMNS (one row per school):
  school_name, state, size, admission_rate, pell_grant_rate,
  median_debt, cost_of_attendance,
  net_price_0_30k ... net_price_110k_plus,
  par_q1        -- % of students from bottom income quintile (OI data)
  par_top1pc    -- % from top 1% (OI data)
  par_median    -- median parent income (OI data)
  mobility_rate -- % bottom-quintile kids reaching top quintile as adults
"""

import csv
import difflib
import io
import os
import sys
import requests

OI_URL = "https://opportunityinsights.org/wp-content/uploads/2018/03/mrc_table1.csv"

HERE = os.path.dirname(os.path.abspath(__file__))
SCORECARD_CSV = os.path.join(HERE, "..", "data", "scorecard_top100.csv")
OUT_CSV = os.path.join(HERE, "..", "data", "who_gets_in_top100.csv")


def load_scorecard():
    with open(SCORECARD_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_opportunity_insights():
    print("Downloading Opportunity Insights data...")
    resp = requests.get(OI_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    return list(reader)


def best_match(name, oi_rows, threshold=0.6):
    def score(r):
        return difflib.SequenceMatcher(None, name.lower(), r["name"].lower()).ratio()
    best = max(oi_rows, key=score)
    s = score(best)
    return best if s >= threshold else None


def main():
    scorecard = load_scorecard()
    oi_rows = load_opportunity_insights()
    print(f"  Loaded {len(oi_rows)} OI schools")

    merged = []
    unmatched = []

    for row in scorecard:
        name = row["school_name"]
        match = best_match(name, oi_rows)
        if match:
            row["par_q1"] = match.get("par_q1", "")
            row["par_top1pc"] = match.get("par_top1pc", "")
            row["par_median"] = match.get("par_median", "")
            row["mobility_rate"] = match.get("mr_kq5_pq1", "")
        else:
            row["par_q1"] = ""
            row["par_top1pc"] = ""
            row["par_median"] = ""
            row["mobility_rate"] = ""
            unmatched.append(name)
        merged.append(row)

    fieldnames = list(merged[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(merged)

    print(f"\nWrote {len(merged)} rows to {OUT_CSV}")
    if unmatched:
        print(f"Could not match {len(unmatched)} schools to OI data:")
        for n in unmatched:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
