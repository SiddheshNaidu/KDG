"""Writes DRAFT golden courses for family nep26-se-core. Topics drafted by hand from the PDF text (read per course); self-learning topics excluded; prerequisite row (module 0) excluded.
Page ranges come from the course segmenter. Never marked verified."""
import sys, json, importlib, os
sys.path.insert(0, "spikes")
E = importlib.import_module("nep26-se-core_extract")
TV = importlib.import_module("topic_validity")
FAM = "nep26-se-core"
CE = E.L.PDFS[3]
CSE = E.L.PDFS[4]
G = {}
G[(CE, "2113111")] = [
 ("I", "Linear Algebra (Theory of Matrices)", ["Characteristic equation", "Eigenvalues", "Eigenvectors", "Properties of eigenvalues and eigenvectors", "Cayley-Hamilton theorem", "Reduction of higher degree polynomials", "Similarity of matrices", "Diagonalizable matrices", "Non-diagonalizable matrices"]),
 ("II", "Linear and Non-Linear Programming Problems", ["Types of solutions", "Standard form of LPP", "Canonical form of LPP", "Basic and feasible solutions", "Slack variables", "Surplus variables", "Simplex method", "NLPP with equality constraints", "Lagrange's multipliers method"]),
 ("III", "Modular Arithmetic", ["Congruence", "Linear congruence", "Remainder theorem", "Solving polynomials", "System of linear congruence", "Euler's theorem", "Fermat's little theorem", "RSA algorithm"]),
 ("IV", "Fourier Series", ["Dirichlet's conditions", "Fourier series of periodic functions", "Fourier series with period 2l", "Fourier series of even functions", "Fourier series of odd functions"]),
 ("V", "Statistical Techniques", ["Karl Pearson's coefficient of correlation", "Spearman's rank correlation coefficient", "Lines of regression", "Fitting of first-degree curves"]),
 ("VI", "Probability", ["Moment generating function", "Raw moments", "Poisson distribution", "Normal distribution"]),
]
G[(CE, "2113114")] = [
 ("1", "Computer Fundamentals", ["Binary number system", "Octal number system", "Hexadecimal number system", "Sign magnitude representation", "1's complement representation", "2's complement representation", "Logic gates", "Basic organization of computer", "Von Neumann model"]),
 ("2", "ALU Operations", ["Addition and subtraction of binary numbers", "Addition and subtraction of octal numbers", "Addition and subtraction of hexadecimal numbers", "Booth's algorithm", "Restoring division algorithm", "Non-restoring division algorithm", "IEEE 754 floating point representation"]),
 ("3", "Processor Organization and Control Unit Design", ["8086 processor architecture", "Register organization", "Instruction formats", "Instruction cycle", "Addressing modes", "Instruction interpretation and sequencing", "Micro-programmed control unit", "Hardwired control unit", "Microinstruction sequencing and execution", "Micro programs", "RISC architecture", "CISC architecture"]),
 ("4", "Memory Systems Organization", ["Memory parameters", "Primary memory classification", "Secondary memory classification", "RAM types", "ROM types", "Memory hierarchy", "Virtual memory", "Segmentation", "Paging", "Cache memory concept", "Cache hierarchy", "Cache mapping techniques", "Cache coherency", "Interleaved memory", "Associative memory"]),
 ("5", "I/O Organization", ["Types of buses", "Bus arbitration", "Bus standards", "I/O interface", "I/O channels", "I/O modules", "I/O processor", "Programmed I/O", "Interrupt driven I/O", "DMA"]),
 ("6", "Parallel Processing", ["80386DX real model", "80386DX protected model", "80386DX virtual model", "Pipeline stages", "Superscalar architecture", "Pipeline hazards", "Branch prediction", "Data forwarding", "Amdahl's law", "Parallel processing concepts", "Flynn's classification"]),
]
G[(CE, "2113116")] = []  # lab: Suggested List of Experiments, no module table
G[(CE, "2114111")] = [
 ("I", "Basics Concepts and Regular Languages", ["Sets", "Logic", "Relations", "Functions", "Discrete structures", "Importance of TCS", "Alphabets", "Strings", "Languages", "Regular operations", "Regular expression", "Arden's theorem", "RE applications", "Regular language", "Closure properties", "Decision properties of regular languages", "Pumping lemma for regular languages"]),
 ("II", "Finite Automata", ["Finite automata (FA)", "Finite state machine (FSM)", "Deterministic finite automata (DFA)", "Nondeterministic finite automata (NFA)", "Transition diagrams", "Language recognizers", "Equivalence between NFA with and without epsilon transitions", "NFA to DFA conversion", "Minimization of DFA", "Moore machine", "Mealy machine", "Applications of FA", "Limitations of FA"]),
 ("III", "Regular and Context Free Grammars", ["Grammars", "Chomsky hierarchy", "Regular grammar (RG)", "Equivalence of left and right linear grammar", "Equivalence of RG and FA", "Context free grammars (CFG)", "Sentential forms", "Leftmost derivation", "Rightmost derivation", "Parse tree", "Ambiguity", "Simplification of CFG", "Eliminating unit productions", "Eliminating useless productions", "Eliminating useless symbols", "Eliminating epsilon productions", "Chomsky normal form (CNF)", "Greibach normal form (GNF)", "Context free language (CFL)", "Parser application", "Markup languages application", "Pumping lemma", "Closure properties"]),
 ("IV", "Pushdown Automata (PDA)", ["Definition of PDA", "Language of PDA", "PDA as generator", "PDA as decider", "PDA as acceptor of CFG", "Deterministic PDA", "Non-deterministic PDA", "Equivalence of PDA and CFG", "Application of PDA"]),
 ("V", "Turing Machine (TM)", ["Definition of TM", "Design of TM as generator", "Design of TM as decider", "Design of TM as acceptor", "Multitrack TM", "Multitape TM", "Universal TM", "Applications of TM", "Power of TMs", "Limitations of TMs"]),
 ("VI", "Decidability and Computability", ["Decidability", "Undecidability", "Recursive language", "Recursively enumerable language", "Halting problem", "Rice's theorem", "Post correspondence problem"]),
]
G[(CSE, "2493113")] = [
 ("I", "Introduction", ["Performance analysis", "Master method", "Space complexity", "Time complexity", "Growth of function", "Big-Oh notation", "Omega notation", "Theta notation", "Mathematical background for algorithm analysis", "Analysis of selection sort", "Analysis of insertion sort"]),
 ("II", "Divide and Conquer Approach", ["General method", "Merge sort", "Quick sort", "Analysis of binary search"]),
 ("III", "Greedy Method Approach", ["General method", "Single source shortest path", "Dijkstra algorithm", "Fractional knapsack problem", "Minimum cost spanning trees", "Kruskal algorithm", "Prim's algorithm"]),
 ("IV", "Dynamic Programming Approach", ["General method", "Multistage graphs", "All pair shortest path", "Floyd Warshall algorithm", "0/1 knapsack problem", "Travelling salesperson problem", "Longest common subsequence"]),
 ("V", "Backtracking and Branch and bound", ["General method", "Backtracking", "N-queen problem", "Sum of subsets", "Graph coloring", "Branch and bound", "Travelling salesperson problem", "15 puzzle problem"]),
 ("VI", "String Matching Algorithms", ["Naive string-matching algorithm", "Rabin Karp algorithm", "Knuth-Morris-Pratt algorithm"]),
]
os.makedirs("tests/golden/" + FAM, exist_ok=True)
bad = 0
for (pdf, code), mods in G.items():
    c = [x for x in E.courses(pdf) if x["code"] == code][0]
    out = {"family": FAM, "course_code": code, "course_title": c["title"], "source_pdf": "data/raw/2019-scheme/" + pdf,
           "source_pages": c["pages"], "status": "DRAFT - needs human sign-off",
           "modules": [{"number": n, "name": nm, "topics": tp} for n, nm, tp in mods]}
    for n, nm, tp in mods:
        for t in tp:
            v = TV.validate(t)
            if v:
                bad += 1
                print("VIOLATION", code, n, t, v)
    json.dump(out, open(f"tests/golden/{FAM}/{code}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(code, c["title"], c["pages"], sum(len(tp) for _, _, tp in mods), "topics")
print("violations in goldens:", bad)
