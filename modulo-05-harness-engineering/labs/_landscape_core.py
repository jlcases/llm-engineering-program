"""Contratos offline para comparar productos del ecosistema de agent harnesses."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

MECHANISM_MODE = "mechanism"
OUTCOME_MODE = "end_to_end_outcome"
COMPOSITION_MODE = "composition"
COMPARISON_MODES = frozenset({MECHANISM_MODE, OUTCOME_MODE, COMPOSITION_MODE})

REQUIRED_OUTCOME_CONTROLS = frozenset(
    {
        "task_fixture",
        "model",
        "model_parameters",
        "starting_state",
        "tool_authority",
        "network_policy",
        "time_budget",
        "token_budget",
    }
)


class CatalogValidationError(ValueError):
    """El catálogo no satisface el contrato auditable."""


class IncomparableHarnessError(ValueError):
    """La pregunta propuesta no permite atribuir causalidad al harness."""


@dataclass(frozen=True)
class HarnessRecord:
    id: str
    name: str
    repository: str
    primary_layer: str
    comparison_cohort: str
    surfaces: tuple[str, ...]
    loop_ownership: str
    interaction_protocol: str
    backend_portability: str
    trust_boundary: str
    verified_facts: tuple[str, ...]
    benchmark_hypotheses: tuple[str, ...]
    primary_sources: tuple[str, ...]
    composes_with: tuple[str, ...] = ()


@dataclass(frozen=True)
class ComparisonPlan:
    left: str
    right: str
    mode: str
    controlled_variables: tuple[str, ...]
    claim_scope: str
    confounders: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "left": self.left,
            "right": self.right,
            "mode": self.mode,
            "controlled_variables": list(self.controlled_variables),
            "claim_scope": self.claim_scope,
            "confounders": list(self.confounders),
        }


class HarnessLandscape:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.schema_version = payload.get("schemaVersion")
        self.reviewed_at = payload.get("reviewedAt")
        self.layers = payload.get("layers")
        raw_harnesses = payload.get("harnesses")
        if not isinstance(raw_harnesses, list):
            raise CatalogValidationError("harnesses must be a list")

        self._records: dict[str, HarnessRecord] = {}
        for index, item in enumerate(raw_harnesses):
            record = self._parse_record(item, index)
            if record.id in self._records:
                raise CatalogValidationError(f"duplicate harness id: {record.id}")
            self._records[record.id] = record
        self._validate()

    @classmethod
    def from_path(cls, path: Path) -> HarnessLandscape:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CatalogValidationError(f"cannot load catalog: {exc}") from exc
        if not isinstance(payload, dict):
            raise CatalogValidationError("catalog root must be an object")
        return cls(payload)

    @property
    def records(self) -> tuple[HarnessRecord, ...]:
        return tuple(self._records.values())

    def get(self, harness_id: str) -> HarnessRecord:
        try:
            return self._records[harness_id]
        except KeyError as exc:
            raise KeyError(f"unknown harness: {harness_id}") from exc

    def compare(
        self,
        left_id: str,
        right_id: str,
        *,
        mode: str,
        controlled_variables: set[str] | frozenset[str] = frozenset(),
    ) -> ComparisonPlan:
        if mode not in COMPARISON_MODES:
            raise ValueError(f"unknown comparison mode: {mode}")
        if left_id == right_id:
            raise IncomparableHarnessError("a comparison needs two different systems")

        left = self.get(left_id)
        right = self.get(right_id)
        controls = frozenset(controlled_variables)

        if mode == MECHANISM_MODE:
            if left.comparison_cohort != right.comparison_cohort:
                raise IncomparableHarnessError(
                    "mechanism comparisons require the same comparison cohort; "
                    f"{left.id}={left.comparison_cohort}, {right.id}={right.comparison_cohort}"
                )
            return ComparisonPlan(
                left=left.id,
                right=right.id,
                mode=mode,
                controlled_variables=tuple(sorted(controls)),
                claim_scope=f"mechanism differences inside {left.comparison_cohort}",
                confounders=(),
            )

        if mode == OUTCOME_MODE:
            missing = REQUIRED_OUTCOME_CONTROLS - controls
            if missing:
                raise IncomparableHarnessError(
                    f"end-to-end comparison is missing controls: {sorted(missing)}"
                )
            confounders = []
            if left.primary_layer != right.primary_layer:
                confounders.append("architectural_layer")
            if set(left.surfaces) != set(right.surfaces):
                confounders.append("interaction_surface")
            if left.interaction_protocol != right.interaction_protocol:
                confounders.append("interaction_protocol")
            return ComparisonPlan(
                left=left.id,
                right=right.id,
                mode=mode,
                controlled_variables=tuple(sorted(controls)),
                claim_scope="end-to-end system outcome; no isolated harness causality",
                confounders=tuple(confounders),
            )

        if right.id in left.composes_with or left.id in right.composes_with:
            return ComparisonPlan(
                left=left.id,
                right=right.id,
                mode=mode,
                controlled_variables=tuple(sorted(controls)),
                claim_scope="composition contract and orchestration overhead",
                confounders=("composed_system",),
            )
        raise IncomparableHarnessError(
            f"the catalog has no verified composition seam between {left.id} and {right.id}"
        )

    def _parse_record(self, item: Any, index: int) -> HarnessRecord:
        if not isinstance(item, dict):
            raise CatalogValidationError(f"harnesses[{index}] must be an object")
        required_strings = (
            "id",
            "name",
            "repository",
            "primaryLayer",
            "comparisonCohort",
            "loopOwnership",
            "interactionProtocol",
            "backendPortability",
            "trustBoundary",
        )
        for field in required_strings:
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise CatalogValidationError(f"harnesses[{index}].{field} must be non-empty")

        def string_tuple(field: str, *, required: bool = True) -> tuple[str, ...]:
            value = item.get(field, [])
            if not isinstance(value, list) or any(not isinstance(entry, str) or not entry for entry in value):
                raise CatalogValidationError(f"harnesses[{index}].{field} must be a string list")
            if required and not value:
                raise CatalogValidationError(f"harnesses[{index}].{field} cannot be empty")
            return tuple(value)

        return HarnessRecord(
            id=item["id"],
            name=item["name"],
            repository=item["repository"],
            primary_layer=item["primaryLayer"],
            comparison_cohort=item["comparisonCohort"],
            surfaces=string_tuple("surfaces"),
            loop_ownership=item["loopOwnership"],
            interaction_protocol=item["interactionProtocol"],
            backend_portability=item["backendPortability"],
            trust_boundary=item["trustBoundary"],
            verified_facts=string_tuple("verifiedFacts"),
            benchmark_hypotheses=string_tuple("benchmarkHypotheses"),
            primary_sources=string_tuple("primarySources"),
            composes_with=string_tuple("composesWith", required=False),
        )

    def _validate(self) -> None:
        if self.schema_version != 1:
            raise CatalogValidationError("schemaVersion must be 1")
        try:
            date.fromisoformat(self.reviewed_at)
        except (TypeError, ValueError) as exc:
            raise CatalogValidationError("reviewedAt must be an ISO date") from exc
        if not isinstance(self.layers, dict) or not self.layers:
            raise CatalogValidationError("layers must be a non-empty object")

        repositories: set[str] = set()
        for record in self.records:
            if record.primary_layer not in self.layers:
                raise CatalogValidationError(
                    f"{record.id}: unknown primary layer {record.primary_layer}"
                )
            self._validate_https_url(record.repository, f"{record.id}.repository")
            if record.repository in repositories:
                raise CatalogValidationError(f"duplicate repository: {record.repository}")
            repositories.add(record.repository)
            if record.primary_sources[0] != record.repository:
                raise CatalogValidationError(
                    f"{record.id}: the repository must be the first primary source"
                )
            for source in record.primary_sources:
                self._validate_https_url(source, f"{record.id}.primarySources")

        known_ids = set(self._records)
        for record in self.records:
            unknown = set(record.composes_with) - known_ids
            if unknown:
                raise CatalogValidationError(
                    f"{record.id}: unknown composition targets {sorted(unknown)}"
                )

        orcas = {record.id for record in self.records if "orca" in record.id}
        expected_orcas = {"orca-stablyai", "orca-virtuslab", "orca-echovic"}
        if not expected_orcas.issubset(orcas):
            raise CatalogValidationError("the three distinct Orca projects must be explicit")

    @staticmethod
    def _validate_https_url(value: str, field: str) -> None:
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise CatalogValidationError(f"{field} must contain HTTPS URLs")
