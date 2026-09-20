from __future__ import annotations
import math
from ..environments.base import LabEnvironment, FaultConfig

SOURCE_COMMIT='c0c18c90d61510a78ff2d24ac5299ad92c8acc59'
SOURCE_PATH='regression_task/task_info.py'

TASKS={
 'nguyen-1': ('x**3+x**2+x', -10.0,10.0, lambda x:x**3+x**2+x),
 'nguyen-2': ('x**4+x**3+x**2+x', -10.0,10.0, lambda x:x**4+x**3+x**2+x),
 'nguyen-3': ('x**5+x**4+x**3+x**2+x', -10.0,10.0, lambda x:x**5+x**4+x**3+x**2+x),
 'nguyen-4': ('x**6+x**5+x**4+x**3+x**2+x', -10.0,10.0, lambda x:x**6+x**5+x**4+x**3+x**2+x),
 'nguyen-5': ('sin(x**2)*cos(x)-1', -10.0,10.0, lambda x:math.sin(x*x)*math.cos(x)-1.0),
 'nguyen-6': ('sin(x)+sin(x+x**2)', -10.0,10.0, lambda x:math.sin(x)+math.sin(x+x*x)),
 'nguyen-7': ('log(x+1)+log(x**2+1)', 0.0,100.0, lambda x:math.log(x+1.0)+math.log(x*x+1.0)),
 'nguyen-8': ('sqrt(x)', 0.0,100.0, lambda x:math.sqrt(x)),
}

def make_nguyen(task:str,seed:int=0):
    expr,lo,hi,fn=TASKS[task]
    truth_family={'nguyen-8':'sqrt'}.get(task,'external_unrepresented')
    return LabEnvironment('external_'+task,lo,hi,truth_family,fn,FaultConfig(),seed,
        metadata={'external_source':{'repo':'isds-neu/SymbolicPhysicsLearner','commit':SOURCE_COMMIT,'path':SOURCE_PATH,'expression':expr}})

HOLDOUT_TASKS={
 'nguyen-1c': ('3.39*x**3+2.12*x**2+1.78*x', -10.0,10.0, lambda x:3.39*x**3+2.12*x**2+1.78*x),
 'nguyen-2c': ('0.48*x**4+3.39*x**3+2.12*x**2+1.78*x', -10.0,10.0, lambda x:0.48*x**4+3.39*x**3+2.12*x**2+1.78*x),
 'nguyen-5c': ('sin(x**2)*cos(x)-0.75', -10.0,10.0, lambda x:math.sin(x*x)*math.cos(x)-0.75),
 'nguyen-7c': ('log(x+1.4)+log(x**2+1.3)', 0.0,100.0, lambda x:math.log(x+1.4)+math.log(x*x+1.3)),
 'nguyen-8c': ('sqrt(1.23*x)', 0.0,100.0, lambda x:math.sqrt(1.23*x)),
}

def make_nguyen_holdout(task:str,seed:int=0):
    expr,lo,hi,fn=HOLDOUT_TASKS[task]
    return LabEnvironment('external_'+task,lo,hi,'external_holdout',fn,FaultConfig(),seed,
        metadata={'external_source':{'repo':'isds-neu/SymbolicPhysicsLearner','commit':SOURCE_COMMIT,'path':SOURCE_PATH,'expression':expr},
                  'split':'v0.3_constant_transfer_holdout'})
