# -*- coding: utf-8 -*-
"""अध्याय 8 — वैद्युतचुम्बकीय तरंगें: स्वतंत्र संख्यात्मक एवं संरचनात्मक सत्यापन।

यह स्क्रिप्ट Q1–Q60 में प्रदर्शित प्रत्येक संख्यात्मक निष्कर्ष को मूल सम्बन्धों से
स्वतंत्र रूप से पुनः गणना करती है। वैचारिक प्रश्नों को स्पष्ट भौतिक invariants से
कवर किया गया है। किसी भी गणना, कवरेज अथवा 11-key data schema की त्रुटि पर
AssertionError के साथ non-zero exit होता है।
"""

import hashlib
import importlib
import math
import re

C = 3.00e8
EPS0 = 8.85e-12
MU0 = 4 * math.pi * 1e-7
H = 6.626e-34
E_CHARGE = 1.60e-19

# Source is loaded before checks so every independent calculation and invariant can
# be bound back to the exact published record, not merely to a parallel hard-coded list.
parts = []
for part_no in (1, 2, 3):
    module = importlib.import_module(f"ch8_part{part_no}")
    part = getattr(module, f"PART{part_no}")
    parts.append(part)
questions = sum(parts, [])
by_number = {q.get("n"): q for q in questions}


def source_text(qno, *fields):
    """Return selected published fields as one searchable string."""
    q = by_number[qno]
    if not fields:
        fields = ("topic", "q", "formula", "why", "steps", "ans", "trick", "alt")
    chunks = []
    for field in fields:
        value = q[field]
        if field == "steps":
            chunks.extend(piece for step in value for piece in step)
        else:
            chunks.append(value)
    return "\n".join(chunks)


_NUMERIC_TOKEN = re.compile(
    r"(?:\d+(?:\.\d+)?(?:\s*×\s*10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)?[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]*|π(?:/\d+)?)"
)


def numeric_signature(q):
    """Fingerprint every published numeral in all pedagogical fields.

    The hard-coded calculations below establish the physics; this signature binds
    their audited operands, conversions, intermediate values, final values, and
    numerical checks to the source that the builder actually renders.
    """
    text = "\n".join([
        q["q"], q["formula"], q["why"],
        *(piece for step in q["steps"] for piece in step),
        q["ans"], q["trick"], q["alt"],
    ])
    tokens = _NUMERIC_TOKEN.findall(text)
    digest = hashlib.sha256("\x1f".join(tokens).encode("utf-8")).hexdigest()
    return len(tokens), digest


def complete_source_digest(records):
    """Hash every character of every rendered source field and structural scalar.

    This authoritative fail-closed binding deliberately avoids tokenisation, so
    Unicode superscripts/subscripts, symbols, units, and prose cannot bypass it.
    """
    serialised = []
    for q in records:
        serialised.append("\x1d".join([
            str(q["n"]), str(q["cat"]), str(q["marks"]), q["topic"], q["q"],
            q["formula"], q["why"],
            *(piece for step in q["steps"] for piece in step),
            q["ans"], q["trick"], q["alt"],
        ]))
    return hashlib.sha256("\x1c".join(serialised).encode("utf-8")).hexdigest()


checks = []
covered_questions = set()
source_claim_checks = 0


def check(qno, label, got, expected, rel_tol=5e-4, abs_tol=5e-12):
    """Hard-coded published value के विरुद्ध स्वतंत्र calculation जाँचें।"""
    passed = math.isclose(got, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    checks.append((qno, label, passed, got, expected))
    covered_questions.add(qno)
    status = "PASS" if passed else "FAIL"
    print(f"{status} Q{qno:02d} {label:<48} got={got:.12g} expected={expected:.12g}")


def truth(qno, label, condition):
    """Conceptual/derivation invariant को executable assertion बनाइए।"""
    passed = bool(condition)
    checks.append((qno, label, passed, int(passed), 1))
    covered_questions.add(qno)
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} {label}")


def claim(qno, field, *needles):
    """Bind independently verified conclusions to an exact published field."""
    global source_claim_checks
    haystack = source_text(qno, field)
    missing = [needle for needle in needles if needle not in haystack]
    passed = not missing
    source_claim_checks += 1
    checks.append((qno, f"published {field} claim", passed, len(needles) - len(missing), len(needles)))
    covered_questions.add(qno)
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} published {field}: "
          f"{len(needles) - len(missing)}/{len(needles)} required claims"
          + (f" missing={missing}" if missing else ""))


print("=== PART 1: प्रत्यक्ष सूत्र (Q1–Q20) ===")
# Q1: I_d = epsilon_0 dPhi_E/dt, flux-rate 2.00e5 V m/s.
check(1, "displacement current (A)", EPS0 * 2.00e5, 1.77e-6)
check(1, "displacement current (microampere)", EPS0 * 2.00e5 * 1e6, 1.77)

# Q2: I_d = C dV/dt, C=2 microfarad, dV/dt=3.00e3 V/s.
check(2, "capacitor displacement current (A)", 2e-6 * 3.00e3, 6.00e-3)
check(2, "capacitor displacement current (mA)", 2e-6 * 3.00e3 * 1e3, 6.00)

# Q3: E0/B0=c, B0=2 microtesla.
check(3, "electric-field amplitude (V/m)", C * 2e-6, 600.0)

# Q4: B0=E0/c, E0=150 V/m.
check(4, "magnetic-field amplitude (T)", 150 / C, 5.00e-7)
check(4, "magnetic-field amplitude (microtesla)", 150 / C * 1e6, 0.500)

# Q5: 100 MHz radio wave.
check(5, "radio wavelength (m)", C / 100e6, 3.00)

# Q6: 3.00 cm microwave.
check(6, "microwave frequency (Hz)", C / 0.0300, 1.00e10)
check(6, "microwave frequency (GHz)", C / 0.0300 / 1e9, 10.0)

# Q7: 600 km travel in vacuum.
check(7, "travel time (s)", 600e3 / C, 2.00e-3)
check(7, "travel time (ms)", 600e3 / C * 1e3, 2.00)

# Q8: instantaneous electric energy density for E=300 V/m.
check(8, "electric energy density (J/m^3)", 0.5 * EPS0 * 300**2, 3.9825e-7)

# Q9: instantaneous magnetic energy density for B=1 microtesla.
check(9, "magnetic energy density (J/m^3)", (1e-6) ** 2 / (2 * MU0), 3.9789e-7, rel_tol=2e-5)

# Q10: total instantaneous density for E=300 V/m in a vacuum EM wave.
check(10, "total instantaneous energy density (J/m^3)", EPS0 * 300**2, 7.965e-7)

# Q11: average intensity for E0=120 V/m.
check(11, "average intensity (W/m^2)", 0.5 * C * EPS0 * 120**2, 19.116)

# Q12: E0 from average intensity 1000 W/m^2.
e12 = math.sqrt(2 * 1000 / (C * EPS0))
check(12, "electric-field amplitude (V/m)", e12, 867.93, rel_tol=2e-5)

