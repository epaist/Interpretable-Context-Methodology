import json, sqlite3, numpy as np
U='/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/'
IDX=U+'hces-lab/kb/index/'
def book(slug, shape):
    d=sqlite3.connect(IDX+f'{slug}-{shape}.db')
    chunks={cid:np.frombuffer(b,dtype=np.float32).reshape(-1,384) for cid,b in d.execute('select rowid,vectors from vec_vector_chunks00')}
    rows=d.execute('select u.rid,u.unit_id,r.chunk_id,r.chunk_offset from units u join vec_rowids r on r.rowid=u.rid order by u.rid').fetchall()
    ids=[r[1] for r in rows]; V=np.stack([chunks[c][o] for _,_,c,o in rows]).astype(np.float32)
    return ids, V, d
def eb():
    ids=json.load(open(U+'voice-chat/stage07/index/eb1911_vectors.ids.json'))
    V=np.load(U+'voice-chat/stage07/index/eb1911_vectors.npy', mmap_mode='r')
    return ids, np.asarray(V, dtype=np.float32)
def queries():
    ids=json.load(open(U+'hces-lab/scratch/spatial/query_ids.json'))
    Q=np.load(U+'hces-lab/scratch/spatial/query_vectors.npy')
    return dict(zip(ids,Q))
def book_keys(slug):
    return [r for r in map(json.loads,open(U+'hces-lab/stages/02-test-material/output/answer-key.jsonl')) if r['volume']==slug]
def eb_keys():
    return [r for r in map(json.loads,open(U+'voice-chat/stage07/questions.jsonl'))]
def parent_of(uid):
    p=uid.split('/')
    return '/'.join(p[:-1])
