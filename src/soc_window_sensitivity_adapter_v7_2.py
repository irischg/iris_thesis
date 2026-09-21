"""Additive SOC-window adapter for the accepted v7.2 R10 annual core.

This module deliberately does not import or mutate
``src.annual_design_model_v7_2``.  A future authorized runner may load the
hash-pinned R10 source into a private module namespace and configure that
isolated instance for the 20--80 percent SOC sensitivity.  The accepted R10
module object, source bytes, and mainline 10--90 behavior remain untouched.

No model is built and no solver method is called by importing this module.
"""

from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Sequence


ADAPTER_VERSION = "v7.2-soc2080-isolated-r10-adapter-candidate-2026-09-21-r1"
LINEAGE_ID = "SENS-SOC2080-R10"
PARENT_LINEAGE_ID = "MAINLINE-CORRECTED-R10"
CANONICAL_MODULE_NAME = "src.annual_design_model_v7_2"
EXPECTED_R10_CORE_VERSION = (
    "v7.2-annual-design-core-transition-candidate1-exact-d-preflight-2026-09-16-r10"
)
EXPECTED_R10_CORE_SHA256 = "9d828321814b09141497056d1bb17da8b2839c5eb151fce8530059fb7e193da8"
TECHNICAL_BREAKPOINTS = (0.0, 0.30, 0.60, 0.80)
TECHNICAL_SEGMENT_WIDTHS = (0.30, 0.30, 0.20)
FLOAT_TOL = 1e-12


class SocWindowAdapterError(RuntimeError):
    """Fail-closed error raised by the isolated SOC-window adapter."""


@dataclass(frozen=True)
class SocWindowSpec:
    """Immutable physical SOC-window contract."""

    soc_min: float
    soc_max: float
    usable_fraction: float
    lineage_id: str = LINEAGE_ID
    parent_lineage_id: str = PARENT_LINEAGE_ID

    def __post_init__(self) -> None:
        values = (self.soc_min, self.soc_max, self.usable_fraction)
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("SOC-window values must be finite.")
        if not 0.0 <= float(self.soc_min) < float(self.soc_max) <= 1.0:
            raise ValueError("SOC window must satisfy 0 <= soc_min < soc_max <= 1.")
        derived = float(self.soc_max) - float(self.soc_min)
        if not math.isclose(
            float(self.usable_fraction), derived, rel_tol=0.0, abs_tol=FLOAT_TOL
        ):
            raise ValueError(
                "usable_fraction must equal soc_max - soc_min; "
                f"configured={self.usable_fraction}, derived={derived}."
            )
        if not self.lineage_id or not self.parent_lineage_id:
            raise ValueError("Sensitivity and parent lineage identifiers are required.")

    def metadata(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "technical_degradation_breakpoints": list(TECHNICAL_BREAKPOINTS),
            "technical_segment_widths": list(TECHNICAL_SEGMENT_WIDTHS),
            "active_segment_widths": list(
                derive_active_segment_widths(
                    TECHNICAL_BREAKPOINTS, self.usable_fraction
                )
            ),
        }


SOC2080_SPEC = SocWindowSpec(soc_min=0.20, soc_max=0.80, usable_fraction=0.60)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _float_sequence_matches(
    actual: Sequence[float],
    expected: Sequence[float],
    abs_tol: float = FLOAT_TOL,
) -> bool:
    """Strict element-wise float comparison for derived provenance sequences.

    Accepted R10 derives ``SEGMENT_WIDTHS`` by subtracting successive
    ``BREAKPOINTS``, so ``0.80 - 0.60`` is ``0.20000000000000007`` rather than
    the literal ``0.20``.  That representation difference (about 5.6e-17) is not
    a provenance change, but a materially different width still must be
    rejected.  Lengths must match, every value must be finite and numeric, and
    each pair must agree to ``abs_tol``.
    """

    if len(actual) != len(expected):
        return False
    for left, right in zip(actual, expected):
        if isinstance(left, bool) or isinstance(right, bool):
            return False
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return False
        if not math.isfinite(float(left)) or not math.isfinite(float(right)):
            return False
        if not math.isclose(
            float(left), float(right), rel_tol=0.0, abs_tol=float(abs_tol)
        ):
            return False
    return True


def derive_active_segment_widths(
    breakpoints: Sequence[float], usable_fraction: float
) -> tuple[float, ...]:
    """Intersect technical depth intervals with the active usable domain."""

    points = tuple(float(value) for value in breakpoints)
    active_limit = float(usable_fraction)
    if len(points) < 2:
        raise ValueError("At least two technical breakpoints are required.")
    if not all(math.isfinite(value) for value in (*points, active_limit)):
        raise ValueError("Breakpoints and usable fraction must be finite.")
    if points[0] != 0.0 or any(b <= a for a, b in zip(points, points[1:])):
        raise ValueError("Technical breakpoints must start at zero and increase strictly.")
    if not 0.0 < active_limit <= points[-1] + FLOAT_TOL:
        raise ValueError("Usable fraction must lie inside the technical depth domain.")

    widths = tuple(
        max(0.0, min(upper, active_limit) - lower)
        for lower, upper in zip(points, points[1:])
    )
    if not math.isclose(sum(widths), active_limit, rel_tol=0.0, abs_tol=FLOAT_TOL):
        raise ValueError("Active segment widths do not reconcile to usable fraction.")
    return widths


