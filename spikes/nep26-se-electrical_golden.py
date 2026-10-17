"""Spike: write DRAFT golden courses for nep26-se-electrical (hand-drafted by reading each course's module text; status DRAFT)."""
import json, os
FAM = "nep26-se-electrical"
PDF = "data/raw/2019-scheme/Electrical-Computer-Engineering/6.51N-B.E.-Electrical-Computer-EngineeringSem-III-IV.pdf"
R = ["I", "II", "III", "IV", "V", "VI"]
A = ["1", "2", "3", "4", "5", "6"]
G = {}

G["2213112"] = ("Electrical Machines -I", [19, 20], R, [
    ("DC Machines", ["Working principles of DC machines", "Back EMF", "Torque equation", "Commutation", "Armature reaction",
                     "Types of DC machines", "Characteristics of DC machines", "Necessity of starter", "Speed control methods",
                     "Losses and efficiency", "Swinburne's test", "Hopkinson's test"]),
    ("Single phase Transformer", ["Working principle of single phase transformer", "EMF equation", "Equivalent circuit", "Phasor diagram",
                                  "Voltage regulation", "Losses and efficiency", "Condition for maximum efficiency", "Parallel operation",
                                  "No load operation", "On load operation", "Equal and unequal voltage operation", "OC and SC test", "Sumpner's test"]),
    ("Three Phase Transformer", ["Principle of operation", "Connections", "Phasor groups", "Parallel operation",
                                 "Harmonics in three phase transformers", "Suppression of harmonics", "Oscillating neutral phenomenon",
                                 "Open delta or V connection", "Scott connection"]),
    ("Three Phase Induction Motor", ["Constructional details", "Principle of operation", "Slip", "Rotor EMF and frequency",
                                     "Rotor current and power", "Power stages", "Phasor diagram", "Equivalent circuit",
                                     "Torque-speed characteristics", "Losses and efficiency", "No load and blocked rotor test", "Circle diagram"]),
    ("Starting and Speed control of Three Phase Induction Motor", ["Need of starter", "Direct on line starter", "Rotor resistance starter",
                                                                   "Autotransformer starter", "Star delta starter", "Voltage control",
                                                                   "Frequency control", "Pole changing method", "V/f control"]),
    ("Single phase Induction Motor", ["Principle of operation", "Double field revolving theory", "Equivalent circuit",
                                      "Split phase starting", "Resistance split phase starting", "Capacitor split phase starting",
                                      "Capacitor start and run", "Shaded pole starting"]),
])

G["2213113"] = ("Electronics Engineering", [22, 23], R, [
    ("Introduction To Digital Logic", ["Number systems and conversions", "Binary arithmetic", "Logic gates", "Boolean algebra laws",
                                       "Simplification techniques", "De Morgan's theorems", "Karnaugh maps", "K-map simplification up to 4 variables"]),
    ("Combinational, Sequential Circuits & Memory Elements", ["Combinational circuit design", "Adders", "Subtractors", "Multiplexers",
                                                              "Universal logic modules", "Demultiplexers", "SR flip-flop", "JK flip-flop",
                                                              "D flip-flop", "T flip-flop", "Synchronous counters", "Asynchronous counters",
                                                              "ROM types", "RAM types", "Memory operation and differences"]),
    ("Semiconductor Devices", ["P-N junction diodes", "Zener diodes", "Voltage regulation using Zener diodes", "Light emitting diodes",
                               "Opto isolators", "BJT structure and operation", "BJT characteristics", "BJT regions of operation",
                               "JFET construction and operation", "JFET characteristics", "Transconductance", "MOSFET types",
                               "MOSFET operation and characteristics"]),
    ("OP-Amp & Voltage Regulators", ["Op-amp block diagram", "Ideal op-amp characteristics", "Inverting configuration",
                                     "Non-inverting configuration", "Voltage regulators", "Adjustable voltage regulator design"]),
    ("Fundamentals of Microcontroller", ["8-bit microcontrollers", "Microprocessor versus microcontroller", "Harvard architecture",
                                         "Von Neumann architecture", "RISC and CISC", "Pipelining", "Selection of microcontrollers",
                                         "MCS-51 variants"]),
    ("Architecture And Assembly Language Of 8051", ["Hardware of 8051", "Oscillator and clock", "PC and DPTR", "Flags and PSW", "CPU registers",
                                                    "Internal RAM organization", "Internal memory", "Special function registers",
                                                    "I/O pins and ports", "Addressing modes of 8051", "Instruction set of 8051", "Example programs"]),
])

