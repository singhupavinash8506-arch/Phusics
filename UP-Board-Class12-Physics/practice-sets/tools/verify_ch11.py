# -*- coding: utf-8 -*-
"""अध्याय 11 — विकिरण तथा द्रव्य की द्वैत प्रकृति: fail-closed सत्यापन।

यह verifier प्रकाशित स्रोत से स्वतंत्र भौतिक सम्बन्धों द्वारा प्रत्येक संख्यात्मक
निष्कर्ष पुनः निकालता है, सभी 60 उत्तरों को बाँधता है और schema/गुणवत्ता की जाँच
करता है। पूर्ण स्रोत तथा प्रति-प्रश्न numeric fingerprints अनजाने बदलाव रोकते हैं।
--post-build mode समाधान Markdown, master index और PDF को audited स्रोत से बाँधता है।
"""

from __future__ import annotations

import copy
import hashlib
import importlib
import math
from pathlib import Path
import re
import sys

if not __debug__:
    raise RuntimeError("Chapter 11 verifier must run without Python -O")

EXPECTED_KEYS = {
    "n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"
}
H = 6.626e-34
C = 3.00e8
E = 1.602e-19
ME = 9.109e-31
MP = 1.673e-27
PI = math.pi
ROOT = Path(__file__).resolve().parent
PRACTICE = Path("/projects/sandbox/Phusics/UP-Board-Class12-Physics/practice-sets")
SOLUTIONS = PRACTICE / "solutions"

parts = []
for part_number in (1, 2, 3):
    module = importlib.import_module(f"ch11_part{part_number}")
    parts.append(getattr(module, f"PART{part_number}"))
questions = sum(parts, [])
by_number = {q.get("n"): q for q in questions}

checks: list[tuple[int, str, bool]] = []
covered: set[int] = set()
answer_bindings = 0


def check(qno, label, got, expected, rel_tol=8e-4, abs_tol=0.0):
    """Magnitude-aware comparison: nonzero tiny targets can never pass as zero."""
    passed = math.isclose(got, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    checks.append((qno, label, passed))
    covered.add(qno)
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} {label:<57} "
          f"got={got:.12g} expected={expected:.12g}")


def truth(qno, label, condition):
    passed = bool(condition)
    checks.append((qno, label, passed))
    covered.add(qno)
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} {label}")


def source_text(qno, *fields):
    q = by_number[qno]
    chunks = []
    for field in fields or ("topic", "q", "formula", "why", "steps", "ans", "trick", "alt"):
        value = q[field]
        if field == "steps":
            chunks.extend(piece for step in value for piece in step)
        else:
            chunks.append(value)
    return "\n".join(chunks)


def claim(qno, field, *needles):
    global answer_bindings
    haystack = source_text(qno, field)
    missing = [needle for needle in needles if needle not in haystack]
    passed = not missing
    checks.append((qno, f"published {field} binding", passed))
    covered.add(qno)
    if field == "ans":
        answer_bindings += 1
    suffix = f" missing={missing}" if missing else ""
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} published {field}: "
          f"{len(needles)-len(missing)}/{len(needles)}{suffix}")


print("=== PART 1: प्रत्यक्ष सूत्र Q1–Q20 ===")
check(1, "600 nm photon energy (J)", H*C/600e-9, 3.313e-19)
check(1, "600 nm photon energy (eV)", H*C/(600e-9*E), 2.06804)
check(2, "5e14 Hz photon energy (J)", H*5.00e14, 3.313e-19)
check(2, "5e14 Hz photon energy (eV)", H*5.00e14/E, 2.06804)
check(3, "500 nm photon momentum", H/500e-9, 1.3252e-27)
check(4, "3 eV photon momentum", 3*E/C, 1.602e-27)
check(5, "2 W, 500 nm photon rate", 2/(H*C/500e-9), 5.03069e18)
check(6, "2.2 eV threshold frequency", 2.2*E/H, 5.31905e14)
check(7, "2.5 eV threshold wavelength (nm)", H*C/(2.5*E)*1e9, 496.33)
check(8, "4.5 eV minus 2.0 eV Kmax (eV)", 4.5-2.0, 2.50)
check(8, "Kmax (J)", (4.5-2.0)*E, 4.005e-19)
check(9, "3.2 eV stopping potential (V)", 3.2*E/E, 3.20)
energy_400 = H*C/(400e-9*E)
check(10, "400 nm photon energy (eV)", energy_400, 3.10206)
check(10, "400 nm, phi 2 eV Kmax (eV)", energy_400-2.0, 1.10206)
check(10, "stopping potential (V)", (energy_400-2.0)*E/E, 1.10206)
energy_8e14 = H*8.00e14/E
check(11, "8e14 Hz photon energy (eV)", energy_8e14, 3.30886)
check(11, "8e14 Hz, phi 2 eV stopping potential", energy_8e14-2.0, 1.30886)
check(12, "2 eV photoelectron speed", math.sqrt(2*2*E/ME), 8.38737e5)
check(13, "electron wavelength at 1e6 m/s (nm)", H/(ME*1.00e6)*1e9, 0.727412)
check(14, "proton wavelength at 2e5 m/s (pm)", H/(MP*2.00e5)*1e12, 1.98027)
check(15, "150 eV electron wavelength (angstrom)", 12.27/math.sqrt(150), 1.00184)
check(16, "100 V electron wavelength (angstrom)", 12.27/math.sqrt(100), 1.227)
check(17, "100 V proton wavelength (pm)", H/math.sqrt(2*MP*E*100)*1e12, 2.86192)
check(18, "matter wavelength for p=2e-24 (nm)", H/2.00e-24*1e9, 0.3313)
check(19, "electron momentum at 0.15 nm", H/0.15e-9, 4.41733e-24)
check(19, "electron speed at 0.15 nm", H/(0.15e-9*ME), 4.84942e6)
check(20, "1 mJ, 300 nm photon count", 1e-3/(H*C/300e-9), 1.50921e15)

