from __future__ import annotations
import argparse, json
from .runner import run_nguyen_once, run_causal_once
from .adapters.nguyen_source import TASKS as NGUYEN_TASKS

def main():
    p=argparse.ArgumentParser(prog="theorica",description="THEORICA — autonomous experimental science")
    sub=p.add_subparsers(dest="cmd",required=True)
    n=sub.add_parser("nguyen",help="run compositional theory synthesis")
    n.add_argument("--task",choices=sorted(NGUYEN_TASKS),default="nguyen-5")
    n.add_argument("--seed",type=int,default=0)
    n.add_argument("--budget",type=int,default=14)
    c=sub.add_parser("causal",help="run active causal discovery")
    c.add_argument("--nodes",type=int,default=6)
    c.add_argument("--edges",type=int,default=6)
    c.add_argument("--seed",type=int,default=123)
    c.add_argument("--budget",type=int,default=2)
    c.add_argument("--policy",choices=["greedy","random"],default="greedy")
    args=p.parse_args()
    if args.cmd=="nguyen":
        run,score=run_nguyen_once(args.task,args.seed,args.budget)
        print(json.dumps({"score":score,"run":run.as_dict()},indent=2))
    else:
        print(json.dumps(run_causal_once(args.nodes,args.edges,args.seed,args.budget,args.policy),indent=2))

if __name__=="__main__":
    main()
