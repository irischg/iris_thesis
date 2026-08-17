#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NTUST v7.1 operating-calendar builder

Purpose
-------
Convert the official NTUST 113/114 academic-calendar XLSX files into one
canonical daily operating calendar for the thesis case year:

    2024-11-01 through 2025-10-31 (365 calendar days)

The output is intended to be merged by Script 06.  It is deliberately kept
separate from Taipower TOU classification: this file describes NTUST campus
work/class status, not electricity-tariff day type.

Default source files
--------------------
    data/raw/ntust_113_calender.xlsx
    data/raw/ntust_114_calender.xlsx

The historical filename spelling "calender" is retained because it matches the
project source filenames.  The script validates the workbook title itself, so a
113/114 file swap is detected and rejected.

Outputs
-------
    data/reference/ntust_operating_calendar_case_year_v7_1.csv
    results/data_audit/ntust_calendar_event_registry_v7_1.csv
    results/data_audit/ntust_operating_calendar_case_year_v7_1_audit.txt

Dependency policy
-----------------
Uses only the Python standard library.  No openpyxl/pandas dependency is needed.
"""

from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.etree import ElementTree as ET


SCRIPT_VERSION = "v7.1-ntust-operating-calendar-2026-08-17"
CASE_START = dt.date(2024, 11, 1)
CASE_END = dt.date(2025, 10, 31)
EXPECTED_CASE_DAYS = (CASE_END - CASE_START).days + 1

DEFAULT_113 = Path("data/raw/ntust_113_calender.xlsx")
DEFAULT_114 = Path("data/raw/ntust_114_calender.xlsx")
DEFAULT_OUTPUT = Path("data/reference/ntust_operating_calendar_case_year_v7_1.csv")
DEFAULT_EVENT_AUDIT = Path("results/data_audit/ntust_calendar_event_registry_v7_1.csv")
DEFAULT_AUDIT = Path("results/data_audit/ntust_operating_calendar_case_year_v7_1_audit.txt")

WEEKDAY_NAME = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ZH_WEEKDAY_TO_PY = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6}
SUNDAY_FIRST_COLS = list(range(2, 9))  # C:I in the source sheet


@dataclass(frozen=True)
class ParsedEvent:
    date: dt.date
    event: str
    source_academic_year: int
    source_file: str
    source_sheet: str
    source_row: int
    inference_distance_rows: int


# ---------------------------------------------------------------------------
# Minimal XLSX reader (standard library only)
# ---------------------------------------------------------------------------

def _local_name(tag: str) -> str:
    return tag.split("}")[-1]


def _column_index(cell_ref: str) -> int:
    letters = re.match(r"([A-Z]+)", cell_ref)
    if not letters:
        raise ValueError(f"Invalid Excel cell reference: {cell_ref}")
    value = 0
    for ch in letters.group(1):
        value = value * 26 + (ord(ch) - ord("A") + 1)
    return value - 1


def _read_shared_strings(zf: zipfile.ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    strings: List[str] = []
    for si in root:
        if _local_name(si.tag) != "si":
            continue
        texts: List[str] = []
        for node in si.iter():
            if _local_name(node.tag) == "t" and node.text is not None:
                texts.append(node.text)
        strings.append("".join(texts))
    return strings


def _workbook_sheet_target(zf: zipfile.ZipFile) -> Tuple[str, str]:
    workbook_root = ET.fromstring(zf.read("xl/workbook.xml"))
    rel_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_map: Dict[str, str] = {}
    for rel in rel_root:
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rid and target:
            rel_map[rid] = target

    for node in workbook_root.iter():
        if _local_name(node.tag) != "sheet":
            continue
        sheet_name = node.attrib.get("name", "Sheet1")
        rid = None
        for key, value in node.attrib.items():
            if key.endswith("}id") or key == "r:id":
                rid = value
                break
        if not rid or rid not in rel_map:
            continue
        target = rel_map[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        return sheet_name, target
    raise ValueError("Could not resolve the first worksheet in workbook.xml")


def read_xlsx_matrix(path: Path, max_cols: int = 13) -> Tuple[str, List[List[object]]]:
    """Read first worksheet values into a rectangular matrix."""
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path, "r") as zf:
        shared = _read_shared_strings(zf)
        sheet_name, target = _workbook_sheet_target(zf)
        root = ET.fromstring(zf.read(target))

        cell_values: Dict[Tuple[int, int], object] = {}
        max_row = 0

        for cell in root.iter():
            if _local_name(cell.tag) != "c":
                continue
            ref = cell.attrib.get("r")
            if not ref:
                continue
            row_match = re.search(r"(\d+)$", ref)
            if not row_match:
                continue
            row_idx = int(row_match.group(1)) - 1
            col_idx = _column_index(ref)
            if col_idx >= max_cols:
                continue

            cell_type = cell.attrib.get("t")
            value: object = None

            if cell_type == "inlineStr":
                texts = []
                for node in cell.iter():
                    if _local_name(node.tag) == "t" and node.text is not None:
                        texts.append(node.text)
                value = "".join(texts)
            else:
                v_node = None
                for child in cell:
                    if _local_name(child.tag) == "v":
                        v_node = child
                        break
                if v_node is not None and v_node.text is not None:
                    raw = v_node.text
                    if cell_type == "s":
                        value = shared[int(raw)]
                    elif cell_type == "b":
                        value = raw == "1"
                    elif cell_type in ("str", "e"):
                        value = raw
                    else:
                        try:
                            number = float(raw)
                            value = int(number) if number.is_integer() else number
                        except ValueError:
                            value = raw

            cell_values[(row_idx, col_idx)] = value
            max_row = max(max_row, row_idx + 1)

    matrix: List[List[object]] = []
    for r in range(max_row):
        matrix.append([cell_values.get((r, c)) for c in range(max_cols)])
    return sheet_name, matrix


# ---------------------------------------------------------------------------
# NTUST calendar parsing
# ---------------------------------------------------------------------------

def _normalize_text(value: object) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def _numeric_day(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int) and 1 <= value <= 31:
        return value
    if isinstance(value, float) and value.is_integer() and 1 <= int(value) <= 31:
        return int(value)
    return 0


def _grid_vector(row: Sequence[object]) -> List[int]:
    return [_numeric_day(row[c] if c < len(row) else None) for c in SUNDAY_FIRST_COLS]


def _expected_month_weeks(start_gregorian_year: int) -> List[Tuple[int, int, List[int]]]:
    cal = calendar.Calendar(firstweekday=6)  # Sunday first, matching the NTUST sheet
    output: List[Tuple[int, int, List[int]]] = []
    for offset in range(12):
        month = ((8 - 1 + offset) % 12) + 1
        year = start_gregorian_year if month >= 8 else start_gregorian_year + 1
        for week in cal.monthdayscalendar(year, month):
            output.append((year, month, week))
    return output


def build_grid_date_row_map(matrix: Sequence[Sequence[object]], start_year: int) -> Dict[dt.date, int]:
    """Map every date shown in the Aug-Jul calendar grid to its worksheet row."""
    expected = _expected_month_weeks(start_year)
    expected_idx = 0
    date_to_row: Dict[dt.date, int] = {}

    for row_number, row in enumerate(matrix, start=1):
        vector = _grid_vector(row)
        if not any(vector):
            continue

        found: Optional[int] = None
        for j in range(expected_idx, min(len(expected), expected_idx + 6)):
            if vector == expected[j][2]:
                found = j
                break
        if found is None:
            # Non-calendar rows sometimes contain isolated integers; ignore them.
            continue

        year, month, week = expected[found]
        expected_idx = found + 1
        for day in week:
            if day:
                date_to_row[dt.date(year, month, day)] = row_number

    expected_dates = {
        dt.date(start_year, 8, 1) + dt.timedelta(days=i)
        for i in range((dt.date(start_year + 1, 7, 31) - dt.date(start_year, 8, 1)).days + 1)
    }
    if set(date_to_row) != expected_dates:
        missing = sorted(expected_dates - set(date_to_row))
        extra = sorted(set(date_to_row) - expected_dates)
        raise ValueError(
            "Calendar-grid parsing did not reconstruct the complete academic year. "
            f"Missing={missing[:10]}, Extra={extra[:10]}"
        )
    return date_to_row


def _weekday_code(value: object) -> Optional[int]:
    text = _normalize_text(value)
    if not text:
        return None
    first = text[0]
    return ZH_WEEKDAY_TO_PY.get(first)


def validate_workbook_identity(path: Path, matrix: Sequence[Sequence[object]], expected_ay: int) -> None:
    top_text = " ".join(_normalize_text(v) for row in matrix[:4] for v in row if v is not None)
    pattern = rf"{expected_ay}\s*學年度行事曆"
    if not re.search(pattern, top_text):
        raise ValueError(
            f"{path} does not identify itself as NTUST academic year {expected_ay}. "
            "Check whether the 113/114 source files were swapped."
        )


def parse_events(
    matrix: Sequence[Sequence[object]],
    *,
    academic_year: int,
    source_file: Path,
    source_sheet: str,
) -> List[ParsedEvent]:
    start_year = academic_year + 1911  # ROC academic year 113 -> Gregorian 2024
    date_to_grid_row = build_grid_date_row_map(matrix, start_year)
    all_dates = sorted(date_to_grid_row)

    events: List[ParsedEvent] = []
    for row_number, row in enumerate(matrix, start=1):
        event = _normalize_text(row[12] if len(row) > 12 else None)
        day = _numeric_day(row[10] if len(row) > 10 else None)
        weekday = _weekday_code(row[11] if len(row) > 11 else None)
        if not event or not day or weekday is None:
            continue

        candidates = [d for d in all_dates if d.day == day and d.weekday() == weekday]
        if not candidates:
            raise ValueError(
                f"Could not infer date for event at {source_file}:{row_number}: {event}"
            )
        best = min(candidates, key=lambda d: abs(date_to_grid_row[d] - row_number))
        distance = abs(date_to_grid_row[best] - row_number)
        if distance > 6:
            raise ValueError(
                f"Low-confidence date inference at {source_file}:{row_number}. "
                f"Best date={best}, distance={distance}, event={event}"
            )

        events.append(
            ParsedEvent(
                date=best,
                event=event,
                source_academic_year=academic_year,
                source_file=source_file.name,
                source_sheet=source_sheet,
                source_row=row_number,
                inference_distance_rows=distance,
            )
        )

    if not events:
        raise ValueError(f"No dated events parsed from {source_file}")
    return events


# ---------------------------------------------------------------------------
# Operating / class-day logic
# ---------------------------------------------------------------------------

def _events_on(events: Sequence[ParsedEvent]) -> Dict[dt.date, List[ParsedEvent]]:
    grouped: Dict[dt.date, List[ParsedEvent]] = {}
    for ev in events:
        grouped.setdefault(ev.date, []).append(ev)
    return grouped


def _event_contains(event_texts: Iterable[str], *patterns: str) -> bool:
    joined = " | ".join(event_texts)
    return any(p in joined for p in patterns)


def _find_single_event_date(events: Sequence[ParsedEvent], academic_year: int, phrase: str, occurrence: int = 1) -> dt.date:
    matches = [e.date for e in events if e.source_academic_year == academic_year and phrase in e.event]
    matches = sorted(dict.fromkeys(matches))
    if len(matches) < occurrence:
        raise ValueError(f"Could not find occurrence {occurrence} of '{phrase}' in AY{academic_year}")
    return matches[occurrence - 1]


def _build_instruction_intervals(events: Sequence[ParsedEvent]) -> List[Tuple[dt.date, dt.date, str]]:
    """Build formal teaching/activity intervals from 上課開始 to the next break start."""
    intervals: List[Tuple[dt.date, dt.date, str]] = []
    for ay in sorted({e.source_academic_year for e in events}):
        starts = sorted({e.date for e in events if e.source_academic_year == ay and "上課開始" in e.event and "暑期上課開始" not in e.event})
        winter = sorted({e.date for e in events if e.source_academic_year == ay and "寒假開始" in e.event})
        summer = sorted({e.date for e in events if e.source_academic_year == ay and "暑假開始" in e.event})
        ends = sorted(winter + summer)
        for idx, start in enumerate(starts, start=1):
            later_ends = [x for x in ends if x > start]
            if not later_ends:
                raise ValueError(f"No break-start boundary found after class start {start} in AY{ay}")
            end = min(later_ends) - dt.timedelta(days=1)
            intervals.append((start, end, f"AY{ay}_semester_{idx}"))
    return intervals


def _in_instruction_interval(day: dt.date, intervals: Sequence[Tuple[dt.date, dt.date, str]]) -> Tuple[bool, str]:
    for start, end, label in intervals:
        if start <= day <= end:
            return True, label
    return False, "outside_instruction_period"


def _spring_festival_ranges(events: Sequence[ParsedEvent]) -> List[Tuple[dt.date, dt.date]]:
    ranges = []
    for ay in sorted({e.source_academic_year for e in events}):
        starts = sorted({e.date for e in events if e.source_academic_year == ay and "農曆春節開始" in e.event})
        ends = sorted({e.date for e in events if e.source_academic_year == ay and "農曆春節結束" in e.event})
        for start in starts:
            later = [x for x in ends if x >= start]
            if later:
                ranges.append((start, min(later)))
    return ranges


def _date_in_ranges(day: dt.date, ranges: Sequence[Tuple[dt.date, dt.date]]) -> bool:
    return any(start <= day <= end for start, end in ranges)


def _academic_year_for_date(day: dt.date) -> int:
    # Academic year N starts on Aug 1 of Gregorian N+1911.
    return day.year - 1911 if day.month >= 8 else day.year - 1912


def build_case_calendar(events: Sequence[ParsedEvent]) -> List[Dict[str, object]]:
    grouped = _events_on(events)
    instruction_intervals = _build_instruction_intervals(events)
    spring_ranges = _spring_festival_ranges(events)

    rows: List[Dict[str, object]] = []
    day = CASE_START
    while day <= CASE_END:
        day_events = grouped.get(day, [])
        event_texts = [e.event for e in day_events]
        event_text = " | ".join(event_texts)
        weekend = day.weekday() >= 5
        in_instruction, semester_label = _in_instruction_interval(day, instruction_intervals)

        holiday_event_texts = [
            text for text in event_texts
            if not text.startswith("補上班") and "全天上班" not in text
        ]
        explicit_full_holiday = (
            _event_contains(holiday_event_texts, "放假一天", "補假一天", "調整放假", "遇例假日補假")
            or _date_in_ranges(day, spring_ranges)
        )
        # "適用勞基法人員放假" is not a full-campus closure.
        partial_staff_holiday = _event_contains(event_texts, "適用勞基法人員放假")
        if partial_staff_holiday and "放假一天" not in event_text:
            explicit_full_holiday = False

        explicit_work_override = (
            any(text.startswith("補上班") or "全天上班" in text for text in event_texts)
            and not explicit_full_holiday
        )
        explicit_no_class = _event_contains(event_texts, "停課一天") or explicit_full_holiday

        # Work status: ordinary Mon-Fri are workdays; weekends are not, unless an
        # explicit makeup/special workday is stated by NTUST. Full holidays override.
        is_workday = int(not weekend)
        work_status = "regular_workday" if is_workday else "weekend_nonworkday"

        if explicit_full_holiday:
            is_workday = 0
            work_status = "full_holiday"
        if explicit_work_override:
            is_workday = 1
            work_status = "makeup_or_special_workday"
        if partial_staff_holiday:
            is_workday = 1
            work_status = "partial_staff_holiday"

        # Class status: regular academic activity is assumed on Mon-Fri within
        # the formal teaching interval. Explicit holidays / stop-class events override.
        is_class_day = int(in_instruction and not weekend)
        class_status = "regular_class_day" if is_class_day else (
            "weekend_no_regular_class" if weekend else "outside_instruction_period"
        )
        if explicit_full_holiday:
            is_class_day = 0
            class_status = "holiday_no_class"
        if explicit_no_class:
            is_class_day = 0
            class_status = "explicit_no_class"
        # A weekend special workday remains no-class unless NTUST explicitly says otherwise.

        if work_status == "full_holiday":
            day_type = "holiday_no_work_no_class"
        elif work_status == "partial_staff_holiday":
            day_type = "partial_staff_holiday"
        elif explicit_work_override and not is_class_day:
            day_type = "special_work_no_class"
        elif is_workday and is_class_day:
            day_type = "regular_work_class_day"
        elif is_workday and not is_class_day:
            day_type = "regular_work_no_class_day"
        else:
            day_type = "weekend_no_work_no_regular_class"

        source_ay = _academic_year_for_date(day)
        ay_source_files = sorted({e.source_file for e in events if e.source_academic_year == source_ay})
        source_files = ay_source_files
        source_rows = sorted({e.source_row for e in day_events})

        rows.append(
            {
                "date": day.isoformat(),
                "weekday": WEEKDAY_NAME[day.weekday()],
                "is_weekend": int(weekend),
                "ntust_academic_year": source_ay,
                "ntust_semester_period": semester_label,
                "ntust_day_type": day_type,
                "is_ntust_workday": is_workday,
                "is_ntust_class_day": is_class_day,
                "ntust_work_status": work_status,
                "ntust_class_status": class_status,
                "ntust_partial_staff_holiday": int(partial_staff_holiday),
                "ntust_calendar_event": event_text,
                "source_file": ";".join(source_files),
                "source_rows": ";".join(str(x) for x in source_rows),
            }
        )
        day += dt.timedelta(days=1)

    return rows


# ---------------------------------------------------------------------------
# Audit / output
# ---------------------------------------------------------------------------

def _assert_case_calendar(rows: Sequence[Dict[str, object]]) -> None:
    if len(rows) != EXPECTED_CASE_DAYS:
        raise AssertionError(f"Expected {EXPECTED_CASE_DAYS} rows, got {len(rows)}")
    dates = [dt.date.fromisoformat(str(r["date"])) for r in rows]
    if len(set(dates)) != len(dates):
        raise AssertionError("Duplicate dates in NTUST operating calendar")
    expected = [CASE_START + dt.timedelta(days=i) for i in range(EXPECTED_CASE_DAYS)]
    if dates != expected:
        raise AssertionError("Case-year dates are not exactly consecutive 2024-11-01..2025-10-31")

    # High-value semantic guardrails from the official NTUST calendar.
    lookup = {str(r["date"]): r for r in rows}
    guards = {
        "2025-01-27": (0, 0, "adjusted holiday"),
        "2025-02-08": (1, 0, "makeup workday"),
        "2025-03-03": (0, 0, "anniversary-sports makeup holiday"),
        "2025-03-22": (1, 0, "anniversary sports day: work, no class"),
        "2025-09-29": (0, 0, "Teachers' Day substitute holiday"),
        "2025-10-24": (0, 0, "Retrocession Day substitute holiday"),
    }
    for date_s, (work, klass, label) in guards.items():
        row = lookup[date_s]
        if int(row["is_ntust_workday"]) != work or int(row["is_ntust_class_day"]) != klass:
            raise AssertionError(f"Semantic guard failed for {date_s} ({label}): {row}")


def write_csv(path: Path, rows: Sequence[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_event_registry(path: Path, events: Sequence[ParsedEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "date",
        "event",
        "source_academic_year",
        "source_file",
        "source_sheet",
        "source_row",
        "inference_distance_rows",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for e in sorted(events, key=lambda x: (x.date, x.source_academic_year, x.source_row)):
            writer.writerow(
                {
                    "date": e.date.isoformat(),
                    "event": e.event,
                    "source_academic_year": e.source_academic_year,
                    "source_file": e.source_file,
                    "source_sheet": e.source_sheet,
                    "source_row": e.source_row,
                    "inference_distance_rows": e.inference_distance_rows,
                }
            )


def build_audit_text(
    rows: Sequence[Dict[str, object]],
    events: Sequence[ParsedEvent],
    source_113: Path,
    source_114: Path,
) -> str:
    by_type: Dict[str, int] = {}
    workdays = 0
    classdays = 0
    partial = 0
    for row in rows:
        day_type = str(row["ntust_day_type"])
        by_type[day_type] = by_type.get(day_type, 0) + 1
        workdays += int(row["is_ntust_workday"])
        classdays += int(row["is_ntust_class_day"])
        partial += int(row["ntust_partial_staff_holiday"])

    explicit_event_days = len({e.date for e in events if CASE_START <= e.date <= CASE_END})
    max_inference_distance = max(e.inference_distance_rows for e in events)

    type_lines = "\n".join(f"  - {k}: {v}" for k, v in sorted(by_type.items()))
    return f"""NTUST v7.1 Operating Calendar Audit