G["2213114"] = ("Measurements and Measuring Instruments", [25, 26], R, [
    ("Philosophy of Measurement", ["Measurement", "Methods of measurement", "Classification of instruments", "Types of errors",
                                   "Standardization of instruments", "Calibration of instruments"]),
    ("Analog Measurement of Electrical Quantities", ["Classification of analog instruments", "Operating torque", "Controlling torque", "Damping torque",
                                                     "Range extension of ammeter", "Range extension of voltmeter", "Electro-dynamometer wattmeter",
                                                     "Electro-dynamometer power factor meter", "Current transformer", "Types of CT",
                                                     "Potential transformer", "Instrument range extension", "Clamp on ammeter",
                                                     "High voltage potential transformer"]),
    ("AC-DC Bridges and Potentiometer", ["Wheatstone bridge", "Kelvins double bridge", "Megger", "Earth resistance measurement",
                                         "Earth tester", "Maxwell's bridge", "Schering bridge", "Potentiometer applications",
                                         "Calibration of ammeter", "Calibration of voltmeter", "Calibration of wattmeter"]),
    ("Measurement of Non-electrical Quantities", ["Transducers", "Resistive transducers", "Capacitive transducers", "Inductive transducers",
                                                  "Optical transducers", "Digital transducers", "Temperature measurement", "Thermocouple",
                                                  "Thermistor", "Resistance temperature detector", "Displacement measurement",
                                                  "Potentiometer displacement sensor", "LVDT", "Pressure measurement", "Piezoelectric sensor",
                                                  "Strain gauge", "Speed measurement", "Hall effect sensor"]),
    ("Digital Measurement of Electrical Quantities", ["Block diagram of digital instruments", "Digital versus analog instruments",
                                                      "Resolution of digital meters", "Sensitivity of digital meters", "Digital voltmeter",
                                                      "Ramp type digital voltmeter", "Digital ammeter", "Multi-meter", "Digital frequency meter",
                                                      "Digital tachometer", "Digital megger", "Digital storage oscilloscope",
                                                      "Current sensor ACS712", "Voltage sensor B25"]),
    ("Signal Conditioning and Advanced Measuring Instruments", ["AC signal conditioning circuits", "DC signal conditioning circuits",
                                                                "Data acquisition system", "Power analyzer", "Harmonic analyzer",
                                                                "Signal generator", "Q-meter", "Smart sensor",
                                                                "IoT based measuring instrument", "Smart energy meter"]),
])

G["2214112"] = ("Electromagnetic Fields and Waves", [43, 44], A, [
    ("Vector Analysis", ["Vector analysis", "Cartesian coordinate system", "Cylindrical coordinate system", "Spherical coordinate system",
                         "Relationship between coordinate systems", "Properties of coordinate system", "Gradient", "Divergence", "Curl"]),
    ("Electrostatics", ["Coulomb's law", "Electric field intensity", "Electric flux density", "Line charge distribution",
                        "Surface charge distribution", "Volume charge distribution", "Gauss's law", "Electrostatic potential",
                        "Divergence theorem", "Convection current", "Conduction current", "Electric field in free space",
                        "Electric field in conductors", "Electric field in dielectrics", "Electrostatic boundary value problems",
                        "Poisson's equation", "Laplace's equation"]),
    ("Electrostatics Applications", ["Current and current density", "Continuity of current", "Conductor properties",
                                     "Conductor boundary conditions", "Nature of dielectric materials",
                                     "Boundary conditions for perfect dielectric materials", "Capacitance", "Types of capacitances",
                                     "Energy density in electric field"]),
    ("Magnetostatic Fields", ["Magnetic field intensity", "Bio Savart's law", "Ampere's circuit law", "Magnetic flux", "Magnetic flux density",
                              "Magnetic flux density in free space", "Magnetic flux density in conductor",
                              "Magnetic flux density in magnetic materials", "Magnetic force", "Magnetic vector potential", "Stroke's theorem"]),
    ("Maxwells Equations and Electromagnetic Waves", ["Faraday's law", "Lenz's law", "Maxwell's equations in differential form",
                                                      "Maxwell's equations in integral form", "Displacement current",
                                                      "Electromagnetic wave equations", "Wave parameters", "Velocity", "Intrinsic impedance",
                                                      "Propagation constant", "Waves in free space", "Waves in lossy dielectric",
                                                      "Waves in lossless dielectric", "Waves in conductors", "Skin depth", "Poynting theorem"]),
    ("Applications of Electromagnetic Waves", ["EMI and EMC", "EMI sources", "Effects of EMI", "Testing methods for EMI and EMC",
                                               "Methods to suppress EMI", "Grounding and shielding", "EMC standards",
                                               "EMI and EMC non compliance issues", "Biological effects of EMI and EMC", "ESD", "EMP"]),
])