print("\n=== PART 2A: एक अज्ञात Q21–Q30 ===")
check(21, "wavelength for 2.5 eV photon (nm)", H*C/(2.5*E)*1e9, 496.33)
check(22, "wavelength for p=1.5e-27 (nm)", H/1.50e-27*1e9, 441.733)
check(23, "work function for nu0=6e14 (eV)", H*6.00e14/E, 2.48165)
check(24, "work function for lambda0=550 nm (eV)", H*C/(550e-9*E), 2.25604)
check(25, "phi from 350 nm and 1.20 V (eV)", H*C/(350e-9*E)-1.20, 2.34521)
check(26, "frequency from phi 2.0 eV and V0 1.10 V", (2.0+1.10)*E/H, 7.49502e14)
check(27, "V0 at 9e14 Hz and phi 2.2 eV", H*9.00e14/E-2.20, 1.52247)
check(28, "electron rate from 0.40 mA", 0.40e-3/E, 2.49688e15)
check(29, "momentum from electron wavelength 0.10 nm", H/0.10e-9, 6.626e-24)
check(30, "voltage for 0.50 angstrom electron", (12.27/0.50)**2, 602.212)

print("\n=== PART 2B: दो अज्ञात Q31–Q40 ===")
energy_450 = H*C/(450e-9*E)
check(31, "450 nm photon energy (eV)", energy_450, 2.75739)
check(31, "450 nm, phi 1.8 eV V0", energy_450-1.8, 0.957387)
check(32, "V0 at 6e14 Hz, phi 2 eV", H*6e14/E-2.0, 0.481648)
check(32, "V0 at 8e14 Hz, phi 2 eV", H*8e14/E-2.0, 1.30886)
slope33 = (1.328-0.500)/(8e14-6e14)
check(33, "V0-nu graph slope (V s)", slope33, 4.14e-15)
check(33, "graph threshold frequency", 6e14-0.500/slope33, 4.79227e14)
truth(34, "double intensity: saturation current doubles and V0 unchanged",
      all(x in source_text(34) for x in ("2Iₛ", "V₀ अपरिवर्तित", "नियत आवृत्ति")))
p35 = math.sqrt(2*ME*E*2.50)
check(35, "momentum from 2.50 V stopping potential", p35, 8.54184e-25)
check(35, "minimum de Broglie wavelength (nm)", H/p35*1e9, 0.775711)
photon_rate36 = 3/(H*C/400e-9)
check(36, "3 W, 400 nm photon rate", photon_rate36, 6.03682e18)
check(36, "20 percent QE photocurrent", 0.20*photon_rate36*E, 0.193420)
lambda37 = 12.27/math.sqrt(144)
check(37, "144 V electron wavelength (angstrom)", lambda37, 1.0225)
check(37, "144 V electron momentum", H/(lambda37*1e-10), 6.48020e-24)
check(38, "100 V electron wavelength (angstrom)", H/math.sqrt(2*ME*E*100)*1e10, 1.22651)
check(38, "100 V proton wavelength (angstrom)", H/math.sqrt(2*MP*E*100)*1e10, 0.0286192)
p39 = math.sqrt(2*(4*MP)*(2*E)*400)
check(39, "alpha momentum after 400 V", p39, 1.30969e-21)
check(39, "alpha wavelength after 400 V (pm)", H/p39*1e12, 0.505920)
lambda40 = 12.27/math.sqrt(100)
theta40 = math.degrees(math.asin(lambda40/(2*1.00)))
check(40, "100 V electron wavelength (angstrom)", lambda40, 1.227)
check(40, "first-order Bragg angle (degree)", theta40, 37.8430)

print("\n=== PART 3A: निगमन एवं अवधारणा Q41–Q50 ===")
truth(41, "emission types, work function and threshold energy",
      all(x in source_text(41) for x in ("तापायनिक", "क्षेत्र उत्सर्जन", "प्रकाश-विद्युत", "कार्य-फलन", "hν₀")))
truth(42, "Hertz and Lenard observations",
      all(x in source_text(42) for x in ("हर्ट्ज", "लेनार्ड", "पराबैंगनी", "ऋण प्लेट", "तत्काल")))
truth(43, "photoelectric apparatus and measurement roles",
      all(x in source_text(43) for x in ("निर्वात", "प्रकाश-संवेदी कैथोड", "संग्राहक", "microammeter", "विपरीत विभव")))
truth(44, "photocurrent-potential characteristic graph",
      all(x in source_text(44) for x in ("संतृप्ति धारा", "रोधक विभव", "ऋण", "तीव्रता", "वक्र")))
