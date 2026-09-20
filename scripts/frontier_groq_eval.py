from __future__ import annotations
import argparse, json, os
from pathlib import Path
from openai import OpenAI
from frontier_openai_eval import PANEL_PATH, PROMPTS, run_one, sha256

ROOT=Path(__file__).resolve().parents[1]
# Four-world frozen free-tier panel: two clean/compositional + two faulted.
DEFAULT_TASKS="F01,F02,F05,F06"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--model",default=os.getenv("THEORICA_GROQ_MODEL","openai/gpt-oss-120b"))
    ap.add_argument("--conditions",default="vanilla,theorica")
    ap.add_argument("--tasks",default=DEFAULT_TASKS)
    ap.add_argument("--out",default="results/frontier/groq_frontier_v1.json")
    args=ap.parse_args()
    key=os.getenv("GROQ_API_KEY")
    if not key:
        raise SystemExit("GROQ_API_KEY is required; refusing to fabricate a free-tier frontier run")
    panel=json.loads(PANEL_PATH.read_text())
    ids=set(args.tasks.split(","))
    selected=[t for t in panel["tasks"] if t["id"] in ids]
    client=OpenAI(api_key=key,base_url="https://api.groq.com/openai/v1")
    rows=[]
    for task in selected:
        for condition in args.conditions.split(","):
            print(f"running {task['id']} {condition} {args.model}",flush=True)
            rows.append(run_one(client,args.model,task,condition,panel["experiment_budget"],panel["holdout_points"]))
    payload={
      "provider":"Groq free tier",
      "protocol_version":"frontier-v1-free-groq-frozen-2026-09-20",
      "parent_panel_version":panel["protocol_version"],
      "selected_task_ids":[t["id"] for t in selected],
      "panel_sha256":sha256(PANEL_PATH),
      "prompt_sha256":{k:sha256(v) for k,v in PROMPTS.items()},
      "requested_model":args.model,
      "rows":rows,
      "claim_boundary":"Paired vanilla vs THEORICA scaffold on the frozen four-world free-tier panel; not a general frontier-model ranking."
    }
    out=ROOT/args.out;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(payload,indent=2));print(out)

if __name__=="__main__":main()