# Q13: UV photon at 1.00e15 Hz; explicitly cross-chapter context.
e13 = H * 1.00e15
check(13, "photon energy (J)", e13, 6.626e-19)
check(13, "photon energy (eV)", e13 / E_CHARGE, 4.14125)

# Q14: red/orange visible wavelength 600 nm.
check(14, "visible frequency (Hz)", C / 600e-9, 5.00e14)

# Q15: X-ray frequency 3.00e18 Hz.
check(15, "X-ray wavelength (m)", C / 3.00e18, 1.00e-10)
check(15, "X-ray wavelength (nm)", C / 3.00e18 * 1e9, 0.100)

# Q16: f=5 MHz for 2 microseconds.
check(16, "number of cycles", 5e6 * 2e-6, 10.0)

# Q17: phase change over x=lambda/4 for lambda=4 m.
check(17, "phase change (rad)", 2 * math.pi * 1 / 4, math.pi / 2)
check(17, "phase change (degree)", math.degrees(2 * math.pi * 1 / 4), 90.0)

# Q18: enrichment—absorbing surface, I=600 W/m^2.
check(18, "absorbing radiation pressure (Pa)", 600 / C, 2.00e-6)

# Q19: enrichment—normally reflecting surface, I=450 W/m^2.
check(19, "reflecting radiation pressure (Pa)", 2 * 450 / C, 3.00e-6)

# Q20: two radio frequencies.
check(20, "75 MHz wavelength (m)", C / 75e6, 4.00)
check(20, "150 MHz wavelength (m)", C / 150e6, 2.00)
check(20, "wavelength ratio", (C / 75e6) / (C / 150e6), 2.00)

print("\n=== PART 2A: एक अज्ञात (Q21–Q30) ===")
# Q21: flux-rate from displacement current 4.425 microampere.
check(21, "electric-flux rate (V m/s)", 4.425e-6 / EPS0, 5.00e5)

# Q22: voltage rise rate from I_d=1 mA, C=0.25 microfarad.
check(22, "voltage rise rate (V/s)", 1e-3 / 0.25e-6, 4.00e3)

# Q23: capacitance from I_d=2.4 mA and dV/dt=800 V/s.
check(23, "capacitance (F)", 2.4e-3 / 800, 3.00e-6)
check(23, "capacitance (microfarad)", 2.4e-3 / 800 * 1e6, 3.00)

# Q24: E0 from B0=1.2 microtesla.
check(24, "electric-field amplitude (V/m)", C * 1.2e-6, 360.0)

# Q25: B0 from E0=900 V/m.
check(25, "magnetic-field amplitude (T)", 900 / C, 3.00e-6)
check(25, "magnetic-field amplitude (microtesla)", 900 / C * 1e6, 3.00)

# Q26: f from lambda=750 nm.
check(26, "frequency (Hz)", C / 750e-9, 4.00e14)

# Q27: lambda from f=2.50e14 Hz.
check(27, "infrared wavelength (m)", C / 2.50e14, 1.20e-6)
check(27, "infrared wavelength (micrometre)", C / 2.50e14 * 1e6, 1.20)

# Q28: E0 from average total energy density 4.425e-6 J/m^3.
check(28, "electric-field amplitude (V/m)", math.sqrt(2 * 4.425e-6 / EPS0), 1000.0)

# Q29: B0 from average intensity 119.37 W/m^2.
b29 = math.sqrt(2 * MU0 * 119.37 / C)
check(29, "magnetic-field amplitude (T)", b29, 1.00e-6, rel_tol=5e-5)
check(29, "magnetic-field amplitude (microtesla)", b29 * 1e6, 1.00, rel_tol=5e-5)

# Q30: average intensity from total average energy density 2.00e-6 J/m^3.
check(30, "intensity from average energy density (W/m^2)", C * 2.00e-6, 600.0)

print("\n=== PART 2B: दो अज्ञात (Q31–Q40) ===")
# Q31: E0=600 V/m -> B0 and average intensity.
check(31, "magnetic amplitude (T)", 600 / C, 2.00e-6)
check(31, "average intensity (W/m^2)", 0.5 * C * EPS0 * 600**2, 477.9)

# Q32: f=100 MHz -> wavelength and period.
check(32, "wavelength (m)", C / 100e6, 3.00)
check(32, "period (s)", 1 / 100e6, 1.00e-8)
check(32, "period (ns)", 1 / 100e6 * 1e9, 10.0)

# Q33: lambda=500 nm -> frequency and photon energy.
f33 = C / 500e-9
check(33, "frequency (Hz)", f33, 6.00e14)
check(33, "photon energy (J)", H * f33, 3.9756e-19)
check(33, "photon energy (eV)", H * f33 / E_CHARGE, 2.48475)

# Q34: 4 microfarad rises 0 to 120 V in 2 ms.
rate34 = 120 / 2e-3
check(34, "voltage rise rate (V/s)", rate34, 6.00e4)
check(34, "displacement current (A)", 4e-6 * rate34, 0.240)

# Q35: A=.010 m^2; E rises 0 to 2e5 V/m in 5 microseconds.
dedt35 = 2e5 / 5e-6
check(35, "electric-field rise rate (V/m/s)", dedt35, 4.00e10)
check(35, "electric-flux rise rate (V m/s)", 0.010 * dedt35, 4.00e8)
check(35, "displacement current (A)", EPS0 * 0.010 * dedt35, 3.54e-3)
check(35, "displacement current (mA)", EPS0 * 0.010 * dedt35 * 1e3, 3.54)

# Q36: B0=1.50 microtesla -> E0 and average total density.
e36 = C * 1.50e-6
check(36, "electric amplitude (V/m)", e36, 450.0)
check(36, "average total energy density (J/m^3)", 0.5 * EPS0 * e36**2, 8.9606e-7, rel_tol=2e-5)

# Q37: average intensity 53.1 W/m^2 -> E0 and B0.
e37 = math.sqrt(2 * 53.1 / (C * EPS0))
check(37, "electric amplitude (V/m)", e37, 200.0)
check(37, "magnetic amplitude (T)", e37 / C, 6.667e-7, rel_tol=6e-5)

# Q38: distance 1.50e8 m, f=60 MHz.
t38 = 1.50e8 / C
check(38, "travel time (s)", t38, 0.500)
check(38, "cycles during travel", 60e6 * t38, 3.00e7)

# Q39: 3 MHz radio and 30 GHz microwave.
check(39, "radio wavelength (m)", C / 3e6, 100.0)
check(39, "microwave wavelength (m)", C / 30e9, 1.00e-2)
check(39, "wavelength ratio", (C / 3e6) / (C / 30e9), 1.00e4)

# Q40: I=800 W/m^2, A=2 cm^2, t=10 s.
p40 = 800 * 2e-4
check(40, "received power (W)", p40, 0.160)
check(40, "received energy (J)", p40 * 10, 1.60)

