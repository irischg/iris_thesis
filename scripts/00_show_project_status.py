#!/usr/bin/env python3
"""
NTUST Thesis Progress Snapshot
------------------------------
Stateless repository scanner for Iris thesis.

Purpose
- Read the CURRENT repository state only.
- Do NOT save or update any tracker/history file.
- Print a compact evidence snapshot that can be pasted into ChatGPT for interpretation.

Usage (from repo root):
    python scripts/00_show_project_status.py

The script intentionally does NOT assign a final thesis-completion percentage.
It reports observable evidence; ChatGPT can interpret phase, progress, schedule variance,
critical path, and forecast from the snapshot.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Iterable


# ---------- configuration kept deliberately lightweight ----------

SCRIPT_PREFIXES = (
    "00_", "01_", "02_", "03_", "04_", "05_", "06_", "07_", "08_", "09_",
    "10_", "11_", "12_", "13_", "14_", "15_", "16_", "17_", "18_", "19_",
    "20_", "21_", "22_", "23_", "24_", "25_", "26_", "27_", "28_", "29_",
)

KEY_TERMS = {
    "annual_input": ("annual_input", "final_annual", "8760"),
    "billing": ("bill", "billing", "kappa", "tariff"),
    "pnnl_cost": ("pnnl", "cost", "replacement"),
    "degradation": ("degrad", "xu", "pwl", "rainflow"),
    "eob": ("eob", "economic_only", "economic-only"),
    "layer_a": ("layer_a", "layer-a", "response_surface", "alpha_beta"),
    "layer_b": ("layer_b", "layer-b", "stress_test", "fixed_design"),
    "dg": ("diesel", "dg_", "generator", "coverage_sweep"),
}

PASS_WORDS = (
    "PASS",
    "CLOSED",
    "SUCCESS",
)

FAIL_WORDS = (
    "FAIL",
    "FAILED",
    "ERROR",
    "BLOCKED",
)


def repo_root() -> Path:
    """Find repo root from this file, current working directory, or parent folders."""
    candidates = []

    try:
        candidates.append(Path(__file__).resolve().parent.parent)
    except NameError:
        pass

    candidates.append(Path.cwd().resolve())

    seen = set()
    for start in candidates:
        for p in (start, *start.parents):
            if p in seen:
                continue
            seen.add(p)
            if (p / ".git").exists():
                return p

    # fallback: script parent-parent or cwd
    if candidates:
        return candidates[0]
    return Path.cwd().resolve()


ROOT = repo_root()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def human_time(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def version_key(name: str):
    """
    Extract numeric version tuple and date if present.
    Examples:
      v7_2 -> (7,2)
      v7.2 -> (7,2)
      2026-08-24 used as tiebreaker
    """
    lower = name.lower()
    m = re.search(r'v(\d+)(?:[._](\d+))?(?:[._](\d+))?', lower)
    ver = tuple(int(x) if x is not None else 0 for x in (m.groups() if m else ("0","0","0")))
    d = re.search(r'(20\d{2})[-_](\d{2})[-_](\d{2})', lower)
    date = tuple(map(int, d.groups())) if d else (0,0,0)
    return (*ver, *date, lower)


def latest_matching(patterns: Iterable[str]) -> Path | None:
    hits = []
    for pattern in patterns:
        hits.extend(ROOT.glob(pattern))
    hits = [p for p in hits if p.is_file()]
    if not hits:
        return None
    return sorted(hits, key=lambda p: version_key(p.name), reverse=True)[0]


def list_scripts():
    scripts_dir = ROOT / "scripts"
    if not scripts_dir.exists():
        return []

    scripts = []
    for p in scripts_dir.glob("*.py"):
        if p.name.startswith(SCRIPT_PREFIXES):
            scripts.append(p)

    def sort_key(p: Path):
        m = re.match(r'(\d+)([a-z]?)_', p.name.lower())
        if not m:
            return (999, "", p.name)
        return (int(m.group(1)), m.group(2), p.name)

    return sorted(scripts, key=sort_key)


def text_files_under(base_dirs: Iterable[Path]):
    exts = {".txt", ".md", ".json", ".csv", ".log"}
    for base in base_dirs:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                yield p


def safe_tail_text(path: Path, max_bytes: int = 300_000) -> str:
    """Read tail-ish text without choking on large artifacts."""
    try:
        size = path.stat().st_size
        with path.open("rb") as f:
            if size > max_bytes:
                f.seek(-max_bytes, 2)
            data = f.read()
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def status_from_text(text: str) -> tuple[str, list[str]]:
    upper = text.upper()
    found_pass = [w for w in PASS_WORDS if w in upper]
    found_fail = [w for w in FAIL_WORDS if w in upper]

    if found_fail and not found_pass:
        return "CHECK", found_fail
    if found_pass and not found_fail:
        return "PASS-SIGNAL", found_pass
    if found_pass and found_fail:
        return "MIXED", sorted(set(found_pass + found_fail))
    return "NO-SIGNAL", []


def artifact_signals():
    bases = [
        ROOT / "results",
        ROOT / "data" / "processed",
        ROOT / "data" / "reference",
    ]
    items = []

    for p in text_files_under(bases):
        lname = p.name.lower()
        categories = []
        for cat, terms in KEY_TERMS.items():
            if any(t in lname for t in terms):
                categories.append(cat)

        if not categories:
            continue

        txt = safe_tail_text(p)
        status, words = status_from_text(txt)
        items.append({
            "path": p,
            "mtime": p.stat().st_mtime,
            "categories": categories,
            "status": status,
            "words": words,
        })

    return sorted(items, key=lambda x: x["mtime"], reverse=True)


def latest_activity_files(limit: int = 15):
    bases = [
        ROOT / "scripts",
        ROOT / "results",
        ROOT / "data" / "processed",
        ROOT / "data" / "reference",
    ]
    files = []
    for base in bases:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                try:
                    files.append((p.stat().st_mtime, p))
                except OSError:
                    pass
    files.sort(reverse=True, key=lambda x: x[0])
    return files[:limit]


def git_info():
    """Use git CLI if available; fail quietly."""
    import subprocess

    out = {}
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(ROOT), "branch", "--show-current"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        out["branch"] = branch or "(detached)"
    except Exception:
        out["branch"] = "unavailable"

    try:
        commit = subprocess.check_output(
            ["git", "-C", str(ROOT), "log", "-1", "--pretty=%h %ad %s", "--date=short"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        out["commit"] = commit or "none"
    except Exception:
        out["commit"] = "unavailable"

    try:
        porcelain = subprocess.check_output(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            text=True, stderr=subprocess.DEVNULL
        ).splitlines()
        out["dirty_count"] = len(porcelain)
    except Exception:
        out["dirty_count"] = None

    return out


def script_stage_summary(scripts: list[Path]) -> str:
    if not scripts:
        return "No numbered thesis scripts detected."

    parsed = []
    for p in scripts:
        m = re.match(r'(\d+)([a-z]?)_', p.name.lower())
        if m:
            parsed.append((int(m.group(1)), m.group(2), p.name))

    if not parsed:
        return "Numbered scripts detected, but prefixes could not be parsed."

    latest = max(parsed, key=lambda x: (x[0], x[1]))
    return f"Highest detected script prefix: {latest[0]}{latest[1]}  ({latest[2]})"


def print_bar(label: str, present: bool):
    mark = "YES" if present else "no"
    print(f"  {label:<22} {mark}")


def main():
    framework = latest_matching((
        "research_framework_v*.md",
        "**/research_framework_v*.md",
    ))
    registry = latest_matching((
        "thesis_literature_evidence_registry_v*.md",
        "**/thesis_literature_evidence_registry_v*.md",
    ))

    scripts = list_scripts()
    signals = artifact_signals()
    git = git_info()

    print("=" * 72)
    print("NTUST THESIS — LIVE PROGRESS SNAPSHOT")
    print("=" * 72)
    print(f"Repo root       : {ROOT}")
    print(f"Generated at    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Git branch      : {git['branch']}")
    print(f"Latest commit   : {git['commit']}")
    if git["dirty_count"] is None:
        print("Uncommitted     : unavailable")
    else:
        print(f"Uncommitted     : {git['dirty_count']} file(s)")
    print()

    print("[1] CURRENT SOURCE-OF-TRUTH SIGNALS")
    print(f"Framework       : {rel(framework) if framework else 'NOT FOUND'}")
    print(f"Registry        : {rel(registry) if registry else 'NOT FOUND'}")
    print()

    print("[2] SCRIPT PIPELINE")
    print(script_stage_summary(scripts))
    print(f"Detected scripts: {len(scripts)}")
    for p in scripts[-12:]:
        print(f"  - {p.name}")
    print()

    print("[3] KEY RESEARCH-STAGE SIGNALS")
    for cat in KEY_TERMS:
        present = any(cat in x["categories"] for x in signals)
        print_bar(cat, present)
    print()

    print("[4] RECENT MATCHING AUDIT / RESULT SIGNALS")
    if not signals:
        print("  No matching result/audit artifacts found.")
    else:
        for x in signals[:20]:
            flag = x["status"]
            cats = ",".join(x["categories"])
            words = f" [{','.join(x['words'])}]" if x["words"] else ""
            print(
                f"  {human_time(x['mtime'])} | {flag:<11} | {cats:<28} | "
                f"{rel(x['path'])}{words}"
            )
    print()

    print("[5] MOST RECENT REPOSITORY ACTIVITY")
    recent = latest_activity_files()
    if not recent:
        print("  No activity files found.")
    else:
        for ts, p in recent:
            print(f"  {human_time(ts)} | {rel(p)}")
    print()

    print("[6] HANDOFF TO CHATGPT")
    print("Paste this entire output and say:")
    print('  "Update my thesis progress: determine current Phase, progress bars,')
    print('   ahead/on-track/behind status, critical path, next gate, and revised')
    print('   experiment / thesis / PPT / defense-ready forecast."')
    print()
    print("NOTE:")
    print("- This scanner is STATELESS: it writes no tracker/history files.")
    print("- PASS-SIGNAL means matching text was detected; it is not a substitute")
    print("  for research interpretation.")
    print("- The final phase/progress judgment should be made from the evidence,")
    print("  current framework/registry, and the latest conversation context.")
    print("=" * 72)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
