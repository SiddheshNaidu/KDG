"""Spike: measured facts used in docs/formats/nep26-se-chem-it-{a,b}.md (noise, covers, numbering, header variants,
self-learning policy sentences, module counts, hours). Writes docs/evidence/regex_runs/<family>_facts.txt. Throwaway."""
import re, sys, fitz, collections
sys.path.insert(0, 'spikes')
from nep26_se_chem_it_lines import lines, PDFS
from nep26_se_chem_it_seg import segment
import nep26_se_chem_it_tables as T

FAM = {"a": "nep26-se-chem-it-a", "b": "nep26-se-chem-it-b"}
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep26_se_chem_it_facts.py"
NL = chr(10)
for k in "ab":
    doc = fitz.open(PDFS[k])
    out = ["command: " + CMD, "pdf: " + PDFS[k] + " pages=" + str(len(doc))]
    # 1. cover pages
    covers = []
    for pn in range(1, len(doc) + 1):
        L = [l.strip() for l in doc[pn - 1].get_text().split(NL) if l.strip()][:5]
        if pn > 8 and any(re.match(r"(?i)^(semester\s+(III|IV)|sem\.\s*[–-]\s*(III|IV)|vertical\s*[–-]\s*\d)", x) for x in L[:3]) and pn < len(doc) - 1:
            covers.append((pn, L))
    out.append("cover pages (first non-empty lines match Semester|Sem.|Vertical in first 3 lines, page>8): " + str(covers))
    heads = []
    for pn in list(range(1, 15)) + [len(doc) - 1, len(doc)]:
        L = [l.strip() for l in doc[pn - 1].get_text().split(NL) if l.strip()]
        heads.append((pn, [x[:50] for x in L[:3]]))
    out.append("page heads (first 3 non-empty lines; pages 1-14 and last two): " + str(heads))
    # 2. last non-empty line of each page 14..end-1 : bare number?
    bare = []
    allp = []
    for pn in range(14, len(doc)):
        L = [l.strip() for l in doc[pn - 1].get_text().split(NL) if l.strip()]
        if L:
            allp.append(pn)
            if re.fullmatch(r"\d{1,3}", L[-1]):
                bare.append((pn, L[-1]))
    out.append("pages 14..%d whose last non-empty line is a bare 1-3 digit number: %d of %d: %s" % (len(doc) - 1, len(bare), len(allp), bare))
    # 3. private use bullet / bullet glyphs
    pu = collections.Counter()
    for pn in range(1, len(doc) + 1):
        for ch in doc[pn - 1].get_text():
            if ch in "●•":
                pu[hex(ord(ch))] += 1
    out.append("bullet glyph counts over whole PDF: " + str(dict(pu)))
    # 4. per-course: type, module numbering spelling, header cells, hours sum, prerequisite cell
    segs = segment(k)
    cp = dict(T.course_pages(k))
    out.append("per course: code | pages | module-table rows (first cells) | header cells (col1,col3,col4) | hours list")
    for code, s in segs:
        rows = T.extract(k, code, cp[code], doc)
        mr = [r for r in rows if r[0] not in ("0", "") and not r[0].startswith(("Note", "Sr"))]
        hdr = ""
        # re-read the module-table header row from the raw table
        for pn in cp[code]:
            for tb in doc[pn - 1].find_tables().tables:
                d = tb.extract()
                if d and len(d[0]) == 5 and re.match(r"(?i)^(hours?|hrs)$", T.cleanc(d[0][3])):
                    hdr = [T.cleanc(c) for c in d[0]]
                    break
            if hdr:
                break
        out.append("%s | %s-%s | %s | %s | %s" % (code, s[0][0], s[-1][0], [r[0] for r in mr], hdr, [r[3] for r in mr]))
    # 4b. probes: strings quoted in the docs, with page/line of first hit and extra module-table facts
    probes = ["Mappin", "Scmidt", "Synchronizatio", "Mmultithreading", "Free Online Courses", "and Applications", "L02", "REV2024", "Prerequisite:", "Note: No questions"]
    L_all = list(lines(PDFS[k]))
    for pr in probes:
        hits = [(i, j) for i, j, l in L_all if pr in l]
        out.append("probe %r: %d hits, first %s" % (pr, len(hits), hits[:3]))
    for code, s in segs:
        for pn in cp[code]:
            for tb in doc[pn - 1].find_tables().tables:
                d = tb.extract()
                for r in d:
                    if len(r) == 5 and T.cleanc(r[0]) == "" and T.cleanc(r[1]) != "" and T.cleanc(r[3]) == "" and T.cleanc(r[4]) == "":
                        out.append("empty first cell row (name continuation) %s p%d: %r" % (code, pn, T.cleanc(r[1])[:60]))
    for code, s in segs:
        hs = []
        for pn in cp[code]:
            for tb in doc[pn - 1].find_tables().tables:
                d = tb.extract()
                if d and len(d[0]) == 5 and re.match(r"(?i)^(hours?|hrs)$", T.cleanc(d[0][3])):
                    hs.append((pn, [T.cleanc(c) for c in d[0]][1:5:3] + [T.cleanc(d[0][4])]))
        if len(hs) > 1:
            out.append("course %s has %d tables with an Hours header: %s" % (code, len(hs), hs))
    # 5. self-learning policy sentences (outside module table): sentence mentioning self-learning / self-study without Topics marker
    pol = []
    for code, s in segs:
        for i, j, l in s:
            if re.search(r"(?i)self[\s\-–]*(learning|study)", l) and not re.search(r"(?i)self[\s\-–]*(learning|study)[\s\-–]*topics?\s*:", l) and re.search(r"(?i)question|students|assign|encourage|guidelines|focus|mini", l):
                pol.append("%s p%d l%d: %s" % (code, i, j, l.strip()[:110]))
    out.append("self-learning/self-study mentions that are sentences about policy (not a Topics marker): %d" % len(pol))
    out += pol
    open("docs/evidence/regex_runs/%s_facts.txt" % FAM[k], "w", encoding="utf-8", newline="\n").write(NL.join(out) + NL)
print("done")
