"""Throwaway: writes the 5 DRAFT golden JSON files (topics typed by hand after reading each course's module text)."""
import json,os
FAM="nep26-fe-sem12"
D="tests/golden/"+FAM+"/"
os.makedirs(D,exist_ok=True)
def w(code,title,pdf,pages,mods):
    j={"family":FAM,"course_code":code,"course_title":title,"source_pdf":pdf,"source_pages":pages,"status":"DRAFT - needs human sign-off",
       "modules":[{"number":n,"name":nm,"topics":tp} for n,nm,tp in mods]}
    open(D+code+".json","w",encoding="utf-8").write(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
w("BSC101","Applied Mathematics-I","data/raw/2019-scheme/AIML/6.9N-AIML.pdf",[15,16,17,18],[
 ("01","Complex Numbers",["Expansion of sin nθ and cos nθ","Expansion in powers of sinθ and cosθ","Powers and roots of a complex number"]),
 ("02","Hyperbolic Functions & Logarithms of Complex Numbers",["Circular functions of complex number","Hyperbolic functions of complex number","Inverse circular functions","Inverse hyperbolic functions","Separation into real and imaginary parts","Logarithm of complex number"]),
 ("03","Partial Differentiation",["Functions of two and three variables","Partial derivatives of first and higher order","Differentiation of composite function","Euler's theorem on homogeneous functions","Deductions from Euler's theorem"]),
 ("04","Applications of Partial Differentiation and Successive Differentiation",["Maxima and minima of two variables","Successive differentiation","nth derivative of standard functions","Leibnitz's theorem"]),
 ("05","Matrices",["Hermitian matrices","Skew Hermitian matrices","Unitary matrices","Orthogonal matrices","Properties of matrices","Rank using echelon form","Reduction to normal form","PAQ form","Homogeneous system of equations","Non-homogeneous system of equations","Consistency of linear systems"]),
 ("06","Numerical Solutions of Transcendental Equations and System of Linear Equations and Expansion of Function",["Solution of transcendental equations","Newton Raphson method","Regula Falsi method","Solution of linear algebraic equations","Gauss Jacobi iteration method","Gauss Seidel iteration method"]),
])
w("BSC102","Applied Physics","data/raw/2019-scheme/AIML/6.9N-AIML.pdf",[19,20,21,22],[
 ("I","Lasers",["Spontaneous emission","Stimulated emission","Population inversion","Pumping","Active medium","Resonant cavity","Coherence length","Coherence time","Characteristics of lasers","He-Ne laser","Fiber laser","LiDAR","Barcode reader","Laser in metal work"]),
 ("II","Fibre Optics",["Critical angle","Acceptance angle","Acceptance cone","Numerical aperture","Total internal reflection","Propagation of light in fibers","Single mode fibers","Multimode fibers","Step index fibers","Graded index fibers","Attenuation","Attenuation coefficient","Factors affecting attenuation","Fibre optic communication system","Advantages of optical fiber communication"]),
 ("III","Interference in Thin Films",["Interference in thin film of uniform thickness","Maxima and minima conditions for reflected system","Maxima and minima conditions for wedge shaped film","Newton's rings","Anti-reflecting coating"]),
 ("IV","Electrodynamics",["Gradient","Divergence","Curl","Gauss's law","Ampere's circuital law","Faraday's law","Divergence theorem","Stokes theorem","Maxwell's equations in point form","Maxwell's equations in integral form"]),
 ("V","Quantum Physics",["de Broglie hypothesis","de Broglie wavelength for electron","Properties of matter waves","Wave function","Probability density","Mathematical conditions for wave function","Schrodinger time independent equation","Schrodinger time dependent equation","Energy of particle in rigid box","Quantum mechanical tunneling","Qubit"]),
 ("VI","Basics of Semiconductor Physics",["Direct band gap semiconductors","Indirect band gap semiconductors","Electrical conductivity of semiconductors","Drift velocity","Mobility","Fermi-Dirac distribution function","Fermi level in intrinsic semiconductors","Fermi level in extrinsic semiconductors"]),
])
w("ESC101","Engineering Mechanics","data/raw/2019-scheme/AIML/6.9N-AIML.pdf",[31,32,33],[
 ("I","System of Forces",["Classification of force systems","Principle of transmissibility","Composition of forces","Resolution of forces","Resultant of coplanar force system","Moment of force about a point","Couples","Varignon's theorem","Resultant of non-coplanar force system"]),
 ("II","Centroid",["Centroids of plane laminas"]),
 ("III","Equilibrium of Force system and Friction",["Conditions of equilibrium","Equilibrium of rigid bodies","Free body diagrams","Types of beams","Types of supports","Reactions at supports","Laws of friction","Cone of friction","Angle of repose","Angle of friction","Equilibrium on inclined plane"]),
 ("IV","Kinematics of particle and rigid bodies",["Motion with variable acceleration","Motion along plane curved path","Rectangular components of velocity and acceleration","Tangential and normal acceleration","General plane motion","Instantaneous center method"]),
 ("V","Kinetics of particle",["Force and acceleration","D'Alembert's principle","Inertia force","Equations of dynamic equilibrium","Linear impulse and momentum","Impact and collision","Coefficient of restitution","Direct central impact","Oblique central impact","Loss of kinetic energy in collision"]),
 ("VI","Introduction to Robot Kinematics",["Fundamentals of robot mechanics","Degree of freedom","D-H parameters","Forward kinematics","Homogeneous transformation"]),
])
w("VSEC102","C Programming","data/raw/2019-scheme/AIML/6.9N-AIML.pdf",[55,56,57],[
 ("01","Fundamentals of C-Programming",["Character set","Identifiers and keywords","Data types","Constants","Variables","Arithmetic operators","Relational operators","Logical operators","Assignment operators","Unary operators","Conditional operator","Bitwise operators","Comma operator","Expressions","Statements","Library functions","Preprocessor","Data input and output","Structure of C program"]),
 ("02","Control Structures",["If statement","If-else statement","Multiway decision","While loop","Do-while loop","For loop","Nested control structure","Switch statement","Continue statement","Break statement","Goto statement"]),
 ("03","Functions and Parameter",["Function main","Defining a function","Accessing a function","Function prototype","Passing arguments to a function","Recursion","Storage classes"]),
 ("04","Arrays, String, Structure",["Array declaration","Array definition","Accessing array element","One-dimensional array","Multidimensional array","Basics of string","Array of string","String.h functions","Structure declaration","Structure initialization","Structure within structure","Operations on structures","Array of structure"]),
 ("05","Pointer",["Pointer variables","Address operator","Dereferencing pointer","Void pointer","Pointer arithmetic","Pointers to pointers","Pointers and array"]),
 ("06","Files",["File opening","File closing","File creation","File reading","File processing"]),
])
w("IKS201","Indian Knowledge System","data/raw/2019-scheme/EXTC/6.19-N-EXTC.pdf",[119,120,121],[
 ("I","Introduction to the Indian Knowledge System (I.K.S.)",["Basic knowledge and scope of IKS","IKS in ancient and modern India","Bhartiya education system","Sources of education","Aim of education","Curriculum","Methods of learning","Educational institutes","Higher educational institutions","Gurukul system","Modern education system"]),
 ("II","Development of Scientific Thoughts in Ancient India",["Science and technology development","Astronomy","Mathematics","Life sciences","Physiology","Ayurveda"]),
 ("III","Development of Arts & Culture in India",["Ancient architecture","Forts","Paintings","Sculpture","Temple architecture","Performing arts","Music","Art of singing","Art of dancing","Natyakala","Cultural traditions","Folk arts"]),
 ("IV","Good Governance in Ancient India",["Indian religions","Moral and ethical governance","Vishva Kalyan","Vasudhaiva Kutumbkam","Principles of good governance","Artha Sastra","Kautilyan state"]),
 ("V","Contribution of Indian Scientist & Nobel Laureates",["Baudhayan","Aryabhatta","Brahmgupta","Bhaskaracharya","Varahamihira","Nagarjuna","Susruta","Kanada","Charak","Rabindranath Tagore","C.V. Raman","Har Gobind Khorana","Mother Teresa","Subrahmanyan Chandrasekhar","Amartya Sen","V.S. Naipaul","Venkatraman Ramakrishnan","Kailash Satyarthi","Abhijit Banerjee"]),
 ("VI","Sustainable Practices in Ancient India",["Agriculture","Waste management","Water conservation","Forest conservation","Architecture","Urban planning","Biodiversity preservation","Yoga","Pranayama","Meditation for health"]),
])
