from scripts.anytime_falsification_dev import task
from theorica.agents.anytime_falsification import AnytimeRepresentationFalsifier
from theorica.agents.representation_closure import normalized_rmse

for i, family in enumerate(("gaussian","erf","dawson","sinc","polynomial","trig")):
    seed=7000+i
    x0,y0,probe,xt,truth,sigma,observe=task(family,seed)
    print("\n",family)
    for policy in ("disagreement","uniform"):
        r=AnytimeRepresentationFalsifier().run(
            x0,y0,bounds=(float(xt.min()),float(xt.max())),
            probe_pool=probe,observe=observe,noise_sigma=sigma,budget=8,
            policy=policy,random_seed=seed+1
        )
        print(policy,r.mode,r.rejected_at,r.log_e_value,
              normalized_rmse(r.predict(xt),truth))
