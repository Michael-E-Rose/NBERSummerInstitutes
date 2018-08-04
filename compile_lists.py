#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Compiles source files to generate two json objects.

One json dump is sorted by year and then group, the other one by group first
and then by year.
"""

import os
from collections import defaultdict
from glob import glob
from json import dumps
from os.path import basename, join, splitext

import pandas as pd

SOURCE = "./source/"
TARGET = "./output/"


def main():
    # Read list of files
    files = list()
    for root, subdirs, filenames in os.walk(SOURCE):
        for filename in filenames:
            if not filename.endswith('dat'):
                continue
            files.append(join(root, filename))

    # Compile each file separately
    by_year = defaultdict(lambda: defaultdict(list))
    by_group = defaultdict(lambda: defaultdict(list))
    df = pd.DataFrame()
    for file in files:
        group = splitext(basename(file))[0]
        year = int(file.split("/")[-2])
        with open(file, 'r') as inf:
            lines = inf.readlines()
        for line in lines:
            tokens = line.strip().split(': ', 1)
            cat = tokens[0]
            if cat == "TITLE":
                title = tokens[1].strip()
                d = {'title': title, 'authors': [], "discussants": []}
            elif cat == "AUTH":
                auth = tokens[1].split(",")[0].replace(".", "")
                d['authors'].append(auth)
            elif cat == "DIS":
                discussants = tokens[1].replace(".", "").split(";")
                try:
                    discussants.remove("-")
                except:
                    pass
                for dis in discussants:
                    dis = dis.split(",")[0].strip()
                    d['discussants'].append(dis)
            elif cat == "":
                # by_group[group][year].append(d)
                # by_year[year][group].append(d)
                d['authors'] = "; ".join(d['authors'])
                d['discussants'] = "; ".join(d['discussants'])
                d.update({'group': group, 'year': year})
                df = df.append(d, ignore_index=True)

    # Write out
    with open(TARGET + 'by_year.json', 'w') as ouf:
        ouf.write(dumps(by_year, indent=2, sort_keys=True))
    with open(TARGET + 'by_group.json', 'w') as ouf:
        dumps(by_group, indent=2, sort_keys=True)
    df['year'] = df['year'].astype(int)
    df.to_csv(TARGET + "by_title.csv")
    overview = pd.crosstab(df['group'], df['year'])
    # Find way to write as markdown


if __name__ == '__main__':
    main()