def required_nameplate_energy_kwh(
    reserve_kwh_battery: float, spec: SocWindowSpec = SOC2080_SPEC
) -> float:
    reserve = float(reserve_kwh_battery)
    if not math.isfinite(reserve) or reserve < 0.0:
        raise ValueError("Reserve must be finite and non-negative.")
    return reserve / float(spec.usable_fraction)


def physical_energy_kwh(
    nameplate_energy_kwh: float,
    shifted_energy_kwh: float,
    spec: SocWindowSpec = SOC2080_SPEC,
) -> float:
    nameplate = float(nameplate_energy_kwh)
    shifted = float(shifted_energy_kwh)
    if not math.isfinite(nameplate) or nameplate < 0.0:
        raise ValueError("Nameplate energy must be finite and non-negative.")
    if not math.isfinite(shifted) or shifted < -FLOAT_TOL:
        raise ValueError("Shifted energy must be finite and non-negative.")
    maximum = float(spec.usable_fraction) * nameplate
    if shifted > maximum + FLOAT_TOL:
        raise ValueError("Shifted energy exceeds the configured usable SOC window.")
    return float(spec.soc_min) * nameplate + shifted


def _canonical_snapshot() -> tuple[ModuleType, dict[str, Any]] | None:
    canonical = sys.modules.get(CANONICAL_MODULE_NAME)
    if canonical is None:
        return None
    return canonical, {
        name: getattr(canonical, name, None)
        for name in (
            "CORE_VERSION",
            "SOC_MIN",
            "SOC_MAX",
            "BREAKPOINTS",
            "SEGMENT_WIDTHS",
            "N_SEGMENTS",
            "build_eob_model",
            "solve_eob",
        )
    }


def _assert_canonical_unchanged(
    snapshot: tuple[ModuleType, dict[str, Any]] | None,
) -> None:
    if snapshot is None:
        if CANONICAL_MODULE_NAME in sys.modules:
            raise SocWindowAdapterError(
                "The adapter unexpectedly imported the canonical R10 module."
            )
        return
    module_before, values_before = snapshot
    if sys.modules.get(CANONICAL_MODULE_NAME) is not module_before:
        raise SocWindowAdapterError("Canonical R10 module identity changed.")
    for name, value in values_before.items():
        if getattr(module_before, name, None) is not value and getattr(
            module_before, name, None
        ) != value:
            raise SocWindowAdapterError(f"Canonical R10 global changed: {name}")


@dataclass(frozen=True)
class IsolatedSocCore:
    """Configured private R10 module plus its explicit sensitivity contract."""

    module: ModuleType
    spec: SocWindowSpec
    core_path: Path
    core_sha256: str
    technical_breakpoints: tuple[float, ...]
    technical_segment_widths: tuple[float, ...]
    active_segment_widths: tuple[float, ...]
    inactive_segment_indices: tuple[int, ...]

    def metadata(self) -> dict[str, Any]:
        return {
            "adapter_version": ADAPTER_VERSION,
            "lineage_id": self.spec.lineage_id,
            "parent_lineage_id": self.spec.parent_lineage_id,
            "configured_soc_min": self.spec.soc_min,
            "configured_soc_max": self.spec.soc_max,
            "usable_fraction": self.spec.usable_fraction,
            "technical_degradation_breakpoints": list(self.technical_breakpoints),
            "technical_segment_widths": list(self.technical_segment_widths),
            "active_segment_widths": list(self.active_segment_widths),
            "inactive_segment_indices_zero_based": list(self.inactive_segment_indices),
            "inactive_segment_state_and_flows_forced_zero": True,
            "canonical_core_module_mutated": False,
            "r10_core_version": EXPECTED_R10_CORE_VERSION,
            "r10_core_sha256": self.core_sha256,
        }


