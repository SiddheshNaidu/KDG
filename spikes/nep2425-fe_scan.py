import fitz,glob,re
for f in sorted(glob.glob("data/raw/2024-25-scheme/FE/*.pdf")):
    print("==",f.split("/")[-1])
    for pi,p in enumerate(fitz.open(f),1):
        for i,l in enumerate(p.get_text().split("\n")):
            if re.match(r"^\s*[A-Z]{2,4}\d{3,4}\s*$",l) or re.search(r"DETAILED SYLLABUS|Detailed Syllabus|Prerequisite|Self.?[Ll]earning|Self.?[Ss]tudy|Total Hours|Lab Objectives|Course Objectives|Sr\. *$",l):
                print(pi,i,repr(l[:70]))
