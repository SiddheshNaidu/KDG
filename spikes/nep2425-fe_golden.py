"""Writes tests/golden/nep2425-fe/*.json (DRAFT, hand-drafted from the dumps/pages read in this session) and the topic validity census.
Usage: PYTHONIOENCODING=utf-8 python spikes/nep2425-fe_golden.py"""
import json, sys, collections
sys.path.insert(0, "spikes")
from topic_validity import validate

FAM = "nep2425-fe"
C = {}
C["ESC102"] = ("Basic Electrical and Electronics Engineering", "data/raw/2024-25-scheme/FE/02 Syllabus.pdf", [1, 2], [
    ("DC Circuits", ["Kirchhoff's Laws", "Ideal and Practical Voltage Sources", "Ideal and Practical Current Sources", "Source Transformation",
                     "Mesh Analysis", "Nodal Analysis", "Star-Delta Transformation", "Delta-Star Transformation", "Superposition Theorem",
                     "Thevenin's Theorem", "Norton's Theorem", "Maximum Power Transfer Theorem"]),
    ("AC Circuits", ["Generation of Alternating Voltage", "Average and RMS Values", "Phasor and Phase Difference", "Sums on Phasors",
                     "Single-Phase AC Series and Parallel Circuits", "Real, Reactive and Apparent Power", "Admittance",
                     "Series and Parallel Resonance", "Generation of Three-Phase Voltages", "Star and Delta Connections"]),
    ("Single Phase Transformer", ["Working Principle of Single-Phase Transformer", "Types of Single-Phase Transformer", "Transformation Ratio",
                                  "Practical and Ideal Transformer", "Transformer Losses", "Transformer Efficiency", "Applications of Transformer"]),
    ("Electrical Machines", ["DC Motor", "Three-Phase Induction Motor", "Single-Phase Induction Motor", "BLDC Motor"]),
    ("Special Purpose Diodes", ["Zener Diode", "Zener Diode as Voltage Regulator", "Structure of LED", "LED in Indicative and Lighting Displays"]),
    ("Introduction to Transistors", ["Structure and Operation of BJT", "BJT Configurations", "FET Structure and Operation", "BJT and FET Applications"]),
])
C["BSC103"] = ("Applied Chemistry", "data/raw/2024-25-scheme/FE/Applied Chemistry syllabus 2024-25.pdf", [2, 3], [
    ("Fuels and Combustion", ["Characteristics of Good Fuel", "Calorific Value", "Proximate Analysis of Coal", "Ultimate Analysis of Coal", "Combustion of Coal"]),
    ("Corrosion", ["Types of Corrosion", "Dry or Atmospheric Corrosion", "Wet or Electrochemical Corrosion", "Factors Affecting Rate of Corrosion",
                   "Methods to Control Corrosion", "Corrosion in Electronic Devices"]),
    ("Alloys", ["Purpose of Making Alloys", "Gibbs Phase Rule", "Reduced Phase Rule", "Two-Component System", "Merits and Limitations of Phase Rule"]),
    ("Introduction to Polymers", ["Basic Concepts of Polymers", "Chemical Bonding in Polymers", "Classification of Polymers", "Molecular Weight of Polymers",
                                  "Crystallinity of Polymers", "Glass Transition Temperature", "Mechanical Properties of Polymers",
                                  "Electrical Properties of Polymers", "Optical Properties of Polymers"]),
    ("Introduction to Composites", ["Characteristics of Composites", "Constituents of Composites", "Matrix Phase", "Dispersed Phase", "Classification of Composites"]),
    ("Green Chemistry for Sustainable Development", ["Green Synthesis of Indigo Dye", "Green Synthesis of Adipic Acid", "Green Synthesis of Carbaryl",
                                                     "Supercritical Solvents", "Ionic Liquids", "Biodiesel", "Ethanol as Green Fuel"]),
])
C["ESC101"] = ("Engineering Mechanics", "data/raw/2024-25-scheme/FE/NEW EM SYLLABUS 2024-25.pdf", [2, 3], [
    ("System of Forces", ["Classification of Force Systems", "Principle of Transmissibility", "Composition of Forces", "Resolution of Forces",
                          "Resultant of Coplanar Force System", "Moment of Force", "Resultant of Non-Coplanar Space Force"]),
    ("Centroid", ["Centroid"]),
    ("Equilibrium of Force system and Friction", ["Conditions of Equilibrium", "Couples", "Equilibrium of Rigid Bodies", "Free Body Diagrams",
                                                  "Types of Beams", "Types of Supports and Reactions", "Reactions at Supports of Beams", "Friction"]),
    ("Kinematics of particle and rigid bodies", ["Motion of Particle with Variable Acceleration", "Motion Along Plane Curved Path",
                                                 "Velocity and Acceleration in Rectangular Components", "Tangential and Normal Components of Acceleration"]),
    ("Kinetics of particle", ["Force and Acceleration", "Equations of Dynamic Equilibrium", "Principle of Linear Impulse and Momentum", "Impact and Collision",
                              "Law of Conservation of Momentum", "Coefficient of Restitution", "Direct Central Impact", "Oblique Central Impact",
                              "Loss of Kinetic Energy in Collision"]),
    ("Introduction to Robot Kinematics", ["Robot Kinematics"]),
])
C["AEC101"] = ("Professional Communication and Ethics", "data/raw/2024-25-scheme/FE/Professional_Comm._Ethics_Theory_Sem_I 2024-25.pdf", [2, 3, 4, 5], [
    ("Fundamentals of Communication", ["Basic Concepts of Communication", "Process of Communication", "Methods of Communication",
                                       "Barriers to Communication", "Organisational Communication"]),
    ("Developing Basic Listening Skills", ["Concepts of Active Listening", "Enhancing Listening Proficiency"]),
    ("Developing Basic Speaking Skills", ["Conversational Activities - Monologues", "Conversational Activities - Dialogues", "Pronunciation",
                                          "Stress and Rhythm", "Intonation"]),
    ("Developing Basic Reading Skills", ["Verbal Aptitude", "Grammar", "Techniques to Improve Reading Fluency and Comprehension",
                                         "Reading and Summarisation Skills"]),
    ("Developing Basic Writing Skills", ["Coherence and Cohesion in Writing", "Seven Cs of Business Writing", "Format and Types of Formal Letters",
                                         "Writing User Instructions", "Social Media and e-Commerce Content Creation"]),
    ("Ethical and Managerial Skills for Engineers", ["Team Building", "Goal Setting", "Fairness and Honesty", "Difference between Values and Ethics",
                                                     "Ethical Principles", "Ethical Use of AI Tools", "Plagiarism and Copyright Infringement",
                                                     "Ethical-Dilemma Case Studies"]),
])
C["VSEC102"] = ("C Programming", "data/raw/2024-25-scheme/FE/Syllabus-C Prog.pdf", [1, 2], [
    ("Fundamentals of C-Programming", ["Character Set", "Identifiers and Keywords", "Data Types", "Constants", "Variables", "Arithmetic Operators",
                                       "Relational and Logical Operators", "Assignment Operators", "Unary Operators", "Conditional Operator",
                                       "Bitwise Operators", "Comma Operator", "Expressions", "Statements", "Library Functions", "Preprocessor",
                                       "Data Input and Output Functions", "Structure of C Program"]),
    ("Control Structures", ["If Statement", "If-Else Statement", "Multiway Decision", "While Loop", "Do-While Loop", "For Loop",
                            "Nested Control Structure", "Switch Statement", "Continue Statement", "Break Statement", "Goto Statement"]),
    ("Functions and Parameter", ["Function Definition", "Accessing a Function", "Function Prototype", "Passing Arguments to a Function", "Recursion",
                                 "Auto Storage Class", "Extern Storage Class", "Static Storage Class", "Register Storage Class"]),
    ("Arrays, String Structure", ["Array Declaration and Definition", "Accessing Array Elements", "One-Dimensional Array", "Multidimensional Array",
                                  "Strings", "Array of Strings", "String.h Functions", "Structure Declaration and Initialization",
                                  "Structure within Structure", "Operations on Structures", "Array of Structures"]),
    ("Pointer", ["Pointers", "Address Operator", "Pointer Variables", "Dereferencing Pointer", "Void Pointer", "Pointer Arithmetic",
                 "Pointers to Pointers", "Pointers and Arrays"]),
    ("Files", ["File Operations", "Opening a File", "Closing a File", "Creating a File", "Reading a File", "Processing a File"]),
])
census = collections.Counter()
total = 0
viol = []
for code, (title, pdf, pages, mods) in C.items():
    out = {"family": FAM, "course_code": code, "course_title": title, "source_pdf": pdf, "source_pages": pages,
           "status": "DRAFT - needs human sign-off",
           "modules": [{"number": str(i), "name": n, "topics": t} for i, (n, t) in enumerate(mods, 1)]}
    json.dump(out, open(f"tests/golden/{FAM}/{code}.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    for m in out["modules"]:
        for t in m["topics"]:
            total += 1
            v = validate(t)
            for r in v:
                census[r] += 1
            if v:
                viol.append(f"{code} module {m['number']}: {t!r} -> {v}")
rules = ["R1_word_count_1_to_8", "R2_len_over_80_chars", "R3_contains_colon_or_semicolon", "R4_generic_heading", "R5_procedural",
         "R6_leading_numbering", "R7_hours_or_CO_leak", "R8_no_letters"]
lines = [f"command: PYTHONIOENCODING=utf-8 python spikes/nep2425-fe_golden.py", "scope: topics of the 5 DRAFT golden courses tests/golden/nep2425-fe/*.json (these are hand-drafted, not parser output)",
         f"total topics: {total}", f"courses: {len(C)}"] + [f"{r}: {census[r]}" for r in rules] + [f"topics with at least one violation: {len(viol)}"] + ["violations:"] + (["  " + v for v in viol] or ["  (none)"])
per = {code: sum(len(m['topics']) for m in json.load(open(f'tests/golden/{FAM}/{code}.json', encoding='utf-8'))['modules']) for code in C}
lines.append("topics per course: " + json.dumps(per))
open("docs/evidence/regex_runs/nep2425-fe_topic_validity.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