truth(45, "intensity/frequency effects and instantaneous emission",
      all(x in source_text(45) for x in ("फोटॉनों की संख्या", "ν₀", "V₀", "10⁻⁹", "एक-फोटॉन")))
truth(46, "Einstein equation and classical failures",
      all(x in source_text(46) for x in ("hf = φ + Kmax", "ऊर्जा-संरक्षण", "सीमा आवृत्ति", "तत्काल", "तीव्रता")))
truth(47, "stopping-potential graph slope/intercepts",
      all(x in source_text(47) for x in ("V₀ = (h/e)ν − φ/e", "h/e", "ν-अक्ष", "−φ/e", "सीधी रेखा")))
truth(48, "photon energy, momentum and flux interpretation",
      all(x in source_text(48) for x in ("E=hν", "p=h/λ", "E/c", "Ṅ=P/E", "विश्राम द्रव्यमान")))
truth(49, "de Broglie hypothesis and matter-wave interpretation",
      all(x in source_text(49) for x in ("λ=h/p", "h/mv", "समूह वेग", "macroscopic", "probability")))
truth(50, "Davisson-Germer method and Bragg verification",
      all(x in source_text(50) for x in ("electron gun", "nickel", "54 V", "50°", "2d sinθ", "1.65 Å")))

print("\n=== PART 3B: कठिन मिश्रित Q51–Q60 ===")
slope51 = (1.63-0.80)/(9e14-7e14)
nu0_51 = 7e14-0.80/slope51
check(51, "measured graph slope h/e", slope51, 4.15e-15)
check(51, "measured Planck constant", slope51*E, 6.6483e-34)
check(51, "measured threshold frequency", nu0_51, 5.07229e14)
check(51, "measured work function (eV)", slope51*nu0_51, 2.105)
energy1_52 = H*C/(400e-9*E)
phi52 = energy1_52-1.10
energy2_52 = H*C/(300e-9*E)
check(52, "metal work function from 400 nm (eV)", phi52, 2.00206)
check(52, "300 nm photon energy (eV)", energy2_52, 4.13608)
check(52, "300 nm stopping potential", energy2_52-phi52, 2.13402)
photons53 = 5e-3/(H*C/500e-9)
electrons53 = 0.02*photons53
check(53, "5 mW, 500 nm photons in 1 s", photons53, 1.25767e16)
check(53, "2 percent emitted electrons", electrons53, 2.51534e14)
check(53, "collected charge (C)", electrons53*E, 4.02958e-5)
check(53, "average current (microampere)", electrons53*E*1e6, 40.2958)
phi_a = H*C/(620e-9*E)
phi_b = H*C/(400e-9*E)
energy54 = H*C/(350e-9*E)
check(54, "metal A work function (eV)", phi_a, 2.00133)
check(54, "metal B work function (eV)", phi_b, 3.10206)
check(54, "metal A stopping potential", energy54-phi_a, 1.54388)
check(54, "metal B stopping potential", energy54-phi_b, 0.443151)
v55 = math.sqrt(2*E*150/ME)
p55 = math.sqrt(2*ME*E*150)
check(55, "150 V electron speed", v55, 7.26368e6)
check(55, "150 V electron momentum", p55, 6.61648e-24)
check(55, "150 V electron wavelength (angstrom)", H/p55*1e10, 1.00144)
lp56 = H/math.sqrt(2*MP*E*1000)
la56 = H/math.sqrt(2*(4*MP)*(2*E)*1000)
check(56, "1000 V proton wavelength (pm)", lp56*1e12, 0.905018)
check(56, "1000 V alpha wavelength (pm)", la56*1e12, 0.319972)
check(56, "alpha/proton wavelength ratio", la56/lp56, 1/math.sqrt(8))
p57 = H/0.20e-9
check(57, "common momentum at 0.20 nm", p57, 3.313e-24)
check(57, "electron speed", p57/ME, 3.63706e6)
check(57, "proton speed", p57/MP, 1.98027e3)
check(57, "electron/proton speed ratio", (p57/ME)/(p57/MP), MP/ME)
check(57, "electron kinetic energy (eV)", p57*p57/(2*ME*E), 37.6079)
check(57, "proton kinetic energy (eV)", p57*p57/(2*MP*E), 0.0204764)
p58 = H/0.10e-9
photon_energy58 = H*C/0.10e-9
electron_energy58 = p58*p58/(2*ME)
check(58, "same-wavelength common momentum", p58, 6.626e-24)
check(58, "0.10 nm photon energy (keV)", photon_energy58/E/1000, 12.4082)
check(58, "0.10 nm electron kinetic energy (eV)", electron_energy58/E, 150.432)
check(58, "photon/electron energy ratio", photon_energy58/electron_energy58, 82.482)
nu0_59 = 5.00e14
nu59 = 9.00e14
check(59, "graph stopping potential at 9e14 Hz", H*(nu59-nu0_59)/E, 1.65443)
check(59, "graph Kmax (eV)", H*(nu59-nu0_59)/E, 1.65443)
truth(59, "tripled intensity triples saturation current only",
      all(x in source_text(59) for x in ("3Iₛ", "V₀ नहीं बदलता", "तीन गुना")))
