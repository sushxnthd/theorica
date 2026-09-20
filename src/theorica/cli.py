from __future__ import annotations
import argparse, json
from .runner import run_once, run_suite, summarize, save_json
from .environments.tasks import TASKS


def main():
    p=argparse.ArgumentParser(prog="theorica")
    sub=p.add_subparsers(dest="cmd",required=True)
    r=sub.add_parser("run")
    r.add_argument("--agent",choices=["uniform","random","falsification"],default="falsification")
    r.add_argument("--task",choices=TASKS,default="faulted_cos2")
    r.add_argument("--seed",type=int,default=0)
    r.add_argument("--budget",type=int,default=30)
    r.add_argument("--out",default="")
    d=sub.add_parser("demo")
    d.add_argument("--seeds",type=int,default=20)
    d.add_argument("--budget",type=int,default=30)
    d.add_argument("--out",default="results/demo_results.json")
    args=p.parse_args()
    if args.cmd=="run":
        run,m=run_once(args.agent,args.task,args.seed,args.budget)
        payload={"metrics":m,"run":run.as_dict()}
        if args.out: save_json(args.out,payload)
        print(json.dumps(payload,indent=2))
    else:
        rows=run_suite(args.seeds,args.budget)
        summary=summarize(rows)
        payload={"summary":summary,"rows":rows}
        save_json(args.out,payload)
        print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
