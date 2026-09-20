from __future__ import annotations
import argparse, hashlib, json, math, os, random
from pathlib import Path
import numpy as np
from openai import OpenAI

ROOT=Path(__file__).resolve().parents[1]
PANEL_PATH=ROOT/'configs/frontier_panel.json'
PROMPTS={
 'vanilla':ROOT/'prompts/frontier_vanilla.txt',
 'theorica':ROOT/'prompts/frontier_theorica.txt',
}
FAULT_ENUM=['noise','drift','sensor_bias','sensor_gain','actuator_bias','outliers','saturation','none']

def sha256(path:Path): return hashlib.sha256(path.read_bytes()).hexdigest()

def clean_law(task,x):
    p=task['params']; law=task['law']; x=float(x)
    if law=='poly3': return p[0]*x**3+p[1]*x**2+p[2]*x
    if law=='nested_trig': return p[0]*math.sin(x*x)*math.cos(p[1]*x)+p[2]
    if law=='log_combo': return p[0]*math.log(x+1.0)+p[1]*math.log(x*x+1.0)+p[2]
    if law=='sqrt_scale': return p[0]*math.sqrt(max(x,0.0))+p[1]
    if law=='cos2': return p[0]*(math.cos(x-p[1])**2)+p[2]
    if law=='inverse': return p[0]/(x+p[1])+p[2]
    if law=='gaussian': return p[0]*math.exp(-0.5*((x-p[1])/p[2])**2)+p[3]
    if law=='piecewise':
        cut=p[4]
        return (p[0]*x+p[1]) if x<cut else (p[2]*x*x+p[3])
    raise KeyError(law)

class HiddenLab:
    def __init__(self,task,budget,holdout_n):
        self.task=task; self.budget=budget; self.used=0; self.locked=False; self.submission=None
        seed=int(hashlib.sha256(task['id'].encode()).hexdigest()[:8],16)
        self.rng=random.Random(seed)
        hrng=random.Random(seed^0xA5A5A5A5)
        self.holdout=sorted(hrng.uniform(task['x_min'],task['x_max']) for _ in range(holdout_n))
        self.measurements=[]
    def measure(self,x):
        x=float(x)
        if self.locked: return {'ok':False,'error':'laboratory locked after holdout disclosure'}
        if self.used>=self.budget: return {'ok':False,'error':'experiment budget exhausted','remaining':0}
        if not self.task['x_min']<=x<=self.task['x_max']:
            return {'ok':False,'error':'x outside allowed range','range':[self.task['x_min'],self.task['x_max']]}
        self.used+=1
        xa=x+float(self.task.get('actuator_bias',0.0))
        y=clean_law(self.task,xa)
        y*=1.0+float(self.task.get('drift',0.0))*(self.used-1)
        y+=self.rng.gauss(0.0,float(self.task.get('noise_sd',0.0)))
        if self.task.get('outlier_at')==self.used: y+=float(self.task.get('outlier_delta',0.0))
        sat=False
        hi=self.task.get('saturation_high')
        if hi is not None and y>hi: y=float(hi); sat=True
        rec={'n':self.used,'x':x,'y':float(y),'saturated':sat,'remaining':self.budget-self.used}
        self.measurements.append(rec); return {'ok':True,**rec}
    def get_holdout(self):
        self.locked=True
        return {'ok':True,'measurement_locked':True,'x_values':self.holdout,'count':len(self.holdout)}
    def submit(self,predictions,model_summary,suspected_faults):
        if not self.locked:return {'ok':False,'error':'call get_holdout_queries before submitting'}
        if len(predictions)!=len(self.holdout):return {'ok':False,'error':f'expected {len(self.holdout)} predictions'}
        self.submission={'predictions':[float(v) for v in predictions],'model_summary':str(model_summary),'suspected_faults':list(suspected_faults)}
        return {'ok':True,'accepted':True}

TOOLS=[
 {'type':'function','name':'measure','description':'Run one physical-style measurement at a chosen control x. Consumes one experiment.','parameters':{'type':'object','properties':{'x':{'type':'number'}},'required':['x'],'additionalProperties':False},'strict':True},
 {'type':'function','name':'get_holdout_queries','description':'Lock the lab and reveal x coordinates requiring final predictions. Measurements are disabled after this call.','parameters':{'type':'object','properties':{},'additionalProperties':False},'strict':True},
 {'type':'function','name':'submit_predictions','description':'Submit predictions for the holdout x values in exactly the returned order.','parameters':{'type':'object','properties':{'predictions':{'type':'array','items':{'type':'number'}},'model_summary':{'type':'string'},'suspected_faults':{'type':'array','items':{'type':'string','enum':FAULT_ENUM}}},'required':['predictions','model_summary','suspected_faults'],'additionalProperties':False},'strict':True},
]

