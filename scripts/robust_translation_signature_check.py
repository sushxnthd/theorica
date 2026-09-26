from itertools import combinations, permutations, product

def hamming(a,b):
    return sum(x != y for x,y in zip(a,b))

def restrict(g,R):
    return tuple(g[i] for i in R)

def d_R(G,R):
    return min(hamming(restrict(g,R),restrict(h,R))
               for i,g in enumerate(G) for h in G[i+1:])

def decode(G,R,z,e):
    c=[g for g in G if hamming(restrict(g,R),z) <= e]
    return c[0] if len(c)==1 else None

def cyclic(n):
    return [tuple((i+k)%n for i in range(n)) for k in range(n)]

def dihedral(n):
    out=set(cyclic(n))
    out.update(tuple((k-i)%n for i in range(n)) for k in range(n))
    return sorted(out)

def symmetric(n):
    return list(permutations(range(n)))

def min_signature(G,e):
    n=len(G[0])
    for m in range(n+1):
        for R in combinations(range(n),m):
            if d_R(G,R) >= 2*e+1:
                return R
    return None

def exhaustive(G,R,e):
    n,m=len(G[0]),len(R)
    count=0
    for g in G:
        truth=list(restrict(g,R))
        for k in range(e+1):
            for pos in combinations(range(m),k):
                opts=[[v for v in range(n) if v != truth[j]] for j in pos]
                for repl in product(*opts):
                    z=truth.copy()
                    for j,v in zip(pos,repl): z[j]=v
                    assert decode(G,R,z,e)==g
                    count += 1
    return count

def ambiguity_witness(G,R,e):
    best=None
    for i,g in enumerate(G):
        for h in G[i+1:]:
            d=hamming(restrict(g,R),restrict(h,R))
            if best is None or d < best[0]: best=(d,g,h)
    d,g,h=best
    assert d <= 2*e
    a,b=restrict(g,R),restrict(h,R)
    diff=[i for i,(x,y) in enumerate(zip(a,b)) if x != y]
    z=list(a)
    for i in diff[:(len(diff)+1)//2]: z[i]=b[i]
    z=tuple(z)
    assert hamming(a,z)<=e and hamming(b,z)<=e
    return g,h,z

if __name__ == "__main__":
    cases=[("C5",cyclic(5),1,65),("C7",cyclic(7),2,2737),("D7",dihedral(7),1,350)]
    for name,G,e,expected in cases:
        R=min_signature(G,e)
        assert R is not None
        checked=exhaustive(G,R,e)
        assert checked==expected
        print(name,e,R,d_R(G,R),checked)

    G=symmetric(3); R=tuple(range(3)); e=1
    assert d_R(G,R)==2
    print("S3 ambiguity",ambiguity_witness(G,R,e))
