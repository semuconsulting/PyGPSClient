"""
translate_po.py

Simple script to add machine translations to messages.po localisation files.

Edit the messages.po.txt output file as required and then rename to messages.po.

The messages.po text file must then be compiled via the pybabel CLI utility
to create the final messages.mo runtime binary file.

See https://github.com/semuconsulting/PyGPSClient/blob/main/CONTRIBUTING.md#localisation
for further instructions.

May provide a reasonable 'first pass' but will invariably require refinement.
Pay particular attention to:
- Strings containing Python braces {}.
- Strings containing abbreviations/truncations, acronyms and GNSS jargon.
- Noun/verb transpositions.

*** Apologies to native speakers - better contributions welcome! ***

Usage:

python3 translate_po.py infile="locales/fr/LC_MESSAGES/messages.po"

***************************************************************************
NB: excessive use is likely to result in a "Too many requests" error and/or
possible IP ban by the translation provider !!!
***************************************************************************

Created by semuadmin on 16 Nov 2026. My hovercraft is full of eels.
"""

from sys import argv
from time import sleep

from translate import Translator  # python3 -m pip install translate

DELAY = 0.01


def convert(translator: Translator, msg: str) -> str:
    """
    Translate string.
    """

    if translator is None:
        return msg
    return translator.translate(msg)


def getstring(line: str) -> str:
    """
    Extract string from line.
    """

    return line.split('"')[1]


def main(**kwargs):
    """
    Main routine.
    """

    infile = kwargs.get("infile", "messages.po")
    provider = kwargs.get("provider", "mymemory")
    secret = kwargs.get("secret", "")
    outfile = infile + ".txt"
    translator = None
    count = 0
    locale = ""
    source = ""
    dest = ""
    status = ""

    with open(outfile, "w", encoding="utf-8") as fileout:
        with open(infile, "r", encoding="utf-8") as filein:
            for line in filein:
                ln = line
                if line[0:11] == '"Language: ':
                    locale = line[11:13]
                    translator = Translator(
                        from_lang="en", to_lang=locale, provider=provider, secret=secret
                    )  # nosec
                elif line[0:7] == 'msgid "':
                    status = "from"
                elif line[0:8] == 'msgstr "':
                    status = "to"
                if status == "from":
                    source += getstring(line)
                elif status == "to":
                    dest = convert(translator, source)
                    print(source, dest)
                    ln = f'msgstr "{dest}"\n'
                    source = ""
                    status = ""
                fileout.write(ln)
                fileout.flush()
                count += 1
                sleep(DELAY)

    print(f" {locale=} - {count} lines written to {outfile}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
