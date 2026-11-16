import sys, time, json, sqlite3, struct, numpy as np, psutil, os
sys.path.insert(0,'/mnt/project-files/hces-core/src')
from hces.spatial import SpatialIndex
import sqlite_vec
from data import *
ids,V=eb(); Qs=queries(); keys=[r for r in eb_keys()]
qv=np.stack([Qs['eb1911/'+r['id']] for r in keys]); ans=[r for r in keys if r['answerable']]
base='/tmp/claude-0/eb'
t=time.perf_counter(); idx=SpatialIndex.build(ids,V); bt=time.perf_counter()-t
idx.save(base); del idx
idx=SpatialIndex.load(base); print('build_s',round(bt,1), idx.stats(), 'files_mb', round(os.path.getsize(base+'.spatial.npz')/2**20,1), round(os.path.getsize(base+'.f32.npy')/2**20,1))
# flat exact (numpy, float32, all in RAM)
def flat(q,k): s=V@q; top=np.argpartition(-s,k)[:k]; top=top[np.argsort(-s[top])]; return [ids[i] for i in top]
# sqlite-vec, same as hces.retrieve.Index.vector_search
db='/tmp/claude-0/eb_vec.db'
if not os.path.exists(db):
    d=sqlite3.connect(db); d.enable_load_extension(True); sqlite_vec.load(d)
    d.execute('CREATE VIRTUAL TABLE vec USING vec0(embedding float[384] distance_metric=cosine)')
    with d:
        d.executemany('INSERT INTO vec(rowid,embedding) VALUES (?,?)',((i+1,V[i].tobytes()) for i in range(len(V))))
    d.close()
d=sqlite3.connect(db); d.enable_load_extension(True); sqlite_vec.load(d)
def sv(q,k): return [ids[r[0]-1] for r in d.execute('SELECT rowid FROM vec WHERE embedding MATCH ? AND k=? ORDER BY distance',(q.astype(np.float32).tobytes(),k))]
def timeit(fn,k,reps=1):
    ts=[];res=[]
    for q in qv:
        t=time.perf_counter(); r=fn(q,k); ts.append((time.perf_counter()-t)*1000); res.append(r)
    return res, float(np.median(ts)), float(np.percentile(ts,90))
K=150
exact,fm,f90=timeit(flat,K); sres,sm,s90=timeit(sv,K)
print(f'sqlite-vec vs numpy top{K} agree', np.mean([len(set(a)&set(b))/K for a,b in zip(exact,sres)]))
def gold(res,k): return np.mean([r['gold'] in res[i][:k] for i,r in enumerate(keys) if r['answerable']])
rows=[('sqlite-vec flat (current)',sm,s90,sres),('numpy flat float32',fm,f90,exact)]
for npb in (4,8,16,32,64,128):
    res,m,p90=timeit(lambda q,k: [u for u,_ in idx.search(q,k,npb)],K); rows.append((f'spatial nprobe {npb}',m,p90,res))
print(f"{'path':28}{'median ms':>10}{'p90 ms':>8}{'=exact@20':>10}{'=exact@150':>11}"+''.join(f'{"gold@"+str(k):>9}' for k in (5,20,50,150)))
for n,m,p,res in rows:
    o20=np.mean([len(set(a[:20])&set(b[:20]))/20 for a,b in zip(exact,res)]); o150=np.mean([len(set(a)&set(b))/K for a,b in zip(exact,res)])
    print(f'{n:28}{m:10.1f}{p:8.1f}{o20:10.3f}{o150:11.3f}'+''.join(f'{gold(res,k):9.3f}' for k in (5,20,50,150)))
print('rss_mb', round(psutil.Process().memory_info().rss/2**20))
