import sys, json, sqlite3, time, numpy as np
sys.path.insert(0,'/mnt/project-files/hces-core/src')
import sqlite_vec
from data import *
U='/mnt/user-data/uploads/0001_LOCAL_RAG/workspaces/voice-chat/stage07/'
ids,V=eb(); pos={u:i for i,u in enumerate(ids)}
text=['']*len(ids)
for l in open(U+'passages.jsonl',encoding='utf-8'):
    r=json.loads(l); text[pos[r['id']]]=r['text']
assert all(text)
d=sqlite3.connect('/tmp/claude-0/eb_index.db'); d.enable_load_extension(True); sqlite_vec.load(d)
d.executescript("""CREATE TABLE units (rid INTEGER PRIMARY KEY, unit_id TEXT UNIQUE NOT NULL, text TEXT NOT NULL);
CREATE VIRTUAL TABLE vec USING vec0(embedding float[384] distance_metric=cosine);
CREATE VIRTUAL TABLE fts USING fts5(text, content='units', content_rowid='rid', tokenize='porter unicode61');""")
t=time.time()
with d:
    d.executemany('INSERT INTO units VALUES (?,?,?)',((i+1,ids[i],text[i]) for i in range(len(ids))))
    d.executemany('INSERT INTO vec(rowid,embedding) VALUES (?,?)',((i+1,V[i].tobytes()) for i in range(len(ids))))
    d.execute("INSERT INTO fts(fts) VALUES('rebuild')")
print('built', round(time.time()-t,1),'s')
