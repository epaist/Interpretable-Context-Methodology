import sys, json; sys.path.insert(0, r"D:\0001_LOCAL_RAG")
from hces import pilot as P
for l in open(P.out_dir()/"answers.jsonl"):
    r=json.loads(l); a=r["same_as"] or r["arm"]
    c=P.code_checks(P.run_path(r["domain"],r["stage"],a).read_text(encoding="utf-8"))
    if c["over_cap"] or c["bad_placeholders"]: print(r["domain"],r["stage"],r["arm"],c["over_cap"],c["bad_placeholders"][:5])
