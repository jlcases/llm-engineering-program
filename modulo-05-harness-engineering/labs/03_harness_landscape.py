"""Lab 03 — Diseña comparaciones válidas entre harnesses actuales.

Ejecución:
    python modulo-05-harness-engineering/labs/03_harness_landscape.py --list
    python modulo-05-harness-engineering/labs/03_harness_landscape.py \
      --compare pi opencode --mode mechanism
    python modulo-05-harness-engineering/labs/03_harness_landscape.py \
      --compare orca-stablyai pi --mode composition
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _landscape_core import COMPARISON_MODES, HarnessLandscape, IncomparableHarnessError

CATALOG_PATH = Path(__file__).with_name("data") / "harness_landscape.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List the audited systems by layer.")
    parser.add_argument("--compare", nargs=2, metavar=("LEFT", "RIGHT"))
    parser.add_argument("--mode", choices=sorted(COMPARISON_MODES), default="mechanism")
    parser.add_argument(
        "--control",
        action="append",
        default=[],
        help="Record one controlled variable. Repeat this option as needed.",
    )
    return parser


def list_records(landscape: HarnessLandscape) -> list[dict[str, object]]:
    return [
        {
            "id": record.id,
            "name": record.name,
            "layer": record.primary_layer,
            "cohort": record.comparison_cohort,
            "sources": list(record.primary_sources),
        }
        for record in sorted(landscape.records, key=lambda item: (item.primary_layer, item.id))
    ]


def main() -> int:
    arguments = build_parser().parse_args()
    landscape = HarnessLandscape.from_path(CATALOG_PATH)

    if arguments.list or not arguments.compare:
        print(
            json.dumps(
                {
                    "reviewed_at": landscape.reviewed_at,
                    "systems": list_records(landscape),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    try:
        plan = landscape.compare(
            *arguments.compare,
            mode=arguments.mode,
            controlled_variables=set(arguments.control),
        )
    except (IncomparableHarnessError, KeyError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    print(json.dumps({"ok": True, "plan": plan.as_dict()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
