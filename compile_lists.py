#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Compiles source files to generate two json objects.

One json dump is sorted by year and then group, the other one by group first
and then by year.
"""
# TODO
# Should we add chairs
# Missing Adjourn: AGING 2000, EFRW 2000

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

_group_correction = {"AW": "AG", "AGING": "AG", "PELS": "PESS", "PEC": "PE",
    "PRHC": "HC", "PRHA": "HC", "PRPM": "CRIW", "CRF": "CRIW", "PRIPE": "IPE",
    "EFCO": "EFG", "EFGS04": "EFG", "EFGS05": "EFG", "EFGS07": "EFG",
    "EFDW": "EFWW", "EFBGZ": "EFABG", "EFAC": "EFACR", "CR": "CRP"}


def correct_time(title, group, year, df, start=None, end=None):
    """Correct the start or end time for a presentation."""
    mask = ((df["title"] == title) & (df["group"] == group) &
            (df["year"] == year))
    if start:
        df.loc[mask, "start"] = start
    if end:
        df.loc[mask, "end"] = end


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
        group = splitext(basename(file))[0]
        group = _group_correction.get(group, group)
        year = int(file.split("/")[-2])
        if year >= 2012:  # hasn't been parsed yet
            continue
        with open(file, 'r') as inf:
            lines = inf.readlines()
        meta = {'group': group, 'year': year}  # General information
        entry = False  # Help filtering header information
        joint = None  # To possibly add other authors
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
            elif cat == "TITLE":
                if entry:  # Get end in next line to finish current entry
                    next_line = lines[num+1].strip()
                    if next_line.split(': ', 1)[0] == "TIME":
                        end = next_line.split(": ", 1)[-1]
                        d["end"] = end
                        for t in add_end:
                            correct_time(t, group, year, by_title, end=end)
                        add_end = []
                    else:
                        add_end.append(d["title"])
                    # Finalize
                    if joint:
                        d["joint"] = joint
                    by_group[group][year].append(d)
                    by_year[year][group].append(d)
                    by_title = by_title.append(d, ignore_index=True)
                    if not "start" in d:
                        add_start.append(d["title"])
                d = {"title": tokens[1]}
                d.update(meta)
                entry = True
            elif cat in ("AUTHOR", "DISCUSSANT", "LINK"):
                d[cat.lower()] = tokens[1]
            elif cat == "JOINT":
                d["group"] += "; " + tokens[1]
            elif cat == "WITH":
                if entry:
                    d["author"] += " " + tokens[1]
                else:
                    joint = tokens[1]
            elif cat == "TIME":
                d["start"] = tokens[1]
                # For presentations w/o start, add previous start time
                for t in add_start:
                    correct_time(t, group, year, by_title, start=start)
                add_start = []
                start = tokens[1]
            elif cat in _end_categories:
                d["end"] = tokens[1]
                # For presentations w/o end, add this end time
                for t in add_end:
                    correct_time(t, group, year, by_title, end=tokens[1])
                add_end = []
            elif (last_line and not end_of_entry) or (cat == "" and entry and end_of_entry):
                # Finalize
                if joint:
                    d["joint"] = joint
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
    with open(TARGET + 'by_year.json', 'w') as ouf:
        ouf.write(dumps(by_year, indent=2, sort_keys=True))
    with open(TARGET + 'by_group.json', 'w') as ouf:
        ouf.write(dumps(by_group, indent=2, sort_keys=True))
    by_title["year"] = by_title["year"].astype(int)
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
