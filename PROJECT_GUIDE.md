# "Who Gets In" — Project Guide

A working playbook for building this project from zero to OJSS submission. This is the doc to come back to each week.

## 1. What you're actually building

**End product:** A public website (one page) with two interactive charts:

1. **Scatter plot** — each dot is one of the Top 100 universities. X-axis = overall admission rate. Y-axis = share of students from low-income families (bottom income quintile). This shows whether "harder to get into" correlates with "fewer low-income students get in."
2. **Bar chart** — for each school, average net price (what a family actually pays after aid) broken out by family income bracket, plus % of students receiving Pell Grants. This shows whether financial aid actually closes the gap implied by chart 1.

Below the charts: a short written interpretation (this becomes the basis of your Substack post and OJSS paper).

**The core argument the data should let you make:** "Top universities talk about meritocracy and need-blind aid, but [X]% of seats at the most selective schools go to students from families that aren't low-income, and even with aid, low-income families pay [Y]% of their income compared to [Z]% for high-income families." You won't know the exact numbers until you pull the data — that's the point.

## 2. The data reality check (read this first)

The original brief says "pull income brackets + admission rates by school" from College Scorecard. One important nuance: **College Scorecard does not report admission rate broken down by applicant income.** No public dataset does — schools don't release that.

What you can actually get, from two sources:

**A. College Scorecard** (U.S. Dept of Education) — per school:
- Overall admission rate (`latest.admissions.admission_rate.overall`)
- Average net price *by family income bracket* (5 brackets: $0–30K, $30–48K, $48–75K, $75–110K, $110K+) — this is what families actually pay after grants/scholarships
- % of undergrads receiving Pell Grants (`latest.aid.pell_grant_rate`) — Pell is a strong proxy for low-income status
- Median student debt at completion
- Cost of attendance, enrollment size, etc.

**B. Opportunity Insights — College Mobility Report Cards** (Harvard, free download, no API key) — per school:
- % of students from each parent income quintile (this is your "who actually gets in by income" data)
- Mobility rate (% of bottom-quintile kids who reach top-quintile income as adults)

**Your project = College Scorecard (admission rate, cost, Pell %) joined with Opportunity Insights (income quintile breakdown)**, matched by school. This is *more rigorous* than the original brief, not a downgrade — and it's a more defensible methodology section for OJSS.

## 3. Tech stack (kept simple on purpose)

- **Python** (`requests`, `pandas`) — pull and clean data. You'll write 2 small scripts.
- **CSV/JSON files** — your dataset, committed to the project repo.
- **A simple HTML + Chart.js or Recharts page** — the dashboard. No build tools needed if you use Chart.js via CDN; Recharts if you want a React app.
- **GitHub Pages** — free hosting, deploys straight from your repo. Simplest path: GitHub Pages over Vercel for a static site.

You do not need to learn D3 from scratch — Chart.js or Recharts will produce both chart types with far less code, and "I built this with D3" isn't what makes the project compelling. The data and the analysis are what matter for your essays.

## 4. Step-by-step plan

### Week 1–2 (June): Get the data

1. **Get a College Scorecard API key** — go to https://collegescorecard.ed.gov/data/api-documentation/, fill out the form (free, takes 2 minutes, key arrives by email). Do this yourself — it requires your email address.
2. Save the key somewhere safe (you'll set it as an environment variable, never commit it to GitHub).
3. Use the starter script (`src/fetch_scorecard_data.py`, already written for you in this project folder) to pull data for a list of ~100 schools. The list is in `data/top100_schools.txt` — review it and adjust against the current US News Top 100 National Universities list if you want a specific ranking year.
4. Download the **Mobility Report Cards "College-Level Data"** file from https://opportunityinsights.org/data/ (look for "Mobility Report Cards" → college-level CSV). This gives you income-quintile shares per school.
5. Run `src/merge_datasets.py` (you'll fill this in together with Claude in a future session, or now if you want) to join the two datasets on school name / OPEID.

**Output of this phase:** one clean CSV, `data/who_gets_in_top100.csv`, with one row per school and columns for admission rate, Pell %, net price by income bracket, and income-quintile shares.

### Week 3 (June): Build the charts

1. Open `dashboard/index.html` (starter file included).
2. Load `who_gets_in_top100.csv` into the page (Chart.js + PapaParse for CSV parsing, both via CDN — no install needed).
3. Build the scatter plot (admission rate vs. % low-income students).
4. Build the bar chart (net price by income bracket, per school — start with a dropdown to pick a school, or show a fixed set of 10 representative schools so it's not overwhelming).

### Week 4 (June): Add financial aid overlay

1. Add Pell Grant % as a third data dimension — e.g., color-code scatter plot dots by Pell %, or add a second small chart.
2. Compute and highlight the "gap" metric: for each school, (admission rate) vs (% low-income enrollment) — schools where these diverge most are your headline finding.

### Week 1 (July): Publish the dashboard

1. Push the `dashboard/` folder to a GitHub repo.
2. Enable GitHub Pages (Settings → Pages → deploy from branch, root or `/dashboard`).
3. Test the live URL.

### Week 2 (July): Write the Substack article

1. ~800 words. Structure: hook (a surprising number from your data) → context (what "meritocratic admissions" claims to mean) → your findings (2-3 charts embedded as images or links to the live dashboard) → what it means → call back to your own experience.
2. Embed the dashboard link or screenshot the key charts.

### August: Expand to OJSS paper

1. Target: 2,000–8,000 words (OJSS range), abstract 150–300 words, consistent citation style (pick one — APA is standard for social science).
2. Structure: Abstract → Intro/motivation (your John Locke essay material fits here) → Data & Methods (describe College Scorecard + Opportunity Insights, your matching methodology, limitations) → Findings (your charts + statistical description) → Discussion (policy implications) → Conclusion → References.
3. Submit via https://www.oxfordjss.org/submission-guidelines. Fast Track = $125, 2-week turnaround, but doesn't guarantee acceptance and if accepted the standard $200 APC still applies — factor that into your decision; standard review is free of the fast-track fee.
4. Confirm OJSS allows simultaneous "in review" status to be listed on Common App — generally yes, "under review" is an accurate and common thing to list.

## 5. What to do right now

1. Register for a College Scorecard API key (link above) — 2 minutes, do this today so it's not a bottleneck.
2. Look at `data/top100_schools.txt` and adjust the school list if you have specific schools you care about (e.g., your own application list).
3. Once you have the key, come back and we'll run the data pull together.

## 6. Risks / things that could derail timeline

- **API key approval delay** — usually instant, but budget a day just in case.
- **Name matching between datasets** — College Scorecard and Opportunity Insights use different school identifiers; the merge script handles common cases but ~10-20% of schools may need manual name fixes. Budget time for this in Week 2.
- **Opportunity Insights data is from ~2013-2017 cohorts** — it's the best available, but you should explicitly note this as a limitation in your writeup (recent data doesn't exist publicly at this granularity).
- **Scope creep** — the dashboard does not need to be fancy. Two clear charts + good interpretation beats five mediocre ones. Resist adding features once Week 3 is done.
