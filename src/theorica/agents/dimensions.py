from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Dimension:
    # SI base exponents: M,L,T,I,Theta,N,J
    exp: tuple[float,...]=(0,0,0,0,0,0,0)
    def __mul__(self,o): return Dimension(tuple(a+b for a,b in zip(self.exp,o.exp)))
    def __truediv__(self,o): return Dimension(tuple(a-b for a,b in zip(self.exp,o.exp)))
    def __pow__(self,p): return Dimension(tuple(a*p for a in self.exp))
    def compatible(self,o,tol=1e-12): return all(abs(a-b)<tol for a,b in zip(self.exp,o.exp))

DIMENSIONLESS=Dimension()
MASS=Dimension((1,0,0,0,0,0,0)); LENGTH=Dimension((0,1,0,0,0,0,0)); TIME=Dimension((0,0,1,0,0,0,0))
VELOCITY=LENGTH/TIME; ACCEL=LENGTH/(TIME**2); FORCE=MASS*ACCEL

def additive_allowed(*dims):
    return all(dims[0].compatible(d) for d in dims[1:]) if dims else True
def transcendental_allowed(dim): return dim.compatible(DIMENSIONLESS)
