from theorica.causal import random_world,ActiveCausalScientist

def test_causal_runs_and_scores():
    w=random_world(6,6,123,1.0)
    s=ActiveCausalScientist(policy='greedy').run(w,budget=2,seed=99)
    assert 0<=s['directed_f1']<=1
    assert s['interventions_used']<=2
