"""Spike: run every documented regex against EVERY course of both sub-families and write docs/evidence/regex_runs/*.
Throwaway; no product code. Run: PYTHONIOENCODING=utf-8 python spikes/nep26_se_chem_it_runs.py"""
import re, sys, json, collections, fitz, os
sys.path.insert(0, 'spikes')
from nep26_se_chem_it_lines import lines, PDFS
from nep26_se_chem_it_seg import segment, CODE
import nep26_se_chem_it_tables as T
import nep26_se_chem_it_mod as M
from topic_validity import validate

FAM = {"a": "nep26-se-chem-it-a", "b": "nep26-se-chem-it-b"}
OUT = "docs/evidence/regex_runs"
CMD = "PYTHONIOENCODING=utf-8 python spikes/nep26_se_chem_it_runs.py"
REG = {
    "detect": r"(?s)Item No\.\s*[–-]\s*6\.\d+\s*\(N\).*?As Per NEP 2020|As Per NEP 2020.*?Item No\.\s*[–-]\s*6\.\d+\s*\(N\)",
    "course_header": r"(?m)^Course\s*\nCode\s*\n(?:.*\n){0,38}?[ \t]*(\d{7})[ \t]*\n",
    "title_end": r"^\s*(?:\d{1,2}|--|–|\d\*\+\d)\s*$",
    "prereq_row": r"(?m)^0[ \t]*\n[ \t]*Prerequisites?\.?[ \t]*\n",
    "prereq_heading": r"(?m)^Prerequisites?[ \t]*:[ \t]*$",
    "hours_cell": r"^\d{1,2}$",
    "co_cell": r"^(?:(?:CO|LO|L0|L)?\s?\d+)(?:\s*,\s*(?:CO|LO|L0|L)?\s?\d+)*$",
    "selflearning": r"(?i)self[\s\-–]*(?:learning|study)[\s\-–]*(?:topics?)?\s*:?",
    "stop_books": r"(?im)^\s*(?:Text\s*Books?|Textbooks?|References?|Reference\s+Books?|Assessment)\b.*$",
}
ITEM = r"Item No\.\s*[–-]\s*6\.\d+\s*\(N\)"


def w(path, txt):
    open(path, "w", encoding="utf-8").write(txt)


def page_text(doc, pn):
    return doc[pn - 1].get_text()


def overview_codes(k):
    cnt = collections.defaultdict(list)
    for i, j, l in lines(PDFS[k]):
        m = CODE.match(l)
        if m:
            cnt[i].append(m.group(1))
    ov = []
    for i, cs in cnt.items():
        if len(set(cs)) >= 3:
            ov += cs
    return list(dict.fromkeys(ov)), sorted(i for i, cs in cnt.items() if len(set(cs)) >= 3)


def course_text(segl):
    return "".join(l + "\n" for _, _, l in segl)


def modrows(rows):
    return [r for r in rows if r[0] not in ("0", "") and not r[0].startswith(("Note", "Sr"))]


