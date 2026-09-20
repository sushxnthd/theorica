from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DP=ROOT/"external"/"DiscoverPhysics"
sys.path.insert(0,str(DP/"ScienceAgent"))
sys.path.insert(0,str(DP/"PhysicsSchool"))
from scienceagent.worlds import get_world
from scienceagent.evaluator import Evaluator

WORLDS=["gravity","yukawa","fractional","coulomb_easy","extra_dimensions"]
RADII=np.array([0.35,0.50,0.75,1.10,1.60,2.30,3.30,4.70,6.50,8.50],float)
SCALE_CASES=[(1.0,1.0),(0.5,1.0),(2.0,1.0),(1.0,0.5),(1.0,2.0)]
TIMES=[0.02,0.04,0.06,0.08]

def radial_acceleration(executor,r,p1=1.0,p2=1.0):
    exp={"p1":float(p1),"p2":float(p2),"pos2":[float(r),0.0],"velocity2":[0.0,0.0],"measurement_times":TIMES}
    out=executor.run([exp])[0]
    v=np.asarray(out["velocity2"],float)[:,0]
    t=np.asarray(out["measurement_times"],float)
    denom=float(np.dot(t,t))
    return float(np.dot(t,v)/max(denom,1e-12))

def fit_exponents(executor):
    rows=[]
    r0=3.0
    for p1,p2 in SCALE_CASES:
        a=radial_acceleration(executor,r0,p1,p2)
        rows.append((p1,p2,a))
    signs=[np.sign(a) for _,_,a in rows if abs(a)>1e-12]
    sign=float(np.sign(np.median(signs))) if signs else -1.0
    X=[]; y=[]
    for p1,p2,a in rows:
        if abs(a)<=1e-12: continue
        X.append([1.0,math.log(abs(p1)),math.log(abs(p2))])
        y.append(math.log(abs(a)))
    beta,*_=np.linalg.lstsq(np.asarray(X),np.asarray(y),rcond=None)
    return sign,float(beta[1]),float(beta[2]),rows

def build_law_source(radii,accels,sign,alpha,beta):
    logs_r=np.log(np.asarray(radii,float))
    logs_a=np.log(np.maximum(np.abs(np.asarray(accels,float)),1e-14))
    return f"""
import numpy as np
RLOG=np.array({logs_r.tolist()!r},dtype=float)
ALOG=np.array({logs_a.tolist()!r},dtype=float)
SIGN={float(sign)!r}
P1_EXP={float(alpha)!r}
P2_EXP={float(beta)!r}

def _log_interp(x):
    x=float(x)
    if x<=RLOG[0]:
        slope=(ALOG[1]-ALOG[0])/(RLOG[1]-RLOG[0])
        return ALOG[0]+slope*(x-RLOG[0])
    if x>=RLOG[-1]:
        slope=(ALOG[-1]-ALOG[-2])/(RLOG[-1]-RLOG[-2])
        return ALOG[-1]+slope*(x-RLOG[-1])
    return float(np.interp(x,RLOG,ALOG))

def _acc(pos,p1,p2):
    pos=np.asarray(pos,dtype=float)
    r=float(np.linalg.norm(pos))
    r=max(r,0.05)
    base=np.exp(_log_interp(np.log(r)))
    scale=(max(abs(float(p1)),1e-12)**P1_EXP)*(max(abs(float(p2)),1e-12)**P2_EXP)
    return SIGN*base*scale*(pos/r)

def discovered_law(pos1,pos2,p1,p2,velocity2,duration):
    x=np.asarray(pos2,dtype=float).copy()
    v=np.asarray(velocity2,dtype=float).copy()
    duration=float(duration)
    dt=min(0.004,max(duration/5000.0,0.0005))
    n=max(1,int(np.ceil(duration/dt)))
    dt=duration/n
    a=_acc(x,p1,p2)
    for _ in range(n):
        x_new=x+v*dt+0.5*a*dt*dt
        a_new=_acc(x_new,p1,p2)
        v=v+0.5*(a+a_new)*dt
        x=x_new
        a=a_new
    return x.tolist(),v.tolist()
"""

def discover(executor):
    sign,alpha,beta,scale_rows=fit_exponents(executor)
    accels=[radial_acceleration(executor,float(r),1.0,1.0) for r in RADII]
    # exactly 15 external experiments total: 5 scaling + 10 radius probes.
    source=build_law_source(RADII,accels,sign,alpha,beta)
    return {
        "sign":sign,"p1_exponent":alpha,"p2_exponent":beta,
        "radii":RADII.tolist(),"radial_accelerations":accels,
        "scaling_probes":[{"p1":p1,"p2":p2,"a":a} for p1,p2,a in scale_rows],
        "experiment_count":15,"law_source":source,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--worlds",default=",".join(WORLDS))
    ap.add_argument("--out",default="results/native/discoverphysics_forcemap.json")
    args=ap.parse_args()
    selected=args.worlds.split(",")
    rows=[]
    for name in selected:
        print("WORLD",name,flush=True)
        world=get_world(name,engine="nbody",noise_std=0.0,noise_seed=20260920)
        executor=world["executor"]
        discovery=discover(executor)
        # Use only the native trajectory evaluator. No hidden law/rubric fields are accessed.
        evaluator=Evaluator(executor)
        result=evaluator.evaluate(discovery["law_source"],verbose=True)
        row={
            "world":name,
            "experiment_count":discovery["experiment_count"],
            "p1_exponent":discovery["p1_exponent"],
            "p2_exponent":discovery["p2_exponent"],
            "radial_accelerations":discovery["radial_accelerations"],
            "mean_pos_error":result["mean_pos_error"],
            "max_pos_error":result["max_pos_error"],
            "native_evaluator_pass":bool(result["passed"]),
            "per_case":result["per_case"],
        }
        rows.append(row)
        print(json.dumps(row,indent=2),flush=True)
    payload={
        "benchmark":"DiscoverPhysics native trajectory evaluator",
        "method":"generic 15-experiment radial force-map identification",
        "worlds":rows,
        "passes":sum(r["native_evaluator_pass"] for r in rows),
        "total":len(rows),
        "mean_position_mse":float(np.mean([r["mean_pos_error"] for r in rows])),
        "claim_boundary":"Trajectory evaluator only; no LLM explanation judge, no official leaderboard placement."
    }
    out=ROOT/args.out
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2))
    print(json.dumps({k:v for k,v in payload.items() if k!="worlds"},indent=2))

if __name__=="__main__":
    main()