print("\n=== PART 3A: व्युत्पत्ति/अवधारणा (Q41–Q50) ===")
# Q41: Maxwell correction and continuity in a charging capacitor.
truth(41, "conduction and displacement currents have equal continuity value",
      "I_d = dQ/dt = I_c" in source_text(41, "ans"))
truth(41, "steady field gives zero displacement current",
      "स्थिर E पर dΦ_E/dt = 0 तथा I_d = 0" in source_text(41, "steps"))

# Q42: vacuum wave speed from electromagnetic constants.
c42 = 1 / math.sqrt(MU0 * EPS0)
check(42, "speed from 1/sqrt(mu0 epsilon0) (m/s)", c42, 2.9986e8, rel_tol=2e-5)
truth(42, "wave-equation coefficient is inverse speed squared",
      math.isclose(MU0 * EPS0, 1 / c42**2, rel_tol=1e-15)
      and "∂²E/∂x² = μ₀ε₀ ∂²E/∂t²" in source_text(42, "formula"))

# Q43: transverse geometry and phase.
e_axis = (0, 1, 0)
b_axis = (0, 0, 1)
cross = (e_axis[1] * b_axis[2] - e_axis[2] * b_axis[1],
         e_axis[2] * b_axis[0] - e_axis[0] * b_axis[2],
         e_axis[0] * b_axis[1] - e_axis[1] * b_axis[0])
truth(43, "E perpendicular to B", sum(a * b for a, b in zip(e_axis, b_axis)) == 0
      and "E, B और प्रसार दिशा परस्पर लम्बवत्" in source_text(43, "ans"))
truth(43, "E cross B points along +x propagation", cross == (1, 0, 0)
      and "E × B +x में" in source_text(43, "ans"))
truth(43, "E and B have zero phase difference",
      "E तथा B समान कला में" in source_text(43, "ans")
      and "कला-अन्तर 0°" in source_text(43, "steps"))

# Q44: equal electric and magnetic energy contributions.
truth(44, "E=cB plus c^2=1/(mu0 epsilon0) implies uE=uB",
      math.isclose(0.5 * EPS0 * (c42 * 2e-6) ** 2,
                   (2e-6) ** 2 / (2 * MU0), rel_tol=1e-12))
truth(44, "total density is twice either equal contribution",
      math.isclose(2 * 0.5, 1.0) and "u_E = u_B प्रत्येक क्षण" in source_text(44, "ans"))

# Q45: average intensity derivation.
check(45, "cycle average of sin squared", sum(math.sin((i + 0.5) * 2 * math.pi / 100000) ** 2
                                                for i in range(100000)) / 100000, 0.500, abs_tol=1e-12)
check(45, "intensity coefficient c epsilon0 / 2", C * EPS0 / 2, 1.3275e-3)

# Q46: production requires time-varying/accelerated source at board level.
truth(46, "static charge does not launch a continuing EM wave",
      "स्थिर आवेश निरन्तर EM तरंग नहीं बनाता" in source_text(46, "ans"))
truth(46, "accelerated charge supplies time-varying fields",
      "त्वरित या दोलित आवेश" in source_text(46, "ans")
      and "समय-परिवर्ती E और B" in source_text(46, "ans"))
truth(46, "radiated energy comes from the driving source",
      "बाहरी साधन" in source_text(46, "steps") and "ऊर्जा" in source_text(46, "steps"))

# Q47: standard spectrum order, trends, and bounded hazards.
spectrum_order_hi = "रेडियो, सूक्ष्मतरंग, अवरक्त, दृश्य, पराबैंगनी, एक्स-किरण, गामा-किरण"
truth(47, "seven spectrum bands in increasing-frequency order",
      spectrum_order_hi in source_text(47, "ans"))
truth(47, "wavelength decreases while frequency and energy increase",
      "f और ऊर्जा बढ़ते तथा λ घटती" in source_text(47, "ans"))
truth(47, "all seven bands include appropriate safety context",
      all(term in source_text(47, "steps") for term in
          ("उच्च-शक्ति प्रेषक", "तीव्र संपर्क ऊतक", "तीव्र IR", "अत्यधिक तेज प्रकाश",
           "त्वचा और आँख", "आयनीकारक")))

# Q48: capacitor gap—A=.020 m^2; field 0 to 1.5e5 V/m in 3 microseconds.
dedt48 = 1.5e5 / 3e-6
check(48, "electric-field rise rate (V/m/s)", dedt48, 5.00e10)
check(48, "electric-flux rise rate (V m/s)", 0.020 * dedt48, 1.00e9)
check(48, "gap displacement current (A)", EPS0 * 0.020 * dedt48, 8.85e-3)
check(48, "gap displacement current (mA)", EPS0 * 0.020 * dedt48 * 1e3, 8.85)
truth(48, "specified wire current equals gap displacement current",
      math.isclose(8.85e-3, EPS0 * 0.020 * dedt48)
      and "I_d = 8.85 mA = I_c" in source_text(48, "ans"))

# Q49: self-sustaining fields and no-medium property.
truth(49, "published answer identifies field rather than particle oscillation",
      "EM तरंग क्षेत्र-दोलन है, कण-दोलन नहीं" in source_text(49, "ans"))
truth(49, "changing E and B are mutually linked",
      "समय-परिवर्ती E" in source_text(49, "steps")
      and "समय-परिवर्ती B" in source_text(49, "steps"))
truth(49, "published answer states vacuum propagation and transverse geometry",
      "निर्वात में भी c" in source_text(49, "ans")
      and "अनुप्रस्थ" in source_text(49, "ans"))

# Q50: order four given radiations by converting all to frequency.
f_radio50 = C / 10
f_ir50 = C / 10e-6
f_uv50 = 1.5e15
f_x50 = 3.0e18
check(50, "10 m radio frequency (Hz)", f_radio50, 3.00e7)
check(50, "10 micrometre IR frequency (Hz)", f_ir50, 3.00e13)
check(50, "UV wavelength from frequency (m)", C / f_uv50, 2.00e-7)
check(50, "X-ray wavelength from frequency (m)", C / f_x50, 1.00e-10)
truth(50, "frequency/energy order radio < IR < UV < X-ray",
      f_radio50 < f_ir50 < f_uv50 < f_x50
      and "A (रेडियो) < B (अवरक्त) < C (पराबैंगनी) < D (एक्स-किरण)" in source_text(50, "ans"))

print("\n=== PART 3B: कठिन/बहुचरणीय (Q51–Q60) ===")
# Q51: C=5 microfarad, dV/dt=2e4 V/s, loop r=2 cm enclosing full current.
id51 = 5e-6 * 2e4
check(51, "displacement current (A)", id51, 0.100)
check(51, "gap magnetic field (T)", MU0 * id51 / (2 * math.pi * 0.020), 1.00e-6)
check(51, "gap magnetic field (microtesla)", MU0 * id51 / (2 * math.pi * 0.020) * 1e6, 1.00)
truth(51, "circular axial symmetry required by field calculation is published",
      "वृत्ताकार समानांतर प्लेटों" in source_text(51, "q")
      and "अक्ष के सहकेन्द्रीय" in source_text(51, "q"))

