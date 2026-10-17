"""Generic table-first extractor for NEP Mumbai University syllabus PDFs.

Idea (measured in spikes/table_probe.py): PyMuPDF find_tables() returns module tables with clean columns
(number | name | content | hours | CO) and continuation tables on the next page. This module only extracts;
topic cleaning lives in nep_topics.py and the accept/reject gate in nep_gate.py.
No network, no LLM. Family quirks are handled by explicit, tested rules, never silently."""
from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass, field
import fitz

CODE_RE = re.compile(r"^(?:\d{7,8}|[A-Z]{2,5}\d{3,5}[A-Z]?)$")
HDR_COURSE = re.compile(r"Course\s*Code", re.I)
HDR_MODULE = re.compile(r"Detail(?:ed)?\s+Content", re.I)
LAB_TITLE = re.compile(r"(?<![A-Za-z])(?:lab|laboratory|workshop|practical|mini[\s-]*project|capstone|seminar|internship)(?![A-Za-z])", re.I)
MAX_PAGE_GAP = 4  # a module table further than this from its course header is NOT attached (reported instead)
STOP_CELL = re.compile(r"^\s*(?:Website|Course\s+Outcomes?|Course\s+Objectives?|Title\s+of\s+Book|Text\s*books?|Reference|Experiment|List\s+of\s+Experiments)", re.I)
STOP_HDR = re.compile(r"Website|Course\s+Outcome|Course\s+Objective|Title\s+of\s+Book|Textbook|Reference|Experiment|Sr\.?\s*No\.?\s*Name\s+of\s+Experiment", re.I)
HOURS_RE = re.compile(r"^\d{1,2}$")
END_CELL = re.compile(r"^\s*(?:Text\s*Books?|Reference\s*Books?|Textbooks?|Web\s+References?|Suggested\s+Reading|Books?\s*:)", re.I)
URL_CELL = re.compile(r"^\s*(?:https?://|www\.)", re.I)

