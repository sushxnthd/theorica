import numpy as np
from theorica.agents.multivariate_synthesis import MultivariateTheorySynthesizer, normalized_rmse
from theorica.agents.dimensions import MASS,ACCEL,FORCE,LENGTH,TIME,additive_allowed,transcendental_allowed,DIMENSIONLESS

def test_multivariate_nguyen10():
    rng=np.random.default_rng(1)
    X=rng.uniform(-2,2,(20,2))
    y=2*np.sin(X[:,0])*np.cos(X[:,1])
    th,_=MultivariateTheorySynthesizer().fit(X,y)
    Xt=rng.uniform(-2,2,(200,2))
    assert normalized_rmse(th.predict(Xt),2*np.sin(Xt[:,0])*np.cos(Xt[:,1]))<1e-6

def test_dimensions():
    assert (MASS*ACCEL).compatible(FORCE)
    assert not additive_allowed(FORCE,LENGTH)
    assert transcendental_allowed(DIMENSIONLESS)
    assert not transcendental_allowed(TIME)