def load_isolated_r10_soc_core(
    root: Path,
    spec: SocWindowSpec = SOC2080_SPEC,
) -> IsolatedSocCore:
    """Load and configure R10 privately; this function does not build a model.

    The returned module's ``build_eob_model`` is wrapped so every future model,
    including EOB, receives explicit zero constraints on state, charge flow and
    discharge flow for each inactive segment.  Production use is restricted to
    binary mode, matching the accepted solver contract.
    """

    root = Path(root).resolve()
    core_path = root / "src" / "annual_design_model_v7_2.py"
    actual_sha = sha256_file(core_path)
    if actual_sha != EXPECTED_R10_CORE_SHA256:
        raise SocWindowAdapterError(
            "Accepted R10 core hash mismatch; isolated sensitivity load refused."
        )

    active_widths = derive_active_segment_widths(
        TECHNICAL_BREAKPOINTS, spec.usable_fraction
    )
    inactive = tuple(
        index for index, width in enumerate(active_widths) if width <= FLOAT_TOL
    )
    if not _float_sequence_matches(active_widths, (0.30, 0.30, 0.0)) or inactive != (2,):
        raise SocWindowAdapterError(
            "SOC2080 active-domain derivation is not the audited (.30,.30,0) contract."
        )

    canonical_before = _canonical_snapshot()
    private_name = f"_iris_soc2080_r10_private_{uuid.uuid4().hex}"
    module_spec = importlib.util.spec_from_file_location(private_name, core_path)
    if module_spec is None or module_spec.loader is None:
        raise SocWindowAdapterError(f"Cannot create isolated R10 module for {core_path}.")
    isolated = importlib.util.module_from_spec(module_spec)
    sys.modules[private_name] = isolated
    try:
        module_spec.loader.exec_module(isolated)
        if isolated.CORE_VERSION != EXPECTED_R10_CORE_VERSION:
            raise SocWindowAdapterError("Isolated core version is not accepted R10.")
        if not _float_sequence_matches(
            tuple(isolated.BREAKPOINTS), TECHNICAL_BREAKPOINTS
        ):
            raise SocWindowAdapterError("R10 degradation breakpoints changed.")
        if not _float_sequence_matches(
            tuple(isolated.SEGMENT_WIDTHS), TECHNICAL_SEGMENT_WIDTHS
        ):
            raise SocWindowAdapterError("R10 technical segment widths changed.")
        if int(isolated.N_SEGMENTS) != len(TECHNICAL_SEGMENT_WIDTHS):
            raise SocWindowAdapterError("R10 segment count changed.")

        original_builder: Callable[..., tuple[Any, dict[str, Any]]] = (
            isolated.build_eob_model
        )
        isolated.SOC_MIN = float(spec.soc_min)
        isolated.SOC_MAX = float(spec.soc_max)
        isolated.SEGMENT_WIDTHS = tuple(active_widths)
        isolated.N_SEGMENTS = len(active_widths)

        def build_soc2080_model(
            inputs: Any,
            settings: Any,
            layer_a_requirements: Any | None = None,
        ) -> tuple[Any, dict[str, Any]]:
            if str(settings.mode).strip().lower() != "binary":
                raise SocWindowAdapterError(
                    "SOC2080 production construction requires the accepted binary mode."
                )
            model, handles = original_builder(inputs, settings, layer_a_requirements)
            state_count = len(inputs.annual) + 1
            interval_count = len(inputs.annual)
            for segment_index in inactive:
                for t in range(state_count):
                    model.addConstr(
                        handles["e_seg"][t, segment_index] == 0.0,
                        name=f"soc2080_inactive_state_t{t}_k{segment_index + 1}",
                    )
                for t in range(interval_count):
                    model.addConstr(
                        handles["p_ch_seg"][t, segment_index] == 0.0,
                        name=f"soc2080_inactive_charge_t{t}_k{segment_index + 1}",
                    )
                    model.addConstr(
                        handles["p_dis_seg"][t, segment_index] == 0.0,
                        name=f"soc2080_inactive_discharge_t{t}_k{segment_index + 1}",
                    )
            for t in range(state_count):
                model.addConstr(
                    isolated.gp.quicksum(
                        handles["e_seg"][t, k] for k in range(isolated.N_SEGMENTS)
                    )
                    <= float(spec.usable_fraction) * handles["E_N"],
                    name=f"soc2080_aggregate_shifted_cap_t{t}",
                )
            handles["soc_window_spec"] = spec.metadata()
            handles["technical_segment_widths"] = TECHNICAL_SEGMENT_WIDTHS
            handles["active_segment_widths"] = active_widths
            handles["inactive_segment_indices"] = inactive
            handles["finite_design_bounds"].update(
                {
                    "configured_soc_min": float(spec.soc_min),
                    "configured_soc_max": float(spec.soc_max),
                    "usable_fraction": float(spec.usable_fraction),
                    "technical_segment_widths": list(TECHNICAL_SEGMENT_WIDTHS),
                    "active_segment_widths": list(active_widths),
                    "inactive_segment_state_and_flows_forced_zero": True,
                }
            )
            return model, handles

        build_soc2080_model.__name__ = "build_soc2080_model"
        build_soc2080_model.__doc__ = (
            "Build the isolated R10 model with the explicit SOC2080 active domain."
        )
        isolated.build_eob_model = build_soc2080_model
        isolated.SOC_WINDOW_SPEC = spec
        isolated.TECHNICAL_BREAKPOINTS = TECHNICAL_BREAKPOINTS
        isolated.TECHNICAL_SEGMENT_WIDTHS = TECHNICAL_SEGMENT_WIDTHS
        isolated.ACTIVE_SEGMENT_WIDTHS = active_widths
        isolated.INACTIVE_SEGMENT_INDICES = inactive
        _assert_canonical_unchanged(canonical_before)
    except Exception:
        sys.modules.pop(private_name, None)
        raise

    return IsolatedSocCore(
        module=isolated,
        spec=spec,
        core_path=core_path,
        core_sha256=actual_sha,
        technical_breakpoints=TECHNICAL_BREAKPOINTS,
        technical_segment_widths=TECHNICAL_SEGMENT_WIDTHS,
        active_segment_widths=active_widths,
        inactive_segment_indices=inactive,
    )