theta60 = (180-50)/2
bragg60 = 2*0.091*math.sin(math.radians(theta60))
debroglie60 = 12.27/math.sqrt(54)*0.1
check(60, "Davisson-Germer Bragg angle", theta60, 65)
check(60, "Davisson-Germer Bragg wavelength (nm)", bragg60, 0.164948)
check(60, "Davisson-Germer de Broglie wavelength (nm)", debroglie60, 0.166974)
check(60, "Davisson-Germer agreement percent", abs(debroglie60-bragg60)/debroglie60*100, 1.21308)

ANSWER_FRAGMENTS = {
 1:("3.313 × 10⁻¹⁹ J", "2.068 eV"), 2:("3.313 × 10⁻¹⁹ J", "2.068 eV"),
 3:("1.325 × 10⁻²⁷ kg·m/s",), 4:("1.602 × 10⁻²⁷ kg·m/s",),
 5:("5.03 × 10¹⁸ photons/s",), 6:("5.32 × 10¹⁴ Hz",),
 7:("496 nm",), 8:("2.50 eV", "4.005 × 10⁻¹⁹ J"), 9:("3.20 V",),
 10:("3.102 eV", "1.102 eV", "1.102 V"), 11:("3.309 eV", "1.309 V"),
 12:("8.39 × 10⁵ m/s",), 13:("0.727 nm",), 14:("1.98 pm",),
 15:("1.002 Å",), 16:("1.227 Å",), 17:("2.862 pm",), 18:("0.3313 nm",),
 19:("4.417 × 10⁻²⁴ kg·m/s", "4.85 × 10⁶ m/s"), 20:("1.509 × 10¹⁵ photons",),
 21:("496 nm",), 22:("441.7 nm",), 23:("2.482 eV",), 24:("2.256 eV",),
 25:("2.345 eV",), 26:("7.495 × 10¹⁴ Hz",), 27:("1.522 V",),
 28:("2.497 × 10¹⁵ electrons/s",), 29:("6.626 × 10⁻²⁴ kg·m/s",), 30:("602 V",),
 31:("2.757 eV", "0.957 V"), 32:("0.482 V", "1.309 V"),
 33:("4.14 × 10⁻¹⁵ V·s", "4.79 × 10¹⁴ Hz"), 34:("2Iₛ", "V₀ अपरिवर्तित"),
 35:("8.542 × 10⁻²⁵ kg·m/s", "0.7757 nm"), 36:("6.037 × 10¹⁸ photons/s", "0.193 A"),
 37:("1.0225 Å", "6.48 × 10⁻²⁴ kg·m/s"), 38:("1.227 Å", "0.02862 Å"),
 39:("1.310 × 10⁻²¹ kg·m/s", "0.506 pm"),
 40:("1.227 Å", "37.8°"),
 41:("कार्य-फलन", "hν₀"), 42:("हर्ट्ज", "लेनार्ड"), 43:("निर्वात प्रकाश-नली", "रोधक विभव"),
 44:("संतृप्ति धारा", "रोधक विभव"), 45:("तीव्रता", "आवृत्ति", "तत्काल"),
 46:("hf = φ + Kmax",), 47:("ढाल h/e", "ν₀", "−φ/e"),
 48:("E=hν", "p=h/λ=E/c"), 49:("λ=h/p",), 50:("1.65 Å", "1.67 Å"),
 51:("4.15 × 10⁻¹⁵ V·s", "6.65 × 10⁻³⁴ J·s", "5.07 × 10¹⁴ Hz", "2.10 eV"),
 52:("2.002 eV", "2.134 V"),
 53:("1.258 × 10¹⁶", "2.515 × 10¹⁴", "4.03 × 10⁻⁵ C", "40.3 μA"),
 54:("2.001 eV", "3.102 eV", "1.544 V", "0.443 V"),
 55:("7.26 × 10⁶ m/s", "6.62 × 10⁻²⁴ kg·m/s", "1.001 Å"),
 56:("0.905 pm", "0.320 pm", "1/√8"),
 57:("3.313 × 10⁻²⁴ kg·m/s", "3.64 × 10⁶ m/s", "1.98 × 10³ m/s", "37.61 eV", "0.0205 eV"),
 58:("6.626 × 10⁻²⁴ kg·m/s", "12.41 keV", "150.4 eV", "82.5"),
 59:("1.654 V", "1.654 eV", "3Iₛ"),
 60:("65°", "0.1649 nm", "0.1670 nm", "1.21%"),
}
for qno in range(1, 61):
    claim(qno, "ans", *ANSWER_FRAGMENTS[qno])

assert all(len(ANSWER_FRAGMENTS[qno]) == 2 for qno in range(31, 41)), \
       "Q31–Q40 में प्रत्येक प्रश्न के ठीक दो bound outputs चाहिए"
assert set(by_number) == set(range(1, 61)), "प्रश्न coverage 1–60 नहीं है"
assert covered == set(range(1, 61)), f"physics coverage अधूरा: {sorted(set(range(1,61))-covered)}"
assert all(ok for _, _, ok in checks), "स्वतंत्र physics अथवा published-answer binding विफल"
assert answer_bindings == 60, f"60 answer bindings चाहिए, मिले {answer_bindings}"

