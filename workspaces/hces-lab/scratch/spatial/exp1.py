import numpy as np, collections
from data import *
Qs=queries()
def norm(X): return X/np.linalg.norm(X,axis=1,keepdims=True)
def structure(ids):
    par=[parent_of(u) for u in ids]
    # plain shape: no chapters -> parent = whole volume; treat as no parent
    pid={p:i for i,p in enumerate(dict.fromkeys(par))}
    P=np.array([pid[p] for p in par])
    prev=np.array([i-1 if i>0 and par[i-1]==par[i] else i for i in range(len(ids))])
    nxt=np.array([i+1 if i+1<len(ids) and par[i+1]==par[i] else i for i in range(len(ids))])
    return P,prev,nxt
def ctx_vectors(V,P,prev,nxt,lam,mu):
    C=np.zeros((P.max()+1,V.shape[1]),np.float32); np.add.at(C,P,V); C=norm(C)
    return norm(V+lam*C[P]+mu*(V[prev]+V[nxt])/2)
def rank(V,q,k): s=V@q; return np.argsort(-s)[:k], s
def region(V,q,prev,nxt,g,k):
    s=V@q; s2=s+g*np.maximum(s[prev],s[nxt]); return np.argsort(-s2)[:k]
def evaluate(sets):
    out=collections.defaultdict(list)
    for name,ids,V,keys,shape in sets:
        P,prev,nxt=structure(ids); pos={u:i for i,u in enumerate(ids)}
        flat=chapters= 'plain' not in ids[0]
        variants={'flat':V}
        for lam in (0.15,0.3,0.5):
            for mu in (0.0,0.3,0.6):
                if lam==0 and mu==0: continue
                variants[f'ctx l{lam} m{mu}']=ctx_vectors(V,P,prev,nxt,lam if chapters else 0,mu)
        for r in keys:
            if not r['answerable']: continue
            gold=r['gold'][shape] if shape else [r['gold']]
            gi=[pos[g] for g in gold]
            q=Qs[r['id'] if shape else 'eb1911/'+r['id']]
            for vn,X in variants.items():
                s=X@q; order=np.argsort(-s); rk=np.empty(len(order),int); rk[order]=np.arange(1,len(order)+1)
                out[vn].append(min(rk[gi]))
            for g in (0.2,0.5):
                s=V@q; s2=s+g*np.maximum(s[prev],s[nxt]); order=np.argsort(-s2); rk=np.empty(len(order),int); rk[order]=np.arange(1,len(order)+1)
                out[f'region g{g}'].append(min(rk[gi]))
    return out
def report(out,ks):
    print(f"{'variant':18}"+''.join(f'@{k:<6}' for k in ks)+' median_first_gold')
    for vn,ranks in out.items():
        r=np.array(ranks); print(f'{vn:18}'+''.join(f'{(r<=k).mean():.2f}   ' for k in ks)+f'{np.median(r):.0f}  (n={len(r)})')
import sys
if sys.argv[1]=='books':
    sets=[]
    for slug in ('secret-adversary','moonstone','way-we-live-now'):
        for shape in ('chaptered','plain'):
            ids,V,_=book(slug,shape); sets.append((slug,ids,V,book_keys(slug),shape))
    report(evaluate(sets),(1,3,5,10,20,50))
else:
    ids,V=eb(); report(evaluate([('eb',ids,V,[r for r in eb_keys()],None)]),(1,5,10,20,50,150))
