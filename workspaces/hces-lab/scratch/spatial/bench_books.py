import sys, time, numpy as np
sys.path.insert(0,'/mnt/project-files/hces-core/src')
from hces.spatial import SpatialIndex
from hces.retrieve import Index, rrf
from data import *
Qs=queries(); out={}
U='/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/hces-lab/kb/index/'
for slug in ('secret-adversary','moonstone','way-we-live-now'):
    for shape in ('chaptered','plain'):
        ids,V,_=book(slug,shape); idx=Index(U+f'{slug}-{shape}.db',384)
        sp=SpatialIndex.build(ids,V); 
        for r in book_keys(slug):
            if not r['answerable']: continue
            q=Qs[r['id']]; gold=set(r['gold'][shape])
            paths={
             'sqlite-vec vector (current)': lambda: [u for u,_ in idx.vector_search(list(map(float,q)),50)],
             'spatial vector nprobe 8': lambda: [u for u,_ in sp.search(q,50,8)],
             'spatial vector exact': lambda: [u for u,_ in sp.search(q,50,10**6)],
             'hybrid sqlite-vec+FTS (current)': lambda: [u for u,_ in rrf([[u for u,_ in idx.vector_search(list(map(float,q)),50)],[u for u,_ in idx.keyword_search(r['question'],50)]])[:50]],
             'hybrid spatial+FTS': lambda: [u for u,_ in rrf([[u for u,_ in sp.search(q,50,10**6)],[u for u,_ in idx.keyword_search(r['question'],50)]])[:50]],
            }
            for n,f in paths.items():
                t=time.perf_counter(); res=f(); ms=(time.perf_counter()-t)*1000
                out.setdefault(n,[]).append((ms,[any(g in res[:k] for g in gold) for k in (5,10,20,50)]))
print(f"{'path':34}{'median ms':>10}  gold@5 @10 @20 @50  (146 question x shape runs)")
for n,v in out.items():
    ms=np.median([a for a,_ in v]); g=np.mean([b for _,b in v],axis=0)
    print(f'{n:34}{ms:10.2f}  '+' '.join(f'{x:.2f}' for x in g))