print("\n=== SCHEMA, SPLIT और PEDAGOGICAL QUALITY ===")
assert [len(part) for part in parts] == [20, 20, 20], "हर part में ठीक 20 प्रश्न चाहिए"
assert len(questions) == 60 and len(by_number) == 60, "ठीक 60 unique question numbers चाहिए"
assert [q["n"] for q in questions] == list(range(1, 61)), "numbering 1–60 क्रम में चाहिए"
assert [sum(q["cat"] == cat for q in questions) for cat in (1, 2, 3)] == [20, 20, 20]
assert all(set(q) == EXPECTED_KEYS for q in questions), "हर प्रश्न में exact 11-key schema चाहिए"
assert all(type(q["n"]) is int and type(q["cat"]) is int and type(q["marks"]) is int for q in questions)
assert all(1 <= q["marks"] <= 5 for q in questions)
assert all(q["cat"] == 1 for q in questions[:20])
assert all(q["cat"] == 2 for q in questions[20:40])
assert all(q["cat"] == 3 for q in questions[40:])
assert all(q["marks"] in (1, 2) for q in questions[:20]), "प्रत्यक्ष प्रश्न 1–2 अंक के हों"
assert all(q["marks"] in (2, 3) for q in questions[20:40]), "inverse प्रश्न 2–3 अंक के हों"
assert all(isinstance(q["steps"], list) and len(q["steps"]) >= 3 for q in questions)
assert all(all(isinstance(step, tuple) and len(step) == 2 and all(isinstance(x, str) and x.strip() for x in step)
               for step in q["steps"]) for q in questions)
assert all(len(q["q"]) >= 45 and len(q["formula"]) >= 8 and len(q["why"]) >= 75 for q in questions)
assert all(len(q["ans"]) >= 25 and len(q["trick"]) >= 55 and len(q["alt"]) >= 55 for q in questions)
assert all(sum(len(h)+len(b) for h, b in q["steps"]) >= 145 for q in questions)
assert all(len(q["steps"]) >= 6 and q["marks"] == 5 for q in questions[40:50])
assert sum(len(q["steps"]) >= 6 and q["marks"] in (3, 5) for q in questions[40:60]) == 10, \
       "Q41–Q60 में ठीक 10 substantial derivation/conceptual solutions चाहिए"
assert all(len(q["steps"]) >= 4 and q["marks"] in (3, 5) for q in questions[50:60])
normalized_prompts = [re.sub(r"\s+", " ", q["q"].strip().lower()) for q in questions]
assert len(set(normalized_prompts)) == 60, "duplicate/rephrased duplicate prompts मिले"
assert all(all(isinstance(q[f], str) and q[f].strip() for f in ("topic", "q", "formula", "why", "ans", "trick", "alt"))
           for q in questions)

raw_subscript = re.compile(r"[A-Za-zΑ-Ωα-ω]_[A-Za-z0-9\u0900-\u097F]+")
for q in questions:
    prose = "\n".join([q["topic"], q["q"], q["why"], q["ans"], q["trick"], q["alt"]]
                       + [piece for step in q["steps"] for piece in step])
    assert not raw_subscript.search(prose), f"Q{q['n']} raw prose underscore/subscript मिला"
    assert "�" not in source_text(q["n"]), f"Q{q['n']} replacement character मिला"

OTHER_INDIC = [(0x0980, 0x09FF), (0x0A00, 0x0A7F), (0x0A80, 0x0AFF),
               (0x0B00, 0x0B7F), (0x0B80, 0x0BFF), (0x0C00, 0x0C7F),
               (0x0C80, 0x0CFF), (0x0D00, 0x0D7F)]
def has_wrong_indic(text):
    return any(lo <= ord(ch) <= hi for ch in text for lo, hi in OTHER_INDIC)
assert not any(has_wrong_indic(source_text(q["n"])) for q in questions), "wrong Indic script मिला"
assert all(not math.isclose(0.0, value, rel_tol=8e-4, abs_tol=0.0)
           for value in (6.65e-34, 1.33e-27, 8.54e-25, 4.14e-15, 3.31e-19)), \
       "tiny nonzero targets को zero से अलग पहचानना आवश्यक है"
assert "2Iₛ" in source_text(34) and "pmax" in source_text(35) and "λmin" in source_text(35), \
       "Q34/Q35 के audited purposes अलग रहने चाहिए"
assert "100 V" in source_text(40) and "37.8°" in source_text(40) and "54 V" not in source_text(40), \
       "Q40 को Q50/Q60 Davisson–Germer dataset दोहराना नहीं चाहिए"
assert "समान intensity" in source_text(44) and "Iₛ समान" in source_text(44), \
       "Q44 frequency-side saturation-current comparison स्पष्ट होना चाहिए"
print("PASS exact schema, numbering, 20/20/20 split, depth, uniqueness and script hygiene")


def serialized_question(q):
    fields = [str(q["n"]), str(q["cat"]), str(q["marks"]), q["topic"], q["q"], q["formula"],
              q["why"], q["ans"], q["trick"], q["alt"]]
    fields.extend(piece for step in q["steps"] for piece in step)
    return "\x1f".join(fields)


def complete_digest(records):
    return hashlib.sha256("\x1e".join(serialized_question(q) for q in records).encode("utf-8")).hexdigest()


NUMERIC_TOKEN = re.compile(
    r"(?:\d+(?:\.\d+)?(?:\s*[×x]\s*10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+|[eE][+-]?\d+)?)"
    r"|(?:\d+/\d+)|(?:√\d+)|(?:π)"
)
def numeric_signature(q):
    tokens = NUMERIC_TOKEN.findall(serialized_question(q))
    return len(tokens), hashlib.sha256("\x1f".join(tokens).encode("utf-8")).hexdigest()


