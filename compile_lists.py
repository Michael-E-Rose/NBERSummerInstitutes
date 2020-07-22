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
GROUP_CORRECTION = "./corrections/groups.csv"
START_CORRECTION = "./corrections/start.csv"
END_CORRECTION = "./corrections/end.csv"
TARGET = "./output/"

_end_categories = ("BREAKFAST", "BREAK", "LUNCH", "ADJOURN")


def list_files():
    """List files in nested subfolders."""
    for root, subdirs, filenames in sorted(os.walk(SOURCE)):
        for filename in filenames:
            if not filename.endswith('dat'):
                continue
            yield join(root, filename)


def main():
    # Correction files
    group_correction = pd.read_csv(GROUP_CORRECTION, index_col=0)["new"].to_dict()
    start_correction = pd.read_csv(START_CORRECTION, index_col=0)["time"].to_dict()
    end_correction = pd.read_csv(END_CORRECTION, index_col=0)["time"].to_dict()

    # Containers
    by_year = defaultdict(lambda: defaultdict(list))
    by_group = defaultdict(lambda: defaultdict(list))
    by_title = {}
    idx = 0

    # Compile each file separately
    for file in list_files():
        # Workshop information
        group = splitext(basename(file))[0]
        group = group_correction.get(group, group)
        year = int(file.split("/")[-2])
        if year >= 2012 and year <= 2016:  # hasn't been parsed yet
            continue
        with open(file, 'r') as inf:
            lines = inf.readlines()
        meta = {'group': group, 'year': year}
        # Auxiliary variables
        entry = False  # Help filtering header information
        discussion = False
        more_authors = None
        add_start = []
        add_end = []
        # Parse entries
        d = {}
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
                            by_title[t]["end"] = end
                        add_end = []
                    else:  # Correct time for entries w/o end time later
                        add_end.append(idx)
                    # Finalize
                    if more_authors:
                        d["joint"] = more_authors
                    if not discussion:
                        by_group[group][year].append(d)
                        by_year[year][group].append(d)
                        by_title[idx] = d
                    if not "start" in d:
                        add_start.append(idx)
                title = tokens[1]
                d = {"title": title}
                idx += 1
                try:
                    d["start"] = start = start_correction[title]
                except KeyError:
                    pass
                try:
                    d["end"] = end_correction[title]
                except KeyError:
                    pass
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
                    more_authors = tokens[1]
            elif cat == "TIME":
                d["start"] = tokens[1]
                # For presentations w/o start, add previous start time
                for t in add_start:
                    by_title[t]["start"] = start
                add_start = []
                start = tokens[1]
            elif cat in _end_categories:
                d["end"] = tokens[1]
                # For presentations w/o end, add this end time
                for t in add_end:
                    by_title[t]["end"] = tokens[1]
                add_end = []
            elif (last_line and not end_of_entry) or (cat == "" and entry and end_of_entry):
                # Finalize
                if more_authors:
                    d["joint"] = more_authors
                if not discussion:
                    by_group[group][year].append(d)
                    by_year[year][group].append(d)
                    by_title[idx] = d
                if not "start" in d:
                    add_start.append(idx)
                # For presentations w/o start, add previous start time
                for t in add_start:
                    by_title[t]["start"] = start
                add_start = []
                entry = False

    # Write out
    for data, label in ((by_year, "by_year"), (by_group, "by_group")):
        with open(f'{TARGET}{label}.json', 'w') as ouf:
            ouf.write(dumps(data, indent=2, sort_keys=True))
    by_title = pd.DataFrame.from_dict(by_title, orient="index")
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
