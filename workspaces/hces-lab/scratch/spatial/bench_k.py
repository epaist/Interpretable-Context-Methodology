import sys, json, re, time, numpy as np
sys.path.insert(0,'/mnt/project-files/hces-core/src')
from hces.retrieve import Index, rrf, _blob
from data import *
exec(open('/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/voice-chat/stage07/eb_search.py').read().split('STOP = ')[1].split('\n\n')[0].join(['STOP = ','\n']))
Qs=queries(); KS=(20,50,100,150)
def native(idx,q,k):
    return [r[0] for r in idx.db.execute("SELECT u.unit_id FROM vec v JOIN units u ON u.rid=v.rowid WHERE v.embedding MATCH ? AND k=? ORDER BY v.distance",(_blob(q),k))]
def timed(f):
    t=time.perf_counter(); r=f(); return r,(time.perf_counter()-t)*1000
def check(idx,qs):
    agree=[];tn=[];tp=[]
    idx.vector_search(qs[0],1)  # load matrix once (timed separately below)
    for q in qs:
        a,t1=timed(lambda: native(idx,q,150)); b,t2=timed(lambda: [u for u,_ in idx.vector_search(q,150)])
        agree.append(a==b); tn.append(t1); tp.append(t2)
    return np.mean(agree), np.median(tn), np.median(tp)
print('== equivalence and speed, top 150 ==')
U='/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/hces-lab/kb/index/'
book_gold={k:[] for k in KS}
for slug in ('secret-adversary','moonstone','way-we-live-now'):
    keys=book_keys(slug)
    for shape in ('chaptered','plain'):
        idx=Index(U+f'{slug}-{shape}.db',384); qs=[np.array(Qs[r['id']],dtype=np.float32) for r in keys]
        t=time.perf_counter(); idx._matrix=None; idx._load_matrix(); lt=(time.perf_counter()-t)*1000
        ag,tn,tp=check(idx,qs)
        print(f'{slug}-{shape}: identical order {ag:.0%} of {len(qs)}, sqlite-vec {tn:.2f} ms, numpy {tp:.2f} ms, matrix load {lt:.0f} ms')
        for r,q in zip(keys,qs):
            if not r['answerable']: continue
            hy=[u for u,_ in rrf([[u for u,_ in idx.vector_search(q,150)],[u for u,_ in idx.keyword_search(r['question'],150)]])][:150]
            g=set(r['gold'][shape])
            for k in KS: book_gold[k].append(bool(g & set(hy[:k])))
print('books hybrid, gold in candidates (146 runs):', {k:f'{np.mean(v):.3f}' for k,v in book_gold.items()})
# Britannica
idx=Index('/tmp/claude-0/eb_index.db',384); keys=eb_keys(); qs=[np.array(Qs['eb1911/'+r['id']],dtype=np.float32) for r in keys]
t=time.perf_counter(); idx._load_matrix(); lt=(time.perf_counter()-t)*1000
ag,tn,tp=check(idx,qs)
print(f'eb1911: identical order {ag:.0%} of {len(qs)}, sqlite-vec {tn:.1f} ms, numpy {tp:.1f} ms, matrix load {lt:.0f} ms')
N=idx.count(); dfc={}
def df(w):
    if w not in dfc: dfc[w]=idx.db.execute('SELECT count(*) FROM fts WHERE fts MATCH ?',(f'"{w}"',)).fetchone()[0]
    return dfc[w]
def kw(question,k):
    words=[w for w in dict.fromkeys(re.findall(r"[a-z0-9']+",question.lower())) if w not in STOP and len(w)>1]
    kept=[w for w in words if 0<df(w)<=0.02*N]
    if not kept and words:
        r=min(words,key=lambda w: df(w) or N); kept=[r] if df(r) else []
    if not kept: return []
    return [r[0] for r in idx.db.execute("SELECT u.unit_id FROM fts JOIN units u ON u.rid=fts.rowid WHERE fts MATCH ? ORDER BY bm25(fts) LIMIT ?",(' OR '.join(f'"{w}"' for w in kept),k))]
gate={r['id']:r for r in map(json.loads,open('/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/voice-chat/stage07/gate.jsonl')) if r['path']=='flat'}
rows=[]
for r,q in zip(keys,qs):
    hy=[u for u,_ in rrf([[u for u,_ in idx.vector_search(q,150)],kw(r['question'],150)])][:150]
    g=gate[r['id']]
    if r['answerable']:
        rank=hy.index(r['gold'])+1 if r['gold'] in hy else None
        rows.append((r['id'],rank,g['gold_in_candidates'],g['gold_kept']))
    else:
        rows.append((r['id'],None,None,len(g['kept'])==0))
ans=[x for x in rows if x[1] is not None or x[2] is not None]
ans=[x for x,r in zip(rows,keys) if r['answerable']]
print('eb hybrid: my candidates match stage 07 gold_in_candidates:', sum((x[1] is not None)==x[2] for x in ans),'of',len(ans))
for k in KS:
    inc=sum(x[1] is not None and x[1]<=k for x in ans); kept=sum(x[3] and x[1] is not None and x[1]<=k for x in ans)
    print(f'  k {k}: gold in candidates {inc}/40, gold kept by JEV {kept}/40 (stage 07 at 150: {sum(x[3] for x in ans)}/40), JEV requests {k}/question')
print('  gold ranks:',sorted([x[1] for x in ans if x[1]],reverse=True)[:8])
print('  unanswerables kept nothing at 150 (stage 07):',sum(x[3] for x,r in zip(rows,keys) if not r['answerable']),'/ 8; a subset of candidates cannot keep more')