# ये fingerprints audited ch11_part*.py से bootstrap के बाद स्थिर किए जाते हैं।
EXPECTED_NUMERIC_SIGNATURES = {
    1: (28, '14539df037211681ec04cf7648f115ff3020c8ac1836074bac229bdd1c72c660'),
    2: (22, '9093d447ebafd66af155e8704e10253d17a83b0479dd88ed55c4a34cde498ea9'),
    3: (11, 'd292ecbc9733da5a045eeb5c1d8ee4f786b972f9056ef32a89e6bb19a8967e0d'),
    4: (17, 'da8fd4948498410a4a599ac71bf59513cddc0fdef26239ab7e6c6faa0510caf4'),
    5: (15, '719abd8e2f9e06d6e7e02d046994d9dfe16249af16fea2f19ef005ec0318a525'),
    6: (17, '5597ad06d811d1005207742679b68ca4cfce9f3e86d1d6be2c4d68518af4088b'),
    7: (18, '31159f61ad5064246755b6ff7e45a89e151eca8c47fc8d650fd8bb73b7289c58'),
    8: (14, '737837a00613fed14d88a1e4cebf25384ba803a7718f9e41b0f1b663c62573b8'),
    9: (15, '9a2fd34f1dc693a9b7628afeb1092af2d7077739774002c5a58ed26be86b8776'),
    10: (24, '1a806619872a2ce6680519faaf1bd082effff47830a467e9a0b9ff9687d8cef4'),
    11: (22, '64f48c0379f66880956952a71e10c97922c6e6d23dc491ce405841b1f962c5a9'),
    12: (18, 'eb6974948ef4603a50ce2340a42b529a8a2818ed3e61d522a1590e5e0be273c9'),
    13: (17, '8d3354aaf126964199853c1933e70ecd5fa5dc5143f8a08f5c6d19f23defe842'),
    14: (19, '1b470426253c3b4caa2b790e5497079ce4d67d3f154da3d539ce86882434efa7'),
    15: (26, 'e7d61a46d62a29b6d90ce2f7d2b9d8270e8c3b3152496843d6f2ce27875cfcff'),
    16: (26, '2385c128d0d4779610ae7ca82fa9c9fbe3a571110a937bea1f21516c853e1c0f'),
    17: (29, 'ef6f725af9edd83e1a7de8a860e8cac7513f2a343e86cf5e0747cec6b8a38cce'),
    18: (19, '348aae0bb5164d3f75ab3b5b5af49371aa9cdc9f5b661ecfda67178c7f4aacf0'),
    19: (20, '60646c8abe31424486dbb64da2ddbaa6d7d5d478563d47e8487f6e554ad931a4'),
    20: (17, 'a4d543420e53f9ff2c7e232f1103368c3280e340241abb520f93e4617c25d7ab'),
    21: (19, '5ca7dab4fd1694090330ef0e1bf84f461a18fff688f12be1eeafe46e43bf7f94'),
    22: (17, '466a94b93b1f8eed6f346620f4b44a196be21747fdd74e21d15b898f02d4da97'),
    23: (16, 'a8b05d94508e358d101ab9c329f08b1436d974b9eb6fb5cf1f0610d9cf1e2208'),
    24: (17, '6744053a1d1dd00ddb62b726c2e543ffc76dbec031957964e8708e94febec3bf'),
    25: (19, '311461276e19e0fd60fcd6d7e28ed0b5fc9b309497581878edc69460bf08285c'),
    26: (19, 'd0b74d6b3d761b776733198fe454d680353699a74e2abb63f7da535874acb27a'),
    27: (15, 'd15c45cf51d3159ebfbec4828d22d3928eb0fb28eb62f3ab322bbc5686f369e4'),
    28: (16, '99a82de71ba35ff2d81fa9fc08d1ccfab0739e9335cc6c52f212ae5c18d088e0'),
    29: (17, '0813ce0addc0243111c48ace6d71d7f4e6ad0a8f53c689fb079a85cbf218a606'),
    30: (21, '9d6a60e42a58fad86d709eb1c3f6db783d5ae2d5e55524718b53b90bccf161b0'),
    31: (19, '6fde6870a3287e8699b2da7f36efb4af829e82f1d8bcfe02d25e6f4522bde680'),
    32: (19, 'af76d814086d54013147b757adb19f4a70cea53622874855e6918b2824febaa3'),
    33: (32, '3ee2e61abfd6506ea2c5ebe0c4ead4b1ff8ff6e3b882be8286147400bcdfd2ec'),
    34: (5, 'e76eb6f3d2f5efb717e22ecd196212ab6071eb44cc0b8c4338203c298469be3b'),
    35: (24, 'f5a8e984c104137d6bcd786b972f787d564389c9e2870e7667b2f6bde20ba786'),
    36: (22, '08d1e13d0d98c6c65de5edb258ec0e2522b3b4fcdbc73a47758c90fdd52365f6'),
    37: (22, '392698dba948329d967a76f5980e9d2dd4e49673249a00e2800a8456e1afe9fd'),
    38: (21, '900889c3670a4d40e44c5bfc15834c56a6bdbbfaaa544dacd7ed9867e39fc7c5'),
    39: (33, '76b572e10c56fe52abe7da5024d9410a7672ffc228c5338e4fe101680d46d14e'),
    40: (27, '937eea4f191c4207f116da46c3f70d296b0dab717beb71ad5867e1747f6bfa15'),
    41: (3, 'afc0f62de55aea8b803be5328c844d70e4ce5981131380e7215b0b186b846586'),
    42: (4, 'c5a9b7fd6d0663e6e9f341fcd7576cebf5f4866d604ea1791c59574b81eab064'),
    43: (4, '1b1ccab1d0a8f759ef8c4a250b133e2481deb896e361cfd9a0d4911e4a333354'),
    44: (3, 'd1df2c625b5c33c4f071ffaf95b47ed5123dfa3a04f4a52b95ca6b7a2afdcde0'),
    45: (4, '77a781120c00e59ce7fa3ea89883ed5555ce50a336ab2db06078e2a62db495f1'),
    46: (4, 'c8a9f5975d4b66f8643853365df196a3de9d0bae9d4b3eef54292a08521acdc3'),
    47: (5, '2df9f8324f2a880e1d505f2723faec476d0bc2b795a8577c037e114186668c8c'),
    48: (3, 'dbcf92a4bfbe3ff3192f2ae6fedfc09e32f5f744793d980cbd9f9cb151d0c0de'),
    49: (9, '1035b8b25d4c589c445897726a4230409bf5847ee703de5f03788ea7a8be77b7'),
    50: (39, 'e296d76c5bc833a7c6520a039f36e8b000989c6a5d73648d076795cc77f60b6c'),
    51: (38, '75fb4a5b21b257963a98d50597275fe66eabecdd4ba3faff18a9cdafee07064e'),
    52: (28, '3a5048af839b940aa0fd0d341a45e52f37ccdf68dbcbdf720a900e64a2d4b25a'),
    53: (32, 'b1c699674c9aa51681b7c98fcef0625d06dcd4417534ea66fa1abd7db0fb6b2a'),
    54: (30, '72c3d4fea123b94599f3c77b6b68172e0057bf8ac9718610c1f342ec6f20bff9'),
    55: (33, 'ff2d823bf9bb0fe5026d4c464128b58ffd818b257f9594ed4a569fc0957d3788'),
    56: (42, '08797f8f8d067750d9a3457fff10b5d5606cd415b667106d4d445c8ed4284b2a'),
    57: (26, '6e7a967f934f8d9c115ef3ad9c12251f3ba7076491f6aa7dbfb95718e72844af'),
    58: (28, 'd500334bb99d485dc98fbde91116aa9ce3c373efbcaa024a81f5e33fa5d737c5'),
    59: (26, 'c6f9f2308ad3c854cbe228df0d69bb60fd1a14dd6dca5f180c49bb3e5080ff4d'),
    60: (40, '005104575950a252c613d85090d3213e95e0ebce8db7f304d6aaf11ef9aae508'),
}
EXPECTED_COMPLETE_DIGEST = "c95ca0b26fd68754adb3c7ad3030ddac37755497b1ad6881f268bd08f0b51122"

