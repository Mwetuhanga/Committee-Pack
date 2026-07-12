#!/usr/bin/env python3
"""Scaffold the next cycle's data file from the current one.

There is no automated ingestion step by design (see README) — this script
only saves the preparer from re-typing the schema every quarter. It copies
the previous cycle's file forward and blanks out everything that is expected
to change (key information, each report's KPIs/sections, the rotating other
items bucket), while keeping:
  - the five standing report ids/labels/tabled flags in place
  - the `trends` chart definitions, so you only need to append one new point
    per chart rather than rebuild them

Usage:
    python build/new_cycle.py data/pack.yaml data/pack.q3-2026.yaml
"""
import sys
from pathlib import Path

import yaml

HEADER = """\
# ==============================================================================
# Scaffolded by build/new_cycle.py from {source} — fill in the TODOs below.
#
# Kept as-is from last cycle: report ids/labels/tabled flags, trend chart
# definitions (append one new data point per chart for this cycle).
# Cleared for you to re-enter: meeting dates, key information, each report's
# KPIs/sections, and the other_items bucket (policies/procedures/one-off
# items tabled THIS cycle only — last cycle's items do not carry forward).
# ==============================================================================

"""


def scaffold(data: dict) -> dict:
    data["meeting"]["cycle_label"] = "TODO — e.g. Q3 2026"
    data["meeting"]["meeting_date"] = "TODO — YYYY-MM-DD"
    data["key_information"] = []

    for report in data["reports"]:
        report["tabled"] = True
        report["source_file"] = None
        report["strapline"] = "TODO"
        report["kpis"] = []
        report["sections"] = []

    data["other_items"] = []
    # trends left untouched — append a new point to each chart's series by hand,
    # since only the preparer knows this cycle's actual figures.
    return data


def main(src_path: Path, dst_path: Path) -> None:
    with open(src_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    data = scaffold(data)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(HEADER.format(source=src_path))
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=100)

    print(f"Wrote {dst_path}")
    print("Next: fill in the TODOs, add this cycle's key_information / report")
    print("content / other_items, append one point per trends chart, then run:")
    print(f"    python build/generate_pack.py {dst_path} dist/committee-pack.html")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(Path(sys.argv[1]), Path(sys.argv[2]))