# Q52: E=240 sin(6pi*10^8 t - 2pi x) y-hat.
omega52 = 6 * math.pi * 1e8
k52 = 2 * math.pi
check(52, "frequency (Hz)", omega52 / (2 * math.pi), 3.00e8)
check(52, "wavelength (m)", 2 * math.pi / k52, 1.00)
check(52, "magnetic amplitude (T)", 240 / C, 8.00e-7)
truth(52, "sin(omega t-kx) travels in +x and B is +z for E +y",
      cross == (1, 0, 0) and "तरंग +x में चलती है" in source_text(52, "ans")
      and "B +z में" in source_text(52, "ans"))

# Q53: solar-like intensity 1360 W/m^2.
e53 = math.sqrt(2 * 1360 / (C * EPS0))
b53 = e53 / C
check(53, "electric amplitude (V/m)", e53, 1012.2, rel_tol=6e-5)
check(53, "magnetic amplitude (T)", b53, 3.3739e-6, rel_tol=6e-5)
check(53, "average total energy density (J/m^3)", 1360 / C, 4.5333e-6, rel_tol=2e-5)

# Q54: enrichment—500 W/m^2, area .010 m^2, duration .20 s, absorption.
p54 = 500 * 0.010
u54 = p54 * 0.20
check(54, "incident power (W)", p54, 5.00)
check(54, "absorbed energy (J)", u54, 1.00)
check(54, "transferred momentum (kg m/s)", u54 / C, 3.333e-9, rel_tol=2e-4)

# Q55: radio lambda=100 m versus UV lambda=300 nm.
f_r55 = C / 100
f_u55 = C / 300e-9
check(55, "radio frequency (Hz)", f_r55, 3.00e6)
check(55, "UV frequency (Hz)", f_u55, 1.00e15)
check(55, "radio photon energy (J)", H * f_r55, 1.9878e-27)
check(55, "UV photon energy (J)", H * f_u55, 6.626e-19)
check(55, "frequency and photon-energy ratio", f_u55 / f_r55, 3.3333e8, rel_tol=2e-5)
truth(55, "photon calculation is visibly labelled cross-chapter",
      "अन्तर-अध्याय" in source_text(55, "topic", "q"))

# Q56: I=0.50 A, A=.010 m^2, starts from E=0, t=2 ns, plate gap 1 mm.
dedt56 = 0.50 / (EPS0 * 0.010)
e56 = dedt56 * 2e-9
check(56, "electric-field rise rate (V/m/s)", dedt56, 5.6497e12, rel_tol=2e-5)
check(56, "field after 2 ns (V/m)", e56, 1.12994e4, rel_tol=2e-5)
check(56, "gap voltage after 2 ns (V)", e56 * 1e-3, 11.2994, rel_tol=2e-5)

# Q57: amplitude doubled from a 20 W/m^2 wave.
check(57, "intensity scale factor", (2.0) ** 2, 4.00)
check(57, "new intensity (W/m^2)", 20 * 4, 80.0)
check(57, "original average density (J/m^3)", 20 / C, 6.667e-8, rel_tol=6e-5)
check(57, "new average density (J/m^3)", 80 / C, 2.667e-7, rel_tol=2e-4)

# Q58: visible interval 400–700 nm.
f_violet58 = C / 400e-9
f_red58 = C / 700e-9
check(58, "violet-end frequency (Hz)", f_violet58, 7.50e14)
check(58, "red-end frequency (Hz)", f_red58, 4.286e14, rel_tol=8e-5)
truth(58, "visible frequency decreases as wavelength increases",
      f_violet58 > f_red58 and "बैंगनी सिरे की आवृत्ति अधिक" in source_text(58, "ans"))

# Q59: safe spectrum matching invariants bound to the published answer/steps.
truth(59, "microwaves are matched to radar",
      "रडार—सूक्ष्मतरंग" in source_text(59, "ans"))
truth(59, "infrared is matched to remote controls",
      "रिमोट—अवरक्त" in source_text(59, "ans"))
truth(59, "UV, X-rays and gamma include exposure precautions",
      all(term in source_text(59, "steps") for term in ("त्वचा और आँख", "आयनीकारक", "परिरक्षण")))
truth(59, "X-rays are matched to medical bone imaging",
      "हड्डी चित्र—एक्स-किरण" in source_text(59, "ans"))

# Q60: B0=4 microtesla, f=75 MHz; absorbing A=20 cm^2 for 5 s.
b60 = 4e-6
e60 = C * b60
lam60 = C / 75e6
i60 = 0.5 * C * b60**2 / MU0
check(60, "electric amplitude (V/m)", e60, 1200.0)
check(60, "wavelength (m)", lam60, 4.00)
check(60, "average intensity (W/m^2)", i60, 1909.9, rel_tol=3e-5)
check(60, "absorbed energy (J)", i60 * 20e-4 * 5, 19.099, rel_tol=3e-5)
check(60, "absorbing radiation pressure (Pa)", i60 / C, 6.3662e-6, rel_tol=3e-5)
truth(60, "radiation-pressure portion is visibly labelled enrichment",
      "समृद्धि" in source_text(60, "topic", "q"))

