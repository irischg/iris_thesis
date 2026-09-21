#!/usr/bin/env python3
"""W-18: independent calendar / observed-meter-to-bill validation, no solver.

Gate A is an implementation correction under Framework/Registry v7.2.
This script never imports the calendar generator, Script 06, Script 13c, or
the model. It reads their artifacts and uses a separately transcribed ROC-114
calendar oracle and explicit tariff time bands. All outputs are additive.

Use --capture-baseline BEFORE 06a/06 regeneration; then validate with
--baseline-dir and a fresh --output-dir. No downstream pipeline is invoked.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd


VERSION = "v7.2-w18-gate-a-2026-09-14-r1"
ROOT = Path(__file__).resolve().parents[1]
CALENDAR = ROOT / "data/reference/taipower_tou_day_calendar_case_year_v7_1.csv"
ANNUAL = ROOT / "data/processed/annual_input_v7_1.csv"
PARQUET = ANNUAL.with_suffix(".parquet")
BILLING = ROOT / "data/reference/billing_demand_registry.csv"
BILLS = ROOT / "data/reference/taipower_bills_final_clean.csv"
TARIFF = ROOT / "data/reference/taipower_tariff_registry_v7_1.csv"
FRAMEWORK = ROOT / "docs/research_framework_v7_2_2026-08-24.md"
REGISTRY = ROOT / "docs/thesis_literature_evidence_registry_v7_2_2026-08-24.md"
START = pd.Timestamp("2024-11-01")
END = pd.Timestamp("2025-11-01")
SPECIAL_2025 = frozenset(
    "2025-01-01 2025-01-28 2025-01-29 2025-01-30 2025-01-31 "
    "2025-02-01 2025-02-28 2025-04-04 2025-05-01 2025-05-31 "
    "2025-10-06 2025-10-10 2025-10-25".split()
)
# Independently visually checked against both colored local images in Gate A.
# Red = all-day offpeak; yellow = Saturday; white = weekday.
EVIDENCE = {
    "data/reference/114日歷電價表-1.png":
        "20de25ac27766534f1ffff433525b793b214c0bd8cbaf6a0e9c71e0d87686769",
    "data/reference/114日歷電價表-2.png":
        "16c385c3aed6475e19b2359511c87f2f95f90d25116f7a53160a74cf0ad4c9a7",
}
PERIODS = ("peak", "half", "sat_half", "off")
ENERGY_COLUMNS = {
    "peak": "Energy - Peak (kWh)",
    "half": "Energy - Semi-peak (kWh)",
    "sat_half": "Energy - Sat Semi-peak (kWh)",
    "off": "Energy - Off-peak (kWh)",
    "total": "Energy Total (kWh) - Invoice",
}
TOLERANCES = {
    "role": "PROJECT-EMPIRICAL; not universal Taipower meter tolerances",
    "total_relative_limit": 0.002,
    "bucket_relative_limit": 0.01,
    "bucket_absolute_limit_kwh": 8000.0,
    "small_billed_bucket_kwh": 50000.0,
    "bucket_rule": "absolute AND relative; billed < 50000 uses absolute only",
}
METER_BOUNDARY = "observed_load_kw - observed_pv_kw; dt=1 hour; no clipping"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(path: Path) -> dict:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"path": str(path.resolve()), "sha256": digest.hexdigest(),
            "bytes": path.stat().st_size}


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def write_json(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def evidence_identities() -> list[dict]:
    result = []
    for name, expected in EVIDENCE.items():
        entry = identity(ROOT / name)
        require(entry["sha256"] == expected, f"Official calendar evidence changed: {name}")
        result.append(entry)
    return result


def expected_day(day: pd.Timestamp) -> str:
    """ROC-114 oracle for 2025; informational weekday rule for Nov/Dec 2024."""
    if day.strftime("%Y-%m-%d") in SPECIAL_2025 or day.weekday() == 6:
        return "offpeak_day"
    return "saturday" if day.weekday() == 5 else "weekday"


def expected_period(hour: int, summer: bool, day_type: str) -> str:
    """Independent time-band transcription; does not call Script 06."""
    if day_type == "offpeak_day":
        return "off"
    off_hours = set(range(9)) if summer else {0, 1, 2, 3, 4, 5, 11, 12, 13}
    if hour in off_hours:
        return "off"
    if day_type == "saturday":
        return "sat_half"
    return "peak" if summer and hour in range(16, 22) else "half"


def calendar_audit(calendar: pd.DataFrame, historical: bool = False) -> pd.DataFrame:
    dates = pd.to_datetime(calendar["date"], errors="raise")
    require(pd.DatetimeIndex(dates).equals(pd.date_range(START, END, inclusive="left")),
            "Calendar must cover the exact ordered 365 case-year dates")
    records = []
    for day, actual in zip(dates, calendar["tou_day_type"]):
        expected = expected_day(day)
        if historical and day == pd.Timestamp("2025-02-01"):
            expected = "saturday"
        require(actual == expected, f"Calendar discrepancy: {day.date()}: {actual} != {expected}")
        records.append({"date": day.strftime("%Y-%m-%d"), "project_day_type": actual,
                        "expected_day_type": expected,
                        "scope": "HARD" if day.year == 2025 else "INFORMATIONAL",
                        "special_non_sunday": day.strftime("%Y-%m-%d") in SPECIAL_2025,
                        "status": "PASS" if day.year == 2025 else "INFORMATIONAL"})
    expected_counts = {"weekday": 251, "saturday": 50 if historical else 49,
                       "offpeak_day": 64 if historical else 65}
    require(calendar.tou_day_type.value_counts().to_dict() == expected_counts,
            "Unexpected case-year day counts")
    return pd.DataFrame(records)


def capture_baseline(destination: Path) -> None:
    """Preserve bytes and identities before permitted mutable input regeneration."""
    require(not destination.exists(), "Baseline destination already exists")
    evidence = evidence_identities()
    calendar_audit(pd.read_csv(CALENDAR), historical=True)
    tracked = [ROOT / name for name in git("ls-files").splitlines()]
    protected = set(tracked) - {ROOT / "scripts/06a_build_taipower_tou_calendar.py"}
    # Preserve authority, downstream inputs, and historical solver results by hash.
    for folder in ("data/reference", "data/processed", "results/eob_production",
                   "results/layer_a/final_81/runs/20260911T112258206802Z_4d0eb9e1da",
                   "docs/checkpoints"):
        protected.update(p for p in (ROOT / folder).rglob("*") if p.is_file())
    protected.difference_update({CALENDAR, ANNUAL, PARQUET})
    for name in ("annual_input_v7_1_data_dictionary.csv", "annual_input_v7_1_flagged_intervals.csv",
                 "annual_input_v7_1_integration_audit.txt", "annual_input_v7_1_tou_hour_counts.csv"):
        protected.add(ROOT / "results/data_audit" / name)
    manifest = {
        "version": VERSION, "created_utc": datetime.now(timezone.utc).isoformat(),
        "branch": git("branch", "--show-current"), "head": git("rev-parse", "HEAD"),
        "git_status": git("status", "--porcelain=v1", "--untracked-files=all"),
        "official_calendar_evidence": evidence,
        "protected_identities": [identity(p) for p in sorted(protected)],
        "snapshots": {},
    }
    destination.mkdir(parents=True, exist_ok=False)
    for path in (CALENDAR, ANNUAL, PARQUET, ROOT / "scripts/06a_build_taipower_tou_calendar.py"):
        target = destination / path.name
        shutil.copyfile(path, target)
        entry = identity(path)
        require(identity(target)["sha256"] == entry["sha256"], "Baseline copy hash mismatch")
        entry["snapshot_path"] = str(target.resolve())
        manifest["snapshots"][path.name] = entry
    write_json(destination / "baseline_manifest.json", manifest)
    print(f"Baseline captured: {destination}")
    print(f"Protected files hashed: {len(protected)}")


def verify_baseline(baseline: Path) -> dict:
    manifest = json.loads((baseline / "baseline_manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["snapshots"].values():
        require(identity(Path(entry["snapshot_path"]))["sha256"] == entry["sha256"],
                f"Baseline snapshot changed: {entry['snapshot_path']}")
    for entry in manifest["protected_identities"]:
        require(identity(Path(entry["path"]))["sha256"] == entry["sha256"],
                f"Protected file changed: {entry['path']}")
    require(git("rev-parse", "HEAD") == manifest["head"], "HEAD changed during Gate A")
    require(git("branch", "--show-current") == manifest["branch"], "Branch changed during Gate A")
    return manifest


def invariant_audit(baseline: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    # Compare CSV lexical values exactly, including status/provenance columns.
    old = pd.read_csv(baseline / ANNUAL.name, dtype=str, keep_default_na=False)
    new = pd.read_csv(ANNUAL, dtype=str, keep_default_na=False)
    require(list(old.columns) == list(new.columns) and old.shape == new.shape,
            "Canonical schema/shape changed")
    counts, cells = [], []
    for column in old:
        changed = old[column].ne(new[column])
        counts.append({"column": column, "changed_rows": int(changed.sum())})
        for i in old.index[changed]:
            cells.append({"timestamp": old.at[i, "timestamp"], "column": column,
                          "before": old.at[i, column], "after": new.at[i, column]})
    actual = {r["column"]: r["changed_rows"] for r in counts if r["changed_rows"]}
    require(actual == {"tou_day_type": 24, "tou_period": 15},
            f"Unexpected canonical changes: {actual}; STOP without accepting unrelated changes")
    require(all(r["timestamp"].startswith("2025-02-01 ") for r in cells),
            "Changes outside February 1")
    old_pq, new_pq = pd.read_parquet(baseline / PARQUET.name), pd.read_parquet(PARQUET)
    for column in old_pq:
        if column not in actual:
            pd.testing.assert_series_equal(old_pq[column], new_pq[column], check_exact=True)
    # Round-trip the Parquet through the same CSV representation before comparing
    # text/date/dtype representations; physical values are not rounded here.
    pq_csv = pd.read_csv(io.StringIO(new_pq.to_csv(index=False)), dtype=str, keep_default_na=False)
    pd.testing.assert_frame_equal(new, pq_csv, check_exact=True)
    old_cal = pd.read_csv(baseline / CALENDAR.name, dtype=str, keep_default_na=False)
    new_cal = pd.read_csv(CALENDAR, dtype=str, keep_default_na=False)
    calendar_audit(old_cal, historical=True)
    require(old_cal.shape == new_cal.shape and list(old_cal) == list(new_cal), "Calendar schema changed")
    changes = old_cal.ne(new_cal).any(axis=1)
    require(old_cal.loc[changes, "date"].tolist() == ["2025-02-01"], "Unexpected calendar row changes")
    old_hours = old.tou_period.value_counts().to_dict()
    new_hours = new.tou_period.value_counts().to_dict()
    delta = {p: new_hours.get(p, 0) - old_hours.get(p, 0) for p in PERIODS}
    require(delta == {"peak": 0, "half": 0, "sat_half": -15, "off": 15}, "Unexpected TOU hour delta")
    feb1 = old.timestamp.str.startswith("2025-02-01 ")
    transitions = pd.crosstab(old.loc[feb1, "tou_period"], new.loc[feb1, "tou_period"])
    return pd.DataFrame(counts), pd.DataFrame(cells), {
        "status": "PASS", "all_50_columns_compared_exactly": len(counts) == 50,
        "changed_columns": actual, "unchanged_columns": [r["column"] for r in counts if not r["changed_rows"]],
        "calendar_rows_before": old_cal.loc[changes].to_dict("records"),
        "calendar_rows_after": new_cal.loc[changes].to_dict("records"),
        "day_counts_before": old_cal.tou_day_type.value_counts().to_dict(),
        "day_counts_after": new_cal.tou_day_type.value_counts().to_dict(),
        "tou_hours_before": old_hours, "tou_hours_after": new_hours, "tou_hours_delta": delta,
        "feb1_period_transitions": transitions.to_dict(), "csv_parquet_consistency": "PASS",
        "season_tou_before": old.groupby(["season", "tou_period"]).size().rename("hours").reset_index().to_dict("records"),
        "season_tou_after": new.groupby(["season", "tou_period"]).size().rename("hours").reset_index().to_dict("records"),
    }


def structural_audit(annual: pd.DataFrame, calendar: pd.DataFrame, tariff: pd.DataFrame) -> dict:
    ts = pd.to_datetime(annual.timestamp, errors="raise")
    expected = pd.date_range(START, END, freq="h", inclusive="left")
    require(len(annual) == 8760 and pd.DatetimeIndex(ts).equals(expected), "Not exact consecutive 8760-hour chronology")
    require(ts.duplicated().sum() == 0, "Duplicate hourly intervals")
    require(pd.to_datetime(annual.timestamp_start).equals(ts), "timestamp_start mismatch")
    require((pd.to_datetime(annual.timestamp_raw_end) == ts + pd.Timedelta(hours=1)).all(), "Hour-ending conversion mismatch")
    require(annual.weekday.eq(ts.dt.weekday).all(), "Weekday metadata mismatch")
    require(annual.hour.eq(ts.dt.hour).all(), "Hour metadata mismatch")
    require(pd.to_datetime(annual.date).eq(ts.dt.normalize()).all(), "Date metadata mismatch")
    require(annual.time_index.eq(np.arange(8760)).all(), "time_index mismatch")
    summer = (ts.dt.month * 100 + ts.dt.day).between(516, 1015)
    require(annual.is_summer.eq(summer).all(), "Summer boundary mismatch")
    require(annual.season.eq(np.where(summer, "summer", "non_summer")).all(), "Season mismatch")
    days = calendar.set_index("date").tou_day_type
    require(annual.tou_day_type.eq(ts.dt.strftime("%Y-%m-%d").map(days)).all(), "Hourly/day calendar disagreement")
    expected_tou = [expected_period(t.hour, bool(s), d) for t, s, d in zip(ts, summer, annual.tou_day_type)]
    require(annual.tou_period.eq(expected_tou).all(), "Hourly TOU time-band mismatch")
    require(not (annual.tou_period.eq("peak") & ~summer).any(), "Impossible non-summer peak")
    require(annual.integration_status.eq("passed").all() and annual.tou_calendar_verified.eq(True).all(), "Script 06 integration metadata not passed")
    rates = tariff.loc[tariff.parameter_group.eq("energy_rate")].copy()
    require(not rates.duplicated(["season", "tou_period"]).any(), "Duplicate energy tariff entries")
    na = rates.loc[rates.season.eq("non_summer") & rates.tou_period.eq("peak")]
    require(len(na) == 1 and not bool(na.iloc[0].applicable) and pd.isna(na.iloc[0].value_numeric),
            "Non-summer peak must be inapplicable and N/A, never an applicable zero rate")
    rate_lookup = rates.set_index(["season", "tou_period"])
    for pair in set(zip(annual.season, annual.tou_period)):
        row = rate_lookup.loc[pair]
        require(bool(row.applicable) and np.isfinite(float(row.value_numeric)) and float(row.value_numeric) > 0,
                f"Impossible or nonpositive applicable tariff: {pair}")
    return {"status": "PASS", "rows": len(annual), "first_timestamp": str(ts.iloc[0]),
            "last_timestamp": str(ts.iloc[-1]), "duplicates": 0, "missing_hours": 0,
            "summer_boundary": "May 16 through October 15 inclusive",
            "non_summer_peak": "N/A / absent; inapplicable tariff row has missing rate"}


def observed_meter(annual: pd.DataFrame) -> tuple[pd.Series, dict]:
    columns = ["observed_load_kw", "observed_pv_kw", "baseline_load_kw", "pv_available_kw"]
    require(np.isfinite(annual[columns].to_numpy(dtype=float)).all(), "Nonfinite meter/planning quantities")
    load_different = int(annual.observed_load_kw.ne(annual.baseline_load_kw).sum())
    pv_different = int(annual.observed_pv_kw.ne(annual.pv_available_kw).sum())
    require(load_different > 0 and pv_different > 0, "Observed/planning fields are aliased or reconstruction distinction lost")
    observed = annual.observed_load_kw - annual.observed_pv_kw
    require(np.allclose(observed, annual.observed_net_load_kw, rtol=0, atol=1e-9), "Observed net-load alias mismatch")
    return observed, {"definition": METER_BOUNDARY, "selected_by": "Framework v7.2 section 4.3 / Registry P2; not empirical fit",
                      "observed_vs_planning_load_different_rows": load_different,
                      "observed_vs_planning_pv_different_rows": pv_different,
                      "negative_net_intervals": int(observed.lt(0).sum()), "status": "PASS"}


def residual(calculated: float, billed: float, total: bool = False) -> dict:
    require(np.isfinite(calculated) and np.isfinite(billed) and billed >= 0, "Invalid energy quantity")
    error = calculated - billed
    relative = error / billed if billed else None
    if total:
        require(billed > 0, "Usage-period total denominator must be positive")
        accepted = abs(relative) <= TOLERANCES["total_relative_limit"]
        rule = "relative <= 0.20%"
    else:
        accepted = abs(error) <= TOLERANCES["bucket_absolute_limit_kwh"]
        small = billed < TOLERANCES["small_billed_bucket_kwh"]
        if not small:
            accepted = accepted and abs(relative) <= TOLERANCES["bucket_relative_limit"]
        rule = "absolute <= 8000 kWh" if small else "absolute <= 8000 kWh AND relative <= 1.00%"
    return {"calculated_kwh": float(calculated), "billed_kwh": float(billed),
            "error_kwh": float(error), "relative_error_pct": None if relative is None else float(relative * 100),
            "criterion_pass": bool(accepted), "criterion": rule}


def reconcile(annual: pd.DataFrame, billing: pd.DataFrame, bills: pd.DataFrame) -> pd.DataFrame:
    """Assign by actual half-open billing boundaries, never by bill-title month."""
    ts = pd.to_datetime(annual.timestamp)
    net, _ = observed_meter(annual)
    require(not billing.bill_id_roc.duplicated().any(), "Duplicate billing registry bill IDs")
    require(not bills["Bill ID (ROC)"].duplicated().any(), "Duplicate actual bill IDs")
    bill_lookup = bills.set_index("Bill ID (ROC)")
    coverage = np.zeros(len(annual), dtype=int)
    records, periods = [], []
    for row in billing.itertuples(index=False):
        start, end = pd.Timestamp(row.usage_period_start), pd.Timestamp(row.usage_period_end_exclusive)
        require(end > start, "Empty/reversed billing period")
        if end <= START or start >= END:
            continue
        require(start >= START and end <= END, "Partially covered bill cannot be silently aggregated")
        mask = ts.ge(start) & ts.lt(end)
        coverage += mask.to_numpy(dtype=int)
        require(int(mask.sum()) == (end-start) / pd.Timedelta(hours=1), "Incomplete billing-period coverage")
        require(annual.loc[mask, "billing_usage_period_id"].eq(row.usage_period_id).all(), "Billing usage identity mismatch")
        require(pd.to_datetime(annual.loc[mask, "usage_period_start"]).eq(start).all(), "Usage start metadata mismatch")
        # Existing Script 06 end-label has sub-microsecond serialization residue.
        # Preserve its bytes in Gate A; prove it selects EXACTLY the same hourly
        # rows as the actual registry boundary, which controls aggregation here.
        metadata_end = pd.to_datetime(annual.loc[mask, "usage_period_end_exclusive"]).unique()
        require(len(metadata_end) == 1 and np.array_equal(mask, ts.ge(start) & ts.lt(metadata_end[0])),
                "Canonical end metadata changes hourly usage-period membership")
        require(row.bill_id_roc in bill_lookup.index, "Registry bill absent from actual bill input")
        bill = bill_lookup.loc[row.bill_id_roc]
        require(pd.to_datetime(bill["Period Start"], format="%m/%d/%Y") == start and
                pd.to_datetime(bill["Period End"], format="%m/%d/%Y") + pd.Timedelta(days=1) == end,
                "Actual bill and registry boundaries differ")
        billed_values = {p: float(bill[c]) for p, c in ENERGY_COLUMNS.items()}
        require(sum(billed_values[p] for p in PERIODS) == billed_values["total"], "Bill bucket sum differs from invoice total")
        scope = "HARD" if start.year == 2025 else "INFORMATIONAL"
        periods.append(row.usage_period_id)
        for p in (*PERIODS, "total"):
            selection = mask if p == "total" else mask & annual.tou_period.eq(p)
            applicable = bool(selection.any())
            if not applicable:
                require(billed_values[p] == 0, f"Inapplicable bucket has billed energy: {row.usage_period_id}/{p}")
            detail = residual(float(net.loc[selection].sum()), billed_values[p], total=p == "total")
            status = ("N/A" if not applicable else "INFORMATIONAL" if scope == "INFORMATIONAL"
                      else "PASS" if detail["criterion_pass"] else "FAIL")
            records.append({"usage_period_id": row.usage_period_id, "bill_id_roc": int(row.bill_id_roc),
                            "bill_title_month": row.bill_title_month, "usage_period_start": str(start),
                            "usage_period_end_exclusive": str(end), "tou_period": p, "hours": int(selection.sum()),
                            "scope": scope, "applicable": applicable, **detail, "status": status})
    require(np.all(coverage == 1), "Hours missing or assigned to overlapping billing periods")
    require(sorted(periods) == pd.period_range("2024-11", "2025-10", freq="M").astype(str).tolist(), "Wrong billing usage periods")
    return pd.DataFrame(records)


def hard_pass(table: pd.DataFrame) -> bool:
    return bool(table.loc[table.scope.eq("HARD") & table.applicable, "criterion_pass"].all())


def run_validation(baseline: Path, output: Path) -> int:
    require(not output.exists(), "Output directory exists; use a fresh additive run directory")
    output.mkdir(parents=True, exist_ok=False)
    report = {"script_version": VERSION, "created_utc": datetime.now(timezone.utc).isoformat(),
              "script": identity(Path(__file__)), "meter_boundary": METER_BOUNDARY,
              "tolerances": TOLERANCES, "real_model_creations": 0, "optimization_calls": 0,
              "execution_boundary": "No solver/model imports or downstream script invocations"}
    try:
        before = verify_baseline(baseline)
        report["baseline_manifest"] = identity(baseline / "baseline_manifest.json")
        report["branch"], report["head"] = before["branch"], before["head"]
        report["protected_files_unchanged"] = len(before["protected_identities"])
        report["official_calendar_evidence"] = evidence_identities()
        report["inputs"] = [identity(p) for p in (ANNUAL, PARQUET, CALENDAR, BILLING, BILLS, TARIFF, FRAMEWORK, REGISTRY,
                                                  ROOT / "scripts/06a_build_taipower_tou_calendar.py",
                                                  ROOT / "scripts/06_build_final_annual_input.py")]
        report["before_artifacts"] = before["snapshots"]
        counts, cells, invariant = invariant_audit(baseline)
        counts.to_csv(output / "canonical_column_comparison.csv", index=False)
        cells.to_csv(output / "canonical_changed_cells.csv", index=False)
        report["invariants"] = invariant
        annual, calendar = pd.read_csv(ANNUAL), pd.read_csv(CALENDAR)
        cal = calendar_audit(calendar)
        cal.to_csv(output / "calendar_authority_comparison.csv", index=False)
        report["calendar_2025"] = {"status": "PASS", "hard_dates": int(cal.scope.eq("HARD").sum()),
                                   "special_dates": sorted(SPECIAL_2025), "source_revision": "114/8/26",
                                   "visual_transcription": "Red/yellow/white semantics visually verified against both pinned PNGs"}
        report["calendar_2024"] = {"status": "STRONGLY CORROBORATED / INFORMATIONAL",
                                   "december_25": "weekday", "hard_primary_visual_validation": False,
                                   "reason": "No locally archived and visually verified applicable ROC-113 color calendar; meter/PV limitations also retained"}
        report["structure"] = structural_audit(annual, calendar, pd.read_csv(TARIFF))
        _, report["meter_boundary_proof"] = observed_meter(annual)
        billing, bills = pd.read_csv(BILLING), pd.read_csv(BILLS)
        table = reconcile(annual, billing, bills)
        table.to_csv(output / "usage_period_tou_reconciliation.csv", index=False)
        report["reconciliation"] = json.loads(table.to_json(orient="records"))
        old = annual.copy(deep=True)
        feb1 = pd.to_datetime(old.timestamp).dt.normalize().eq(pd.Timestamp("2025-02-01"))
        old.loc[feb1, "tou_day_type"] = "saturday"
        old.loc[feb1, "tou_period"] = [expected_period(int(h), False, "saturday") for h in old.loc[feb1, "hour"]]
        old_table = reconcile(old, billing, bills)
        old_table.to_csv(output / "historical_w04_counterfactual_reconciliation.csv", index=False)
        old_feb = old_table.loc[old_table.usage_period_id.eq("2025-02")]
        new_feb = table.loc[table.usage_period_id.eq("2025-02")]
        report["historical_w04_counterfactual"] = {
            "construction": "In-memory February 1 Saturday replacement only; values calculated from current observed inputs",
            "historical_energy_result": "PASS" if hard_pass(old_table) else "FAIL",
            "corrected_energy_result": "PASS" if hard_pass(table) else "FAIL",
            "historical_february": json.loads(old_feb.to_json(orient="records")),
            "corrected_february": json.loads(new_feb.to_json(orient="records")),
            "reclassified_kwh": float((annual.observed_load_kw-annual.observed_pv_kw).loc[feb1 & old.tou_period.eq("sat_half")].sum()),
        }
        clean = table.loc[table.scope.eq("HARD") & table.applicable]
        totals = clean.loc[clean.tou_period.eq("total")]
        buckets = clean.loc[clean.tou_period.ne("total")]
        report["maximum_clean_residuals"] = {
            "total_absolute_relative_pct": float(totals.relative_error_pct.abs().max()),
            "total_absolute_error_kwh": float(totals.error_kwh.abs().max()),
            "bucket_absolute_relative_pct": float(buckets.relative_error_pct.abs().max()),
            "bucket_absolute_error_kwh": float(buckets.error_kwh.abs().max()),
        }
        require(not hard_pass(old_table), "W-18 cannot detect historical W-04")
        require(set(old_feb.loc[~old_feb.criterion_pass, "tou_period"]) == {"sat_half", "off"}, "Unexpected historical W-04 signature")
        require(hard_pass(table), "Corrected 2025 HARD reconciliation failed; STOP without changing tolerances")
        report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["outputs"] = [identity(p) for p in sorted(output.iterdir()) if p.is_file()]
    write_json(output / "w18_audit.json", report)
    print(json.dumps({k: report[k] for k in ("status", "script_version", "real_model_creations", "optimization_calls")}, indent=2))
    if report["status"] == "FAIL":
        print(report["error"], file=sys.stderr)
    print(f"Audit: {output / 'w18_audit.json'}")
    return 0 if report["status"] == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-baseline", type=Path)
    parser.add_argument("--baseline-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.capture_baseline:
        require(not args.baseline_dir and not args.output_dir, "Capture and validation are separate phases")
        capture_baseline(args.capture_baseline.resolve())
        return 0
    require(args.baseline_dir is not None and args.output_dir is not None, "Both --baseline-dir and --output-dir are required")
    return run_validation(args.baseline_dir.resolve(), args.output_dir.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
