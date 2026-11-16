import sys, numpy as np
sys.path.insert(0,'/mnt/project-files/hces-core/src')
from hces.retrieve import Index, _blob
from data import *
Qs=queries()
def run(path,qids):
    idx=Index(path,384); worst=0; setdiff=0; firstpos=[]
    for qid in qids:
        q=np.array(Qs[qid],dtype=np.float32)
        nat=idx.db.execute("SELECT u.unit_id,v.distance FROM vec v JOIN units u ON u.rid=v.rowid WHERE v.embedding MATCH ? AND k=150 ORDER BY v.distance",(_blob(q),)).fetchall()
        ours=idx.vector_search(q,150)
        a=[u for u,_ in nat]; b=[u for u,_ in ours]
        if a!=b:
            i=next(j for j in range(150) if a[j]!=b[j]); firstpos.append(i+1)
            setdiff+=len(set(a)^set(b))//2
            worst=max(worst,max(abs(nat[j][1]-ours[j][1]) for j in range(150)))
            # gap between swapped items
            dn=dict(nat); gap=abs(dn.get(b[i],9)-nat[i][1])
            print(f'  {qid}: first diff at rank {i+1}, distance gap {gap:.2e}, members differing {len(set(a)^set(b))//2}')
    print(path.split('/')[-1],'max |distance diff|',f'{worst:.1e}','first-diff ranks',firstpos)
U='/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/hces-lab/kb/index/'
run(U+'secret-adversary-plain.db',[r['id'] for r in book_keys('secret-adversary')])
run('/tmp/claude-0/eb_index.db',['eb1911/'+r['id'] for r in eb_keys()])
