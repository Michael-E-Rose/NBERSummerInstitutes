#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Compiles source files to generate two json objects.

One json dump is sorted by year and then group, the other one by group first
and then by year.
"""
# TODO
# Parallel tracks: PRIT 2019
# Missing Adjourn: AGING 2000, EFRW 2000, CF 2001, AG 2010

import os
from collections import defaultdict
from glob import glob
from json import dumps
from os.path import basename, join, splitext

import pandas as pd
from tabulate import tabulate

SOURCE = "./source/"
TARGET = "./output/"

_end_categories = ("BREAKFAST", "BREAK", "LUNCH", "ADJOURN")

_group_correction = {
    # Aging groups
    "AW": "AG", "AGING": "AG",
    "PELS": "PESS",
    # Public Economy
    "PEC": "PE",
    # Health
    "PRHC": "HC", "PRHA": "HC",
    # Income and Welath
    "PRPM": "CRIW", "CRF": "CRIW",
    # Macro Perspectives
    "EFRW": "EFMPL",
    # Innovation Policy
    "PRIPE": "IPE",
    # Growth
    "EFCO": "EFG", "EFGS04": "EFG", "EFGS05": "EFG", "EFGS07": "EFG",
    # Income Distribution
    "EFABG": "EFDIS", "EFBGZ": "EFDIS",
    # Forecasting
    "EFDW": "EFFE", "EFWW": "EFFE",
    # Aggregate Consumption Behaviour
    "EFAC": "EFACR",
    # Corruption
    "CR": "CRP"}
_start_correction = {
    "The Liquidity Service of Sovereign Bonds": "JULY 19, 10:00 AM",
    "Stock Market Liberalizations and the Repricing of Systematic Risk": "JULY 19, 11:15 AM",
    "Does Financial Liberalization Improve the Allocation of Investment? Micro Evidence from Developing Countries": "JULY 19, 12:15 PM"
}
_end_correction = {
    "Does Financial Liberalization Improve the Allocation of Investment? Micro Evidence from Developing Countries": "JULY 19, 11:15 PM",
    "Financial Conservatism: Evidence on Capital Structure from Low Leverage Firms": "AUGUST 7, 2:30 PM",
    "Climbing Atop the Shoulders of Giants: The Economics of Cumulative Knowledge Hubs": "JULY 23, 4:00 PM",
    "Cost and Selection in Private Medicare Advantage Plans: Evidence from the Medicare Current Beneficiary Survey": "JULY 29, 5:00 pm",
    "Aggregate Implications of Workweek Restrictions": "JULY 24, 4:30 PM",
    "Unveiling the Home Sector: Bayesian Estimates of Aggregate Home Production Models": "JULY 25, 4:30 PM",
    "Matching, Searching, and Heterogeneity": "JULY 26, 4:30 PM",
    "Turnover, Wage Determination and the Formation of Human Capital": "JULY 27, 4:30 PM",
}


def correct_time(title, group, year, df, start=None, end=None):
    """Correct the start or end time for a presentation."""
    mask = ((df["title"] == title) & (df["group"] == group) &
            (df["year"] == year))
    if start:
        df.loc[mask, "start"] = start
    if end:
        df.loc[mask, "end"] = end


def group_from_filename(fname):
    """Extract name of group from filename."""
    group = splitext(basename(fname))[0]
    return _group_correction.get(group, group)


def list_files():
    """List files in nested subfolders."""
    for root, subdirs, filenames in sorted(os.walk(SOURCE)):
        for filename in filenames:
            if not filename.endswith('dat'):
                continue
            yield join(root, filename)


def main():
    # Compile each file separately
    by_year = defaultdict(lambda: defaultdict(list))
    by_group = defaultdict(lambda: defaultdict(list))
    by_title = pd.DataFrame()
    for file in list_files():
        # Workshop information
        group = group_from_filename(file)
        year = int(file.split("/")[-2])
        if year >= 2012 and year <= 2016:  # hasn't been parsed yet
            continue
        with open(file, 'r') as inf:
            lines = inf.readlines()
        meta = {'group': group, 'year': year}
        # Auxiliary variables
        entry = False  # Help filtering header information
        discussion = False
        joint = None  # To possibly add other authors
        # Parse entries
        d = {}
        add_start = []
        add_end = []
        for num, line in enumerate(lines):
            last_line = num == len(lines)-1
            end_of_entry = "end" in d
            tokens = line.strip().split(': ', 1)
            cat = tokens[0]
            if cat in ("DATE", "VENUE", "ORGANIZER"):
                meta[cat.lower()] = tokens[1].strip()
            elif cat in ("TITLE", "DISCUSSION"):
                if entry:  # Find start time in this block to finish previous block
                    next_line = lines[num+1].strip()
                    if next_line.split(': ', 1)[0] == "TIME":
                        end = next_line.split(": ", 1)[-1]
                        d["end"] = end
                        for t in add_end:
                            correct_time(t, group, year, by_title, end=end)
                        add_end = []
                    else:  # Correct time for entries w/o end time later
                        add_end.append(d["title"])
                    # Finalize
                    if joint:
                        d["joint"] = joint
                    if not discussion:
                        by_group[group][year].append(d)
                        by_year[year][group].append(d)
                        by_title = by_title.append(d, ignore_index=True)
                    if not "start" in d:
                        add_start.append(d["title"])
                d = {"title": tokens[1]}
                d.update(meta)
                entry = True
                discussion = cat == "DISCUSSION"
            elif cat in ("AUTHOR", "DISCUSSANT", "LINK"):
                d[cat.lower()] = tokens[1]
            elif cat == "JOINT":
                d["group"] += "; " + tokens[1]
            elif cat == "WITH":
                if entry:
                    d["author"] += "; " + tokens[1]
                else:
                    joint = tokens[1]
            elif cat == "TIME":
                d["start"] = _start_correction.get(d["title"], tokens[1])
                # For presentations w/o start, add previous start time
                for t in add_start:
                    correct_time(t, group, year, by_title, start=start)
                add_start = []
                start = tokens[1]
            elif cat in _end_categories:
                d["end"] = _end_correction.get(d["title"], tokens[1])
                # For presentations w/o end, add this end time
                for t in add_end:
                    correct_time(t, group, year, by_title, end=tokens[1])
                add_end = []
            elif (last_line and not end_of_entry) or (cat == "" and entry and end_of_entry):
                # Finalize
                if joint:
                    d["joint"] = joint
                if not discussion:
                    by_group[group][year].append(d)
                    by_year[year][group].append(d)
                    by_title = by_title.append(d, ignore_index=True)
                if not "start" in d:
                    add_start.append(d["title"])
                # For presentations w/o start, add previous start time
                for t in add_start:
                    correct_time(t, group, year, by_title, start=start)
                add_start = []
                entry = False

    # Write out
    for data, label in ((by_year, "by_year"), (by_group, "by_group")):
        with open(f'{TARGET}{label}.json', 'w') as ouf:
            ouf.write(dumps(data, indent=2, sort_keys=True))
    by_title["year"] = by_title["year"].astype("uint16")
    order = ['group', 'year', 'date', 'venue', 'organizer', 'title', 'author',
             'discussant', 'start', 'end', 'link']
    by_title[order].to_csv(TARGET + "by_title.csv", index=False)

    # Overview table
    by_title['group'] = by_title['group'].str.split(";").str[0]
    overview = pd.crosstab(by_title['group'], by_title['year'])
    overview = overview.astype(str).replace("0", "")
    with open("overview.md", "w") as ouf:
        ouf.write(tabulate(overview, tablefmt="pipe", headers="keys"))


if __name__ == '__main__':
    main()
