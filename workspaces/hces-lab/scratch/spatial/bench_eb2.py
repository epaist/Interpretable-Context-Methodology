import sys, time, numpy as np
sys.path.insert(0,'/mnt/project-files/hces-core/src')
from hces.spatial import SpatialIndex
from data import *
ids,V=eb(); Qs=queries(); keys=eb_keys()
qv=np.stack([Qs['eb1911/'+r['id']] for r in keys])
def flat(q,k): s=V@q; top=np.argpartition(-s,k)[:k]; return [ids[i] for i in top[np.argsort(-s[top])]]
exact=[flat(q,150) for q in qv]
def gold(res,k): return np.mean([r['gold'] in res[i][:k] for i,r in enumerate(keys) if r['answerable']])
for cells in (459,):
    idx=SpatialIndex.build(ids,V,cells); idx.save('/tmp/claude-0/eb459'); idx=SpatialIndex.load('/tmp/claude-0/eb459')
    for npb in (16,32,64,459):
        ts=[];res=[]
        for q in qv:
            t=time.perf_counter(); res.append([u for u,_ in idx.search(q,150,npb)]); ts.append((time.perf_counter()-t)*1000)
        o=np.mean([len(set(a)&set(b))/150 for a,b in zip(exact,res)])
        print(cells,npb,f'{np.median(ts):.1f}ms =exact@150 {o:.3f}',' '.join(f'gold@{k} {gold(res,k):.3f}' for k in (5,20,50,150)))
