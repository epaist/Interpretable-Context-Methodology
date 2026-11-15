import sys; sys.path.insert(0, r"D:\0001_LOCAL_RAG")
from hces import gate as G, pilot as P, sections as S
from hces.config import load
from hces.store import Store
from hces.passages import TokenCounter
from hces.arms import scored
from hces.rollup import fill
from hces.units import Unit
cfg=load(); st=Store(cfg.results_store); cnt=TokenCounter()
for d, desc in P.domains().items():
    for s in P.stage_dirs():
        if s.name not in ("01-discovery","05-validation","03-scaffolding"): continue
        allu,_=G.stage_units(s,S.root(),cnt)
        rub=G.task_rubric(P.qid(d,s),s.name,P.task_text(s,desc))
        j=G.judgments(st,rub.rubric_id)
        by={u["id"]:Unit(u["id"],"",tokens=u["tokens"]) for u in allu}
        kept,cut=fill(scored(by,j,rub,[u["id"] for u in allu]),2000,G.frozen())
        print(d,s.name)
        for x,why in cut: print("   CUT",x.unit_id.split("/")[-1],x.tokens,round(x.score,2),round(x.critical_p,2),why)