def score(task,lab):
    if not lab.submission:return {'valid':False,'reason':'no_submission','nrmse':None}
    truth=np.array([clean_law(task,x) for x in lab.holdout],float)
    pred=np.array(lab.submission['predictions'],float)
    rmse=float(np.sqrt(np.mean((pred-truth)**2)))
    span=max(float(np.quantile(truth,.95)-np.quantile(truth,.05)),1e-9)
    nrmse=rmse/span
    true=set(task.get('faults',[])) or {'none'}
    guessed=set(lab.submission.get('suspected_faults',[])) or {'none'}
    tp=len(true&guessed); fp=len(guessed-true); fn=len(true-guessed)
    prec=tp/(tp+fp) if tp+fp else 1.0; rec=tp/(tp+fn) if tp+fn else 1.0
    return {'valid':True,'rmse':rmse,'nrmse':nrmse,'success':nrmse<.08,'experiments_used':lab.used,'fault_precision':prec,'fault_recall':rec,'true_faults':sorted(true),'guessed_faults':sorted(guessed)}

def run_one(client,model,task,condition,budget,holdout_n,max_turns=30):
    lab=HiddenLab(task,budget,holdout_n)
    instructions=PROMPTS[condition].read_text()
    user=f"Hidden laboratory {task['id']}. Control x is bounded to [{task['x_min']}, {task['x_max']}]. Experiment budget: {budget}. Use the provided tools. When ready, lock measurements with get_holdout_queries and submit predictions."
    input_items=[{'role':'user','content':user}]
    transcript=[]; returned_models=[]; usage=[]
    for turn in range(max_turns):
        resp=client.responses.create(model=model,instructions=instructions,input=input_items,tools=TOOLS,parallel_tool_calls=False,store=False,max_output_tokens=1200)
        returned_models.append(resp.model)
        if getattr(resp,'usage',None): usage.append(resp.usage.model_dump() if hasattr(resp.usage,'model_dump') else str(resp.usage))
        input_items += resp.output
        calls=[item for item in resp.output if getattr(item,'type',None)=='function_call']
        transcript.append({'turn':turn,'response_id':resp.id,'model':resp.model,'output_text':resp.output_text,'calls':[{'name':c.name,'arguments':c.arguments,'call_id':c.call_id} for c in calls]})
        if not calls:
            input_items.append({'role':'user','content':'Continue using the laboratory tools. A run is valid only after submit_predictions is accepted.'})
            continue
        for call in calls:
            try: args=json.loads(call.arguments)
            except Exception: args={}
            if call.name=='measure': result=lab.measure(args.get('x',float('nan')))
            elif call.name=='get_holdout_queries': result=lab.get_holdout()
            elif call.name=='submit_predictions': result=lab.submit(args.get('predictions',[]),args.get('model_summary',''),args.get('suspected_faults',[]))
            else: result={'ok':False,'error':'unknown tool'}
            transcript[-1].setdefault('tool_results',[]).append({'call_id':call.call_id,'name':call.name,'result':result})
            input_items.append({'type':'function_call_output','call_id':call.call_id,'output':json.dumps(result)})
        if lab.submission:break
    return {'task_id':task['id'],'condition':condition,'requested_model':model,'returned_models':returned_models,'score':score(task,lab),'measurements':lab.measurements,'holdout_x':lab.holdout,'submission':lab.submission,'transcript':transcript,'usage':usage}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--model',default=os.getenv('THEORICA_MODEL','gpt-6-astra')); ap.add_argument('--conditions',default='vanilla,theorica'); ap.add_argument('--tasks',default='all'); ap.add_argument('--out',default='results/frontier/openai_frontier_v1.json'); args=ap.parse_args()
    if not os.getenv('OPENAI_API_KEY'): raise SystemExit('OPENAI_API_KEY is required; refusing to fabricate a frontier run')
    panel=json.loads(PANEL_PATH.read_text()); selected=panel['tasks'] if args.tasks=='all' else [t for t in panel['tasks'] if t['id'] in set(args.tasks.split(','))]
    client=OpenAI(); rows=[]
    for task in selected:
        for condition in args.conditions.split(','):
            print(f"running {task['id']} {condition} {args.model}",flush=True)
            rows.append(run_one(client,args.model,task,condition,panel['experiment_budget'],panel['holdout_points']))
    payload={'protocol_version':panel['protocol_version'],'panel_sha256':sha256(PANEL_PATH),'prompt_sha256':{k:sha256(v) for k,v in PROMPTS.items()},'requested_model':args.model,'rows':rows}
    out=ROOT/args.out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(payload,indent=2)); print(out)

if __name__=='__main__':main()
