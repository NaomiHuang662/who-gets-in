# Who Gets In — College Admissions & Family Income Analyzer

Start with **PROJECT_GUIDE.md** — it lays out the full plan, what data sources to use, and the step-by-step timeline.

## Quick start

```bash
pip install -r requirements.txt

# 1. Get a free API key: https://collegescorecard.ed.gov/data/api-documentation/
export COLLEGE_SCORECARD_API_KEY="your_key_here"

# 2. Pull College Scorecard data for the Top 100 list
python src/fetch_scorecard_data.py
# -> writes data/scorecard_top100.csv

# 3. (Next step) Download Opportunity Insights mobility data and merge
#    See PROJECT_GUIDE.md Week 1-2 for details.
```

## Project structure

```
who-gets-in/
├── PROJECT_GUIDE.md          # full plan + how-to, read this first
├── data/
│   ├── top100_schools.txt    # editable list of schools to analyze
│   └── scorecard_top100.csv  # output of fetch_scorecard_data.py
├── src/
│   └── fetch_scorecard_data.py
├── dashboard/
│   └── index.html            # the public-facing dashboard
└── docs/                      # notes, drafts of Substack/OJSS writeups
```

## Status

- [ ] College Scorecard API key obtained
- [ ] Scorecard data pulled (Top 100)
- [ ] Opportunity Insights data downloaded + merged
- [ ] Scatter plot built
- [ ] Bar chart built
- [ ] Dashboard published (GitHub Pages)
- [ ] Substack article published
- [ ] OJSS paper drafted
- [ ] OJSS submitted
