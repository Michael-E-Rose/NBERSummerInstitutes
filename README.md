# NBERSummerInstitutes
Presentations of manuscripts at NBER Summer Institutes

## What is this?
For my paper "Discussants" (joint with Co-Pierre George and Daniel C. Opolot) I used data on presentations at the Summer Institutes of the National Bureau of Economic Research.  The list of presentations, along with names of authors and presenters and discussants if any, are available online at http://www.nber.org/summer-institute/.

This repository makes this data available in a compressed format.  This way you can avoid having to write your own web scraper.  I also harmonized names of groups and programs.

## How do I use this?

In folder [compiled/](./compiled/) you find the file you are looking for: A long list of presentations with authors, link to paper (if available), discussant, start and end time, organizer, venue, group or program, and eventually information on joint sessions.

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
- No need to deal with broken and differently formatted html.
- Affiliations cleaned.
- Some corrections regarding start and end time applied, see [folder corrections](corrections).
- Names of groups and programmes consolidated, see [`./corrections/groups.csv`](corrections/groups.csv).