CYR = str.maketrans({"а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "і": "i", "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X"})
BREAK = "␞"   # marks a line break that separates two list items (see _break_aware_text)
STOPEND = {"of", "and", "or", "the", "in", "to", "for", "with", "on", "by", "a", "an", "vs", "from", "using", "as", "at", "into", "between", "its", "their"}

def _break_aware_text(page, bbox):
    """Cell text where a line break that ends a SHORT line and is followed by a capital letter is kept as a list-item separator
    (the PDF text layer joins such items with a plain space otherwise: '... Application Training Error ...')."""
    try:
        d = page.get_text("dict", clip=fitz.Rect(bbox))
        lines = []
        for b in d["blocks"]:
            if b.get("type") != 0: continue
            for ln in b["lines"]:
                t = "".join(sp["text"] for sp in ln["spans"]).strip()
                if t: lines.append((round(ln["bbox"][1]), ln["bbox"][0], ln["bbox"][2], t))
        lines.sort(key=lambda x: (x[0], x[1]))
        if not lines: return None
        width = max(1.0, bbox[2] - bbox[0]); out = []
        for i, (_, x0, x1, t) in enumerate(lines):
            out.append(t)
            if i + 1 < len(lines):
                nxt = lines[i + 1][3]; last = t.rstrip().split()[-1].lower().strip(".,;:") if t.split() else ""
                short = (bbox[2] - x1) > 0.10 * width
                bullet = nxt[:1] in "-•·▪" and len(nxt) > 1
                brk = bullet or (short and nxt[:1].isupper() and not t.rstrip().endswith((",", ";", ":", "-", "–", "/", "(", "&")) and last not in STOPEND)
                out.append(BREAK if brk else " ")
        return unicodedata.normalize("NFKC", "".join(out)).translate(CYR)
    except Exception:
        return None

def _norm(c) -> str:
    c = unicodedata.normalize("NFKC", c).translate(CYR) if c else c
    return re.sub(r"[ \t\r\f\v]+", " ", (c or "").replace("\n", " ")).strip()

@dataclass
class ModuleRow:
    number: str
    name: str
    content: str
    hours: str
    co: str
    page: int

@dataclass
class CourseTables:
    code: str
    title: str
    header_page: int
    ncols: int = 0
    rows: list[ModuleRow] = field(default_factory=list)
    has_module_table: bool = False
    pages: list[int] = field(default_factory=list)
    orphan_tables: list[int] = field(default_factory=list)
    is_lab: bool = False
    unstitched: list[int] = field(default_factory=list)
    cols: list = field(default_factory=list)
    x0: float = 0.0
    x1: float = 0.0
    last_page: int = 0
    content_col: int | None = None
    ended: bool = False
    conflict_pages: list[int] = field(default_factory=list)
    last_y1: float = 0.0

def _course_header(rows):
    """Course header tables: 'Course Code' appears in the first two rows (header may be split over rows)."""
    h = " ".join(_norm(c) for r in rows[:2] for c in r)
    if not (HDR_COURSE.search(h) and re.search(r"Teaching|Course\s*Name|Course\s*Description|Credits|IAT|Theory", h, re.I)):
        return None
    for r in rows[1:4]:
        cells = [_norm(c) for c in r]
        if cells and CODE_RE.match(cells[0].replace(" ", "")) and len(cells) > 1 and re.search(r"[A-Za-z]{3}", cells[1]):
            return cells[0].replace(" ", ""), cells[1]
    return None

def _remap(table, raw, cols, content_col=None):
    """Place every cell into the module table's column by x position (robust to spurious/merged columns)."""
    rows = []
    for tr, texts in zip(table.rows, raw):
        out = [""] * len(cols)
        for bbox, txt in zip(tr.cells, texts):
            if bbox is None or not _norm(txt):
                continue
            cx = (bbox[0] + bbox[2]) / 2
            j = next((i for i, (x0, x1) in enumerate(cols) if x0 - 2 <= cx <= x1 + 2), None)
            if j is None:
                j = min(range(len(cols)), key=lambda i: abs(cx - (cols[i][0] + cols[i][1]) / 2))
            if j == content_col:
                bt = _break_aware_text(table.page, bbox)
                if bt: txt = bt
            out[j] = (out[j] + " " + txt).strip() if out[j] else txt
        rows.append(out)
    return rows

def extract_course_tables(pdf_path: str) -> list[CourseTables]:
    doc = fitz.open(pdf_path)
    courses: list[CourseTables] = []
    cur: CourseTables | None = None
    open_table = False
    for pn in range(len(doc)):
        try:
            tabs = doc[pn].find_tables().tables
        except Exception:
            continue
        for t in tabs:
            raw = t.extract()
            if not raw:
                continue
            head = " ".join(_norm(c) for c in raw[0])
            ch = _course_header(raw)
            if ch:
                if cur is not None and cur.code == ch[0] and cur.header_page == pn + 1:
                    pass   # second header table of the same course on the same page
                else:
                    cur = CourseTables(code=ch[0], title=ch[1], header_page=pn + 1)
                    cur.is_lab = bool(LAB_TITLE.search(ch[1]))
                    courses.append(cur); open_table = False
            # The module header may be row 0 or buried inside a bigger mis-detected table (e.g. merged with the exam scheme).
            # The header row must show the text in ONE real cell of a row that has several cells (a merged banner cell also contains the words).
            hdr_row = next((i for i, r in enumerate(raw)
                            if any(HDR_MODULE.search(_norm(c)) for c in r)
                            and sum(1 for c in t.rows[i].cells if c) >= 3), None)
            if cur is None:
                continue
            if ch and hdr_row is None:
                continue
            if pn + 1 - cur.header_page > MAX_PAGE_GAP and (hdr_row is not None or open_table):
                if hdr_row is not None: cur.orphan_tables.append(pn + 1)
                open_table = False
                continue
            if hdr_row is not None and cur.has_module_table and cur.rows:
                # a second module header under the same course header = a course whose header table was not recognised.
                # Never merge it into this course; report it.
                cur.conflict_pages.append(pn + 1); open_table = False
                continue
            if hdr_row is not None:
                cur.has_module_table = True; open_table = True
                hc = [c for c in t.rows[hdr_row].cells if c]
                cur.cols = [(c[0], c[2]) for c in hc]; cur.ncols = len(cur.cols); cur.x0, cur.x1 = min(c[0] for c in cur.cols), max(c[1] for c in cur.cols)   # extent of the real header cells, not of a merged banner
                hdr_cells = [(c, _norm(txt)) for c, txt in zip(t.rows[hdr_row].cells, raw[hdr_row]) if c]
                cur.content_col = next((i for i, (_, txt) in enumerate(hdr_cells) if HDR_MODULE.search(txt)), None)
                body = _remap(t, raw, cur.cols, cur.content_col)[hdr_row + 1:]
            elif open_table:
                # A continuation must directly follow the previous module-table fragment: below it on the same page,
                # or near the top of the next page, with the same horizontal extent, and must not look like another section.
                same_x = abs(t.bbox[0] - cur.x0) < 25 and abs(t.bbox[2] - cur.x1) < 25
                prev_h = doc[cur.last_page - 1].rect.height
                reached_bottom = cur.last_y1 > prev_h - 300  # a table only continues on the next page if it ran to the page bottom
                follows = (pn + 1 == cur.last_page and t.bbox[1] >= cur.last_y1 - 2) or (pn + 1 == cur.last_page + 1 and t.bbox[1] < 140 and reached_bottom)
                if cur.ended or any(STOP_CELL.match(_norm(c)) for c in raw[0]) or not same_x or not follows:
                    open_table = False
                    continue
                body = _remap(t, raw, cur.cols, cur.content_col)
            else:
                continue
            # Stop at the first row that starts the book/reference list (it can share a table with the last module row).
            trimmed = []
            for r in body:
                trimmed.append(r)
                if any(END_CELL.match(_norm(c)) or URL_CELL.match(_norm(c)) for c in r):
                    cur.ended = True; open_table = False
                    break
            body = trimmed
            cur.last_page, cur.last_y1 = pn + 1, t.bbox[3]
            if pn + 1 not in cur.pages:
                cur.pages.append(pn + 1)
            for r in body:
                cells = [_norm(c) for c in r]
                cells += [""] * (cur.ncols - len(cells))
                if cur.ncols >= 5:
                    num, name, content, hours, co = cells[0], cells[1], cells[2], cells[3], cells[4]
                elif cur.ncols == 4:
                    num, name, content, hours, co = cells[0], "", cells[1], cells[2], cells[3]
                else:
                    continue
                cur.rows.append(ModuleRow(num, name, content, hours, co, pn + 1))
    return courses