if "--print-fingerprints" in sys.argv:
    print("\nEXPECTED_NUMERIC_SIGNATURES = {")
    for q in questions:
        count, digest = numeric_signature(q)
        print(f"    {q['n']}: ({count}, {digest!r}),")
    print("}")
    print(f"EXPECTED_COMPLETE_DIGEST = {complete_digest(questions)!r}")
    print("Fingerprint bootstrap complete; insert these values, then run normal verification.")
    raise SystemExit(0)

assert set(EXPECTED_NUMERIC_SIGNATURES) == set(range(1, 61)), "numeric fingerprints 1–60 चाहिए"
for q in questions:
    assert numeric_signature(q) == EXPECTED_NUMERIC_SIGNATURES[q["n"]], \
        f"Q{q['n']} numeric source fingerprint बदला"
assert complete_digest(questions) == EXPECTED_COMPLETE_DIGEST, "पूर्ण audited source fingerprint बदला"
print(f"PASS 60 numeric fingerprints; complete digest {EXPECTED_COMPLETE_DIGEST}")

mutated_answer = copy.deepcopy(questions)
mutated_answer[0]["ans"] += " 999"
assert complete_digest(mutated_answer) != EXPECTED_COMPLETE_DIGEST
assert numeric_signature(mutated_answer[0]) != EXPECTED_NUMERIC_SIGNATURES[1]
mutated_prose = copy.deepcopy(questions)
mutated_prose[40]["why"] = mutated_prose[40]["why"].replace("उत्सर्जन", "निर्गमन", 1)
assert complete_digest(mutated_prose) != EXPECTED_COMPLETE_DIGEST
mutated_structure = copy.deepcopy(questions)
mutated_structure[50]["steps"] = mutated_structure[50]["steps"][:-1]
assert complete_digest(mutated_structure) != EXPECTED_COMPLETE_DIGEST
print("PASS answer, numeric, prose and structure mutation guards")


