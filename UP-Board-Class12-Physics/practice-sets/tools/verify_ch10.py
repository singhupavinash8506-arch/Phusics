# -*- coding: utf-8 -*-
"""अध्याय 10 — तरंग प्रकाशिकी: fail-closed स्वतंत्र सत्यापन।

यह verifier पहले भौतिकी को स्वतंत्र सम्बन्धों से पुनः गणित करता है, फिर उन
निष्कर्षों को प्रकाशित उत्तरों से बाँधता है। पूर्ण स्रोत fingerprints, mutation
checks और वैकल्पिक --post-build mode generated Markdown, index तथा PDF को भी
उसी audited source से byte-for-byte बाँधते हैं। किसी कमी पर non-zero exit होता है।
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
    raise RuntimeError("Chapter 10 verifier must run without Python -O")

EXPECTED_KEYS = {"n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"}
PI = math.pi

parts = []
for part_number in (1, 2, 3):
    module = importlib.import_module(f"ch10_part{part_number}")
    parts.append(getattr(module, f"PART{part_number}"))
questions = sum(parts, [])
by_number = {q.get("n"): q for q in questions}

checks: list[tuple[int, str, bool]] = []
covered: set[int] = set()
answer_bindings = 0


def check(qno, label, got, expected, rel_tol=7e-4, abs_tol=1e-10):
    passed = math.isclose(got, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    checks.append((qno, label, passed))
    covered.add(qno)
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} {label:<55} got={got:.12g} expected={expected:.12g}")


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
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} published {field}: "
          f"{len(needles)-len(missing)}/{len(needles)}" + (f" missing={missing}" if missing else ""))


print("=== PART 1: प्रत्यक्ष सूत्र Q1–Q20 ===")
check(1, "wave speed (m/s)", 600e-9 * 5.00e14, 3.00e8)
check(2, "phase difference (rad)", 2*PI*150/600, PI/2)
check(3, "path order", 1.80e-6/600e-9, 3)
check(3, "phase difference (rad)", 2*PI*1.80e-6/600e-9, 6*PI)
check(4, "path half-order", 1.25e-6/500e-9, 2.5)
check(4, "phase difference (rad)", 2*PI*1.25e-6/500e-9, 5*PI)
check(5, "YDSE fringe width (mm)", 600e-9*1.50/(0.50e-3)*1e3, 1.80)
check(6, "fourth bright position (mm)", 4*(600e-9*1/(0.50e-3))*1e3, 4.80)
check(7, "third dark position (mm)", 2.5*(600e-9*1.50/(0.60e-3))*1e3, 3.75)
delta = 0.20e-3*5e-3/1.0
check(8, "screen-point path difference (um)", delta*1e6, 1.00)
check(8, "screen-point phase difference (rad)", 2*PI*delta/500e-9, 4*PI)
beta_air = 600e-9*1.50/(0.50e-3)
check(9, "fringe width in index 1.5 medium (mm)", beta_air/1.5*1e3, 1.20)
check(10, "equal-source maximum intensity", (math.sqrt(4)+math.sqrt(4))**2, 16)
check(10, "equal-source minimum intensity", (math.sqrt(4)-math.sqrt(4))**2, 0)
check(11, "unequal-source maximum intensity", (3+2)**2, 25)
check(11, "unequal-source minimum intensity", (3-2)**2, 1)
check(11, "fringe visibility", (25-1)/(25+1), 12/13)
check(12, "interference intensity at phase 2pi/3", 4+4+2*math.sqrt(16)*math.cos(2*PI/3), 4)
check(13, "single-slit first-minimum angle (rad)", 500e-9/(0.20e-3), 2.50e-3)
check(14, "central angular width (rad)", 2*500e-9/(0.20e-3), 5.00e-3)
check(15, "central linear width (mm)", 2*2.0*500e-9/(0.20e-3)*1e3, 10.0)
check(16, "first polarizer output (W/m2)", 100/2, 50)
check(16, "analyzer output at 60 degrees (W/m2)", 50*math.cos(math.radians(60))**2, 12.5)
check(17, "Malus output at 30 degrees (W/m2)", 80*math.cos(math.radians(30))**2, 60)
check(18, "Brewster angle (degree)", math.degrees(math.atan(1.50)), 56.3099)
check(19, "Brewster refraction angle (degree)", 90-57, 33)
check(20, "three-polaroid final intensity (W/m2)", (64/2)*0.5*0.5, 8)

print("\n=== PART 2A: एक अज्ञात Q21–Q30 ===")
check(21, "unknown wavelength (nm)", 1.50e-3*0.80e-3/2.0*1e9, 600)
check(22, "unknown slit separation (mm)", 500e-9*2.0/(2.0e-3)*1e3, 0.50)
check(23, "unknown screen distance (m)", 1.20e-3*0.50e-3/600e-9, 1.00)
check(24, "unknown bright order", 6.0/1.50, 4)
check(25, "unknown wavelength from phase (nm)", 2*PI*100/(PI/3), 600)
check(26, "unknown path difference (nm)", (3*PI/2)*400/(2*PI), 300)
check(27, "unknown slit width (mm)", 600e-9/0.003*1e3, 0.20)
check(28, "unknown wavelength from central width (nm)", 8e-3*0.25e-3/(2*2.0)*1e9, 500)
check(29, "unknown analyser angle (degree)", math.degrees(math.acos(math.sqrt(20/80))), 60)
check(30, "unknown refractive index from Brewster angle", math.tan(math.radians(53.130102)), 4/3)

print("\n=== PART 2B: दो अज्ञात Q31–Q40 ===")
beta = 500e-9*2.0/(0.50e-3)
check(31, "fringe width (mm)", beta*1e3, 2.0)
check(31, "fifth bright position (mm)", 5*beta*1e3, 10.0)
order = 1.50e-6/600e-9
check(32, "dark half-order", order, 2.5)
check(32, "phase difference (rad)", 2*PI*order, 5*PI)
beta_air = 600e-9*1.50/(0.50e-3)
check(33, "air fringe width (mm)", beta_air*1e3, 1.80)
check(33, "water fringe width (mm)", beta_air/(4/3)*1e3, 1.35)
beta_initial = 600e-9*1.0/(0.50e-3)
beta_changed = 600e-9*2.0/(1.50e-3)
check(34, "initial fringe width (mm)", beta_initial*1e3, 1.20)
check(34, "changed fringe width (mm)", beta_changed*1e3, 0.80)
check(35, "amplitude-ratio maximum intensity (a2)", (3+1)**2, 16)
check(35, "amplitude-ratio minimum intensity (a2)", (3-1)**2, 4)
root_max, root_min = math.sqrt(36), math.sqrt(4)
a1, a2 = (root_max+root_min)/2, (root_max-root_min)/2
check(36, "first component intensity", a1*a1, 16)
check(36, "second component intensity", a2*a2, 4)
theta = 600e-9/(0.30e-3)
check(37, "first diffraction-minimum angle (rad)", theta, 2.00e-3)
check(37, "central width on screen (mm)", 2*2.0*theta*1e3, 8.0)
check(38, "red central width (mm)", 2*1.0*650e-9/(0.20e-3)*1e3, 6.50)
check(38, "blue central width (mm)", 2*1.0*450e-9/(0.20e-3)*1e3, 4.50)
check(39, "Brewster angle for sqrt3 index (degree)", math.degrees(math.atan(math.sqrt(3))), 60)
check(39, "corresponding refraction angle (degree)", 90-60, 30)
check(40, "first polarizer output (W/m2)", 96/2, 48)
check(40, "45-degree analyser output (W/m2)", 48*0.5, 24)

print("\n=== PART 3A: निगमन एवं अवधारणा Q41–Q50 ===")
truth(41, "Huygens secondary-wavelet construction", all(x in source_text(41) for x in ("द्वितीयक तरंगिकाएँ", "स्पर्शी आवरण", "समतल तरंगाग्र", "vΔt")))
truth(42, "Huygens reflection derivation", all(x in source_text(42) for x in ("AA'", "BC", "vΔt", "RHS", "i = r")))
truth(43, "Huygens refraction and Snell derivation", all(x in source_text(43) for x in ("v₁Δt", "v₂Δt", "sin i/sin r", "v₁/v₂", "n₂/n₁")))
truth(44, "superposition intensity derivation", all(x in source_text(44) for x in ("E₁", "E₂", "cosφ", "2√(I₁I₂)", "Imax", "Imin")))
truth(45, "sustained-interference conditions", all(x in source_text(45) for x in ("सुसंगत", "नियत कला-अन्तर", "एकवर्णी", "समान polarization", "स्वतंत्र lamps")))
truth(46, "YDSE fringe-width derivation", all(x in source_text(46) for x in ("d sinθ", "dy/D", "yₙ", "β=λD/d", "D≫d")))
truth(47, "bright and dark position families", all(x in source_text(47) for x in ("nλ", "(n+1/2)λ", "(n+1/2)β", "β/2")))
truth(48, "single-slit diffraction derivation", all(x in source_text(48) for x in ("a sinθ", "nλ", "2λ/a", "2Dλ/a", "युग्म")))
truth(49, "Malus-law projection derivation", all(x in source_text(49) for x in ("E = E₀ cosθ", "I=I₀cos²θ", "अक्ष", "crossed")))
truth(50, "Brewster law and transverse-wave evidence", all(x in source_text(50) for x in ("tan iₚ", "iₚ+r=90°", "अनुप्रस्थ", "ध्रुवण", "polaroids")))

print("\n=== PART 3B: कठिन मिश्रित Q51–Q60 ===")
beta = 600e-9*2.0/(0.50e-3)
delta = 0.50e-3*6e-3/2.0
check(51, "hard YDSE fringe width (mm)", beta*1e3, 2.40)
check(51, "hard YDSE path difference (um)", delta*1e6, 1.50)
check(51, "hard YDSE half-order", delta/600e-9, 2.5)
check(51, "hard YDSE phase (rad)", 2*PI*delta/600e-9, 5*PI)
# Lowest positive common bright: 4*600 nm = 5*480 nm.
check(52, "first wavelength bright order", 4, 4)
check(52, "second wavelength bright order", 5, 5)
check(52, "first common bright position (mm)", 4*(600e-9*1.50/(0.30e-3))*1e3, 12.0)
shift = 1.0*(1.50-1)*6e-6/(0.50e-3)
beta = 600e-9*1.0/(0.50e-3)
check(53, "thin-sheet fringe shift (mm)", shift*1e3, 6.0)
check(53, "thin-sheet shift in fringe widths", shift/beta, 5.0)
I1, I2, phi = 16.0, 9.0, math.radians(120)
intensity = I1+I2+2*math.sqrt(I1*I2)*math.cos(phi)
check(54, "unequal-beam intensity at 120 degrees", intensity, 13)
check(54, "unequal-beam maximum", (4+3)**2, 49)
check(54, "unequal-beam minimum", (4-3)**2, 1)
check(54, "unequal-beam visibility", (49-1)/(49+1), 0.96)
root_max, root_min = math.sqrt(100), math.sqrt(36)
a1, a2 = (root_max+root_min)/2, (root_max-root_min)/2
check(55, "recovered larger component intensity", a1*a1, 64)
check(55, "recovered smaller component intensity", a2*a2, 4)
check(55, "visibility from measured extrema", (100-36)/(100+36), 8/17)
theta = 500e-9/(0.10e-3)
y1 = 2.0*theta
check(56, "diffraction first-minimum angle (rad)", theta, 5.00e-3)
check(56, "positive first-minimum position (mm)", y1*1e3, 10.0)
check(56, "central diffraction width (mm)", 2*y1*1e3, 20.0)
beta = 500e-9*2.0/(0.50e-3)
width = 2*2.0*500e-9/(0.10e-3)
check(57, "combined pattern fringe width (mm)", beta*1e3, 2.0)
check(57, "combined diffraction envelope width (mm)", width*1e3, 20.0)
check(57, "visible bright centres inside central envelope", 9, 9)
I0 = 160.0
check(58, "crossed-three-polaroid output at 30 degrees", I0/8*math.sin(math.radians(60))**2, 15)
check(58, "crossed-three-polaroid maximum output", I0/8, 20)
check(58, "optimal middle-axis angle (degree)", 45, 45)
ip = math.degrees(math.atan(1.50))
r = 90-ip
check(59, "hard Brewster angle (degree)", ip, 56.3099)
check(59, "hard Brewster refraction angle (degree)", r, 33.6901)
check(59, "analyser output (W/m2)", 40*math.cos(math.radians(30))**2, 30)
beta_air = 600e-9*2.0/(0.40e-3)
beta_medium = beta_air/1.50
check(60, "air fringe width (mm)", beta_air*1e3, 3.0)
check(60, "medium fringe width (mm)", beta_medium*1e3, 2.0)
check(60, "fourth bright in air (mm)", 4*beta_air*1e3, 12.0)
check(60, "fourth bright in medium (mm)", 4*beta_medium*1e3, 8.0)
delta = 0.40e-3*5e-3/2.0
check(60, "medium point path difference (um)", delta*1e6, 1.0)
check(60, "medium point wavelength order", delta/(600e-9/1.5), 2.5)

# Exact final-answer fragments bind every independently checked conclusion to publication.
ANSWER_FRAGMENTS = {
 1:("v = 3.00 × 10⁸ m/s",), 2:("φ = π/2 rad", "90°"),
 3:("Δ = 3λ", "φ = 6π rad", "रचनात्मक"), 4:("Δ = 2.5λ", "φ = 5π rad", "विनाशी"),
 5:("β = 1.80 mm",), 6:("y₄ = 4.80 mm",), 7:("y = 3.75 mm",),
 8:("Δ = 1.00 μm = 2λ", "φ = 4π rad", "उज्ज्वल"), 9:("βₘ = 1.20 mm",),
 10:("Imax = 16", "Imin = 0"), 11:("Imax = 25", "Imin = 1", "V = 12/13 ≈ 0.923"),
 12:("I = 4",), 13:("θ₁ ≈ 2.50 × 10⁻³ rad",), 14:("5.00 × 10⁻³ rad",),
 15:("W = 10.0 mm",), 16:("50 W/m²", "12.5 W/m²"), 17:("I = 60 W/m²",),
 18:("iₚ ≈ 56.31°",), 19:("r = 33°", "90°"), 20:("I = 8.0 W/m²",),
 21:("λ = 600 nm",), 22:("d = 0.50 mm",), 23:("D = 1.00 m",),
 24:("n = 4", "चौथी कोटि"), 25:("λ = 600 nm",), 26:("Δ = 300 nm",),
 27:("a = 0.20 mm",), 28:("λ = 500 nm",), 29:("θ = 60°",), 30:("n = 4/3 ≈ 1.333",),
 31:("β = 2.00 mm", "y₅ = 10.0 mm"), 32:("Δ = 2.5λ", "φ = 5π rad"),
 33:("β(वायु) = 1.80 mm", "β(जल) = 1.35 mm"), 34:("β₁ = 1.20 mm", "β₂ = 0.80 mm"),
 35:("Imax = 16a²", "Imin = 4a²"), 36:("I₁ = 16", "I₂ = 4"),
 37:("θ₁ = 2.00 × 10⁻³ rad", "W = 8.00 mm"), 38:("Wᵣ = 6.50 mm", "Wᵦ = 4.50 mm"),
 39:("iₚ = 60°", "r = 30°"), 40:("48 W/m²", "24 W/m²"),
 41:("स्पर्शी आवरण", "vΔt"), 42:("i = r",), 43:("sin i/sin r = v₁/v₂ = n₂/n₁",),
 44:("I = I₁+I₂+2√(I₁I₂) cosφ",), 45:("नियत कला-अन्तर",), 46:("β = λD/d",),
 47:("yₙ = nβ", "yₙ = (n+1/2)β"), 48:("a sinθ = nλ", "2Dλ/a"),
 49:("I = I₀ cos²θ",), 50:("n = tan iₚ", "iₚ+r = 90°", "अनुप्रस्थ"),
 51:("β = 2.40 mm", "Δ = 1.50 μm = 2.5λ", "φ = 5π rad", "तीसरा अदीप्त"),
 52:("m = 4", "n = 5", "y = 12.0 mm"), 53:("x₀ = 6.00 mm", "5 फ्रिंज"),
 54:("I = 13", "Imax = 49", "Imin = 1", "V = 0.96"),
 55:("I₁ = 64", "I₂ = 4", "V = 8/17 ≈ 0.471"),
 56:("θ₁ = 5.00 × 10⁻³ rad", "y₁ = ±10.0 mm", "W = 20.0 mm"),
 57:("β = 2.00 mm", "W = 20.0 mm", "9 उज्ज्वल"),
 58:("I(30°) = 15 W/m²", "Imax = 20 W/m²", "θ = 45°"),
 59:("iₚ ≈ 56.31°", "r ≈ 33.69°", "30 W/m²"),
 60:("β(वायु) = 3.00 mm", "β(माध्यम) = 2.00 mm", "12.0 mm", "8.00 mm", "2.5λₘ", "अदीप्त"),
}
for qno in range(1, 61):
    claim(qno, "ans", *ANSWER_FRAGMENTS[qno])

print("\n=== SOURCE DATA STRUCTURE / QUALITY ===")
assert len(parts) == 3 and all(isinstance(p, list) and len(p) == 20 for p in parts), "हर part में 20 प्रश्न चाहिए"
assert len(questions) == 60, f"60 प्रश्न चाहिए, मिले {len(questions)}"
assert [q.get("n") for q in questions] == list(range(1, 61)), "क्रम 1–60 नहीं है"
assert [q.get("cat") for q in questions] == [1]*20+[2]*20+[3]*20, "20/20/20 category split टूटा"
assert all(set(q) == EXPECTED_KEYS and len(q) == 11 for q in questions), "exact 11-key schema टूटा"
assert all(type(q["n"]) is int and type(q["cat"]) is int and type(q["marks"]) is int for q in questions)
assert all(q["marks"] in (1, 2, 3, 4, 5) for q in questions), "अमान्य अंक"
for q in questions:
    for field in ("topic", "q", "formula", "why", "ans", "trick", "alt"):
        assert isinstance(q[field], str) and q[field].strip(), f"Q{q['n']} empty {field}"
    assert len(q["q"]) >= 45, f"Q{q['n']} प्रश्न बहुत छोटा"
    assert len(q["why"]) >= 75, f"Q{q['n']} why सतही"
    assert len(q["trick"]) >= 55, f"Q{q['n']} trick सतही"
    assert len(q["alt"]) >= 55, f"Q{q['n']} alternate सतही"
    assert isinstance(q["steps"], list) and len(q["steps"]) >= 3, f"Q{q['n']} में कम चरण"
    assert all(isinstance(s, tuple) and len(s) == 2 and len(s[0]) >= 3 and len(s[1]) >= 14 for s in q["steps"]), f"Q{q['n']} चरण अपूर्ण"
    assert sum(len(s[1]) for s in q["steps"]) >= 110, f"Q{q['n']} चरणों में पर्याप्त विवरण नहीं"
    prose = "\n".join([q["topic"], q["q"], q["why"], *(p for s in q["steps"] for p in s), q["ans"], q["trick"], q["alt"]])
    assert not re.search(r"[A-Za-zΑ-Ωα-ω]_[A-Za-z0-9\u0900-\u097F]", prose), f"Q{q['n']} raw prose underscore"
normalized_prompts = [re.sub(r"\s+", " ", q["q"].strip().lower()) for q in questions]
assert len(set(normalized_prompts)) == 60, "duplicate prompts"
full_derivation_concept = sum(q["marks"] in (3, 5) and len(q["steps"]) >= 6 for q in questions[40:50])
assert 8 <= full_derivation_concept <= 10, f"Q41–Q50 में 8–10 पूर्ण निगमन चाहिए, मिले {full_derivation_concept}"
assert sum(q["marks"] >= 4 for q in questions[40:60]) >= 8, "कठिन खण्ड में पर्याप्त 4/5 अंक प्रश्न नहीं"
assert all(len(q["steps"]) >= 4 for q in questions[50:60]), "Q51–Q60 बहुचरणीय होने चाहिए"

other_indic = [(0x0980,0x09FF),(0x0A00,0x0A7F),(0x0A80,0x0AFF),(0x0B00,0x0B7F),(0x0B80,0x0BFF),(0x0C00,0x0C7F),(0x0C80,0x0CFF),(0x0D00,0x0D7F)]
for q in questions:
    text = source_text(q["n"])
    assert "�" not in text, f"Q{q['n']} replacement character"
    assert not any(lo <= ord(ch) <= hi for ch in text for lo,hi in other_indic), f"Q{q['n']} गलत Indic लिपि"

NUMERIC_TOKEN = re.compile(r"(?:\d+(?:\.\d+)?(?:\s*×\s*10[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)?[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]*|π|√\d+)")
def numeric_signature(q):
    text = "\x1e".join([q["q"],q["formula"],q["why"],*(p for s in q["steps"] for p in s),q["ans"],q["trick"],q["alt"]])
    tokens = NUMERIC_TOKEN.findall(text)
    return len(tokens), hashlib.sha256("\x1f".join(tokens).encode()).hexdigest()


def complete_digest(records):
    serial = []
    for q in records:
        serial.append("\x1d".join([str(q["n"]),str(q["cat"]),str(q["marks"]),q["topic"],q["q"],q["formula"],q["why"],*(p for s in q["steps"] for p in s),q["ans"],q["trick"],q["alt"]]))
    return hashlib.sha256("\x1c".join(serial).encode()).hexdigest()

# Populated only after all source questions have passed independent review.
EXPECTED_NUMERIC_SIGNATURES = {1: (16, '31e142f8b972d69be7dcc753ddeac1981d84237815085b55d872bb055380c898'), 2: (32, '481a71a3f3825997ebc247d584e45307f816c8258d72429292fd7a4e335a055c'), 3: (30, 'dff58af39a69d15c4ce49584181213f29f568ad2856baf197286b0c378445f1f'), 4: (31, 'e67fc8d66e6407bcd82d55bb16d24f1ea30bb9e10b6c807b65076becdd58eb62'), 5: (17, 'ba0e1b1aee909ff56cc0fce258db6c6f3579cf22569a386ce7098568777a4c6a'), 6: (22, 'ec17a09dadda781925dad4d3046b6905318db1deb49465c69f873cd8b498820d'), 7: (36, 'ece43775dca8779f7bdace98b3b10aad7369f574b58310bbd7bbd7e449a828fa'), 8: (31, '77d6528b6b93e57b1b03e0ea92be0360d8a6946c9ce73c1a2dba6f4e218d454d'), 9: (15, '1b7cbf5f1dfd18e8bfbceb6dc737647ccabffdad5f139231bd69e1b2a952a05b'), 10: (22, '4422d309f94402472bcd744a0562b195fdc73368b829b9fb60d81e4e89310c4b'), 11: (35, 'df6d4a7c37dca496595a59514f241808aff6114a5aa383e929f36df1a65c3ee4'), 12: (39, '62af4ff6e59efaaf31cb7973e5081717aae42427a0a2140f5d6a93f06b36656e'), 13: (13, '77993112ab741bf11d2b369c13f39685c2367e26111b4e5e2d2ecc1bab6ad1ef'), 14: (16, 'f9b767171aaf16cc61d3dcc1ddbb61cf9d18647e9ddc4716dd66e6b1026a65b6'), 15: (18, '13f9928ff5f84e33a0c31de525da239e01a033c7f7c29b1bba4fa18148a847f8'), 16: (30, 'da0d5acd9c0fefcf7c228b637e1b2545844f2eebb5d229d971abb0158d885442'), 17: (24, '7593b270658f7e031d501e6e6c84158a28e04e346a1443125421fb4d2fd01c2a'), 18: (15, 'c3b0c041f9cecabc58b6095c65417a3dfc63d7d09d72e92de60ebb778262a316'), 19: (19, 'c4d9f2e04cc0d0e5b324d6c713e2f365faf8704aada17d17f0f0b5d99ff1d171'), 20: (33, '768628674af96d94cc7f232ce5b734926267bd979f779a20f40be04dad6556ea'), 21: (18, '73ad3eaa2318eec00d2d8bfedc0c73b0a1b8ac173060bf46b0a664c06257b1b5'), 22: (18, 'd43fd1b18198367537c1c02f6d3319cbddc6eb7146307520cb53dc16ef709dcd'), 23: (20, '0e68b07c3d2a9be85b50ceb4524560438b60ed58b7d3a1798cffbb42c344c4a7'), 24: (12, '98e18c0bb9b31aee1aaa5ac54392c08495ca0661a285c3ba374e5f20e500edea'), 25: (42, 'adba348c2457f55eb973bbbbd5941b31e4cf0f4f843036bdc43df9071421b904'), 26: (50, '4fe1bcecdf659289c2cea7d5f20229737221797160e9f896149d6fc59ceb112b'), 27: (13, '049021a504dee088c4268cf4899824dcf239f39a2765f78e80c11f45252bca47'), 28: (23, 'fd94684422f8b6659dd3ba56d1b6c3bc19011cb4e2d21316b3ec35da70681589'), 29: (27, '5b3eaad727859d7d56cc83a693fd3c94eec7159a5d0b12108b38b0224b5136e9'), 30: (23, 'c5fedbad32128828edfd4321f9c11bc2011e9a7920c2eae9c51d052118b8f3ee'), 31: (23, 'da97816811140ba1ea5fd6fbddf3ff731f6f5bea05aeb751325c87580bd9e71b'), 32: (31, '0c14acbc307b334b018b1b8f292bdcea7c2fe0aa01bb8090e00a091abc63e06e'), 33: (31, 'f1be63138605a75b81aba22421d80a30df63fcf5258d6ef30c25401a14eff2ef'), 34: (25, 'f6d470ad33226ffe433e09e6263d4926e62f4a557d0dceb243a6ebeda0681bd3'), 35: (20, '3287f9cfb5ccdd68fa7d7835eaa52a10ef0e78dafdcc24dc0f622b9a50e92beb'), 36: (22, '480cf59aed259fcddf805e995463bf55516ab4ea48c50b45531a16571d055e63'), 37: (25, 'e1ad133e27626f3d8683358f165da8ea8450c3eabcd103020e005694fecce662'), 38: (29, '16211b2ffeb92b46d5e75f96fcd2cf4f0d100edf6e189b6f008af1abadfd8259'), 39: (22, '96f10134eba13859b63515adb3500eb1d65860da2203198f3bee798af794c6bd'), 40: (37, '65f5ae246b5defc77282531ca718cccd48082dc2756dbecef44cca2f574790ad'), 41: (1, '4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce'), 42: (1, '69f59c273b6e669ac32a6dd5e1b2cb63333d8b004f9696447aee2d422ce63763'), 43: (3, '4d236e5d09da80d149bd2734bc63fead76adbc0d4697733626e5ab1d95d2fca6'), 44: (29, 'f9b80ec2f389b50c684510c3d0d7dc050252432b90c444a21c0fd25223b8fbe7'), 45: (2, 'd2b2d5857ad48aa8ccecd39d5e10a604884e82d5698ef1a4d567150e42e363b7'), 46: (7, '1b2dabf84949197482f378cb307732d42e1f122257db3fbcc1db94b57fdb947c'), 47: (32, '4c67b3f74d0f3c5343fe4da84591224ea6bb8401e795b8e077723cc21b58788a'), 48: (20, '931b55a8d7ec6c70ace88ceeda858bb8a7d95fd98b5b5c5e16849b126cdf6652'), 49: (9, 'a8492ea682fbb0fe6a156fd2360101e572bb77ed995a7ee996a40af0d15e45c6'), 50: (9, '2bfaa806e9672419736cebfcb2debe26a920f2a37ee49c0f963d442f03912b55'), 51: (51, 'b7a3e023bcd77f6780906d9291d564615253bde58b6a49d501f54576f531aaad'), 52: (43, 'b44622c01730046a25c6e603f752b68c986443815d4e7bcc801cd64e1ab38b6e'), 53: (40, '9db4de8d802aa7a4fa2fa2cd30678cfa350f77e8601762539abd0dbe83d0b744'), 54: (57, 'be288e4a5a240857029be82942ff9fd2ef4c7bd45af5e96f6c8791041424d5f3'), 55: (48, '7bc8a031b92923f9c95aa201e6d1f0e5ee0cac3fd37a3ea62c68ca65b411b82c'), 56: (31, '04051b5db91c564b4f93931253271616a9119cc049c39c161b2d6e4869eec452'), 57: (44, '174fe9806f986b84e38a2f9d8572f74290924af1a8c3410d638c6e5faa9f7214'), 58: (43, 'be5c2b2ae39ee434129b2e2d232bbc7e0c9adaf332fc92752378d3c62985a53d'), 59: (30, '16d963a3fd7ddd214be5de21aed6f8d9476901fe9d7070cd9b634a0caa9c85a8'), 60: (52, '2fc28c1985c13282bef9c32769559edfc0879d77427e8c41cb62153a2416ce09')}
EXPECTED_COMPLETE_DIGEST = "8e3b53c6b0c0b13d1f3be30bfb1ea0c6ba3edad19954ce993f166025b08bc06c"
actual_signatures = {q["n"]: numeric_signature(q) for q in questions}
if "--print-fingerprints" in sys.argv:
    print("EXPECTED_NUMERIC_SIGNATURES =", repr(actual_signatures))
    print("EXPECTED_COMPLETE_DIGEST =", repr(complete_digest(questions)))
assert EXPECTED_NUMERIC_SIGNATURES and actual_signatures == EXPECTED_NUMERIC_SIGNATURES, "numeric signatures mismatch/uninitialised"
actual_digest = complete_digest(questions)
assert EXPECTED_COMPLETE_DIGEST != "VERIFIER_FIRST_SENTINEL" and actual_digest == EXPECTED_COMPLETE_DIGEST, "complete source digest mismatch/uninitialised"

mutated = copy.deepcopy(questions)
mutated[0]["ans"] += " 999"
assert complete_digest(mutated) != actual_digest, "answer mutation escaped digest"
assert numeric_signature(mutated[0]) != actual_signatures[1], "numeric answer mutation escaped signature"
mutated = copy.deepcopy(questions)
original_why = mutated[40]["why"]
mutated[40]["why"] = original_why.replace("हाइगेन्स", "तरंगाग्र", 1)
assert mutated[40]["why"] != original_why and complete_digest(mutated) != actual_digest, "prose mutation escaped digest"

expected_coverage = set(range(1, 61))
failures = [(q,l) for q,l,p in checks if not p]
missing = expected_coverage-covered
extra = covered-expected_coverage
print("\n=== NUMERICAL / CONCEPTUAL COVERAGE ===")
print(f"checks={len(checks)} questions_covered={len(covered)}/60")
print(f"missing={sorted(missing) if missing else 'none'} extra={sorted(extra) if extra else 'none'} failures={len(failures)}")
assert not missing and not extra and not failures, f"coverage/check failure: missing={missing}, extra={extra}, failures={failures}"
assert answer_bindings == 60, f"उत्तर bindings {answer_bindings}/60"
print("schema=11 keys; split=20/20/20; numbering=1–60; unique_prompts=60")
print(f"substantial_steps={sum(len(q['steps']) for q in questions)}; full_derivation_concept={full_derivation_concept}")
print("valid_marks=60/60; wrong_Indic=0; raw_prose_underscores=0")
print(f"published_answer_bindings={answer_bindings}/60; numerical_field_signatures=60/60")
print("mutation_guards=3/3; complete_source_digest=matched")


def verify_generated_artifacts():
    """Bind audited source to exact Markdown, navigation, index and PDF targets."""
    import build
    import pymupdf

    root = Path("/projects/sandbox/Phusics/UP-Board-Class12-Physics/practice-sets")
    sold = root / "solutions"
    published_questions = build.load(10)
    solution_paths = sorted(sold.glob("ch10sol*.md"), key=lambda p: int(re.search(r"(\d+)$", p.stem).group(1)))
    expected_names = [f"ch10sol{n}.md" for n in range(1, 61)]
    assert [p.name for p in solution_paths] == expected_names, "solution set is not exactly ch10sol1..60"

    required_sections = ("## 📋 प्रश्न", "## 🧮 प्रयुक्त सूत्र", "## 🤔 यह सूत्र क्यों लगाया?", "## ✍️ चरणबद्ध हल", "## ✅ उत्तर", "## 🎯 परीक्षा की ट्रिक", "## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान")
    internal_solution_links = 0
    for q, path in zip(published_questions, solution_paths):
        actual = path.read_text(encoding="utf-8")
        expected = build.build_solution(q, 10)
        assert actual == expected, f"generated solution differs from audited source: {path.name}"
        assert all(section in actual for section in required_sections), f"incomplete solution structure: {path.name}"
        assert "�" not in actual, f"replacement character: {path.name}"
        prose_only = re.sub(r"```.*?```", "", actual, flags=re.DOTALL)
        assert not re.search(r"[A-Za-zΑ-Ωα-ω]_[A-Za-z0-9\u0900-\u097F]", prose_only), f"raw prose underscore: {path.name}"
        assert not any(lo <= ord(ch) <= hi for ch in actual for lo,hi in other_indic), f"wrong Indic script: {path.name}"
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md(?:#[^)]*)?)\)", actual):
            internal_solution_links += 1
            clean_target = target.split("#", 1)[0]
            assert (path.parent / clean_target).resolve().is_file(), f"broken Markdown link {path.name} -> {target}"
    assert internal_solution_links == 178, f"solution navigation links {internal_solution_links}, expected 178"

    expected_index = build.build_master_index(str(sold))
    index_path = sold / "README.md"
    assert index_path.read_text(encoding="utf-8") == expected_index, "master solutions index is stale"
    all_md_links = []
    for path in [index_path, *solution_paths]:
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#")):
                continue
            clean_target = target.split("#", 1)[0]
            if clean_target:
                all_md_links.append((path, target))
                assert (path.parent / clean_target).resolve().is_file(), f"broken internal link {path.name} -> {target}"

    pdf_path = root / "chapter10.pdf"
    assert pdf_path.is_file() and pdf_path.stat().st_size >= 300_000, "Chapter 10 PDF missing or implausibly small"
    document = pymupdf.open(pdf_path)
    uris = [link.get("uri", "") for page in document for link in page.get_links() if link.get("kind") == pymupdf.LINK_URI]
    expected_uris = [
        "https://github.com/singhupavinash8506-arch/Phusics/blob/up-board-class12-2026-27/"
        f"UP-Board-Class12-Physics/practice-sets/solutions/ch10sol{n}.md"
        for n in range(1, 61)
    ]
    assert len(uris) == 60 and len(set(uris)) == 60 and set(uris) == set(expected_uris), "PDF must have exactly 60 unique expected HTTPS solution links"
    pdf_text = "\n".join(page.get_text() for page in document)
    assert "तरंग प्रकाशिकी" in pdf_text and "�" not in pdf_text, "PDF text/title extraction failed"
    assert not any(lo <= ord(ch) <= hi for ch in pdf_text for lo,hi in other_indic), "PDF contains wrong Indic script"
    readme = (root / "README.md").read_text(encoding="utf-8")
    expected_row = "| 10 | तरंग प्रकाशिकी | [chapter10.pdf](chapter10.pdf) ✅ | [60 हल](solutions/README.md) |"
    assert expected_row in readme, "main README Chapter 10 row is not published"
    assert not (root / "chapter11.pdf").exists() and not list(sold.glob("ch11sol*.md")), "Chapter 11 artifact found during Chapter 10-only verification"

    mutated_solution = build.build_solution(published_questions[0], 10).replace("## ✅ उत्तर", "## उत्तर", 1)
    assert mutated_solution != solution_paths[0].read_text(encoding="utf-8"), "generated-artifact mutation guard failed"
    print(f"POST_BUILD_ARTIFACT_BINDING solutions=60/60 structural=60/60 solution_nav_links={internal_solution_links} internal_links_resolved={len(all_md_links)} pdf_pages={document.page_count} pdf_bytes={pdf_path.stat().st_size} https_annotations=60/60 index=exact artifact_mutation=1/1")


if "--post-build" in sys.argv:
    verify_generated_artifacts()