print("\n=== SUPPLEMENTAL PUBLISHED NUMERICAL CLAIMS ===")
# Numerical values appearing in checks/alternatives are independently recomputed too.
check(3, "published E0/B0 back-check (m/s)", 600 / (2.00e-6), 3.00e8)
claim(3, "alt", "3.00 × 10⁸ m/s")
check(4, "published cB0 back-check (V/m)", C * 5.00e-7, 150.0)
claim(4, "alt", "150 V/m")
check(5, "300 MHz reference wavelength (m)", C / 300e6, 1.00)
claim(5, "alt", "300 MHz", "1 m")
check(6, "10 GHz period (ns)", 1 / 10e9 * 1e9, 0.100)
check(6, "vacuum distance per nanosecond (cm)", C * 1e-9 * 100, 30.0)
claim(6, "alt", "30 cm प्रति नैनोसेकंड", "0.1 ns")
check(7, "vacuum distance per millisecond (km)", C * 1e-3 / 1000, 300.0)
claim(7, "alt", "1 ms", "300 km")
check(8, "rounded epsilon0 E squared (J/m^3)", EPS0 * 300**2, 8.00e-7, rel_tol=5e-3)
check(8, "rounded half energy density (J/m^3)", 0.5 * EPS0 * 300**2, 4.00e-7, rel_tol=5e-3)
claim(8, "alt", "8 × 10⁻⁷", "4 × 10⁻⁷ J/m³")
check(9, "companion electric amplitude (V/m)", C * 1e-6, 300.0)
check(9, "companion electric density (J/m^3)", 0.5 * EPS0 * 300**2, 3.98e-7, rel_tol=1e-3)
claim(9, "alt", "E ≈ cB = 300 V/m", "3.98 × 10⁻⁷ J/m³")
check(10, "one equal energy contribution (J/m^3)", 0.5 * EPS0 * 300**2, 3.9825e-7)
claim(10, "alt", "u_E = 3.9825 × 10⁻⁷ J/m³")
check(12, "published c epsilon0 denominator", C * EPS0, 2.655e-3)
check(12, "published square-root radicand", 2000 / (C * EPS0), 753295.67, rel_tol=1e-6)
claim(12, "steps", "cε₀ = 2.655 × 10⁻³", "√753295.67")
check(19, "same-intensity absorbing pressure (Pa)", 450 / C, 1.50e-6)
claim(19, "alt", "1.50 × 10⁻⁶ Pa")
check(22, "voltage rise in one millisecond (V)", 4000 * 1e-3, 4.00)
claim(22, "alt", "1.00 ms", "4.00 V")
check(27, "visible lower reference frequency (Hz)", C / 750e-9, 4.00e14)
check(27, "visible upper reference frequency (Hz)", C / 400e-9, 7.50e14)
claim(27, "alt", "4–7.5 × 10¹⁴ Hz")
check(28, "published amplitude radicand", 2 * 4.425e-6 / EPS0, 1.00e6)
claim(28, "steps", "1.00 × 10⁶", "1.00 × 10³ V/m")
check(29, "companion electric amplitude (V/m)", C * 1e-6, 300.0)
check(29, "electric-form intensity check (W/m^2)", 0.5 * C * EPS0 * 300**2, 119.5, rel_tol=3e-4)
claim(29, "alt", "E_0 = cB_0 ≈ 300 V/m", "119.5 W/m²")
check(31, "average density used by alternative (J/m^3)", 0.5 * EPS0 * 600**2, 1.593e-6)
claim(31, "alt", "1.593 × 10⁻⁶ J/m³")
check(34, "charge change alternative (C)", 4e-6 * 120, 480e-6)
claim(34, "alt", "480 μC")
check(36, "intensity alternative (W/m^2)", C * (0.5 * EPS0 * 450**2), 268.8, rel_tol=1e-4)
claim(36, "alt", "268.8 W/m²")
check(38, "wavelength alternative (m)", C / 60e6, 5.00)
claim(38, "alt", "λ = c/f = 5.00 m")
check(50, "lambda-times-frequency consistency (m/s)", (C / f_uv50) * f_uv50, 3.00e8)
claim(50, "alt", "3.00 × 10⁸ m/s")
check(52, "phase-speed direction check (m/s)", omega52 / k52, 3.00e8)
claim(52, "alt", "3.00 × 10⁸ m/s")
check(54, "average force alternative (N)", p54 / C, 1.667e-8, rel_tol=3e-4)
claim(54, "alt", "1.667 × 10⁻⁸ N")
check(56, "parallel-plate capacitance alternative (F)", EPS0 * 0.010 / 1e-3, 8.85e-11)
claim(56, "alt", "8.85 × 10⁻¹¹ F")
check(58, "visible endpoint frequency ratio", f_violet58 / f_red58, 1.75)
claim(58, "alt", "1.75")
check(60, "area conversion (m^2)", 20.0e-4, 2.00e-3)
claim(60, "steps", "2.00 × 10⁻³ m²")

