"""Spike: write the 5 DRAFT golden JSON files for nep26-se-chem-it (a/b). Topics were drafted by hand from module text
(module table cells printed by spikes/nep26_se_chem_it_tables.py), self-learning topics excluded. Throwaway."""
import json, os

A = "data/raw/2019-scheme/Chemical-Engineering/6.40-N-Chemical-Engineering-Sem-III-IV.pdf"
B = "data/raw/2019-scheme/Information-Technology/6.34-N-B.E.-Information-Technology-Sem-III-IV.pdf"
G = {}

G[("nep26-se-chem-it-a", "2073112")] = ("Fluid Flow Operations", A, [19, 20, 21, 22], [
    ("1", "Introduction and Basic Concepts", [
        "Scope and applications of fluid flow", "Properties of fluids", "Types of fluids", "Fluid pressure at a point",
        "Pascal's law", "Pressure variation in a fluid at rest", "Hydrostatic equilibrium", "Measurement of pressure",
        "Piezometers", "U-tube manometer", "Single column manometer", "U-tube differential manometer",
        "Inverted differential U-tube manometer", "Inclined manometer"]),
    ("2", "Fluid Flow Phenomena", [
        "Newton's law of viscosity", "Kinematic viscosity", "Rheological behavior of fluid", "Reynolds experiment",
        "Reynolds number", "Laminar and turbulent flow in boundary layer", "Boundary layer formation in straight tube",
        "Transition length for laminar and turbulent flow"]),
    ("3", "Basic Equations of Fluid Flow", [
        "Continuity equation", "Bernoulli's equation", "Euler's equation", "Modified Bernoulli's equation",
        "Venturi meter", "Orifice meter", "Pitot tube", "Rotameter"]),
    ("4", "Flow of Incompressible fluids: Laminar/Turbulent", [
        "Shear stress distribution", "Velocity distribution", "Relationship between skin friction and wall shear",
        "Friction factor", "Darcy-Weisbach equation", "Local velocity", "Maximum velocity", "Average velocity",
        "Kinetic energy correction factor", "Hagen-Poiseuille equation", "Moody diagram",
        "Equivalent diameter for circular and non-circular ducts", "Major and minor losses", "Equivalent length",
        "Frictional losses in pipe fittings"]),
    ("5", "Flow of Compressible Fluids", [
        "Mach number", "Sonic, supersonic and subsonic flow", "Continuity equation in compressible flow",
        "Bernoulli's equation in compressible flow", "Stagnation properties", "Acoustic velocity", "Adiabatic flow",
        "Isothermal flow", "Drag forces", "Coefficient of drag", "One dimensional motion of particle through fluid",
        "Terminal settling velocity", "Stokes law", "Stagnation point"]),
    ("6", "Pumps, Valves and Agitators", [
        "Classification and types of pumps", "Centrifugal pump construction and working", "Power requirement of pump",
        "Heads and efficiency of pump", "Specific speed", "Minimum speed", "Characteristic curves", "Cavitation", "NPSH",
        "NPSHA", "NPSHR", "Priming", "Reciprocating pump classification and working", "Purpose of agitation",
        "Types of impellers", "Prevention of swirling", "Power curves", "Power number",
        "Compressors, fans and blowers", "Globe valve", "Gate valve", "Butterfly valve", "Non-return valve"]),
])

G[("nep26-se-chem-it-a", "2073111")] = ("Chemical Engineering Mathematics", A, [15, 16, 17], [
    ("01", "Probability and Statistics", [
        "Discrete random variables", "Continuous random variables", "Probability mass function", "Correlation",
        "Karl Pearson's coefficient of correlation", "Lines of regression", "Fitting of first-degree curves"]),
    ("02", "Matrices", [
        "Eigen values and eigen vectors", "Properties of eigen values and eigen vectors", "Similarity of matrices",
        "Diagonalization of matrices"]),
    ("03", "Numerical Methods for Ordinary Differential Equations (ODE):", [
        "Euler's method", "Runge-Kutta second order method"]),
    ("04", "Finite Difference Equations", [
        "Forward difference operator", "Backward difference operator", "Shift operator",
        "Relation between shift and difference operators", "Solution of linear difference equations",
        "Complementary function and particular integral"]),
    ("05", "Numerical Techniques for Models Producing PDEs", [
        "Classification of partial differential equations", "Boundary and initial conditions",
        "Bender-Schmidt method", "Crank-Nicolson method"]),
    ("06", "Laplace Transform", [
        "Laplace transform of standard functions", "Inverse Laplace transform of standard functions",
        "First shifting theorem", "Laplace transform of derivatives", "Laplace transform of integrals",
        "Inverse Laplace transform using first shifting theorem", "Partial fractions method",
        "Applications of Laplace transforms to ODE"]),
])

