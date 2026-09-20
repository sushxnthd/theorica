import numpy as np
from theorica.agents.symbolic_synthesis import CompositionalTheorySynthesizer
from theorica.agents.theory_synthesis import TheorySynthesizingScientist
from theorica.adapters.nguyen_source import make_nguyen
from theorica.evaluation.theory_metrics import evaluate_theory_run

def test_grammar_does_not_store_complete_nguyen_equations():
    synth=CompositionalTheorySynthesizer()
    expressions={t.expression for t in synth.generate_terms()}
    assert 'x**3+x**2+x' not in expressions
    assert 'sin(x**2)*cos(x)-1' not in expressions

def test_synthesizer_builds_polynomial_composition():
    x=np.linspace(-3,3,14); y=x**3+x**2+x
    theory,_=CompositionalTheorySynthesizer().fit(x,y)
    grid=np.linspace(-3,3,101)
    assert np.sqrt(np.mean((theory.predict(grid)-(grid**3+grid**2+grid))**2)) < 1e-7

def test_agent_discovers_nested_nguyen5():
    env=make_nguyen('nguyen-5',seed=1)
    run=TheorySynthesizingScientist().run(env,budget=14)
    score=evaluate_theory_run(env,run)
    assert score['nrmse'] < 0.01