# Exact answer snapshots bind every independently computed final result to what the
# builder renders. A mutation in any published answer therefore makes this verifier fail.
EXPECTED_ANSWERS = {
 1: "विस्थापन धारा I_d = 1.77 × 10⁻⁶ A = 1.77 μA।",
 2: "प्लेटों के बीच विस्थापन धारा I_d = 6.00 mA।",
 3: "वैद्युत क्षेत्र का आयाम E_0 = 600 V/m।",
 4: "चुंबकीय क्षेत्र आयाम B_0 = 5.00 × 10⁻⁷ T = 0.500 μT।",
 5: "रेडियो तरंग की तरंगदैर्घ्य λ = 3.00 m।",
 6: "सूक्ष्मतरंग की आवृत्ति f = 1.00 × 10¹⁰ Hz = 10.0 GHz।",
 7: "संकेत का यात्रा-समय t = 2.00 × 10⁻³ s = 2.00 ms।",
 8: "तात्क्षणिक वैद्युत ऊर्जा घनत्व u_E = 3.9825 × 10⁻⁷ J/m³।",
 9: "तात्क्षणिक चुंबकीय ऊर्जा घनत्व u_B ≈ 3.9789 × 10⁻⁷ J/m³।",
 10: "तरंग का कुल तात्क्षणिक ऊर्जा घनत्व u = 7.965 × 10⁻⁷ J/m³।",
 11: "तरंग की औसत तीव्रता I_av = 19.116 W/m² ≈ 19.1 W/m²।",
 12: "वैद्युत क्षेत्र का आयाम E_0 ≈ 867.93 V/m, अर्थात् लगभग 868 V/m।",
 13: "फोटॉन ऊर्जा E_ph = 6.626 × 10⁻¹⁹ J ≈ 4.14 eV।",
 14: "दृश्य प्रकाश की आवृत्ति f = 5.00 × 10¹⁴ Hz।",
 15: "एक्स-किरण की तरंगदैर्घ्य λ = 1.00 × 10⁻¹⁰ m = 0.100 nm।",
 16: "तरंग 2.00 μs में 10 पूरे चक्र बनाती है।",
 17: "दोनों बिन्दुओं के बीच कला-अन्तर Δφ = π/2 rad = 90°।",
 18: "पूर्ण अवशोषण के लिए औसत विकिरण दाब p_rad = 2.00 × 10⁻⁶ Pa।",
 19: "पूर्ण परावर्तन के लिए औसत विकिरण दाब p_rad = 3.00 × 10⁻⁶ Pa।",
 20: "75.0 MHz के लिए λ₁ = 4.00 m, 150 MHz के लिए λ₂ = 2.00 m; अनुपात 2.00 : 1।",
 21: "वैद्युत फ्लक्स की परिवर्तन-दर dΦ_E/dt = 5.00 × 10⁵ V·m/s।",
 22: "वोल्टता की वृद्धि-दर dV/dt = 4.00 × 10³ V/s।",
 23: "संधारित्र की धारिता C = 3.00 × 10⁻⁶ F = 3.00 μF।",
 24: "वैद्युत क्षेत्र आयाम E_0 = 360 V/m।",
 25: "चुंबकीय क्षेत्र आयाम B_0 = 3.00 × 10⁻⁶ T = 3.00 μT।",
 26: "तरंग की आवृत्ति f = 4.00 × 10¹⁴ Hz।",
 27: "तरंगदैर्घ्य λ = 1.20 × 10⁻⁶ m = 1.20 μm; यह अवरक्त क्षेत्र में है।",
 28: "वैद्युत क्षेत्र आयाम E_0 = 1000 V/m।",
 29: "चुंबकीय क्षेत्र आयाम B_0 ≈ 1.00 × 10⁻⁶ T = 1.00 μT।",
 30: "तरंग की औसत तीव्रता I_av = 600 W/m²।",
 31: "(i) B_0 = 2.00 × 10⁻⁶ T = 2.00 μT; (ii) I_av = 477.9 W/m²।",
 32: "(i) λ = 3.00 m; (ii) T = 1.00 × 10⁻⁸ s = 10.0 ns।",
 33: "(i) f = 6.00 × 10¹⁴ Hz; (ii) E_ph = 3.9756 × 10⁻¹⁹ J ≈ 2.48 eV।",
 34: "(i) dV/dt = 6.00 × 10⁴ V/s; (ii) I_d = 0.240 A।",
 35: "(i) dΦ_E/dt = 4.00 × 10⁸ V·m/s; (ii) I_d = 3.54 × 10⁻³ A = 3.54 mA।",
 36: "(i) E_0 = 450 V/m; (ii) u_av = 8.9606 × 10⁻⁷ J/m³।",
 37: "(i) E_0 = 200 V/m; (ii) B_0 ≈ 6.667 × 10⁻⁷ T।",
 38: "(i) t = 0.500 s; (ii) N = 3.00 × 10⁷ चक्र।",
 39: "(i) रेडियो λ = 100 m; (ii) सूक्ष्मतरंग λ = 1.00 × 10⁻² m = 1.00 cm।",
 40: "(i) प्राप्त शक्ति P = 0.160 W; (ii) अवशोषित ऊर्जा U = 1.60 J।",
 41: "मैक्सवेल की विस्थापन धारा I_d = ε₀ dΦ_E/dt संधारित्र-अंतराल में चालन धारा का सातत्य पूरा करती है; आवेशन के समय I_d = dQ/dt = I_c।",
 42: "गुणांक तुलना से c = 1/√(μ₀ε₀) ≈ 2.9986 × 10⁸ m/s ≈ 3.00 × 10⁸ m/s मिलता है।",
 43: "B +z दिशा में होगा; E, B और प्रसार दिशा परस्पर लम्बवत् हैं, E × B +x में है और E तथा B समान कला में हैं।",
 44: "u_E = u_B प्रत्येक क्षण; कुल u = ε₀E² = B²/μ₀ और ज्यावक्रीय चक्र-औसत u_av = (1/2)ε₀E_0²।",
 45: "औसत तीव्रता I_av = E_0B_0/(2μ₀) = (1/2)cε₀E_0²; ऊर्जा-प्रवाह की दिशा E × B, अर्थात् प्रसार दिशा है।",
 46: "त्वरित या दोलित आवेश समय-परिवर्ती E और B उत्पन्न कर वैद्युतचुम्बकीय तरंग विकिरित करता है; स्थिर आवेश निरन्तर EM तरंग नहीं बनाता।",
 47: "क्रम: रेडियो, सूक्ष्मतरंग, अवरक्त, दृश्य, पराबैंगनी, एक्स-किरण, गामा-किरण; इस क्रम में f और ऊर्जा बढ़ते तथा λ घटती है।",
 48: "I_d = 8.85 mA = I_c; अतः प्लेट-अंतराल और तार के लिए धारा-सातत्य सत्यापित है।",
 49: "EM तरंग क्षेत्र-दोलन है, कण-दोलन नहीं; बदलते E और B का युग्म निर्वात में भी c से ऊर्जा पहुँचाता है। यह अनुप्रस्थ है और E, B समान कला में हैं।",
 50: "बढ़ती आवृत्ति और ऊर्जा का क्रम A (रेडियो) < B (अवरक्त) < C (पराबैंगनी) < D (एक्स-किरण) है।",
 51: "(i) I_d = 0.100 A; (ii) B = 1.00 × 10⁻⁶ T = 1.00 μT।",
 52: "f = 3.00 × 10⁸ Hz, λ = 1.00 m, B_0 = 8.00 × 10⁻⁷ T; B +z में समान कला में और तरंग +x में चलती है।",
 53: "E_0 ≈ 1012.2 V/m, B_0 ≈ 3.3739 × 10⁻⁶ T और u_av ≈ 4.5333 × 10⁻⁶ J/m³।",
 54: "P = 5.00 W, U = 1.00 J और अवशोषित संवेग p = 3.333 × 10⁻⁹ kg·m/s।",
 55: "f_R = 3.00 × 10⁶ Hz, E_R = 1.9878 × 10⁻²⁷ J; f_U = 1.00 × 10¹⁵ Hz, E_U = 6.626 × 10⁻¹⁹ J; अनुपात ≈ 3.3333 × 10⁸।",
 56: "dE/dt ≈ 5.6497 × 10¹² V·m⁻¹·s⁻¹, E ≈ 1.12994 × 10⁴ V/m और V ≈ 11.2994 V।",
 57: "नई तीव्रता 80.0 W/m²; u_old = 6.667 × 10⁻⁸ J/m³ और u_new = 2.667 × 10⁻⁷ J/m³।",
 58: "400 nm पर f ≈ 7.50 × 10¹⁴ Hz और 700 nm पर f ≈ 4.286 × 10¹⁴ Hz; बैंगनी सिरे की आवृत्ति अधिक है।",
 59: "रडार—सूक्ष्मतरंग; रिमोट—अवरक्त; हड्डी चित्र—एक्स-किरण; कीटाणुनाशन—पराबैंगनी; नाभिकीय संक्रमण—गामा, उचित संपर्क-नियंत्रण सहित।",
 60: "E_0 = 1200 V/m, λ = 4.00 m, I_av ≈ 1909.9 W/m², U ≈ 19.099 J और p_rad ≈ 6.3662 × 10⁻⁶ Pa।",
}
for qno, expected_answer in EXPECTED_ANSWERS.items():
    truth(qno, "published final answer matches independently verified result",
          by_number[qno]["ans"] == expected_answer)

