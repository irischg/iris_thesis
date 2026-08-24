#!/usr/bin/env python3
"""
11b_profile_pnnl_v2024_lfp_database.py

NTUST thesis v7.1 — detailed structural/provenance profile of the PNNL v2024
Database worksheet, focused on Lithium-ion LFP.

This is still a READ-ONLY audit:
- no workbook modification;
- no thesis cost linearization;
- no currency conversion;
- no C_E / C_P / FOM / C_rep population.

Outputs are designed to reveal the exact Database schema and the exact LFP
rows/fields that should control the later production extraction script.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path


SCRIPT_VERSION = "v7.1-pnnl-v2024-lfp-profile-2026-08-17"
OFFICIAL_FILENAME = "ESGC_Cost_Performance_Database_v2024.xlsx"

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"

HEADER_TERMS = (
    "technology", "chemistry", "type", "subtype", "year", "power", "mw",
    "duration", "hour", "metric", "parameter", "cost", "value", "unit",
    "o&m", "om", "source", "low", "high", "point", "estimate"
)

LFP_PATTERNS = (
    r"\blfp\b",
    r"lithium iron phosphate",
)

YEAR_PATTERNS = (
    r"\b2023\b",
    r"\b2024\b",
)

CAPEX_PATTERNS = (
    r"capital",
    r"capex",
    r"installed",
    r"total installed",
    r"\$/kw",
    r"\$/kwh",
    r"cost",
)

OM_PATTERNS = (
    r"\bo&m\b",
    r"fixed o&m",
    r"maintenance",
)

REPLACEMENT_PATTERNS = (
    r"replacement",
    r"augmentation",
    r"\barmo\b",
    r"dc storage block",
    r"\bdcsb\b",
)

PERFORMANCE_PATTERNS = (
    r"round trip",
    r"rte",
    r"efficien",
    r"cycle life",
    r"depth of discharge",
    r"\bdod\b",
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    p = argparse.ArgumentParser(
        description="Profile exact PNNL v2024 LFP Database rows and schema."
    )
    p.add_argument(
        "--workbook",
        type=Path,
        default=root / "data" / "reference" / OFFICIAL_FILENAME,
    )
    p.add_argument(
        "--profile-output",
        type=Path,
        default=root / "results" / "data_audit" / "pnnl_v2024_lfp_column_profile.csv",
    )
    p.add_argument(
        "--candidate-output",
        type=Path,
        default=root / "results" / "data_audit" / "pnnl_v2024_lfp_exact_candidates.csv",
    )
    p.add_argument(
        "--audit-output",
        type=Path,
        default=root / "results" / "data_audit" / "pnnl_v2024_lfp_profile_audit.txt",
    )
    return p.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def excel_col_num(ref: str) -> int:
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return 0
    n = 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - ord("A") + 1
    return n


def excel_col_letters(n: int) -> str:
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(ord("A") + rem) + out
    return out


def read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    name = "xl/sharedStrings.xml"
    if name not in zf.namelist():
        return []
    root = ET.fromstring(zf.read(name))
    out = []
    for si in root.findall(f"{{{NS_MAIN}}}si"):
        out.append(
            "".join((t.text or "") for t in si.iter(f"{{{NS_MAIN}}}t"))
        )
    return out


def workbook_sheets(zf: zipfile.ZipFile) -> dict[str, str]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))

    relmap = {}
    for rel in rels.findall(f"{{{NS_REL_PKG}}}Relationship"):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rid and target:
            if target.startswith("/"):
                path = target.lstrip("/")
            else:
                path = "xl/" + target.lstrip("/")
            relmap[rid] = path

    sheets = {}
    node = wb.find(f"{{{NS_MAIN}}}sheets")
    if node is None:
        raise ValueError("Workbook has no sheets node.")

    for sheet in node.findall(f"{{{NS_MAIN}}}sheet"):
        name = sheet.attrib.get("name", "")
        rid = sheet.attrib.get(f"{{{NS_REL_DOC}}}id")
        if rid not in relmap:
            raise ValueError(f"Cannot resolve sheet {name!r}.")
        sheets[name] = relmap[rid]
    return sheets


def cell_value(cell: ET.Element, shared: list[str]) -> str:
    ctype = cell.attrib.get("t", "")
    if ctype == "inlineStr":
        node = cell.find(f"{{{NS_MAIN}}}is")
        if node is None:
            return ""
        return "".join(
            (t.text or "") for t in node.iter(f"{{{NS_MAIN}}}t")
        ).strip()

    v = cell.find(f"{{{NS_MAIN}}}v")
    raw = "" if v is None or v.text is None else v.text.strip()

    if ctype == "s":
        try:
            return shared[int(raw)].strip()
        except (ValueError, IndexError):
            return raw
    if ctype == "b":
        return "TRUE" if raw == "1" else "FALSE"
    return raw


def read_rows(
    zf: zipfile.ZipFile,
    sheet_path: str,
    shared: list[str],
) -> list[tuple[int, dict[int, str]]]:
    root = ET.fromstring(zf.read(sheet_path))
    data = root.find(f"{{{NS_MAIN}}}sheetData")
    if data is None:
        return []

    rows = []
    for row in data.findall(f"{{{NS_MAIN}}}row"):
        row_no = int(row.attrib.get("r", "0") or 0)
        vals = {}
        for cell in row.findall(f"{{{NS_MAIN}}}c"):
            ref = cell.attrib.get("r", "")
            col = excel_col_num(ref)
            txt = cell_value(cell, shared)
            if col and txt != "":
                vals[col] = txt
        if vals:
            rows.append((row_no, vals))
    return rows


def row_text(vals: dict[int, str]) -> str:
    return " | ".join(
        f"{excel_col_letters(c)}={vals[c]}"
        for c in sorted(vals)
    )


def matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(p, text, flags=re.I) for p in patterns)


def detect_header_row(
    rows: list[tuple[int, dict[int, str]]],
) -> tuple[int, dict[int, str], int]:
    best = None
    for row_no, vals in rows[:100]:
        strings = [str(x).strip() for x in vals.values()]
        if len(strings) < 3:
            continue
        lower = " | ".join(strings).lower()
        term_score = sum(1 for term in HEADER_TERMS if term in lower)
        text_score = sum(
            1 for x in strings
            if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", x)
        )
        score = term_score * 100 + text_score
        candidate = (score, -row_no, row_no, vals)
        if best is None or candidate > best:
            best = candidate

    if best is None:
        raise ValueError("Could not identify a plausible Database header row.")

    score, _, row_no, vals = best
    return row_no, vals, score


def normalized_header_map(
    header_vals: dict[int, str],
    max_col: int,
) -> dict[int, str]:
    seen = Counter()
    out = {}

    for col in range(1, max_col + 1):
        raw = header_vals.get(col, "").strip()
        if not raw:
            raw = f"unnamed_{excel_col_letters(col)}"

        clean = re.sub(r"\s+", " ", raw)
        seen[clean] += 1
        if seen[clean] > 1:
            clean = f"{clean} [{excel_col_letters(col)}]"
        out[col] = clean
    return out


def classify_candidate(text: str) -> list[str]:
    flags = []
    if matches_any(text, YEAR_PATTERNS):
        flags.append("year_2023_or_2024")
    if matches_any(text, CAPEX_PATTERNS):
        flags.append("capex_cost")
    if matches_any(text, OM_PATTERNS):
        flags.append("om")
    if matches_any(text, REPLACEMENT_PATTERNS):
        flags.append("replacement_augmentation")
    if matches_any(text, PERFORMANCE_PATTERNS):
        flags.append("performance")
    if re.search(r"(^|[^0-9])1(?:\.0+)?\s*mw\b", text, flags=re.I):
        flags.append("power_1MW_text")
    if re.search(r"(^|[^0-9])10(?:\.0+)?\s*mw\b", text, flags=re.I):
        flags.append("power_10MW_text")
    if re.search(r"\b(?:1|2|4|6|8|10|12)\s*(?:h|hr|hrs|hour|hours)\b", text, flags=re.I):
        flags.append("duration_text")
    return flags


def compact_value_list(counter: Counter, limit: int = 15) -> str:
    if not counter:
        return ""
    parts = []
    for val, count in counter.most_common(limit):
        shown = val.replace("\n", " ").replace("\r", " ")
        if len(shown) > 90:
            shown = shown[:87] + "..."
        parts.append(f"{shown} ({count})")
    return "; ".join(parts)


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        wb_path = args.workbook.resolve()
        if not wb_path.exists():
            raise FileNotFoundError(f"Workbook not found: {wb_path}")
        if not zipfile.is_zipfile(wb_path):
            raise ValueError("Workbook is not a valid XLSX package.")

        sha = sha256_file(wb_path)

        with zipfile.ZipFile(wb_path, "r") as zf:
            shared = read_shared_strings(zf)
            sheets = workbook_sheets(zf)
            if "Database" not in sheets:
                raise ValueError(
                    f"Expected worksheet 'Database'; found {sorted(sheets)}"
                )
            rows = read_rows(zf, sheets["Database"], shared)

        if not rows:
            raise ValueError("Database worksheet has no non-empty rows.")

        max_col = max(max(vals) for _, vals in rows)
        header_row_no, header_vals, header_score = detect_header_row(rows)
        headers = normalized_header_map(header_vals, max_col)

        data_rows = [
            (row_no, vals)
            for row_no, vals in rows
            if row_no > header_row_no
        ]

        lfp_rows = []
        for row_no, vals in data_rows:
            text = row_text(vals)
            if matches_any(text, LFP_PATTERNS):
                lfp_rows.append((row_no, vals, text))

        if not lfp_rows:
            raise ValueError("No LFP rows found below detected header row.")

        # Per-column profile over all LFP rows.
        col_counters = {
            col: Counter()
            for col in range(1, max_col + 1)
        }
        nonempty_counts = Counter()

        for _, vals, _ in lfp_rows:
            for col, value in vals.items():
                if col <= max_col and value != "":
                    col_counters[col][value] += 1
                    nonempty_counts[col] += 1

        profile_rows = []
        for col in range(1, max_col + 1):
            counter = col_counters[col]
            profile_rows.append(
                {
                    "column_letter": excel_col_letters(col),
                    "header": headers[col],
                    "lfp_nonempty_rows": nonempty_counts[col],
                    "lfp_unique_values": len(counter),
                    "top_values": compact_value_list(counter),
                }
            )

        # Exact candidate set: retain LFP rows with cost/O&M/replacement/performance
        # clues, or explicit 2023/2024 / MW / duration evidence.
        candidates = []
        category_counts = Counter()
        for row_no, vals, text in lfp_rows:
            flags = classify_candidate(text)
            if not flags:
                continue
            for flag in flags:
                category_counts[flag] += 1

            rec = {
                "database_row": row_no,
                "candidate_flags": ";".join(flags),
            }
            for col in range(1, max_col + 1):
                rec[f"{excel_col_letters(col)}::{headers[col]}"] = vals.get(col, "")
            candidates.append(rec)

        args.profile_output.parent.mkdir(parents=True, exist_ok=True)
        args.candidate_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)

        with args.profile_output.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "column_letter",
                    "header",
                    "lfp_nonempty_rows",
                    "lfp_unique_values",
                    "top_values",
                ],
            )
            writer.writeheader()
            writer.writerows(profile_rows)

        candidate_fieldnames = ["database_row", "candidate_flags"] + [
            f"{excel_col_letters(col)}::{headers[col]}"
            for col in range(1, max_col + 1)
        ]
        with args.candidate_output.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            writer = csv.DictWriter(f, fieldnames=candidate_fieldnames)
            writer.writeheader()
            writer.writerows(candidates)

        header_display = []
        for col in range(1, max_col + 1):
            if header_vals.get(col, ""):
                header_display.append(
                    f"{excel_col_letters(col)}={header_vals[col]}"
                )

        # Print only informative columns to keep PowerShell output compact.
        informative = [
            r for r in profile_rows
            if r["lfp_nonempty_rows"] > 0
        ]

        lines = [
            "NTUST v7.1 PNNL v2024 LFP Detailed Profile Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Workbook provenance",
            f"- Workbook: {wb_path}",
            f"- SHA-256: {sha}",
            "- Worksheet profiled: Database",
            f"- Non-empty Database rows: {len(rows):,}",
            f"- Maximum populated column index observed: {max_col} ({excel_col_letters(max_col)})",
            "",
            "Detected table structure",
            f"- Detected header row: {header_row_no}",
            f"- Header-detection score: {header_score}",
            "- Header cells:",
        ]
        lines.extend(f"  - {item}" for item in header_display)

        lines.extend([
            "",
            "LFP subset",
            f"- LFP rows below header: {len(lfp_rows):,}",
            f"- Detailed candidate rows retained: {len(candidates):,}",
            "",
            "LFP column profile",
        ])

        for rec in informative:
            top = rec["top_values"]
            if len(top) > 300:
                top = top[:297] + "..."
            lines.append(
                f"- {rec['column_letter']} | {rec['header']} | "
                f"non-empty={rec['lfp_nonempty_rows']:,} | "
                f"unique={rec['lfp_unique_values']:,} | "
                f"top={top}"
            )

        lines.extend([
            "",
            "Candidate evidence counts",
        ])
        for flag in sorted(category_counts):
            lines.append(f"- {flag}: {category_counts[flag]:,}")

        lines.extend([
            "",
            "Outputs",
            f"- LFP column profile: {args.profile_output.resolve()}",
            f"- Exact LFP candidate rows: {args.candidate_output.resolve()}",
            f"- Audit summary: {args.audit_output.resolve()}",
            "",
            "Gate interpretation",
            "- This script identifies exact workbook schema and candidate source rows.",
            "- It does NOT choose final thesis source rows yet.",
            "- It does NOT derive C_E, C_P, FOM, or C_rep.",
            "- It does NOT perform the 1 MW / 10 MW planning linearization.",
            "- Next step is to review this schema/profile and freeze exact source-cell provenance.",
        ])

        args.audit_output.write_text("\n".join(lines), encoding="utf-8-sig")
        print("\n".join(lines))
        return 0

    except Exception as exc:
        print(f"PNNL LFP profile audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