def main():
    for k in "ab":
        fam = FAM[k]
        doc = fitz.open(PDFS[k])
        segs = segment(k)
        cp = dict(T.course_pages(k))
        ocodes, opages = overview_codes(k)
        LL = list(lines(PDFS[k]))
        mods = {code: T.extract(k, code, cp[code], doc) for code, _ in segs}
        # detect
        txt = "".join(page_text(doc, p) for p in range(1, 7))
        m = re.search(REG["detect"], txt)
        w(f"{OUT}/{fam}_detect.txt",
          f"command: {CMD}\nregex: {REG['detect']}\nscope: text of PDF pages 1-6, {PDFS[k]}\n"
          f"matched/total: {1 if m else 0}/1 PDF (positive test only; no other-family PDF tested here)\n"
          f"item_no_found: {re.findall(ITEM, txt)}\nfailures: {'none' if m else 'DETECT FAILED'}\n")
        # course header
        found = {}
        for p in range(1, len(doc) + 1):
            if p in opages:
                continue
            for mm in re.finditer(REG["course_header"], page_text(doc, p)):
                found.setdefault(mm.group(1), p)
        fails = [f"code {c}: no header match on any detail page; appears only on overview pages {opages}" for c in ocodes if c not in found]
        extra = [c for c in found if c not in ocodes]
        w(f"{OUT}/{fam}_course_header.txt",
          f"command: {CMD}\nregex: {REG['course_header']}\n"
          f"scope: page.get_text() of every non-overview page of {PDFS[k]}; overview pages (>=3 distinct 7-digit lines) = {opages}\n"
          f"oracle: distinct 7-digit codes on overview pages = {len(ocodes)}\n"
          f"matched/total: {len([c for c in ocodes if c in found])}/{len(ocodes)} (oracle codes that have a detail header)\n"
          f"detail headers found: {len(found)}; codes found in detail pages but not in oracle: {extra}\nattempts: 1\n"
          f"failures (verbatim):\n" + ("\n".join(fails) if fails else "none") + "\n")
        # title
        rows = []
        tf = []
        for code, s in segs:
            texts = [l.strip() for _, _, l in s]
            idx = [n for n, t in enumerate(texts) if t == code]

            def title_at(n):
                t = []
                for q in range(n + 1, min(n + 8, len(texts))):
                    if re.match(REG["title_end"], texts[q]):
                        break
                    if texts[q]:
                        t.append(texts[q])
                return " ".join(t)

            t1 = title_at(idx[0])
            t2 = title_at(idx[1]) if len(idx) > 1 else None
            if t2 is None:  # oracle fallback: overview-table title
                ot = [(i, j, l.strip()) for i, j, l in LL if i in opages]
                tx = [t for _, _, t in ot]
                oi = [n for n, t in enumerate(tx) if t == code]
                if oi:
                    t2 = "OVERVIEW:" + (lambda n: " ".join(x for x in (tx[q] for q in range(n + 1, min(n + 8, len(tx))) if True) if x)) (oi[0])
                    # overview rows are title then scheme tokens: cut with same terminator
                    tt = []
                    for q in range(oi[0] + 1, min(oi[0] + 8, len(tx))):
                        if re.match(REG["title_end"], tx[q]):
                            break
                        if tx[q]:
                            tt.append(tx[q])
                    t2 = " ".join(tt)
            norm = lambda x: re.sub(r"[\s\-–]", "", x or "")
            ok = t2 is not None and norm(t1) == norm(t2)
            rows.append((code, ok, t1, t2))
            if not ok:
                tf.append(f"{code} page {s[0][0]}: table1='{t1}' | table2='{t2}'")
        w(f"{OUT}/{fam}_title_wrap.txt",
          f"command: {CMD}\nregex (terminator line after the code line; lines before it are joined with a space): {REG['title_end']}\n"
          f"oracle: the same title rebuilt from the SECOND header table on the same page (repeated code line), compared ignoring spaces and hyphens\n"
          f"matched/total: {sum(1 for r in rows if r[1])}/{len(rows)}\ntitles (table 1 reconstruction):\n"
          + "\n".join(f"{c}\t{t1}" for c, ok, t1, t2 in rows) + "\nfailures (verbatim):\n" + ("\n".join(tf) if tf else "none") + "\n")
        # prereq row
        pr = []
        fl = []
        for code, s in segs:
            ctext = course_text(s)
            raw = bool(re.search(REG["prereq_row"], ctext))
            tbl = any(r[0] == "0" for r in mods[code])
            hd = bool(re.search(REG["prereq_heading"], ctext))
            pr.append((code, raw, tbl, hd))
            if raw != tbl and mods[code]:
                fl.append(f"{code}: raw prereq_row regex={raw} but table-oracle row 0 present={tbl}")
        modc = [r for r in pr if mods[r[0]]]
        w(f"{OUT}/{fam}_prereq_row.txt",
          f"command: {CMD}\nregex row: {REG['prereq_row']}\nregex heading: {REG['prereq_heading']}\nscope: raw lines of each course segment\n"
          f"oracle: table-based extraction (find_tables) row whose first cell is '0'\n"
          f"matched/total (raw row regex agrees with table oracle, courses having a module table): {len(modc) - len(fl)}/{len(modc)}\n"
          f"courses with a Prerequisite row (table oracle): {[r[0] for r in modc if r[2]]}\n"
          f"courses with module table but no row 0: {[r[0] for r in modc if not r[2]]}\n"
          f"courses with a 'Prerequisite:' heading line: {[r[0] for r in pr if r[3]]}\n"
          f"courses with neither: {[r[0] for r in pr if not r[2] and not r[3]]}\nfailures (verbatim):\n" + ("\n".join(fl) if fl else "none") + "\n")
        # module row
        mr = []
        mf = []
        for code, s in segs:
            tb = modrows(mods[code])
            if not tb:
                continue
            raw = M.rows(s)
            n_raw = None if raw is None else len(raw)
            seq_raw = [x["num"] for x in raw] if raw else []
            seq_tb = [r[0] for r in tb]
            ok = seq_raw == seq_tb
            mr.append((code, ok, n_raw, len(tb)))
            if not ok:
                mf.append(f"{code}: raw-line rows={n_raw} tokens={seq_raw} | table-oracle rows={len(tb)} tokens={seq_tb}")
        w(f"{OUT}/{fam}_module_row.txt",
          f"command: {CMD}\nmethod A (raw lines, spikes/nep26_se_chem_it_mod.py): scope starts at a line 'Detailed Content' (case-insens) and ends at first Text Books/References/Assessment heading line; "
          f"a row starts at a line equal to the expected next number in spelling N, 0N or Roman, when the next line is not a CO/LO tail.\n"
          f"method B (table-based, spikes/nep26_se_chem_it_tables.py): page.find_tables(); module table = 5 columns whose 4th header is Hours/Hrs and whose 5th matches (CO|LO) Mapping; "
          f"rows with empty first two cells are merged into the previous row.\n"
          f"oracle for method A = method B first-cell token sequence (rows not '0', 'Note...', 'Sr...', empty); a match needs an equal token sequence, not just an equal count\n"
          f"matched/total (A equals B, courses having a module table): {sum(1 for r in mr if r[1])}/{len(mr)}\nfailures (verbatim):\n" + ("\n".join(mf) if mf else "none") + "\n")
        # hours / co tails
        hr = []
        cr = []
        hf = []
        cf = []
        for code, s in segs:
            for r in modrows(mods[code]):
                okh = re.match(REG["hours_cell"], r[3]) is not None
                okc = re.match(REG["co_cell"], re.sub(r"\s+", " ", r[4])) is not None
                hr.append(okh)
                cr.append(okc)
                if not okh:
                    hf.append(f"{code} module {r[0]}: hours cell='{r[3]}'")
                if not okc:
                    cf.append(f"{code} module {r[0]}: co cell='{r[4]}'")
        w(f"{OUT}/{fam}_hours_tail.txt",
          f"command: {CMD}\nregex: {REG['hours_cell']}\nscope: Hours cell (4th column) of every module row from method B\nmatched/total: {sum(hr)}/{len(hr)}\nfailures (verbatim):\n"
          + ("\n".join(hf) if hf else "none") + "\n")
        w(f"{OUT}/{fam}_co_tail.txt",
          f"command: {CMD}\nregex: {REG['co_cell']}\nscope: CO/LO Mapping cell (5th column, whitespace-collapsed) of every module row from method B\nmatched/total: {sum(cr)}/{len(cr)}\nfailures (verbatim):\n"
          + ("\n".join(cf) if cf else "none") + "\n")
        # self learning
        sl = []
        for code, s in segs:
            raw_hits = [re.sub(r"\s+", " ", m.group(0)) for m in re.finditer(REG["selflearning"], course_text(s))]
            tb_hits = []
            for r in mods[code]:
                tb_hits += [re.sub(r"\s+", " ", m.group(0)) for m in re.finditer(REG["selflearning"], r[2] + " " + r[1])]
            sl.append((code, len(raw_hits), len(tb_hits), raw_hits, tb_hits))
        w(f"{OUT}/{fam}_selflearning.txt",
          f"command: {CMD}\nregex: {REG['selflearning']}\nscope: (1) raw lines of each course segment joined by newline; (2) module-table cells (method B: name + content)\n"
          f"per course: code, hits in raw course text, hits in module-table cells, distinct spellings (whitespace-collapsed)\n"
          + "\n".join(f"{c}\traw={a}\ttable={b}\t{sorted(set(x))}" for c, a, b, x, y in sl)
          + f"\ncourses with >=1 raw hit: {sum(1 for r in sl if r[1])}/{len(sl)}\n"
          f"no independent ground truth exists for the true number of self-learning items (UNKNOWN)\n"
          f"spelling inventory (raw): {dict(collections.Counter(h for r in sl for h in r[3]))}\n")
        # stop markers
        sf = []
        st = []
        STOPB = re.compile(REG["stop_books"])
        for code, s in segs:
            ok = bool(STOPB.search(course_text(s)))
            st.append(ok)
            if not ok:
                sf.append(f"{code} pages {s[0][0]}-{s[-1][0]}: no Text Books/Textbooks heading line")
        w(f"{OUT}/{fam}_stop_books.txt",
          f"command: {CMD}\nregex: {REG['stop_books']}\nscope: raw lines of every course segment (cut at the next course header only)\nmatched/total: {sum(st)}/{len(st)}\nfailures (verbatim):\n"
          + ("\n".join(sf) if sf else "none") + "\n")
        # topic validity census
        SPL = re.compile(r"\s*[;,]\s*|\s*\.\s+(?=[A-Z])|\s*[●•]\s*")
        SLM = re.compile(REG["selflearning"])
        cnt = collections.Counter()
        tot = 0
        percourse = {}
        ex = collections.defaultdict(list)
        bad = 0
        for code, s in segs:
            n = 0
            for r in modrows(mods[code]):
                for part in SLM.split(r[2]):
                    for t in SPL.split(part):
                        t = t.strip(" .:-–")
                        if not t:
                            continue
                        n += 1
                        tot += 1
                        v = validate(t)
                        bad += 1 if v else 0
                        for x in v:
                            cnt[x] += 1
                            if len(ex[x]) < 3:
                                ex[x].append(f"{code}: {t[:70]}")
            percourse[code] = n
        nomod = [c for c, _ in segs if not modrows(mods[c])]
        w(f"{OUT}/{fam}_topic_validity.txt",
          f"command: {CMD}\nvalidator: spikes/topic_validity.py validate() (rules R1-R8, docs/formats/topic_validity.md)\n"
          f"candidate topics: NAIVE spike splitter (not a parser): module content cell split on ';' ',' '. <Capital>' and bullets after cutting at every self-learning marker; module name excluded.\n"
          f"scope: courses having a module table ({len(segs) - len(nomod)} of {len(segs)}); excluded (no module table): {nomod}\n"
          f"total candidate topics: {tot}\ncandidates violating >=1 rule: {bad}\nviolations by rule id (a candidate may violate several): {dict(sorted(cnt.items()))}\n"
          f"candidates per course: {percourse}\nexamples (first 3 per rule):\n" + "\n".join(f"{x}: {ex[x]}" for x in sorted(ex)) + "\n")
        json.dump(mods, open(os.environ.get("SCRATCH", "/tmp") + f"/mods_{k}.json", "w", encoding="utf-8"), ensure_ascii=False)
    # discriminating detection over ALL pdfs under data/raw (read-only)
    import glob
    DET = [r"As Per NEP 2020", r"U\.G\. Second Year Programme", r"Semester\s+III\s*&\s*IV",
           r"Name of the Programme\s*[–-]\s*B\.E\.\s*\((?:Chemical Engineering|Information Technology)\)"]
    allp = sorted(glob.glob("data/raw/**/*.pdf", recursive=True))
    hits = {}
    for pdf in allp:
        dd = fitz.open(pdf)
        t = "".join(dd[i].get_text() for i in range(min(6, len(dd))))
        hits[pdf.replace(os.sep, "/")] = all(re.search(r, t) for r in DET)
    for k in "ab":
        pos = [p for p, h in hits.items() if h]
        FAMPDF = ("6.40-N-Chemical-Engineering-Sem-III-IV.pdf", "6.34-N-B.E.-Information-Technology-Sem-III-IV.pdf")
        fp = [q for q in pos if not q.endswith(FAMPDF)]
        NL = chr(10)
        w(f"{OUT}/{FAM[k]}_detect_all_pdfs.txt", NL.join([
            "command: " + CMD,
            "regexes (ALL four must match on text of PDF pages 1-6): " + str(DET),
            "scope: every PDF under data/raw (" + str(len(allp)) + " files)",
            "PDFs matched: " + str(pos),
            "expected positives: the two PDFs of this family (Chem-Eng 6.40 = sub-family a, IT 6.34 = sub-family b)",
            "matched/total: " + str(sum(1 for q in pos if q.endswith(FAMPDF))) + "/2 expected positives; false positives: " + str(fp),
            "note: the detection cannot say a vs b; a = Chemical Engineering programme name, b = Information Technology programme name", ""]))
    HIST = {
        "co_tail": "attempt 1: ^(?:(?:CO|LO|L0|L)\\s?\\d+)(?:\\s*,\\s*(?:CO|LO|L0|L)\\s?\\d+)*$ -> chem-it-a 65/71 (all 6 failures: 2074112 modules 1-6, cell is a bare digit '1'..'6'); chem-it-b 78/78\n"
                   "attempt 2 (current): bare digit allowed via optional prefix (final regex above) -> see matched/total above",
        "title_wrap": "attempt 1: terminator ^\\s*(?:\\d{1,2}|--?|–|\\d\\*\\+\\d)\\s*$ (lone '-' counted as terminator) -> a 16/17 (2994512: second table has no code line, oracle missing), b 12/13 (2344411: table1='Mini-Project - Programming Paradigm' vs table2='Mini-Project', the lone '-' line cut the title)\n"
                      "attempt 2 (current): lone '-' removed from terminator; oracle falls back to the overview-table title when no second table exists -> see matched/total above",
        "module_row": "attempt 1: scope start = line 'Detailed Content' only, single table -> a 11/12 (2993512 header says 'Topic Description'; raw rows None), b 10/12 (2343115 header says 'Suggested list of experiments'; 2344411 has two module tables)\n"
                      "attempt 2: scope start = 'DETAILED SYLLABUS' heading or 'Detailed Content' line, multiple scopes, counter restarts -> a 11/12 and b 12/12 by row COUNT only\n"
                      "attempt 3 (current, FINAL): also reject a number-like line followed by a dash cell (row 0 hours '01' then '--'), and the oracle comparison was tightened from equal row count to equal first-cell TOKEN sequence -> see matched/total above. No attempt 4 (limit 3): remaining mismatches are hours cells such as '05'/'06'/'04' read as row numbers because blank lines sit between the hours line and the CO/LO line; marked PARTIAL.",
        "stop_books": "attempt 1: (?m)^\\s*(?:Text\\s*Books?|Textbooks?)\\b.*$ (case-sensitive) -> a 12/17 (2073111, 2073116, 2073611, 2074115, 2074411), b 12/13 (2343114: 'Text books' lower-case b)\n"
                      "attempt 2 (current): case-insensitive and also References / Reference Books / Assessment as a stop heading -> see matched/total above",
    }
    for k in "ab":
        for nm, txt in HIST.items():
            with open(f"{OUT}/{FAM[k]}_{nm}.txt", "a", encoding="utf-8") as f:
                f.write("attempt history (max 3 attempts per regex):\n" + txt + "\n")
    print("done")


if __name__ == "__main__":
    main()
