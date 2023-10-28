#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Compiles source files to generate two json objects.

One json dump is sorted by year and then group, the other one by group first
and then by year.
"""

from collections import defaultdict
from json import dumps
from pathlib import Path

import pandas as pd
from tabulate import tabulate
from tqdm import tqdm

SOURCE = Path("./source/")
CORRECTIONS = Path("./corrections/")
TARGET = Path("./output/")

_end_categories = ("BREAKFAST", "BREAK", "LUNCH", "ADJOURN")


def main():
    # Correction files
    group_correct = pd.read_csv(CORRECTIONS/"groups.csv", index_col=0)["new"].to_dict()
    start_correct = pd.read_csv(CORRECTIONS/"start.csv", index_col=0)["time"].to_dict()
    end_correct = pd.read_csv(CORRECTIONS/"end.csv", index_col=0)["time"].to_dict()

    # Containers
    by_year = defaultdict(lambda: defaultdict(list))
    by_group = defaultdict(lambda: defaultdict(list))
    by_title = {}
    idx = 0

    # Compile each file separately
    for file in tqdm(sorted(SOURCE.rglob('*.dat'))):
        # Workshop information
        group = file.stem
        group =  group_correct.get(group, group)
        year = int(file.parts[-2])
        if group == "PRIO" and year == 2002:  # wrong name, redundant information
            continue
        with open(file, 'r') as inf:
            lines = inf.readlines()
        meta = {'group': group, 'year': year}
        # Auxiliary variables
        entry = False  # To keep only proper presentations
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
            elif cat in ("AUTHOR", "DISCUSSANT", "LINK", "SESSION"):
                d[cat.lower()] = tokens[1]
            elif cat == "JOINT":
                d["group"] += "; " + tokens[1]
            elif cat == "WITH":
                d["author"] += "; " + tokens[1]
            elif cat == "TIME":
                if not "start" in d:
                    d["start"] = tokens[1]
                # For presentations w/o start, add previous start time
                for t in add_start:
                    by_title[t]["start"] = start
                add_start = []
                start = tokens[1]
            elif cat in _end_categories:
                if not "end" in d:
                    d["end"] = tokens[1]
                # For presentations w/o end, add this end time
                for t in add_end:
                    by_title[t]["end"] = tokens[1]
                add_end = []
            elif (last_line and not end_of_entry) or (cat == "" and entry and end_of_entry):
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
            elif cat:
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
                    if "author" in d:
                        by_group[group][year].append(d)
                        by_year[year][group].append(d)
                        by_title[idx] = d
                    if not "start" in d:
                        add_start.append(idx)
                # Initialize entry
                title = tokens[1]
                d = {"title": title}
                idx += 1
                try:
                    d["start"] = start = start_correct[title]
                except KeyError:
                    pass
                try:
                    d["end"] = end_correct[title]
                except KeyError:
                    pass
                d.update(meta)
                entry = cat == "TITLE"

    # Write out
    for data, label in ((by_year, "by_year"), (by_group, "by_group")):
        with open((TARGET/label).with_suffix('.json'), 'w') as ouf:
            ouf.write(dumps(data, indent=2, sort_keys=True))
    by_title = pd.DataFrame.from_dict(by_title, orient="index")
    by_title["year"] = by_title["year"].astype("uint16")
    order = ['group', 'year', 'date', 'venue', 'organizer', 'title', 'author',
             'discussant', 'session', 'start', 'end', 'link']
    by_title[order].to_csv(TARGET/"by_title.csv", index=False)

    # Overview table
    by_title['group'] = by_title['group'].str.split(";").str[0]
    overview = pd.crosstab(by_title['group'], by_title['year'])
    overview = overview.astype(str).replace("0", "")
    with open("overview.md", "w") as ouf:
        ouf.write(tabulate(overview, tablefmt="pipe", headers="keys"))


if __name__ == '__main__':
    main()
