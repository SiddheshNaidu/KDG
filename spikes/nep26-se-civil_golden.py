"""Throwaway: writes DRAFT golden JSONs (topics drafted by reading each course's module text; NOT verified)."""
import json
PDF = "data/raw/2019-scheme/Civil-Engineeing/6.23-N-B.E.-Civil-Engineeing-Sem-III-IV.pdf"


def mk(code, title, pages, mods, notes):
    j = {"family": "nep26-se-civil", "course_code": code, "course_title": title, "source_pdf": PDF,
         "source_pages": pages, "status": "DRAFT - needs human sign-off",
         "modules": [{"number": i + 1, "name": n, "topics": t} for i, (n, t) in enumerate(mods)],
         "draft_notes": notes}
    json.dump(j, open("tests/golden/nep26-se-civil/%s.json" % code, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(code, sum(len(m[1]) for m in mods))


mk("2093112", "Fluid Mechanics", [20, 21, 22, 23], [
    ("Properties of Fluids", ["Mass density", "Weight density", "Specific gravity", "Specific volume", "Viscosity", "Compressibility", "Elasticity", "Surface tension", "Capillarity", "Vapor pressure", "Types of fluids"]),
    ("Fluid Statics", ["Pascal's law", "Hydrostatic law", "Pressure variation in fluids at rest", "Absolute pressure", "Atmospheric pressure", "Gauge pressure", "U tube differential manometers", "Total pressure", "Center of pressure", "Archimedes principle", "Buoyancy", "Meta-Centre", "Metacentric height"]),
    ("Fluid Kinematics and Dynamics", ["Types of fluid flow", "Description of flow pattern", "Lagrangian method", "Eulerian method", "Continuity equation", "Velocity of fluid particles", "Acceleration of fluid particles", "Control volume", "Control surface", "Forces acting on fluid in motion", "Navier Stokes equation", "Euler's equation of motion", "Bernoulli's theorem", "Bernoulli's equation for real fluid", "Applications of Bernoulli's equation"]),
    ("Flow Measurement", ["Venturimeter", "Orificemeter", "Discharge through Venturimeter", "Orifices", "Mouthpieces", "Hydraulic coefficients", "Flow through large rectangular orifice", "Flow through fully submerged orifice", "Flow through partially submerged orifice", "Notches", "Weirs", "Discharge over rectangular notch", "Discharge over triangular notch", "Discharge over trapezoidal notch", "Velocity of approach"]),
    ("Flow Through Pipe", ["Loss of head through pipes", "Darcy-Weisbach equation", "Major losses", "Minor losses", "Hydraulic gradient line", "Total energy gradient line", "Pipes in series", "Equivalent pipes", "Pipes in parallel", "Siphon", "Water hammer phenomenon", "Power transmission through nozzle"]),
    ("Introduction to Laminar and Turbulent Flow", ["Reynolds experiment", "Critical velocity", "Laminar flow through circular pipes", "Prandtl's mixing length theory", "Smooth and rough boundaries", "Velocity distribution in smooth pipes", "Velocity distribution in rough pipes"]),
], "Normal theory course. Sub-item text uses 'Heading : comma list' (e.g. '2.2 Hydrostatic force on surfaces: ...'); topics here are the listed concepts split by hand. Granularity (e.g. Absolute/Atmospheric/Gauge pressure as separate topics) is a draft judgement. Prerequisite line (Mathematics, Physics, Thermodynamics) not turned into topics.")

mk("2093114", "Mechanics of Structures", [28, 29, 30], [
    ("Stresses and Strains in Elastic members", ["Stress", "Strain", "Stress-strain curve", "Elastic moduli", "Relationships between elastic moduli", "Three-dimensional stress and strain", "Poisson's ratio", "Factor of safety", "Bars of varying sections", "Composite sections", "Temperature stresses"]),
    ("Analysis of beams and portal frames", ["Axial force", "Shear force", "Bending moment", "AF, SF and BM diagrams for beams", "Beams with internal hinges", "AF, SF and BM diagrams for portal frames"]),
    ("Area moment of inertia, Bending and Shear stresses in beams", ["Area moment of inertia", "Bending stresses in beams", "Shear stresses in beams"]),
    ("Torsion in Shafts and Stresses in Columns", ["Torsion in solid circular shafts", "Torsion in hollow circular shafts", "Shafts with varying cross sections", "Shafts transmitting power", "Direct stresses in columns", "Bending stresses in columns", "Core of section", "Buckling of columns", "Effective length", "Support conditions", "Euler's formula", "Rankine's formula"]),
    ("Principal planes and stresses", ["Transformation of stress", "Principal planes", "Principal stresses", "Maximum shear stress", "Mohr's circle"]),
    ("Trusses and three hinged parabolic arches", ["Perfect coplanar trusses", "Method of joints", "Method of sections", "Three hinged arches", "Normal thrust", "Radial shear", "Bending moment in three hinged arches", "Symmetrical parabolic three hinged arches", "Unsymmetrical parabolic three hinged arches"]),
], "Odd: sub-items 3.1, 3.2 and 3.3 of module 3 each repeat the module title verbatim ('Area moment of inertia, Bending and Shear stresses in beams') in the PDF (pdf page 29, see docs/evidence/dumps/nep26-se-civil_2093114_p29.txt); module 3 topics are therefore derived from the module title only and are UNKNOWN vs the intended syllabus. Module 3 name itself wraps over 2 lines.")

mk("2094111", "Applied Mathematics for Civil Engineering-II", [52, 53, 54], [
    ("Vector Calculus", ["Solenoidal vector fields", "Irrotational vector fields", "Conservative vector fields", "Line integrals", "Green's theorem", "Stokes' theorem", "Gauss' divergence theorem"]),
    ("Complex Integration", ["Line integral", "Cauchy's integral theorem", "Cauchy's integral formula", "Taylor's series", "Laurent's series", "Singularity", "Zeroes", "Poles of f(z)", "Residues", "Cauchy's residue theorem"]),
    ("Statistical Techniques", ["Karl Pearson's coefficient of correlation", "Spearman's rank correlation coefficient", "Lines of regression"]),
    ("Probability Theory", ["Discrete random variables", "Continuous random variables", "Probability mass function", "Probability density function", "Probability distribution for random variables", "Expectation", "Variance", "Co-variance", "Moments", "Moment generating functions"]),
    ("Probability Distribution and Sampling Theory-I", ["Poisson distribution", "Normal distribution", "Sampling distribution", "Test of hypothesis", "Level of significance", "Critical region", "One-tailed test", "Two-tailed test", "Degree of freedom", "Student's t-distribution", "Significance of single sample mean", "Significance of two independent sample means", "Paired t-test"]),
    ("Sampling theory-II", ["Chi-square test", "Test of goodness of fit", "Test of independence of attributes", "Contingency table", "Analysis of variance", "F-test"]),
], "Self-learning topics (present in every module 1-6 of this course, with spellings 'Self-learning', 'Self- Learning', 'Self- learning', 'Self -learning') are EXCLUDED here; whether they count as topics is UNKNOWN (open_questions.md). Sub-item 3.2 contains letter-spaced text 'r e p e a t e d' (pdf page 53). Parenthetical qualifiers like '(without proof)' dropped.")

mk("2994511", "Business Model Development", [75, 76, 77], [
    ("Introduction to Entrepreneurship", ["Role of entrepreneurship in economic development", "Entrepreneurial process", "Women entrepreneurs", "Corporate entrepreneurship", "Entrepreneurial mindset"]),
    ("Entrepreneurship Development", ["Types of business ownerships", "Proprietorship", "Public companies", "Private companies", "Co-operative businesses", "Micro, Small and Medium Enterprises", "Role of MSMEs in economic development"]),
    ("Start-up financing", ["Cost and revenue models", "Sources of start-up funding", "Angel investors", "Venture capitalists", "Crowd funding", "Government schemes for start-up funding"]),
    ("Intellectual Property Rights (IPR)", ["Types of IPR", "Patents", "Trademarks", "Copyrights", "Patent search and analysis", "Strategies for IPR protection", "Ethics in technology and innovation"]),
    ("Business Model Development", ["Types of business models", "Value proposition", "Customer segments", "Customer relationships", "Channels", "Key partners", "Key activities", "Key resources", "Prototyping", "MVP"]),
    ("Digital Business Management", ["Digital business models", "Subscription model", "Freemium model", "Digital marketing", "Search Engine Optimization", "Search Engine Marketing", "Social media marketing", "Influencer marketing", "Disruption and innovation in digital business"]),
], "Odd: 'LO' (lab outcome) tails instead of CO, and a module's LO tail may span several lines ('LO2,' / 'LO3,' / 'LO4'); this is a lab-category course (2*+2 contact hours, 'Lab Outcomes:') that still has a Module table. Self-learning items (URLs and book titles, modules 1,3,5,6) are EXCLUDED; their status is UNKNOWN.")

mk("2093115", "Fluid Mechanics lab", [31, 32], [],
   "Lab with NO Module table: the detailed syllabus is a 'List of Experiments (Any 6)' table (11 rows, columns Sr No / title / Hrs / LO Mapping) plus a 'List of Assignments / Tutorials' table (6 rows) on pdf page 32 (docs/evidence/dumps/nep26-se-civil_2093115_p32.txt). The schema has no place for experiments; whether experiments/assignments become modules/topics is UNKNOWN (open_questions.md), so modules is [] and no topic is drafted.")
