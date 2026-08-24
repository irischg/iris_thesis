#!/usr/bin/env python3
"""
11a_audit_pnnl_v2024_workbook.py

Read-only inventory audit for the official PNNL Energy Storage Cost and
Performance Database v2024 workbook.

This script does NOT modify the workbook and does NOT derive thesis parameters.
It only verifies that the local file is a valid XLSX package, inventories
worksheet names, searches cell content for LFP / cost / O&M / scale-duration /
replacement-related evidence, and writes a compact provenance audit.

No third-party Excel package is required; the XLSX Open XML package is read
directly with Python's standard library.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


SCRIPT_VERSION = "v7.1-pnnl-v2024-workbook-inventory-2026-08-17"
OFFICIAL_FILENAME = "ESGC_Cost_Performance_Database_v2024.xlsx"

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    root = project_root()
    p = argparse.ArgumentParser(
        description="Read-only inventory audit of PNNL ESGC v2024 workbook."
    )
    p.add_argument(
        "--workbook",
        type=Path,
        default=(
            root
            / "data"
            / "reference"
            / OFFICIAL_FILENAME
        ),
    )
    p.add_argument(
        "--candidate-rows-output",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "pnnl_v2024_candidate_rows.csv"
        ),
    )
    p.add_argument(
        "--audit-output",
        type=Path,
        default=(
            root
            / "results"
            / "data_audit"
            / "pnnl_v2024_workbook_inventory_audit.txt"
        ),
    )
    return p.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def col_from_ref(cell_ref: str) -> int:
    m = re.match(r"([A-Z]+)", cell_ref or "")
    if not m:
        return 0
    letters = m.group(1)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n


def read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    path = "xl/sharedStrings.xml"
    if path not in zf.namelist():
        return []

    root = ET.fromstring(zf.read(path))
    strings: list[str] = []

    for si in root.findall(f"{{{NS_MAIN}}}si"):
        parts = []
        for t in si.iter(f"{{{NS_MAIN}}}t"):
            parts.append(t.text or "")
        strings.append("".join(parts))
    return strings


def sheet_inventory(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook_xml = "xl/workbook.xml"
    rels_xml = "xl/_rels/workbook.xml.rels"

    if workbook_xml not in zf.namelist():
        raise ValueError("Missing xl/workbook.xml.")
    if rels_xml not in zf.namelist():
        raise ValueError("Missing xl/_rels/workbook.xml.rels.")

    wb_root = ET.fromstring(zf.read(workbook_xml))
    rel_root = ET.fromstring(zf.read(rels_xml))

    rel_map: dict[str, str] = {}
    for rel in rel_root.findall(f"{{{NS_REL_PKG}}}Relationship"):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rid and target:
            if target.startswith("/"):
                normalized = target.lstrip("/")
            else:
                normalized = "xl/" + target.lstrip("/")
            rel_map[rid] = normalized

    result = []
    sheets = wb_root.find(f"{{{NS_MAIN}}}sheets")
    if sheets is None:
        raise ValueError("Workbook has no <sheets> element.")

    for sheet in sheets.findall(f"{{{NS_MAIN}}}sheet"):
        name = sheet.attrib.get("name", "")
        rid = sheet.attrib.get(f"{{{NS_REL_DOC}}}id")
        if not rid or rid not in rel_map:
            raise ValueError(f"Cannot resolve worksheet relationship for {name!r}.")
        result.append((name, rel_map[rid]))

    return result


def cell_text(cell: ET.Element, shared_strings: list[str]) -> str:
    ctype = cell.attrib.get("t", "")
    v = cell.find(f"{{{NS_MAIN}}}v")

    if ctype == "inlineStr":
        is_node = cell.find(f"{{{NS_MAIN}}}is")
        if is_node is None:
            return ""
        return "".join(
            (t.text or "")
            for t in is_node.iter(f"{{{NS_MAIN}}}t")
        )

    raw = "" if v is None or v.text is None else v.text

    if ctype == "s":
        try:
            idx = int(raw)
            return shared_strings[idx]
        except (ValueError, IndexError):
            return raw

    if ctype == "b":
        return "TRUE" if raw == "1" else "FALSE"

    return raw


KEYWORD_GROUPS = {
    "lfp": [
        r"\blfp\b",
        r"lithium[- ]ion",
        r"lithium iron phosphate",
    ],
    "cost": [
        r"\bcost\b",
        r"capital",
        r"capex",
        r"installed",
        r"\$/kw",
        r"\$/kwh",
    ],
    "om": [
        r"\bo&m\b",
        r"operation[s]?\s*(?:and|&)\s*maintenance",
        r"fixed\s*o&m",
        r"maintenance",
    ],
    "scale_duration": [
        r"\bmw\b",
        r"duration",
        r"\bhours?\b",
        r"\bhrs?\b",
    ],
    "replacement": [
        r"replacement",
        r"augmentation",
        r"\barmo\b",
        r"dc storage block",
        r"battery block",
    ],
    "performance": [
        r"efficien",
        r"cycle life",
        r"depth of discharge",
        r"\bdod\b",
    ],
}


def classify_text(text: str) -> list[str]:
    lowered = text.lower()
    groups = []
    for group, patterns in KEYWORD_GROUPS.items():
        if any(re.search(p, lowered, flags=re.I) for p in patterns):
            groups.append(group)
    return groups


def scan_sheet(
    zf: zipfile.ZipFile,
    sheet_name: str,
    sheet_path: str,
    shared_strings: list[str],
) -> tuple[list[dict[str, object]], int]:
    if sheet_path not in zf.namelist():
        raise ValueError(
            f"Worksheet XML for {sheet_name!r} not found: {sheet_path}"
        )

    root = ET.fromstring(zf.read(sheet_path))
    sheet_data = root.find(f"{{{NS_MAIN}}}sheetData")
    if sheet_data is None:
        return [], 0

    candidates: list[dict[str, object]] = []
    nonempty_rows = 0

    for row in sheet_data.findall(f"{{{NS_MAIN}}}row"):
        row_num = int(row.attrib.get("r", "0") or 0)
        cells = []
        for cell in row.findall(f"{{{NS_MAIN}}}c"):
            ref = cell.attrib.get("r", "")
            txt = cell_text(cell, shared_strings).strip()
            if txt:
                cells.append((col_from_ref(ref), ref, txt))

        if not cells:
            continue

        nonempty_rows += 1
        cells.sort(key=lambda x: x[0])
        row_text = " | ".join(f"{ref}={txt}" for _, ref, txt in cells)
        groups = classify_text(row_text)

        if groups:
            candidates.append(
                {
                    "sheet": sheet_name,
                    "row": row_num,
                    "matched_groups": ";".join(groups),
                    "row_text": row_text,
                }
            )

    return candidates, nonempty_rows


def main() -> int:
    args = parse_args()
    print(f"Script version: {SCRIPT_VERSION}")

    try:
        path = args.workbook.resolve()

        if not path.exists():
            raise FileNotFoundError(f"Workbook not found: {path}")
        if not path.is_file():
            raise ValueError(f"Workbook path is not a file: {path}")

        filename_match = path.name == OFFICIAL_FILENAME
        size_bytes = path.stat().st_size
        sha = sha256_file(path)

        if not zipfile.is_zipfile(path):
            raise ValueError(
                "File is not a valid ZIP/XLSX package."
            )

        with zipfile.ZipFile(path, "r") as zf:
            names = set(zf.namelist())
            required_parts = {
                "[Content_Types].xml",
                "xl/workbook.xml",
                "xl/_rels/workbook.xml.rels",
            }
            missing_parts = sorted(required_parts.difference(names))
            if missing_parts:
                raise ValueError(
                    f"XLSX package missing required parts: {missing_parts}"
                )

            shared_strings = read_shared_strings(zf)
            sheets = sheet_inventory(zf)

            all_candidates: list[dict[str, object]] = []
            sheet_rows: dict[str, int] = {}

            for sheet_name, sheet_path in sheets:
                candidates, nrows = scan_sheet(
                    zf,
                    sheet_name,
                    sheet_path,
                    shared_strings,
                )
                all_candidates.extend(candidates)
                sheet_rows[sheet_name] = nrows

        group_counts = defaultdict(int)
        sheets_by_group = defaultdict(set)

        for row in all_candidates:
            for group in str(row["matched_groups"]).split(";"):
                if group:
                    group_counts[group] += 1
                    sheets_by_group[group].add(str(row["sheet"]))

        lfp_found = group_counts["lfp"] > 0
        cost_found = group_counts["cost"] > 0
        om_found = group_counts["om"] > 0
        scale_duration_found = group_counts["scale_duration"] > 0
        performance_found = group_counts["performance"] > 0
        replacement_found = group_counts["replacement"] > 0

        args.candidate_rows_output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        args.audit_output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with args.candidate_rows_output.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "sheet",
                    "row",
                    "matched_groups",
                    "row_text",
                ],
            )
            writer.writeheader()
            writer.writerows(all_candidates)

        lines = [
            "NTUST v7.1 PNNL v2024 Workbook Inventory Audit",
            f"Script version: {SCRIPT_VERSION}",
            "",
            "Local source artifact",
            f"- Workbook: {path}",
            f"- Filename: {path.name}",
            f"- Official filename expected: {OFFICIAL_FILENAME}",
            f"- Exact filename match: {'PASSED' if filename_match else 'WARNING'}",
            f"- Size: {size_bytes:,} bytes",
            f"- SHA-256: {sha}",
            "- Workbook opened as valid XLSX/Open XML package: PASSED",
            "",
            "Worksheet inventory",
            f"- Worksheet count: {len(sheets)}",
        ]

        for idx, (sheet_name, sheet_path) in enumerate(sheets, start=1):
            lines.append(
                f"- [{idx:02d}] {sheet_name} "
                f"(non-empty rows scanned: {sheet_rows.get(sheet_name, 0):,}; "
                f"xml={sheet_path})"
            )

        lines.extend(
            [
                "",
                "Keyword evidence scan",
                f"- LFP / lithium-ion evidence: "
                f"{'FOUND' if lfp_found else 'NOT FOUND'} "
                f"(candidate rows={group_counts['lfp']}; "
                f"sheets={sorted(sheets_by_group['lfp'])})",
                f"- Cost / installed-CAPEX evidence: "
                f"{'FOUND' if cost_found else 'NOT FOUND'} "
                f"(candidate rows={group_counts['cost']}; "
                f"sheets={sorted(sheets_by_group['cost'])})",
                f"- O&M / maintenance evidence: "
                f"{'FOUND' if om_found else 'NOT FOUND'} "
                f"(candidate rows={group_counts['om']}; "
                f"sheets={sorted(sheets_by_group['om'])})",
                f"- Power-scale / duration evidence: "
                f"{'FOUND' if scale_duration_found else 'NOT FOUND'} "
                f"(candidate rows={group_counts['scale_duration']}; "
                f"sheets={sorted(sheets_by_group['scale_duration'])})",
                f"- Performance / efficiency / cycle-life evidence: "
                f"{'FOUND' if performance_found else 'NOT FOUND'} "
                f"(candidate rows={group_counts['performance']}; "
                f"sheets={sorted(sheets_by_group['performance'])})",
                f"- Replacement / augmentation / storage-block evidence: "
                f"{'FOUND' if replacement_found else 'NOT FOUND'} "
                f"(candidate rows={group_counts['replacement']}; "
                f"sheets={sorted(sheets_by_group['replacement'])})",
                "",
                "v7.1 source-suitability gate",
            ]
        )

        core_pass = (
            filename_match
            and lfp_found
            and cost_found
            and om_found
            and scale_duration_found
        )

        if core_pass:
            lines.extend(
                [
                    "- Core PNNL-v2024 source inventory: PASSED",
                    "- Workbook appears suitable for the next detailed "
                    "row/column provenance audit of LFP CAPEX and FOM.",
                ]
            )
        else:
            lines.extend(
                [
                    "- Core PNNL-v2024 source inventory: REVIEW REQUIRED",
                    "- Do NOT derive C_E, C_P, FOM, or C_rep until the "
                    "missing/ambiguous evidence above is reviewed.",
                ]
            )

        lines.extend(
            [
                "",
                "Important scope guardrail",
                "- This script does NOT derive thesis-specific 1 MW / 10 MW "
                "linearization coefficients.",
                "- This script does NOT perform currency normalization.",
                "- This script does NOT populate C_E, C_P, FOM, or C_rep.",
                "- This script does NOT treat legacy 402.50/232.65, "
                "362.17/173.10, or C_rep=5107.57 as mainline inputs.",
                "",
                "Outputs",
                f"- Candidate row inventory: {args.candidate_rows_output.resolve()}",
                f"- Audit summary: {args.audit_output.resolve()}",
                "",
                "Next action",
                "- Review the printed worksheet names and candidate-row evidence.",
                "- If this gate is acceptable, build the detailed PNNL LFP "
                "parameter-extraction script from exact workbook cells.",
            ]
        )

        args.audit_output.write_text(
            "\n".join(lines),
            encoding="utf-8-sig",
        )
        print("\n".join(lines))
        return 0

    except Exception as exc:
        print(f"PNNL workbook audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