# Every number in q/formula/why/steps/answer/trick/alternative is pinned to the
# independently audited case. This makes prompt, conversion, intermediate-step,
# final-answer, and alternative-check mutations fail closed.
EXPECTED_NUMERIC_SIGNATURES = {
 1: (13, "dc5c2625f693134ca5756b65003c86c23547e0b16780274356546aba102c68d7"),
 2: (15, "7340fd6e534f76e44d3781cea51497cb75f97bca5d09ce0b079aafa10cfbf27e"),
 3: (28, "0c9ac96469138bd0aedb484de457a7f34a7be6c6e4705a18e240eb8407cbe102"),
 4: (32, "2e8e9a88539963f06f99163607a2c11385abdd130aab94a9d2f7ec0e504d7e1a"),
 5: (17, "6e99172a988034cc8da98653065b58372a224610034facd0244392671e712844"),
 6: (21, "484e531986156809ca4c56db0ea06fe751587bf32fedfdc8bfd7f066762e6205"),
 7: (15, "3055ab3ae6ff4a33fba559b1924dcb70526bb21945408266b033ed7c12f08449"),
 8: (23, "023010019d3080e7b488b8de3c0f204c8bf11e112802eb86b9a7f6b9cf4c1622"),
 9: (26, "5f4d4f636da79ad51705ce9cead624d83840ba6b4dbb2b2c09e4aa7e7e19d057"),
 10: (14, "c17a0c8ecb919dcb3456b753833c480f6ce3899b4e0b3f820ea0c80969bd433f"),
 11: (35, "ac26ec5d40df6268400b5df1a49e9bb0b3309a92804cb405c1e1ef4f6a1edb91"),
 12: (29, "b63467ff1eeb553736ab05928c08dd7e78e4998925ce540dfe767aaa9a0b1aa3"),
 13: (15, "69b47d017d201d2987ce302691989f8bb46dfd859fc1dcc62b1b9a00bc924dbe"),
 14: (15, "a83cb0b59b0a2cb12ef5c7e7e9accca5bfc9e748c758d966270d220a278f82a8"),
 15: (13, "b71c4216c1252408681c88589c9462b5acd743f3a27b94dbf315f7f934c5e189"),
 16: (19, "5ea9bbd690bbaf083d7003227b79b7826aec2ae9aef0476dde235e75052b20af"),
 17: (24, "f2ba04d85ec3085a9d8a80ec076419123443b20d43734fff24208d700a162a02"),
 18: (7, "3f93b44878d9477bac974ddd80e19e0b88db2350cf2c6a2ff782457e015a9337"),
 19: (14, "bd9f1badbc4d11dca14dec4de6088d2ebc637cd32c596d890a35f539a2149f4b"),
 20: (21, "d0581b76276656e9761a22ea05ff734579d41eef8fcb0e3dd2fff37b593feb16"),
 21: (17, "992eb729b899579d4bd9b50f9f19ec26bb317a5fc15ffb7b92f5779246b7e6e5"),
 22: (19, "ee108c208e82d0d4d17cfb8cf3cd05bc2b1169391437600724fa706af51ef34a"),
 23: (15, "2b2fcf71e5b9ee1739fa7d4c3e870c6ec8663623d541778be347d2ee06c24a5c"),
 24: (28, "4f359a068648b80dd528b0ec7812c76e5cc1f8451d269082404cdc5eb7de20d7"),
 25: (26, "92230e9ee1d77270a99ca6963045bea3fe0c4f61ae2f8af1240dacca60395d1f"),
 26: (14, "826a3b05ea2e0e633fd0bbb9d78b92bdb2f76f7243c08e0589553fcbe504e6c8"),
 27: (11, "81de67e54cc31cd43d8d3de2f587daf4f6d7f3dbf03e98857b228ae1cb3901dc"),
 28: (28, "82234c83c5d0f73c3d2656551776a2c2b093b16d5de220b27808ceded744c758"),
 29: (33, "1cd687c53314f1f1a91b52a8eb63051af69ca75d2ef39aa3f2729cb5282aebe8"),
 30: (14, "e911a7f60a5a5ad4adb8598ae4e1b6027d8a26174fe5fe4b5f46cc2e17bc01ab"),
 31: (36, "7168cf4c616b1b730b34db85e1fab4fcee25a78410312e4098730cbaf45e953b"),
 32: (18, "fa1ff923931b0dc8ca0929b7906a8ff9246be1ef31e42a0edbd8d80434a578a8"),
 33: (18, "ed9d59d767c5e0ab79b5e0806a87d70cc5fd79a2eb590e7c6b3d1cf23d9b6ff6"),
 34: (24, "7aac35f02d63b38ff61025327aecfcea1dad0427c2ef1dc9abd95fa46a123635"),
 35: (22, "7d2e0415ca00eda30f976cb463e72e9d565e0131393b5e69e75a93753dbb4ffa"),
 36: (31, "a62e3e0f8a6a0a4f9c085f853018592ee885efa80b11be4c24726b1a264999f8"),
 37: (31, "7422978add092932475a759ecee05762ce86f48d18a4ffe5678b4e6a4211ee95"),
 38: (17, "c7241942c1f01e5b92cdd9a60f979d06e775a1c444436bffa85b5ed8f4bcc22c"),
 39: (25, "5cccd2e9b8abc3a5a48ca11a8b4088a9f60cc54fa37a02c780d546fb6046d4c8"),
 40: (22, "2f4d08e878910e8f18eab615b4fec613ca6d6384f6317909952b376ee6e13471"),
 41: (2, "8c9bfe969acdc3509c27b313bbc9c005520b5d8b172e280cb9c35213572372d5"),
 42: (18, "10c6e80b976e2e1a2248ace89c1fe10ad4dd881375e6eca0be050902f53c13fb"),
 43: (9, "8cfdff8f7468c764b008d4c89f314733d2105f98e0178ca018d31ee13a5b2e1a"),
 44: (27, "7b054482dc93490ef15f81f3b2ffbb32a0b0f29ffc850d0bdc66ca2ed2bf6c3a"),
 45: (40, "00cf4475364ce554cc721936967017e5880971f04f63048d8aa05d1c6b8561e8"),
 46: (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
 47: (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
 48: (18, "84b78b1c3ca160ec044463f15389714599d2ff974cd8ee9de4377e242c805783"),
 49: (2, "b938c7e394e2a43e45ac554fe585c5222c6fb85df92fcbe87e2bada5154c770b"),
 50: (17, "1f4651a8ffed3fa8f8b486fe5af3bf2383a6ed0be8ceb970f1906b645e3fa1d9"),
 51: (29, "5f66deea5252f133567703206efec8c88560c5a369e24d6ae7af4b7b73e2d01b"),
 52: (60, "dc707698c0c8917a44b7f6d7a6d4b7c76e5bcf07b38e9cd119c937a0a85d049b"),
 53: (32, "9d3c8224419241d3e10f7f71957951c90c4408b0689f89a9bd34ff233b92d511"),
 54: (21, "6fbb856d61fedff64cb82a1a2125b262c8bfc6fc225fb6c600dbf2bd008f20ea"),
 55: (28, "74afb7271fb25c656457b8c9802ee67e9bbb518b3faf5fe3b3cbfee145ed4dd8"),
 56: (29, "26bd377c585ab47650f27261b32884957549022ea360d200f570eccabb8ec1d3"),
 57: (26, "53643f7194121c07f399dd11b5d38c526592a0cb6db6b8ad61441555b694c5aa"),
 58: (29, "2747e2672c25d777d6517d1e2354530656dc39cfaf508ccd9085755d2bc7af4d"),
 59: (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
 60: (50, "60ae9bfae5c7a001be19376a04db1adeafe1b95fb30bf8ad815533b1a5bbdee5"),
}
for qno, expected_signature in EXPECTED_NUMERIC_SIGNATURES.items():
    truth(qno, "all published numerical text matches audited calculation case",
          numeric_signature(by_number[qno]) == expected_signature)

EXPECTED_COMPLETE_SOURCE_DIGEST = "10f26b40965786fe7ceddfbcc922ffc1ec3277bd0cfff48e59b369ba16ceb453"
truth(1, "complete source fields match the fully audited character-level digest",
      complete_source_digest(questions) == EXPECTED_COMPLETE_SOURCE_DIGEST)

# Derived results that are not repeated in the final answer are bound to their steps.
claim(35, "steps", "4.00 × 10¹⁰ V·m⁻¹·s⁻¹", "4.00 × 10⁸ V·m/s")
claim(39, "steps", "10⁴ = 100/0.0100")
claim(45, "steps", "⟨sin²θ⟩ = 1/2")
claim(48, "steps", "5.00 × 10¹⁰ V·m⁻¹·s⁻¹", "1.00 × 10⁹ V·m/s")
claim(50, "steps", "3.00 × 10⁷ Hz", "3.00 × 10¹³ Hz", "2.00 × 10⁻⁷ m", "1.00 × 10⁻¹⁰ m")
claim(57, "steps", "2² = 4.00")

print("\n=== NUMERICAL / CONCEPTUAL COVERAGE ===")
expected_coverage = set(range(1, 61))
missing = sorted(expected_coverage - covered_questions)
extra = sorted(covered_questions - expected_coverage)
failed = [(q, label, got, expected) for q, label, passed, got, expected in checks if not passed]
print(f"checks={len(checks)} questions_covered={len(covered_questions)}/60")
print(f"missing={missing or 'none'} extra={extra or 'none'} failures={len(failed)}")
assert not missing, f"बिना स्वतंत्र जाँच के प्रश्न: {missing}"
assert not extra, f"अमान्य प्रश्न कवरेज: {extra}"
assert not failed, "असफल जाँचें:\n" + "\n".join(map(str, failed))

print("\n=== SOURCE DATA STRUCTURE / QUALITY ===")
for part_no, part in enumerate(parts, 1):
    assert isinstance(part, list), f"PART{part_no} list होना चाहिए"
    assert len(part) == 20, f"PART{part_no} में 20 प्रश्न चाहिए, मिले {len(part)}"

SCHEMA = {"n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"}
assert len(questions) == 60
assert [q["n"] for q in questions] == list(range(1, 61)), "क्रम 1–60 ठीक नहीं"
assert [len(p) for p in parts] == [20, 20, 20], "20/20/20 split टूटा"
assert [q["cat"] for q in questions] == [1] * 20 + [2] * 20 + [3] * 20, "category split गलत"
assert [q["n"] for q in parts[1][:10]] == list(range(21, 31)), "one-unknown range Q21–Q30 चाहिए"
assert [q["n"] for q in parts[1][10:]] == list(range(31, 41)), "two-unknown range Q31–Q40 चाहिए"

normalised_prompts = []
for q in questions:
    assert set(q) == SCHEMA, f"Q{q.get('n', '?')}: exact 11-key schema नहीं: {set(q) ^ SCHEMA}"
    assert isinstance(q["n"], int) and isinstance(q["cat"], int)
    assert isinstance(q["marks"], int) and q["marks"] in {1, 2, 3, 4, 5}, f"Q{q['n']}: marks अमान्य"
    for field in ("topic", "q", "formula", "why", "ans", "trick", "alt"):
        assert isinstance(q[field], str) and q[field].strip(), f"Q{q['n']} {field}: रिक्त/अमान्य"
    assert len(q["q"].strip()) >= 45, f"Q{q['n']}: prompt बहुत छोटा"
    assert len(q["why"].strip()) >= 70, f"Q{q['n']}: formula rationale पर्याप्त नहीं"
    assert len(q["trick"].strip()) >= 55, f"Q{q['n']}: trick/common-error पर्याप्त नहीं"
    assert len(q["alt"].strip()) >= 55, f"Q{q['n']}: alternative/check पर्याप्त नहीं"
    assert isinstance(q["steps"], list) and len(q["steps"]) >= 3, f"Q{q['n']}: कम-से-कम 3 substantial steps चाहिए"
    for idx, step in enumerate(q["steps"], 1):
        assert isinstance(step, tuple) and len(step) == 2, f"Q{q['n']} step {idx}: (heading, body) tuple चाहिए"
        heading, body = step
        assert isinstance(heading, str) and heading.strip()
        assert isinstance(body, str) and len(body.strip()) >= 18, f"Q{q['n']} step {idx}: विवरण छोटा"
    normalised_prompts.append(re.sub(r"\s+", " ", q["q"].strip().casefold()))

assert len(set(normalised_prompts)) == 60, "duplicate prompts मिले"
full_derivation = [q for q in questions[40:50] if q["marks"] in {3, 4, 5} and len(q["steps"]) >= 4]
assert 8 <= len(full_derivation) <= 10, f"Q41–Q50 में 8–10 पूर्ण derivation/concept solutions चाहिए, मिले {len(full_derivation)}"
assert sum(q["marks"] == 4 for q in questions[40:]) >= 8, "4-mark unit emphasis पर्याप्त नहीं"

# Forbidden Indic scripts; generated Hindi must remain Devanagari.
other_indic = [(0x0980, 0x09FF), (0x0A00, 0x0A7F), (0x0A80, 0x0AFF),
               (0x0B00, 0x0B7F), (0x0B80, 0x0BFF), (0x0C00, 0x0C7F),
               (0x0C80, 0x0CFF), (0x0D00, 0x0D7F)]
for q in questions:
    values = [q[k] for k in ("topic", "q", "formula", "why", "ans", "trick", "alt")]
    values += [piece for step in q["steps"] for piece in step]
    for text in values:
        for char in text:
            assert not any(lo <= ord(char) <= hi for lo, hi in other_indic), \
                f"Q{q['n']}: wrong Indic character U+{ord(char):04X}"

print(f"schema=11 keys; split=20/20/20; numbering=1–60; unique_prompts={len(set(normalised_prompts))}")
print(f"substantial_steps={sum(len(q['steps']) for q in questions)}; full_derivation_concept={len(full_derivation)}")
print(f"valid_marks=60/60; wrong_Indic=0")
print(f"published_answer_bindings={len(EXPECTED_ANSWERS)}/60; numerical_field_signatures={len(EXPECTED_NUMERIC_SIGNATURES)}/60; additional_source_claims={source_claim_checks}")
print("complete_source_digest=matched (all rendered fields, Unicode symbols and exponents)")
print(f"\nALL CHAPTER 8 CHECKS PASSED: {len(checks)} independent/source-bound checks, 60/60 question coverage")