G[("nep26-se-chem-it-b", "2343114")] = ("Automata Theory", B, [26, 27, 28], [
    ("I", "Introduction and Regular Languages", [
        "Alphabets and strings", "Regular expressions", "Regular languages", "Regular grammars",
        "RL and LL grammars", "Closure properties of regular languages"]),
    ("II", "Finite Automata", [
        "Finite automata as language acceptor", "Nondeterministic finite automata", "Deterministic finite automata",
        "NFA with and without epsilon moves", "RE to NFA conversion", "NFA to DFA conversion", "Reduced DFA",
        "NFA-DFA equivalence", "FA to RE conversion", "Moore machine", "Mealy machine",
        "Moore and Mealy machine conversion", "Limitations of finite automata"]),
    ("III", "Context Free Grammars", [
        "Context free grammars", "Leftmost and rightmost derivations", "Ambiguity", "Simplification of context free grammars",
        "Chomsky normal form", "Greibach normal form", "Chomsky hierarchy"]),
    ("IV", "Push Down Automata", [
        "Deterministic pushdown automata", "Equivalence between PDA and CFG", "Power of PDA", "Limitations of PDA"]),
    ("V", "Turing Machine", [
        "Deterministic Turing machine", "Variants of Turing machine", "Halting problem", "Power of Turing machine"]),
    ("VI", "Applications of Automata", [
        "Applications of finite automata", "Applications of context free grammars", "Applications of pushdown automata",
        "Applications of Turing machines", "Introduction to compiler", "Phases of compiler"]),
])

G[("nep26-se-chem-it-b", "2344112")] = ("Operating System", B, [40, 41, 42], [
    ("I", "Introduction to Operating Systems", [
        "Definition of operating system", "Types of operating systems", "OS structure and operations", "Process management",
        "Memory management", "Storage management", "Operating system services and interface", "System calls and types",
        "System boot", "Operating system design and implementation", "Virtual machines"]),
    ("II", "Process Management", [
        "Process definition", "Process states", "Process state transitions", "Process control block", "Context switching",
        "Threads", "Multithreading", "Thread models", "Benefits of threads", "Process scheduling objectives",
        "Types of schedulers", "Scheduling criteria", "CPU utilization", "Throughput", "Turnaround time", "Waiting time",
        "Response time", "Preemptive scheduling algorithms", "Non-preemptive scheduling algorithms", "Thread scheduling",
        "Multiple processor scheduling"]),
    ("III", "Process Synchronization", [
        "Inter-process communication", "Process synchronization", "Race condition", "Critical section problem",
        "Peterson's solution", "Synchronization hardware", "Semaphores", "Producer consumer problem", "Message passing",
        "System model for deadlocks", "Deadlock characterization", "Methods for handling deadlocks", "Deadlock prevention",
        "Deadlock avoidance", "Deadlock detection", "Recovery from deadlock"]),
    ("IV", "Memory Management", [
        "Logical and physical address map", "Contiguous memory allocation", "Fixed and variable partition",
        "Internal and external fragmentation", "Compaction", "Swapping", "Paging", "Structure of the page table",
        "Segmentation", "Virtual memory basics", "Hardware and control structures", "Locality of reference", "Demand paging",
        "Page replacement algorithms", "Thrashing"]),
    ("V", "File Management", [
        "File concept", "Access methods", "Directory and disk structure", "File-system mounting", "File sharing",
        "File protection", "File-system structure", "File-system implementation", "Directory implementation",
        "Allocation methods", "Free-space management", "Efficiency and performance", "Recovery", "Mass storage structure",
        "Disk scheduling", "RAID structure", "I/O systems"]),
    ("VI", "Special-purpose Operating Systems", [
        "Open-source and proprietary operating systems", "Distributed operating system", "Network operating system",
        "Embedded operating systems", "Cloud and IoT operating systems", "Real-time operating system",
        "Mobile operating system", "Multimedia operating system", "Comparison of special-purpose operating systems"]),
])

G[("nep26-se-chem-it-b", "2344114")] = ("Unix Lab", B, [47, 48, 49], [
    ("I", "Introduction to Unix", ["History of UNIX", "Unix architecture"]),
    ("II", "Basic Commands", ["Unix general purpose utility commands", "Vi editor"]),
    ("III", "Commands for File System Management and User Management", [
        "Unix file system", "File and directory permissions", "Single and multiuser environment",
        "File system management commands", "Piping and redirection", "User management commands"]),
    ("IV", "Commands for Process Management and Memory Management", [
        "Process management commands", "Memory management commands"]),
    ("V", "Basic Scripts", ["Shell", "Types of shell", "Variables and operators in shell"]),
    ("VI", "Advanced Scripts", ["grep command", "egrep command", "sed command", "awk scripting", "perl scripting"]),
])

for (fam, code), (title, pdf, pages, mods) in G.items():
    d = f"tests/golden/{fam}"
    os.makedirs(d, exist_ok=True)
    obj = {"family": fam, "course_code": code, "course_title": title, "source_pdf": pdf, "source_pages": pages,
           "status": "DRAFT - needs human sign-off",
           "modules": [{"number": n, "name": nm, "topics": tp} for n, nm, tp in mods]}
    json.dump(obj, open(f"{d}/{code}.json", "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=2)
    print(fam, code, sum(len(m[2]) for m in mods), "topics")
