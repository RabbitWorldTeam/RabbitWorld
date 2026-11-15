#!/usr/bin/env python3
"""Write the changelog section for a Rabbit World release tag."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def release_notes(changelog, version):
    heading = f"## {version}"
    sections = list(re.finditer(r"^## [^\n]+", changelog, re.MULTILINE))
    matching = [index for index, section in enumerate(sections) if section.group().strip() == heading]
    if len(matching) != 1:
        raise ValueError(f"CHANGELOG.md must contain exactly one '{heading}' heading.")
    index = matching[0]
    end = sections[index + 1].start() if index + 1 < len(sections) else len(changelog)
    notes = changelog[sections[index].end():end].strip()
    if not notes:
        raise ValueError(f"CHANGELOG.md has no release notes under '{heading}'.")
    return notes + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if args.tag != f"v{version}":
        raise ValueError(f"Release tag {args.tag!r} does not match manifest version {version!r}.")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    args.output.write_text(release_notes(changelog, version), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
