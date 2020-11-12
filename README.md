# NBERSummerInstitutes
Presentations of manuscripts at NBER Summer Institutes

## What is this?
For my paper "[Discussants](https://papers.ssrn.com/abstract=3727173)" (joint with Co-Pierre George and Daniel C. Opolot) I used data on presentations at the Summer Institutes of the National Bureau of Economic Research.  The list of presentations, along with names of authors and presenters and discussants if any, used to be online available online at http://www.nber.org/summer-institute/ (until November 2020).

This repository makes this data available in a compressed format.  This way you can avoid having to write your own web scraper.  I also harmonized names of groups and programs.

## How do I use this?

The table [overview.md](overview.md) summarizes the number of presentations per NBER program (or working group) and year. It does account joint workshops.

In folder [output/](./output/) you find the compressed data, both as flat files and as nested json.

## What's the benefit?
- No need to deal with broken and differently formatted html.
- Affiliations cleaned.
- Some corrections regarding start and end time applied, see [folder corrections](corrections).
- Names of groups and programmes consolidated, see [`./corrections/groups.csv`](corrections/groups.csv).
- The original programs aren't available any more!

## Citation
When using this data, please cite: Rose, ME, C-P Georg and DC Opolot, “Discussants”, *Max Planck Institute for Innovation & Competition Research Paper* No. 20-19, November 2020.
