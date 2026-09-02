"""Require every known-bad mutation to fail only its measured contracts."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EXPECTED = {
    "portal_bypass": ["locked_portal_contract"],
    "missing_star_seed": ["complete_vertical_slice", "inventory_contract"],
    "missing_completion": ["complete_vertical_slice"],
    "wrong_forest_spawn": ["complete_vertical_slice", "save_load_roundtrip", "landmark_collisions", "location_boundaries"],
    "forest_corridor_blocker": ["complete_vertical_slice", "landmark_collisions"],
    "save_state_drift": ["save_load_roundtrip"],
}


def main() -> int:
    failures = []
    evidence = {}
    for mutation, expected in EXPECTED.items():
        path = ROOT / "diagnostics" / f"test_results_{mutation}.json"
        if not path.exists():
            failures.append(f"Missing result: {mutation}")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        actual = payload["failed_test_names"]
        evidence[mutation] = {"expected_failed_tests": expected, "actual_failed_tests": actual}
        if actual != expected or payload["passed"]:
            failures.append(f"Unexpected mutation result: {mutation}")
    report = {"passed": not failures, "mutation_count": len(EXPECTED), "failures": failures, "evidence": evidence}
    (ROOT / "diagnostics" / "mutation_verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
