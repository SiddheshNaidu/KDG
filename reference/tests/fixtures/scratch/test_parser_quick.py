import sys; sys.path.insert(0, '.')
from app.parser.nep_syllabus_parser import parse_nep_pdf_bytes

with open('tests/fixtures/nep_sem5_6.pdf', 'rb') as f:
    data = f.read()

ok, courses, t = parse_nep_pdf_bytes(data)
print(f'Gate: {ok}, Courses: {len(courses)}, Time: {t:.2f}s')
for c in courses:
    print(f'  {c.code} | {c.title} | {c.kind} | modules={len(c.modules)} | topics={len(c.topics)}')
    if c.code == '2345113':
        names = [tp["name"] for tp in c.topics[:15]]
        print(f'    Sample topics: {names}')

