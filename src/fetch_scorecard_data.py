"""
fetch_scorecard_data.py

Pulls College Scorecard data for the schools listed in data/top100_schools.txt
and writes a clean CSV to data/scorecard_top100.csv.

SETUP:
1. Get a free API key: https://collegescorecard.ed.gov/data/api-documentation/
2. Set it as an environment variable before running:
     export COLLEGE_SCORECARD_API_KEY="your_key_here"
3. Run:
     python src/fetch_scorecard_data.py

OUTPUT COLUMNS:
- school_name, state, size
- admission_rate          (overall admission rate, 0-1)
- pell_grant_rate         (% of undergrads on Pell Grants, 0-1; proxy for low-income)
- net_price_0_30k ... net_price_110k_plus  (avg net price by family income bracket, $)
- median_debt
- cost_of_attendance
"""

import os
import sys
import time
import csv
import difflib
import requests

API_BASE = "https://api.data.gov/ed/collegescorecard/v1/schools"

# Income bracket field suffixes used by the College Scorecard API.
# Public and private institutions report these under different field paths,
# so we request both and use whichever is populated.
INCOME_BRACKETS = {
    "net_price_0_30k": "0_30000",
    "net_price_30_48k": "30001_48000",
    "net_price_48_75k": "48001_75000",
    "net_price_75_110k": "75001_110000",
    "net_price_110k_plus": "110001_plus",
}

FIELDS = [
    "id",
    "school.name",
    "school.state",
    "latest.student.size",
    "latest.admissions.admission_rate.overall",
    "latest.aid.pell_grant_rate",
    "latest.aid.median_debt.completers.overall",
    "latest.cost.attendance.academic_year",
    "latest.cost.net_price.public.by_income_level.0-30000",
    "latest.cost.net_price.public.by_income_level.30001-48000",
    "latest.cost.net_price.public.by_income_level.48001-75000",
    "latest.cost.net_price.public.by_income_level.75001-110000",
    "latest.cost.net_price.public.by_income_level.110001-plus",
    "latest.cost.net_price.private.by_income_level.0-30000",
    "latest.cost.net_price.private.by_income_level.30001-48000",
    "latest.cost.net_price.private.by_income_level.48001-75000",
    "latest.cost.net_price.private.by_income_level.75001-110000",
    "latest.cost.net_price.private.by_income_level.110001-plus",
]


# Schools where name-based API search reliably returns the wrong result.
# Maps the name in top100_schools.txt to the exact API school.name value.
NAME_OVERRIDES = {
    "University of Chicago": "University of Chicago",
    "University of Florida": "University of Florida",
    "University of Georgia": "University of Georgia",
    "University of Houston": "University of Houston",
    "New York University": "New York University",
}


def fetch_school(api_key, school_name):
    params = {
        "api_key": api_key,
        "school.name": school_name,
        "fields": ",".join(FIELDS),
        "per_page": 5,
    }
    resp = requests.get(API_BASE, params=params, timeout=30)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    # Pick the result whose name is closest to what we searched for
    def similarity(r):
        return difflib.SequenceMatcher(
            None, school_name.lower(), r.get("school.name", "").lower()
        ).ratio()
    # If an override exists, require an exact name match in the results
    target = NAME_OVERRIDES.get(school_name)
    if target:
        for r in results:
            if r.get("school.name", "").lower() == target.lower():
                return r
        print(f"  Override target '{target}' not in results for '{school_name}' — skipping")
        return None

    best = max(results, key=similarity)
    score = similarity(best)
    if score < 0.6:
        print(f"  Low confidence match ({score:.2f}): '{best.get('school.name')}' for '{school_name}' — skipping")
        return None
    return best


def first_present(record, *keys):
    for k in keys:
        v = record.get(k)
        if v is not None:
            return v
    return None


def main():
    api_key = os.environ.get("COLLEGE_SCORECARD_API_KEY")
    if not api_key:
        print("ERROR: Set COLLEGE_SCORECARD_API_KEY environment variable first.")
        print('  export COLLEGE_SCORECARD_API_KEY="your_key_here"')
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    schools_path = os.path.join(here, "..", "data", "top100_schools.txt")
    out_path = os.path.join(here, "..", "data", "scorecard_top100.csv")

    with open(schools_path) as f:
        schools = [line.strip() for line in f if line.strip()]

    rows = []
    for i, name in enumerate(schools, 1):
        print(f"[{i}/{len(schools)}] Fetching: {name}")
        try:
            record = fetch_school(api_key, name)
        except requests.HTTPError as e:
            print(f"  HTTP error for {name}: {e}")
            continue

        if record is None:
            print(f"  No match found for: {name}")
            continue

        def net_price(bracket):
            # API field names use hyphens: "0-30000", "110001-plus", etc.
            pub = record.get(f"latest.cost.net_price.public.by_income_level.{bracket}")
            priv = record.get(f"latest.cost.net_price.private.by_income_level.{bracket}")
            return pub if pub is not None else priv

        row = {
            "school_name": record.get("school.name"),
            "state": record.get("school.state"),
            "size": record.get("latest.student.size"),
            "admission_rate": record.get("latest.admissions.admission_rate.overall"),
            "pell_grant_rate": record.get("latest.aid.pell_grant_rate"),
            "median_debt": record.get("latest.aid.median_debt.completers.overall"),
            "cost_of_attendance": record.get("latest.cost.attendance.academic_year"),
            "net_price_0_30k":    net_price("0-30000"),
            "net_price_30_48k":   net_price("30001-48000"),
            "net_price_48_75k":   net_price("48001-75000"),
            "net_price_75_110k":  net_price("75001-110000"),
            "net_price_110k_plus": net_price("110001-plus"),
        }
        rows.append(row)

        # Be polite to the API (default limit: 1000 req/hour, so this is generous)
        time.sleep(0.2)

    if not rows:
        print("No data fetched. Check your API key and school names.")
        sys.exit(1)

    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Wrote {len(rows)} schools to {out_path}")


if __name__ == "__main__":
    main()
