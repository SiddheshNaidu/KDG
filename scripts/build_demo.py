"""Embed demo/graph_data.json into demo/kdg_demo.template.html -> demo/kdg_demo.html (single self-contained file, no network)."""
import json
t = open("demo/kdg_demo.template.html", encoding="utf-8").read()
d = open("demo/graph_data.json", encoding="utf-8").read()
assert "/*DATA*/null" in t
open("demo/kdg_demo.html", "w", encoding="utf-8").write(t.replace("/*DATA*/null", d))
print("built demo/kdg_demo.html")
