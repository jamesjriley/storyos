from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from storyos.ingest.extract import extract_to_proposals


@dataclass(frozen=True)
class EvalCase:
    id: str
    input_path: str
    characters_min: int
    must_include_names: List[str]


def load_dataset(path: str) -> List[EvalCase]:
    d = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    cases = []
    for c in d.get("cases", []):
        cases.append(
            EvalCase(
                id=c["id"],
                input_path=c["input"],
                characters_min=int(c.get("expected", {}).get("characters_min", 0)),
                must_include_names=list(c.get("expected", {}).get("must_include_names", [])),
            )
        )
    return cases


def eval_one(project_dir: str, case: EvalCase, pack_dir: str, pack: str) -> Tuple[bool, Dict]:
    res = extract_to_proposals(project_dir=project_dir, input_path=case.input_path, pack_dir=pack_dir, pack=pack)
    run_dir = Path(res.proposals_dir)
    parsed_json = run_dir / "parsed.json"
    data = json.loads(parsed_json.read_text(encoding="utf-8"))

    names = [c.get("name","") for c in (data.get("characters") or [])]
    missing = [n for n in case.must_include_names if n not in names]

    ok = True
    ok &= len(names) >= case.characters_min
    ok &= len(missing) == 0

    report = {
        "case": case.id,
        "run_dir": str(run_dir),
        "characters_count": len(names),
        "missing_names": missing,
    }
    return ok, report


def run(project_dir: str, dataset: str, pack_dir: str, pack: str) -> int:
    cases = load_dataset(dataset)
    all_ok = True
    reports = []
    for c in cases:
        ok, rep = eval_one(project_dir, c, pack_dir, pack)
        all_ok &= ok
        reports.append(rep)
        print(f"[{c.id}] ok={ok} characters={rep['characters_count']} missing={rep['missing_names']}")

    out_path = Path(project_dir) / "00_INGEST" / "eval_reports"
    out_path.mkdir(parents=True, exist_ok=True)
    (out_path / "latest_ingest_eval.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
    return 0 if all_ok else 2


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("--dataset", default="evals/datasets/ingest/winnie_ch1.yaml")
    ap.add_argument("--pack-dir", default="content/packs")
    ap.add_argument("--pack", default="ingest_v1")
    args = ap.parse_args()
    raise SystemExit(run(args.project_dir, args.dataset, args.pack_dir, args.pack))
