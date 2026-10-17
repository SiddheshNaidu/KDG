"""Merge two independent labelling passes (A = data/labelling/claude, B = data/labelling/pass_B) per course.
Classes: agree (same directed edge in both), a_only, b_only, reverse (same pair, opposite direction in the other pass).
Writes data/labelling/merged/<course>.json and prints agreement statistics. Usage: python scripts/merge_labels.py"""
import json, os, glob, pathlib, collections
A = pathlib.Path("data/labelling/claude"); A2 = pathlib.Path("data/labelling/pass_A"); B = pathlib.Path("data/labelling/pass_B"); OUT = pathlib.Path("data/labelling/merged"); OUT.mkdir(exist_ok=True)
T = json.load(open("data/processed/topics_nep.json", encoding="utf-8"))
rows = []; tot = collections.Counter()
for f in sorted(B.glob("*.json")):
    c = f.stem
    fa = A / f.name if (A / f.name).exists() else A2 / f.name
    if not fa.exists() or c not in T: continue
    ea = {(e["a"], e["b"]) for e in json.load(open(fa))["edges"]}; eb = {(e["a"], e["b"]) for e in json.load(open(f))["edges"]}
    agree = ea & eb; rev = {(a, b) for a, b in ea - eb if (b, a) in eb}; revb = {(b, a) for a, b in rev}
    a_only = ea - eb - rev; b_only = eb - ea - revb
    n = T[c]["n_topics"]; pairs = n * (n - 1)
    # Cohen's kappa over all ordered pairs
    po = 1 - (len(ea ^ eb)) / pairs; pa = len(ea) / pairs; pb = len(eb) / pairs; pe = pa * pb + (1 - pa) * (1 - pb); kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    jacc = len(agree) / max(1, len(ea | eb)); p_ab = len(agree) / max(1, len(ea)); r_ab = len(agree) / max(1, len(eb))
    json.dump(dict(split=T[c]["split"], agree=sorted(agree), a_only=sorted(a_only), b_only=sorted(b_only), reverse=sorted(rev)), open(OUT / f.name, "w"))
    rows.append((c, T[c]["split"], n, len(ea), len(eb), len(agree), len(a_only), len(b_only), len(rev), round(jacc, 2), round(kappa, 2)))
    for k, v in (("a", len(ea)), ("b", len(eb)), ("agree", len(agree)), ("a_only", len(a_only)), ("b_only", len(b_only)), ("rev", len(rev)), ("union", len(ea | eb))): tot[k] += v
print("course | split | topics | A | B | agree | A-only | B-only | reversed | jaccard | kappa")
for r in rows: print(*r, sep=" | ")
print(f"TOTAL A {tot['a']} B {tot['b']} agree {tot['agree']} A-only {tot['a_only']} B-only {tot['b_only']} reversed {tot['rev']} | Jaccard {tot['agree']/max(1,tot['union']):.3f} | agree/A {tot['agree']/max(1,tot['a']):.3f} agree/B {tot['agree']/max(1,tot['b']):.3f}")