G["2214113"] = ("Power Electronics Devices and Circuits", [46, 47], R, [
    ("Thyristors (Silicon Controlled Rectifier)", ["Modes of operation of SCR", "Static V-I characteristics of SCR", "Gate control",
                                                   "Two transistor analogy", "Thyristor voltage rating", "Thyristor current rating",
                                                   "Firing circuits", "R triggering", "RC triggering", "Ramp triggering using UJT",
                                                   "SCR protection circuit"]),
    ("Power Semiconductor Devices", ["Power diode characteristics", "Power BJT characteristics", "Power MOSFET characteristics",
                                     "IGBT characteristics", "Safe operation area", "Comparison of Power BJT PMOSFET and IGBT",
                                     "Wide band gap devices", "Silicon carbide devices", "GaN devices", "Conduction losses",
                                     "Switching losses", "Loss numericals", "MOSFET data sheet", "IGBT data sheet"]),
    ("Controlled Rectifiers (AC to DC Converter)", ["Single phase full wave controlled rectifier", "Mid-point configuration",
                                                    "Bridge configuration", "R load", "R-L load", "Output voltage calculation",
                                                    "Rectification mode", "Inversion mode", "Single phase dual converter",
                                                    "Three phase full converter with R load", "Single phase PWM rectifier",
                                                    "PWM rectifier working principle", "Controlled rectifier applications"]),
    ("DC-DC switched Mode Converters", ["Step-down operation of DC-DC converter", "PWM control of DC-DC converter", "Buck converter",
                                        "Boost converter", "Buck-boost converter", "Output voltage ripple",
                                        "Comparison of non-isolated converters", "Bidirectional DC-DC converters",
                                        "Power factor correction circuits", "LED lamp driver"]),
    ("DC-AC Converter (Inverter)", ["Single phase half bridge inverter", "Single phase full bridge inverter",
                                    "Voltage control in single phase inverters", "Pulse width modulated inverters", "Multiple PWM",
                                    "Sinusoidal PWM", "Three phase VSI", "Conduction mode at 120 degrees", "Conduction mode at 180 degrees",
                                    "Single phase current source inverter", "Comparison of VSI and CSI", "Inverter applications"]),
    ("Auxiliary Circuits", ["Need for snubber circuit", "Function of snubber circuits", "Types of snubber circuits", "Turn-off snubber",
                            "Requirement of gate driver circuits", "Gate drivers for Power MOSFET", "Gate drivers for IGBT",
                            "Level shifters", "Bootstrap drivers", "Isolated drivers", "Heat sinks", "Heat sink calculation examples"]),
])

if __name__ == "__main__":
    os.makedirs(f"tests/golden/{FAM}", exist_ok=True)
    for code, (title, pages, nums, mods) in G.items():
        assert len(nums) == len(mods) == 6
        d = {"family": FAM, "course_code": code, "course_title": title, "source_pdf": PDF, "source_pages": pages,
             "status": "DRAFT - needs human sign-off",
             "modules": [{"number": n, "name": nm, "topics": tp} for n, (nm, tp) in zip(nums, mods)]}
        with open(f"tests/golden/{FAM}/{code}.json", "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print(code, sum(len(tp) for _, tp in mods), "topics")
