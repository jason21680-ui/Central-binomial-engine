import itertools

S = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,137]
N = 200
P_MAX = 2*N

def primes_upto(n):
    if n < 2: return []
    a = bytearray(b"\x01")*(n+1)
    a[0:2] = b"\x00\x00"
    for i in range(2, int(n**0.5)+1):
        if a[i]:
            a[i*i:n+1:i] = b"\x00"*(((n - i*i)//i)+1)
    return [i for i in range(n+1) if a[i]]

def vp_C(n,p):
    if n <= 0 or p > 2*n: return 0
    s = 0
    pk = p
    two = 2*n
    while pk <= two:
        s += (two//pk) - 2*(n//pk)
        pk *= p
    return s

def generator_keys_upto(N):
    keys = set()
    a = 2
    while True:
        c = 8*a*a + 8*a + 1
        lhs = (a, 2*a+2, c)
        rhs = (a+1, 2*a, c+1)
        if max(lhs+rhs) > N: break
        keys.add(frozenset([frozenset(lhs), frozenset(rhs)]))
        a += 1
    return keys

P = primes_upto(P_MAX)
p_index = {p:i for i,p in enumerate(P)}
anchor_idx = [p_index[p] for p in S]  # assumes all in range

# VP[n][i] = v_{P[i]}(C(n))
VP = [[0]*len(P) for _ in range(N+1)]
for n in range(1, N+1):
    row = VP[n]
    for i,p in enumerate(P):
        row[i] = vp_C(n,p)

# A[n] = 16D anchor valuation vector for C(n)
A = [None]*(N+1)
A[0] = (0,)*len(S)
for n in range(1, N+1):
    A[n] = tuple(VP[n][idx] for idx in anchor_idx)

GEN = generator_keys_upto(N)

def anchor_sum(t):
    a1,a2,a3 = t
    v1,v2,v3 = A[a1],A[a2],A[a3]
    return tuple(v1[i]+v2[i]+v3[i] for i in range(len(S)))

def stage2_ok(lhs,rhs):
    for i,_p in enumerate(P):
        if (VP[lhs[0]][i]+VP[lhs[1]][i]+VP[lhs[2]][i] !=
            VP[rhs[0]][i]+VP[rhs[1]][i]+VP[rhs[2]][i]):
            return False
    return True

buckets = {}  # vec -> triple OR list of triples
for t in itertools.combinations(range(1, N+1), 3):
    v = anchor_sum(t)
    prev = buckets.get(v)
    if prev is None:
        buckets[v] = t
    elif isinstance(prev, tuple):
        buckets[v] = [prev, t]
    else:
        prev.append(t)

hits = 0
for grp in buckets.values():
    if isinstance(grp, tuple): 
        continue
    k = len(grp)
    for i in range(k):
        lhs = grp[i]
        lhs_set = set(lhs)
        for j in range(i+1, k):
            rhs = grp[j]
            if lhs_set & set(rhs): 
                continue
            if frozenset([frozenset(lhs), frozenset(rhs)]) in GEN:
                continue
            if stage2_ok(lhs,rhs):
                hits += 1
                print("SPORADIC:", lhs, "=", rhs)

print("DONE. Sporadic nodes:", hits)
