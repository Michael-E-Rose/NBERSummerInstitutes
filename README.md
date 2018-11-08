# NBERSummerInstitutes
Presentations of manuscripts at the prestigious NBER Summer Institutes

## What is this?
For my paper "Informal Collaboration with Central Colleagues" (joint with Co-Pierre George and Daniel C. Opolot) I used data on presentations at the Summer Institutes of the National Bureau of Economic Research.  The list of presentations, along with names of authors and presenters and discussants if any, are available online at http://www.nber.org/summer-institute/.

This repository makes this data available in a compressed format.  This way you can avoid having to write your own web scraper.

## How do I use this?

In folder [compiled/](./compiled/) you find the file you are looking for: A long list of Journals with their yearly SJR (Scimago Journal Rank), the h-index and avgerage citations.  All of them are measured using articles from the previous three years.

Usage in your scripts is easy:

* In python (with pandas):
```python
import pandas as pd
url = 'https://raw.githubusercontent.com/Michael-E-Rose/ScimagoEconJournalImpactFactors/master/compiled/Scimago_JIFs.csv'
df = pd.read_csv(url)
```

* In R:
```R
url = 'https://raw.githubusercontent.com/Michael-E-Rose/ScimagoEconJournalImpactFactors/master/compiled/Scimago_JIFs.csv'
df <- read.csv(url)
```

* In Stata:
```Stata
insheet using "https://raw.githubusercontent.com/Michael-E-Rose/ScimagoEconJournalImpactFactors/master/compiled/Scimago_JIFs.csv"
```

## What's the benefit?
- Central and continuously updated online storage for seamless inclusion in local scripts.
- No need to deal with broken and differntly formatted html.
