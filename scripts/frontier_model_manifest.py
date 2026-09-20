"""Fail-closed manifest for frontier-model evaluation.

This script never converts a missing credential into a claimed run.
"""
from pathlib import Path
import os, json, datetime

providers={"openai":bool(os.getenv("OPENAI_API_KEY"))}
manifest={
    "created_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "credentials_present":providers,
    "executed":False,
    "frozen_protocol":"docs/FRONTIER_EVAL_PROTOCOL.md",
    "reason":"Frontier evaluation requires a fresh API credential and must not be backfilled from chat outputs."
}
out=Path(__file__).resolve().parents[1]/"results/frontier_model_manifest.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2))