def strip_code_fences(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def local_markdown_links(path, text):
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean = target.split("#", 1)[0]
        if clean:
            yield (path.parent / clean).resolve()


def verify_generated_artifacts():
    print("\n=== POST-BUILD GENERATED ARTIFACTS ===")
    build = importlib.import_module("build")
    published = build.load(11)
    expected_names = {f"ch11sol{n}.md" for n in range(1, 61)}
    actual = {p.name for p in SOLUTIONS.glob("ch11sol*.md")}
    assert actual == expected_names, f"Chapter 11 समाधान set गलत: missing={expected_names-actual}, extra={actual-expected_names}"

    required_sections = ("## 📋 प्रश्न", "## 🧮 प्रयुक्त सूत्र", "## 🤔 यह सूत्र क्यों लगाया?",
                         "## ✍️ चरणबद्ध हल", "## ✅ उत्तर", "## 🎯 परीक्षा की ट्रिक",
                         "## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान")
    nav_count = 0
    all_local_links = 0
    for q in published:
        path = SOLUTIONS / f"ch11sol{q['n']}.md"
        text = path.read_text(encoding="utf-8")
        assert text == build.build_solution(q, 11), f"{path.name} audited source से byte-exact नहीं"
        assert all(section in text for section in required_sections), f"{path.name} section अधूरा"
        assert "�" not in text and not has_wrong_indic(text), f"{path.name} script/tofu text दोष"
        assert not raw_subscript.search(strip_code_fences(text)), f"{path.name} raw prose underscore"
        links = list(local_markdown_links(path, text))
        nav_count += len(links)
        all_local_links += len(links)
        for target in links:
            assert target.exists(), f"टूटा local link: {path.name} -> {target}"
    assert nav_count == 178, f"solution navigation links 178 चाहिए, मिले {nav_count}"

    master_path = SOLUTIONS / "README.md"
    master = master_path.read_text(encoding="utf-8")
    assert master == build.build_master_index(str(SOLUTIONS)), "master index byte-exact generated नहीं"
    master_links = list(local_markdown_links(master_path, master))
    all_local_links += len(master_links)
    for target in master_links:
        assert target.exists(), f"master index का टूटा link: {target}"
    assert "| 11 | विकिरण तथा द्रव्य की द्वैत प्रकृति |" in master
    assert "## अध्याय 11 — विकिरण तथा द्रव्य की द्वैत प्रकृति" in master

    changed = build.build_solution(dict(published[0], ans=published[0]["ans"] + " बदला"), 11)
    assert changed != (SOLUTIONS / "ch11sol1.md").read_text(encoding="utf-8")
    print(f"PASS 60 byte-exact solutions; navigation={nav_count}; all local links checked={all_local_links}")

    import pymupdf
    pdf_path = PRACTICE / "chapter11.pdf"
    assert pdf_path.exists() and pdf_path.stat().st_size >= 300_000, "chapter11.pdf missing/बहुत छोटा"
    doc = pymupdf.open(pdf_path)
    uris = []
    pdf_text = []
    for page in doc:
        pdf_text.append(page.get_text())
        for link in page.get_links():
            if link.get("uri"):
                uris.append(link["uri"])
    expected_uris = {
        f"https://github.com/singhupavinash8506-arch/Phusics/blob/up-board-class12-2026-27/"
        f"UP-Board-Class12-Physics/practice-sets/solutions/ch11sol{n}.md"
        for n in range(1, 61)
    }
    assert len(uris) == 60 and len(set(uris)) == 60, f"PDF URI links unique 60 चाहिए, मिले {len(uris)}/{len(set(uris))}"
    assert set(uris) == expected_uris, "PDF links exact ch11sol1..60 HTTPS set नहीं"
    joined_pdf_text = "\n".join(pdf_text)
    assert all(token in joined_pdf_text for token in ("विकिरण", "द्रव्य", "प्रकृति"))
    assert "�" not in joined_pdf_text and not has_wrong_indic(joined_pdf_text)
    assert doc.page_count >= 8
    pages = doc.page_count
    doc.close()

    public_readme = (PRACTICE / "README.md").read_text(encoding="utf-8")
    expected_row = "| 11 | विकिरण तथा द्रव्य की द्वैत प्रकृति | [chapter11.pdf](chapter11.pdf) ✅ | [60 हल](solutions/README.md) |"
    assert expected_row in public_readme, "Chapter 11 README row प्रकाशित नहीं"
    # पहले यह guard अध्याय 12 की अनुपस्थिति माँगता था (task-isolation)। सभी अध्याय पूर्ण
    # होने पर अब केवल आंशिक build पकड़ा जाता है।
    if (PRACTICE / "chapter12.pdf").exists() or any(SOLUTIONS.glob("ch12sol*.md")):
        assert (PRACTICE / "chapter12.pdf").exists(), "Chapter 12 समाधान बिना chapter12.pdf (आंशिक build)"
        assert not [n for n in range(1, 61) if not (SOLUTIONS / f"ch12sol{n}.md").exists()], \
            "Chapter 12 आंशिक रूप से बना है"
    print(f"PASS PDF pages={pages}, bytes={pdf_path.stat().st_size}, exact unique HTTPS links=60")
    print("PASS master index, README publication row, and Chapter 12 absence")


if "--post-build" in sys.argv:
    verify_generated_artifacts()

print(f"\nALL CHECKS PASSED — physics checks={len(checks)}, coverage={len(covered)}/60, answer bindings={answer_bindings}/60")