====================================
Script version: {SCRIPT_VERSION}

Sources
- AY113: {source_113}
- AY114: {source_114}
- Workbook-title identity checks: PASSED

Case-year coverage
- Start: {CASE_START}
- End: {CASE_END}
- Rows: {len(rows)}
- Expected rows: {EXPECTED_CASE_DAYS}
- Consecutive daily chronology: PASSED
- Duplicate dates: 0

Parsed official calendar events
- Total dated events parsed from AY113 + AY114: {len(events)}
- Explicit event dates inside case year: {explicit_event_days}
- Maximum event-date inference distance from matching calendar-grid row: {max_inference_distance} rows

Operating summary
- NTUST workdays: {workdays}
- NTUST class/activity weekdays: {classdays}
- Partial-staff-holiday days: {partial}
- Day-type counts:
{type_lines}

Semantic guardrails
- 2025-01-27: adjusted holiday -> no work / no class
- 2025-02-08: makeup workday -> work / no regular class (before class start)
- 2025-03-03: anniversary-sports makeup holiday -> no work / no class
- 2025-03-22: campus sports day -> work / explicitly no class
- 2025-09-29: Teachers' Day substitute holiday -> no work / no class
- 2025-10-24: Retrocession Day substitute holiday -> no work / no class
- Semantic guardrail checks: PASSED

