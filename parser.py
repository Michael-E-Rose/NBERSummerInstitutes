#!/usr/bin/env python3
# Author:   Michael E. Rose <michael.ernst.rose@gmail.com>
"""Parses raw html files of NBER Summer Institutes."""

import re
import string
from pathlib import Path

from bs4 import BeautifulSoup

SOURCE_FOLDER = Path("./html/")
TARGET_FOLDER = Path("./source/")
YEAR = "2016"


def clean(s):
    """Clean a string."""
    return s.replace(u'\\xa0', u' ').replace("\\n", " ").strip()


def main():
    timepattern = re.compile(r'^\d+:\d+\s+(am|pm|a\.m\.|p\.m\.)', re.IGNORECASE)

    for filename in sorted(SOURCE_FOLDER.glob(f"{YEAR}*.html")):
        # Read file
        with open(filename, 'rb') as f:
            intext = str(f.read())

        intext = intext.replace('\r', '').replace('\n', ' ').replace("&nbsp;", ' ')

        # Parse
        soup = BeautifulSoup(intext, "lxml")
        for x in soup.find_all():  # remove empty tags
            if len(x.text.strip()) == 0:
                x.extract()

        # Browse main part
        outtext = []
        org = None
        date = None
        venue = None
        start = False
        previous = ""
        for entry in soup.find_all('p'):
            # Extract information
            text = clean(entry.text)
            if text.endswith("Organizer") or text.endswith("Organizers"):
                org = text.rsplit(",", 1)[0].replace(" and ", ", ").split(", ")
            if previous.endswith("Organizer") or previous.endswith("Organizers"):
                venue = text
            if YEAR in text:
                date = text
            if "PROGRAM" in text:
                start = True
            # Combine information
            if start:
                try:
                    link = "LINK: " + entry.find("a")["href"]
                    title = clean("TITLE: " + entry.find("a").text)
                    outtext.append(title)
                    outtext.append(link)
                    outtext.append("")
                except (TypeError, KeyError):
                    text = text.replace("Discussant: ", "DISCUSSANT:")
                    outtext.append(text)
            previous = text

        # Prepare text
        header = [f"DATE: {date or ''}",
                  f"VENUE: {venue or ''}",
                  f"ORGANIZER: {'; '.join(org or [''])}",
                  ""]
        outtext = header + outtext

        # Write out
        ident = filename.stem
        year, group = ident.split('_')
        fname = TARGET_FOLDER/f"{year}/{group}.dat"
        if len(outtext) > 4:  # filter empty files
            with open(fname, 'w') as f:
                for item in outtext:
                    f.write(f"{item}\n".replace("\t", ""))
            print(f">>> {filename} ... successfully saved")
        else:  # file is empty and needs to be done manually
            with open(fname, 'w') as f:
                for item in outtext:
                    f.write(f"{item}\n".replace("\t", ""))
                f.write(clean(soup.text))
            print(f">>> {filename} ... locally saved")


if __name__ == '__main__':
    main()
