import sys; sys.path.insert(0, '.')
from app.parser.nep_syllabus_parser import parse_nep_pdf_bytes, is_syllabus

# Test 1: calendar text must fail gate
calendar = "Oct 20, 2026 Tuesday all subjects DIWALI BREAK Nov 2-7 Mod. 1-3 SEAP carried from original plan UNIT TEST 2"
print("Gate on calendar:", is_syllabus(calendar))  # must be False

# Test 2: Parse fixture
with open('tests/fixtures/nep_sem5_6.pdf', 'rb') as f:
    data = f.read()

ok, courses, t = parse_nep_pdf_bytes(data)
print(f'Gate: {ok}, Courses: {len(courses)}')

# Check golden topics
for c in courses:
    names_lower = [tp["name"].lower() for tp in c.topics]
    
    if c.code == '2345113':
        print(f'\n2345113 Web Technology: {len(c.modules)} modules, {len(c.topics)} topics')
        must_have = ['arrow functions', 'state and props', 'hooks', 'crud operations', 'event loops', 'express router', 'rest api', 'model-view']
        must_not = ['asynchronous javascript', 'react vs angular', 'next.js framework', 'fastapi', 'react native', 'query optimization', 'environment setup', 'first app', 'installation']
        for t_name in must_have:
            found = any(t_name in n for n in names_lower)
            print(f'  MUST {t_name}: {"OK" if found else "MISSING"}')
        for t_name in must_not:
            found = any(t_name in n for n in names_lower)
            print(f'  MUST NOT {t_name}: {"PRESENT (BAD)" if found else "OK"}')
    
    if c.code == '2345111':
        print(f'\n2345111 SE: {len(c.modules)} modules, {len(c.topics)} topics')
        must_have = ['waterfall', 'cocomo', 'rmmm', 'scrum', 'kanban', 'regression']
        for t_name in must_have:
            found = any(t_name in n for n in names_lower)
            print(f'  MUST {t_name}: {"OK" if found else "MISSING"}')
    
    if c.code == '2345112':
        print(f'\n2345112 AI/ML: {len(c.modules)} modules, {len(c.topics)} topics')
        must_have = ['breadth first search', 'a* algorithm', 'linear regression', 'k-means', 'confusion matrix', 'roc curve']
        for t_name in must_have:
            found = any(t_name in n for n in names_lower)
            print(f'  MUST {t_name}: {"OK" if found else "MISSING"}')

# Check Self-Learning leakage
for c in courses:
    for tp in c.topics:
        if 'self' in tp["name"].lower() and 'learning' in tp["name"].lower():
            print(f'SL LEAKAGE: {tp["name"]} in {c.code}')
        if 'online resource' in tp["name"].lower() or 'explore' in tp["name"].lower():
            print(f'SL content leakage: {tp["name"]} in {c.code}')
print('Self-learning check done.')