Interpretation boundary
- This registry describes NTUST campus operating / academic status.
- It MUST NOT be used as the source of Taipower TOU day classification.
- Taipower tariff tags remain a separate Script-06 input/regeneration layer.
- Winter/summer break means no regular class, not automatic staff closure.
- 'Labor Day (applicable to Labor Standards Act personnel)' is retained as partial_staff_holiday,
  not treated as a full-campus closure.

Output status
- Canonical NTUST operating calendar: PASSED
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build canonical NTUST v7.1 operating calendar")
    parser.add_argument("--calendar-113", type=Path, default=DEFAULT_113)
    parser.add_argument("--calendar-114", type=Path, default=DEFAULT_114)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--event-audit", type=Path, default=DEFAULT_EVENT_AUDIT)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("NTUST v7.1 Operating Calendar Builder")
    print(f"Script version: {SCRIPT_VERSION}\n")

    sheet_113, matrix_113 = read_xlsx_matrix(args.calendar_113)
    sheet_114, matrix_114 = read_xlsx_matrix(args.calendar_114)

    validate_workbook_identity(args.calendar_113, matrix_113, 113)
    validate_workbook_identity(args.calendar_114, matrix_114, 114)
    print("Source identity")
    print(f"- AY113: {args.calendar_113} [sheet={sheet_113}] -> PASS")
    print(f"- AY114: {args.calendar_114} [sheet={sheet_114}] -> PASS")

    events_113 = parse_events(
        matrix_113,
        academic_year=113,
        source_file=args.calendar_113,
        source_sheet=sheet_113,
    )
    events_114 = parse_events(
        matrix_114,
        academic_year=114,
        source_file=args.calendar_114,
        source_sheet=sheet_114,
    )
    events = events_113 + events_114

    rows = build_case_calendar(events)
    _assert_case_calendar(rows)

    fieldnames = [
        "date",
        "weekday",
        "is_weekend",
        "ntust_academic_year",
        "ntust_semester_period",
        "ntust_day_type",
        "is_ntust_workday",
        "is_ntust_class_day",
        "ntust_work_status",
        "ntust_class_status",
        "ntust_partial_staff_holiday",
        "ntust_calendar_event",
        "source_file",
        "source_rows",
    ]
    write_csv(args.output, rows, fieldnames)
    write_event_registry(args.event_audit, events)

    audit_text = build_audit_text(rows, events, args.calendar_113, args.calendar_114)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.audit.write_text(audit_text, encoding="utf-8")

    counts: Dict[str, int] = {}
    for row in rows:
        counts[str(row["ntust_day_type"])] = counts.get(str(row["ntust_day_type"]), 0) + 1

    print("\nCase-year integration")
    print(f"- Coverage: {CASE_START} through {CASE_END}")
    print(f"- Daily rows: {len(rows)}")
    print("- Chronology / duplicate / semantic guards: PASS")
    print("\nDay-type counts")
    for key in sorted(counts):
        print(f"- {key}: {counts[key]}")

    print("\nOutputs")
    print(f"- Canonical calendar: {args.output}")
    print(f"- Parsed-event audit: {args.event_audit}")
    print(f"- Audit summary: {args.audit}")
    print("\nScript 05c completed. Script 06 may merge the canonical NTUST operating calendar by date.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
