#!/usr/bin/env python3
"""
06a_build_taipower_tou_calendar.py

Build the audited Taipower TOU day calendar used by thesis v7.1 Script 06.

Coverage:
    2024-11-01 through 2025-10-31 inclusive

Evidence logic:
1) 2024 case-year slice is only Nov-Dec. The official 2024 TOU off-peak
   holiday list has no special off-peak dates in November or December,
   so classify by weekday:
       Sunday -> offpeak_day
       Saturday -> saturday
       otherwise -> weekday

2) 2025 uses the Taipower 114-year revised TOU calendar marked
   "114/8/26 revised". Special off-peak dates within the case year are
   encoded explicitly below. Sundays remain offpeak_day automatically.

Output:
    data/reference/taipower_tou_day_calendar_case_year_v7_1.csv
"""

from pathlib import Path
from datetime import date, timedelta
import csv

FORMAL_START = date(2024, 11, 1)
FORMAL_END = date(2025, 10, 31)
ALLOWED = {"weekday", "saturday", "offpeak_day"}

SPECIAL_OFFPEAK_2025 = {
    date(2025, 1, 1),
    date(2025, 1, 28),
    date(2025, 1, 29),
    date(2025, 1, 30),
    date(2025, 1, 31),
    date(2025, 2, 28),
    date(2025, 4, 4),
    date(2025, 5, 1),
    date(2025, 5, 31),
    date(2025, 10, 6),
    date(2025, 10, 10),
    date(2025, 10, 25),
}

def project_root() -> Path:
    return Path(__file__).resolve().parents[1]

def classify(d: date) -> tuple[str, str]:
    if d.year == 2024:
        if d.weekday() == 6:
            return "offpeak_day", (
                "113-rule audited: Sunday; no Nov/Dec special off-peak date"
            )
        if d.weekday() == 5:
            return "saturday", (
                "113-rule audited: Saturday; no Nov/Dec special off-peak date"
            )
        return "weekday", (
            "113-rule audited: weekday; no Nov/Dec special off-peak date"
        )

    if d in SPECIAL_OFFPEAK_2025 or d.weekday() == 6:
        if d in SPECIAL_OFFPEAK_2025 and d.weekday() == 5:
            detail = "special holiday overrides Saturday"
        elif d in SPECIAL_OFFPEAK_2025 and d.weekday() != 6:
            detail = "special off-peak holiday"
        else:
            detail = "Sunday"
        return (
            "offpeak_day",
            f"114 revised Taipower TOU calendar (114/8/26 revised): {detail}",
        )

    if d.weekday() == 5:
        return (
            "saturday",
            "114 revised Taipower TOU calendar (114/8/26 revised): Saturday",
        )

    return (
        "weekday",
        "114 revised Taipower TOU calendar (114/8/26 revised): weekday",
    )

def main() -> int:
    out = (
        project_root()
        / "data"
        / "reference"
        / "taipower_tou_day_calendar_case_year_v7_1.csv"
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    d = FORMAL_START
    while d <= FORMAL_END:
        day_type, source_note = classify(d)
        rows.append(
            {
                "date": d.isoformat(),
                "tou_day_type": day_type,
                "source_note": source_note,
            }
        )
        d += timedelta(days=1)

    assert len(rows) == 365
    assert len({r["date"] for r in rows}) == 365
    assert all(r["tou_day_type"] in ALLOWED for r in rows)
    assert rows[0]["date"] == "2024-11-01"
    assert rows[-1]["date"] == "2025-10-31"

    # Explicitly guard the two Saturday holiday overrides that would otherwise
    # be misclassified as sat_half in Script 06.
    lookup = {r["date"]: r["tou_day_type"] for r in rows}
    assert lookup["2025-05-31"] == "offpeak_day"
    assert lookup["2025-10-25"] == "offpeak_day"

    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["date", "tou_day_type", "source_note"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Taipower TOU calendar built.")
    print(f"- Output: {out}")
    print(f"- Rows: {len(rows)}")
    print("- Coverage: 2024-11-01 through 2025-10-31")
    print("- Audit guardrails: PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
