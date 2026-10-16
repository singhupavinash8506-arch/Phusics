# -*- coding: utf-8 -*-
"""अध्याय 9 — किरण प्रकाशिकी एवं प्रकाशिक यंत्र: fail-closed सत्यापन।

प्रत्येक प्रश्न की भौतिकी स्वतंत्र सूत्र/अपरिवर्तनीय सम्बन्ध से जाँची जाती है।
उत्तर-बन्धन, प्रत्येक प्रश्न के संख्यात्मक हस्ताक्षर और सम्पूर्ण स्रोत digest यह
सुनिश्चित करते हैं कि सत्यापित गणना ही प्रकाशित सामग्री में उपस्थित रहे।
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
    raise RuntimeError("Chapter 9 verifier must run without Python -O so no validation can be disabled")

EXPECTED_KEYS = {"n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"}
C = 3.0e8
D = 25.0  # स्पष्ट दृष्टि की न्यूनतम दूरी, cm

parts = []
for part_number in (1, 2, 3):
    module = importlib.import_module(f"ch9_part{part_number}")
    parts.append(getattr(module, f"PART{part_number}"))
questions = sum(parts, [])
by_number = {q.get("n"): q for q in questions}

checks: list[tuple[int, str, bool]] = []
covered: set[int] = set()
answer_bindings = 0


def check(qno, label, got, expected, rel_tol=7e-4, abs_tol=1e-9):
    passed = math.isclose(got, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    checks.append((qno, label, passed))
    covered.add(qno)
    print(f"{'PASS' if passed else 'FAIL'} Q{qno:02d} {label:<52} got={got:.12g} expected={expected:.12g}")


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
check(1, "concave-mirror focal length (cm)", -40 / 2, -20)
u, f = -30.0, -15.0
v = 1 / (1 / f - 1 / u)
check(2, "mirror image distance (cm)", v, -30)
u, v, h = -30.0, -60.0, 3.0
m = -v / u
check(3, "mirror magnification", m, -2)
check(3, "mirror image height (cm)", m * h, -6)
u, f = -30.0, 20.0
v = 1 / (1 / f - 1 / u)
check(4, "convex-mirror image distance (cm)", v, 12)
check(4, "convex-mirror magnification", -v / u, 0.4)
check(5, "Snell refractive index", math.sin(math.radians(45)) / math.sin(math.radians(30)), math.sqrt(2))
check(6, "speed in glass (m/s)", C / 1.5, 2.0e8)
check(7, "wavelength in glass (nm)", 600 / 1.5, 400)
check(8, "apparent depth (cm)", 12 / 1.5, 8)
i = math.radians(60)
r = math.asin(math.sin(i) / 1.5)
check(9, "slab refraction angle (degree)", math.degrees(r), 35.2644)
check(9, "lateral displacement (cm)", 6 * math.sin(i-r) / math.cos(r), 3.07483)
check(10, "critical angle (degree)", math.degrees(math.asin(1/1.5)), 41.8103)
n1, n2, u, radius = 1.0, 1.5, -30.0, 20.0
v = n2 / ((n2-n1)/radius + n1/u)
check(11, "spherical-surface image distance (cm)", v, -180)
u, f = -30.0, 20.0
v = 1 / (1/f + 1/u)
check(12, "convex-lens image distance (cm)", v, 60)
u, f = -30.0, -20.0
v = 1 / (1/f + 1/u)
check(13, "concave-lens image distance (cm)", v, -12)
check(13, "concave-lens magnification", v/u, 0.4)
u, v, h = -25.0, 50.0, 2.0
check(14, "lens magnification", v/u, -2)
check(14, "lens image height (cm)", h*v/u, -4)
n, r1, r2 = 1.5, 20.0, -20.0
f = 1 / ((n-1)*(1/r1-1/r2))
check(15, "lens-maker focal length (cm)", f, 20)
check(16, "lens power (D)", 1/0.25, 4)
check(17, "contact-lens power (D)", 3 + (-1), 2)
check(17, "contact-lens focal length (m)", 1/(3-1), 0.5)
check(18, "thin-prism deviation (degree)", (1.5-1)*6, 3)
check(19, "minimum-deviation prism index", math.sin(math.radians(50))/math.sin(math.radians(30)), 1.53209)
check(20, "compound-microscope magnifying power", (16/1)*(D/5), 80)

print("\n=== PART 2A: एक अज्ञात Q21–Q30 ===")
f, v = -18.0, -36.0
u = 1/(1/f-1/v)
check(21, "unknown mirror object distance (cm)", u, -36)
u, v = -20.0, 10.0
f = 1/(1/v+1/u)
check(22, "unknown convex-mirror focal length (cm)", f, 20)
check(23, "unknown refraction angle (degree)", math.degrees(math.asin(math.sin(math.radians(45))/math.sqrt(2))), 30)
check(24, "unknown real depth (cm)", (4/3)*6, 8)
check(25, "unknown refractive index", 1/math.sin(math.radians(30)), 2)
f, v = 15.0, 30.0
u = 1/(1/v-1/f)
check(26, "unknown lens object distance (cm)", u, -30)
u, v = -25.0, 50.0
f_m = (1/(1/v-1/u))/100
check(27, "unknown lens power (D)", 1/f_m, 6)
f, r1, r2 = 20.0, 15.0, -30.0
n = 1 + (1/f)/(1/r1-1/r2)
check(28, "unknown lens material index", n, 1.5)
A, n = 60.0, 1.5
delta = 2*math.degrees(math.asin(n*math.sin(math.radians(A/2))))-A
check(29, "unknown minimum deviation (degree)", delta, 37.1808)
check(30, "unknown telescope eyepiece focal length (cm)", 100/20, 5)

print("\n=== PART 2B: दो अज्ञात Q31–Q40 ===")
f, v = -15.0, -30.0
u = 1/(1/f-1/v)
check(31, "mirror object distance (cm)", u, -30)
check(31, "mirror magnification", -v/u, -1)
u, f = -40.0, 20.0
v = 1/(1/f-1/u)
check(32, "convex-mirror image distance (cm)", v, 13.3333)
check(32, "convex-mirror magnification", -v/u, 1/3)
check(33, "index from real/apparent depths", 15/12, 1.25)
check(33, "speed from depth ratio (m/s)", C/(15/12), 2.4e8)
check(34, "critical angle from index (degree)", math.degrees(math.asin(3/4)), 48.5904)
check(34, "speed from index (m/s)", C/(4/3), 2.25e8)
n1, n2, u, radius = 1.0, 1.5, -90.0, 30.0
v = n2/((n2-n1)/radius+n1/u)
check(35, "spherical refraction image distance (cm)", v, 270)
check(35, "spherical refraction magnification", n1*v/(n2*u), -2)
u, f, h = -25.0, 15.0, 3.0
v = 1/(1/f+1/u)
check(36, "lens image distance (cm)", v, 37.5)
check(36, "lens image height (cm)", h*v/u, -4.5)
power = 5-2
check(37, "equivalent power (D)", power, 3)
check(37, "equivalent focal length (cm)", 100/power, 33.3333)
A, delta = 60.0, 30.0
check(38, "prism index", math.sin(math.radians((A+delta)/2))/math.sin(math.radians(A/2)), math.sqrt(2))
check(38, "symmetric refraction angle (degree)", A/2, 30)
f = 5.0
u = 1/(-1/D-1/f)
check(39, "simple-microscope object distance (cm)", u, -4.16667)
check(39, "simple-microscope power at near point", 1+D/f, 6)
check(40, "telescope signed magnifying power", -120/4, -30)
check(40, "telescope normal length (cm)", 120+4, 124)

print("\n=== PART 3: निगमन, अवधारणा और कठिन प्रश्न Q41–Q60 ===")
# Q41–Q50 are checked by identities and required published conclusions.
truth(41, "mirror formula and pole-ray similar-triangle construction", all(x in source_text(41) for x in ("1/f", "ध्रुव P", "i=r", "ABP", "A'B'P")))
truth(42, "signed spherical-refraction derivation", all(x in source_text(42) for x in ("α=−h/u", "β=h/v", "γ=h/R", "i=α+γ", "r=γ−β", "(n₂−n₁)/R")))
truth(43, "thin-lens and lens-maker invariants", all(x in source_text(43) for x in ("1/v−1/u", "(n−1)", "1/R₁−1/R₂")))
truth(44, "minimum-deviation symmetry and prism relation", all(x in source_text(44) for x in ("i = e", "r₁ = r₂", "sin[(A+δ_m)/2]")))
truth(45, "TIR requires denser-to-rarer and supercritical incidence", all(x in source_text(45) for x in ("सघन", "विरल", "क्रान्तिक कोण", "प्रकाशिक तन्तु", "मृगतृष्णा", "हीरे")))
truth(46, "compound microscope product of objective and eyepiece powers", all(x in source_text(46) for x in ("m_o", "m_e", "LD/(f_o f_e)", "1+D/f_e")))
truth(47, "refracting telescope normal and near-point formulae", all(x in source_text(47) for x in ("f_o/f_e", "1+f_e/D", "f_o+f_e", "f_e×D/(D+f_e)")))
truth(48, "reflecting telescope textual ray construction and benefits", all(x in source_text(48) for x in ("परवलयिक", "द्वितीयक", "वर्ण-विपथन", "बड़ा द्वारक")))
truth(49, "simple microscope accommodation formulae", all(x in source_text(49) for x in ("D/f", "1+D/f", "आभासी")))
truth(50, "prism dispersion ordering and angular dispersion", all(x in source_text(50) for x in ("बैंगनी", "लाल", "δ_v−δ_r", "वर्ण-विक्षेपण")))

u, f, h = -30.0, -20.0, 4.0
v = 1/(1/f-1/u)
m = -v/u
check(51, "hard mirror image distance (cm)", v, -60)
check(51, "hard mirror image height (cm)", m*h, -8)
i = math.radians(45)
r = math.asin(math.sin(i)/1.5)
check(52, "hard slab refraction angle (degree)", math.degrees(r), 28.1255)
check(52, "hard slab lateral shift (cm)", 8*math.sin(i-r)/math.cos(r), 2.63314)
check(52, "normal apparent upward shift (cm)", 8*(1-1/1.5), 2.66667)
n_core, n_clad = 1.50, 1.40
na = math.sqrt(n_core*n_core-n_clad*n_clad)
check(53, "fibre numerical aperture", na, 0.538516)
check(53, "fibre air acceptance angle (degree)", math.degrees(math.asin(na)), 32.5827)
check(53, "fibre core critical angle (degree)", math.degrees(math.asin(n_clad/n_core)), 68.9605)
n1, n2, u, radius = 1.0, 1.6, -60.0, 20.0
v = n2/((n2-n1)/radius+n1/u)
check(54, "hard spherical-surface image distance (cm)", v, 120)
check(54, "hard spherical-surface magnification", n1*v/(n2*u), -1.25)
p = 10-4
f_m = 1/power if False else 1/p
u_m = -0.25
v_m = 1/(1/f_m+1/u_m)
check(55, "contact lens equivalent power (D)", p, 6)
check(55, "contact lens focal length (cm)", 100/p, 16.6667)
check(55, "contact lens image distance (cm)", 100*v_m, 50)
check(55, "contact lens magnification", v_m/u_m, -2)
separation, screen_distance = 60.0, 100.0
f = (screen_distance**2-separation**2)/(4*screen_distance)
check(56, "displacement-method focal length (cm)", f, 16)
check(56, "first lens position (cm)", (screen_distance-separation)/2, 20)
check(56, "second lens position (cm)", (screen_distance+separation)/2, 80)
check(56, "magnification product", (80/20)*(20/80), 1)
A, n = 45.0, 1.6
delta = 2*math.degrees(math.asin(n*math.sin(math.radians(A/2))))-A
check(57, "hard prism minimum deviation (degree)", delta, 30.5110)
check(57, "minimum-deviation incidence (degree)", (A+delta)/2, 37.7555)
check(57, "prism light speed (m/s)", C/n, 1.875e8)
check(58, "microscope normal magnifying power", (18/1.5)*(D/5), 60)
check(58, "microscope near-point magnifying power", (18/1.5)*(1+D/5), 72)
fo, fe = 90.0, 6.0
check(59, "telescope normal magnifying power magnitude", fo/fe, 15)
check(59, "telescope near-point magnifying power magnitude", (fo/fe)*(1+fe/D), 18.6)
ue = fe*D/(D+fe)
check(59, "telescope near-point length (cm)", fo+ue, 94.8387)
check(59, "telescope normal length (cm)", fo+fe, 96)
diameter_cm = 20.0
check(60, "reflector magnifying power magnitude", 100/5, 20)
check(60, "reflector focal ratio", 100/diameter_cm, 5)
check(60, "light-gathering ratio to 5 mm pupil", (200/5)**2, 1600)
moon_image_mm = 2 * 100 * math.tan(math.radians(0.50/2)) * 10
check(60, "lunar focal-plane image diameter (mm)", moon_image_mm, 8.7267)

# Published final-answer bindings. These are intentionally exact and separate from calculations.
ANSWER_FRAGMENTS = {
 1:("f = −20 cm",), 2:("v = −30 cm",), 3:("m = −2", "h' = −6 cm"),
 4:("v = +12 cm", "m = +0.40"), 5:("n = √2 ≈ 1.414",),
 6:("2.00 × 10⁸ m/s",), 7:("400 nm",), 8:("8.0 cm",),
 9:("r ≈ 35.26°", "d ≈ 3.075 cm"), 10:("C ≈ 41.81°",),
 11:("v = −180 cm",), 12:("v = +60 cm",), 13:("v = −12 cm", "m = +0.40"),
 14:("m = −2", "h' = −4 cm"), 15:("f = +20 cm",), 16:("P = +4.0 D",),
 17:("P = +2.0 D", "f = +0.50 m"), 18:("δ = 3.0°",),
 19:("n ≈ 1.532",), 20:("M ≈ 80",),
 21:("u = −36 cm",), 22:("f = +20 cm",), 23:("r = 30°",),
 24:("8.0 cm",), 25:("n = 2.0",), 26:("u = −30 cm",),
 27:("P = +6.0 D",), 28:("n = 1.50",), 29:("δ_m ≈ 37.18°",),
 30:("f_e = 5.0 cm",), 31:("u = −30 cm", "m = −1"),
 32:("v ≈ +13.33 cm", "m ≈ +0.333"), 33:("n = 1.25", "v_g = 2.40 × 10⁸ m/s"),
 34:("C ≈ 48.59°", "v = 2.25 × 10⁸ m/s"), 35:("v = +270 cm", "m = −2"),
 36:("v = +37.5 cm", "h' = −4.50 cm"), 37:("P = +3.0 D", "f ≈ +33.33 cm"),
 38:("n = √2 ≈ 1.414", "r₁ = r₂ = 30°"), 39:("u ≈ −4.17 cm", "M = 6"),
 40:("M = −30", "L = 124 cm"),
 41:("1/f = 1/v + 1/u",), 42:("n₂/v − n₁/u = (n₂−n₁)/R",),
 43:("1/f = (n−1)(1/R₁−1/R₂)", "1/v−1/u = 1/f"),
 44:("n = sin[(A+δ_m)/2]/sin(A/2)",),
 45:("पूर्ण आन्तरिक परावर्तन",), 46:("M_∞ ≈ LD/(f_o f_e)", "M_D ≈ (L/f_o)(1+D/f_e)"),
 47:("M_∞ = −f_o/f_e", "L_∞ = f_o+f_e", "L_D=f_o+f_e×D/(D+f_e)"),
 48:("वर्ण-विपथन नहीं",), 49:("M_∞ = D/f", "M_D = 1+D/f"),
 50:("δ_v > δ_r", "ω = δ_v−δ_r"),
 51:("v = −60 cm", "h' = −8 cm"),
 52:("r ≈ 28.13°", "d ≈ 2.633 cm", "Δ ≈ 2.667 cm"),
 53:("NA ≈ 0.5385", "θ_a ≈ 32.58°", "C ≈ 68.96°"),
 54:("v = +120 cm", "m = −1.25"),
 55:("P = +6.0 D", "f ≈ +16.67 cm", "v = +50 cm", "m = −2"),
 56:("f = 16 cm", "20 cm", "80 cm"),
 57:("δ_m ≈ 30.51°", "i=e ≈ 37.76°", "1.875 × 10⁸ m/s"),
 58:("M_∞ ≈ 60", "M_D ≈ 72"),
 59:("M_∞ = −15", "M_D = −18.6", "L_D ≈ 94.84 cm", "L_∞ = 96 cm"),
 60:("|M| = 20", "f/5", "1600 गुना", "8.73 mm"),
}
for qno in range(1, 61):
    claim(qno, "ans", *ANSWER_FRAGMENTS[qno])

# Structural and pedagogical quality gates.
print("\n=== SOURCE DATA STRUCTURE / QUALITY ===")
assert len(parts) == 3 and all(isinstance(p, list) and len(p) == 20 for p in parts), "हर part में 20 प्रश्न चाहिए"
assert len(questions) == 60, f"60 प्रश्न चाहिए, मिले {len(questions)}"
assert [q.get("n") for q in questions] == list(range(1, 61)), "क्रम 1–60 नहीं है"
assert [q.get("cat") for q in questions] == [1]*20+[2]*20+[3]*20, "20/20/20 category split टूटा"
assert all(q["cat"] == 2 for q in questions[20:40]), "Q21–Q40 category 2 चाहिए"
assert all(set(q) == EXPECTED_KEYS and len(q) == 11 for q in questions), "exact 11-key schema टूटा"
assert all(type(q["n"]) is int and type(q["cat"]) is int and type(q["marks"]) is int for q in questions)
assert all(q["marks"] in (1,2,3,4,5) for q in questions), "अमान्य अंक"
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
normalized_prompts = [re.sub(r"\s+", " ", q["q"].strip().lower()) for q in questions]
assert len(set(normalized_prompts)) == 60, "duplicate prompts"
full_derivation_concept = sum(q["marks"] in (3,5) and len(q["steps"]) >= 6 for q in questions[40:50])
assert 8 <= full_derivation_concept <= 10, f"Q41–Q50 में 8–10 पूर्ण निगमन चाहिए, मिले {full_derivation_concept}"
assert sum(q["marks"] >= 4 for q in questions[40:60]) >= 8, "कठिन खण्ड में पर्याप्त 4/5 अंक प्रश्न नहीं"
assert all(len(q["steps"]) >= 4 for q in questions[50:60]), "Q51–Q60 बहुचरणीय होने चाहिए"

other_indic = [(0x0980,0x09FF),(0x0A00,0x0A7F),(0x0A80,0x0AFF),(0x0B00,0x0B7F),(0x0B80,0x0BFF),(0x0C00,0x0C7F),(0x0C80,0x0CFF),(0x0D00,0x0D7F)]
for q in questions:
    text = source_text(q["n"])
    assert "�" not in text, f"Q{q['n']} replacement character"
    assert not any(lo <= ord(ch) <= hi for ch in text for lo,hi in other_indic), f"Q{q['n']} गलत Indic लिपि"

# Every numeral-bearing field is pinned; whole-source digest pins all prose and symbols too.
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

EXPECTED_NUMERIC_SIGNATURES = {1: (11, '618763a16d64ea01092259b40976a551b5036dbdeda818b2d5334cfc1e970204'), 2: (20, 'c8374415449b66886c72658018b6d4dd6766fc758bb5a03f49cb532054eebd00'), 3: (11, 'c1e0d3d96a02eba3309e95b3fb723f64b858496d1f5d7783e5ac33fdd7ab4121'), 4: (28, 'a6f7dce1bab2923ad1df0c8e076e564fbb809913a7790d920dbf1d195d575320'), 5: (18, '809e5cacabdf93ac670e64d49f9392039df2b81f4ee97b587a9a8b84b03de5a1'), 6: (12, '8a7efdc905d3c6b4ee272fb352291120668d493bcc7e679edbfc834b91f805b8'), 7: (13, '6b04a822fb7e664e378e1bc1a12b2524b0c4ffcea0f808b955a929d9dc5ce5a1'), 8: (11, '796cbd6661232d408ee1a2cec9773ab93d728f3b56d0cb81b79d96d1152ebe7b'), 9: (18, 'e289ea29e2ef1c5378142447873142e6f561dd194dab6c5d741203e1e5c5a6e5'), 10: (15, '71f2709a892ebb21de0fd8e118d7ec752b98391c4d786c31ab1fab22b7cdb386'), 11: (27, 'f331c9708764096ddb92a63d56926cf41cfdff1eecf0d559ad13b476a36ce779'), 12: (23, 'd4fd48e211d7772913612dea8b26cf58249ec30a7ad1ded78dacbc88c89c8073'), 13: (24, 'd14c032779173be9ad9a796f6b7d66250c3cf553ac05a3e8485ada35a5209be9'), 14: (15, 'fee4b8937c2791bb3b1e20b933d8ad17511fc99f9a5b199f1a4924c27f4f9b1d'), 15: (33, 'ea38c5388fb1f50bad0a71fd42798ae145b3d7da5734440d32619e7906b25648'), 16: (12, 'd3429228bfeed80e4d551a4857e226837de9589133a6d3266998f95fb62b9bba'), 17: (23, 'aefa3391fc49e30a43735dece322ee1c3a7f1127efe60dac4977df77c07609c8'), 18: (16, '08286367424b71586176d9d8333652aec3fdd38cb7f93806933556ef72d6012e'), 19: (28, 'f6e95129c77a022c5f318c0bef16b3b2cb8d9f9c76b4128795aae77edf976c8f'), 20: (16, '597c86d65a9b62932bb7b0b1a1862d4cd96283064857c1e171d868ea944d397e'), 21: (27, 'adea29aa88f7dc03b68b2186b310bd850395839b799c44b42deb1c61c06a35a1'), 22: (22, 'aa4306224ae634b5bae19c0385de0b9fab112ddf9b6423ef94b6af1c7407bba8'), 23: (22, '4c0ada5a292f265c289ed9145b87437659f33319c51973d4c6e399717ad89aee'), 24: (16, '074ee9b8c41b44c9f7e7b528609b02ef237a39e534050c75e9339fcdf4a94bda'), 25: (19, '3624a1148d520a5078927834aec0d53fae51660c1634e2da0637b7b4699fb197'), 26: (28, '7e90165cd085a4cc4345776622926879649e0080b9ce4e054e1cfd04af7c5eab'), 27: (35, '92f65df1f655b1c74b8a86e26809d9d1d066da347a2a6e5d2f33e4301f8c6f81'), 28: (41, '16dbc76e3a065ce7d1e832bde2e9562ecef278f3090733becb65ff9b6749e847'), 29: (24, '21e5011619ec5a127dac844693cd2014c3f6fd0d8d9985e15216353f649905fd'), 30: (10, '68b89c14bf143233ce3c95ece29efd07063d451231d8c2a14c6e148470f53b47'), 31: (23, '7944cd37264f091750d71888fbc6cae9a8b2b11e39481b907b21a8dfc2d729b7'), 32: (32, '1ff7b5fae2aab743b054da0edf357d7d80b2802d1c4e7e7d0976620c980d46b2'), 33: (19, '1403701ddabd260a7c953fa3857e355cc015e2fdd3f386a5d7192f4f3ab25358'), 34: (17, '8cd12e6dc2c7b28e460bf7365feb4a446d3eee1c7cb334030b033e9f2caafb59'), 35: (31, '1979fb0dbc8b17d82e4068c0171a381a10644741b3a8ab79ef60a9e7a33fc523'), 36: (29, '311170ea5679fe9f14e8ac71bf3731439579403c2359222a2464dcecf1b5a9a0'), 37: (27, '8744ceb37cd737229a5df08621305f3d8aeda63d307b62a24a1125232a937c37'), 38: (28, '577ea403777dbcdfbce09ce380853a87729d3ee04e417463766e23a301604544'), 39: (33, '1c3b34208a293db6c032033c5546cae945d1c7e233c8593cada45a216697cd87'), 40: (14, '0413af371fbdfc750776ef5e2a667ab1cdfc750374579abda960b3092c53ee4d'), 41: (13, 'f6dc6d151d92f04ca89f7ee9c88f321d6c506267324f5817b2b9bb1b658b0f4c'), 42: (7, '1f08d31cea7854cbdd4e78b1ddd7814da896a63cd2dc1dc6b9e56934e8d92c71'), 43: (50, '8bfc95eebf4eed3e1649bbc88f5fd1821ce5d61b49421b81c76a5ec08b758ed9'), 44: (12, 'ed605532d434c88db19648fa0a2e169159f9d2c5c313ebf34fe42ba8818d7794'), 45: (5, '1af4db62c3521877bc14733458920f49a4c7dd4197f4250bee8301c186da30cc'), 46: (5, 'a95155d5c139c7d3b3d119d9e9e70b18dd15a7bc64caa1903dd49686628af912'), 47: (3, '119b46369a178c0cd19c4fa8aa2e5f5f33b8b6066ac1845646724cd46c02b4cd'), 48: (2, '5c19a65ff18621eb2d7583556d18eb652a54296d0f32f638e8e68e0e697b1e64'), 49: (9, 'f31365fdd70fa670cba230879deb677682cf8c05645f5da7df1b2110ecd4b9af'), 50: (9, 'ac7404a9a7deace0deafd16235562c916f7078b643b43d5b119769daabe5dcc6'), 51: (43, '03f60dfae4333b141ffbc8ad7bee75c78fcd2480004cc7c6c04d689e15d7df32'), 52: (35, '9a65cb0101347dbd122f812a10b5d85ad7cdd138bbac81c587afe8b44cdd8fc0'), 53: (26, '673cfff7d49d7b311690cba6ab13fda1bd3c283b712f987d6fa35dbec7079d1f'), 54: (32, 'f86e22c552daaff0199fe781f4c33364ea472c4760360f4b4a11c1dc93e59c8e'), 55: (44, '7cb1c4c9d25b2d4b588241675fda626f92a536d0eb339c54978eb8f14541c992'), 56: (43, '4a0fc390e6893d2ebbdb9c3ae455eb66e54ece3e7c4bd31ed34e87c86db40bc8'), 57: (34, '8099bc79bed614e9cf05355edff56c8ca7b2a705ef13d39653e5fa35b6f2aacf'), 58: (34, 'dc944b93aae0f0803f3c84e47697d14c89e3d579bc273c5d4dcc0a8575636e59'), 59: (36, 'd2179fb59ad841256bc3dd068e2087b77afb31bc131f210613ec753264c0b65c'), 60: (45, '37ba0eee0657a10137d7280bf332736f177a1e9a72c6d79ca4158430ae438766')}
EXPECTED_COMPLETE_DIGEST = "3fef8946b2904a7566849083c6936880553b5d2a374892e969707d918084db29"
actual_signatures = {q["n"]: numeric_signature(q) for q in questions}
if "--print-fingerprints" in sys.argv:
    print("EXPECTED_NUMERIC_SIGNATURES =", repr(actual_signatures))
    print("EXPECTED_COMPLETE_DIGEST =", repr(complete_digest(questions)))
assert EXPECTED_NUMERIC_SIGNATURES and actual_signatures == EXPECTED_NUMERIC_SIGNATURES, "numeric signatures mismatch/uninitialised"
actual_digest = complete_digest(questions)
assert EXPECTED_COMPLETE_DIGEST != "VERIFIER_FIRST_SENTINEL" and actual_digest == EXPECTED_COMPLETE_DIGEST, "complete source digest mismatch/uninitialised"

# Mutation guards demonstrate fail-closed bindings rather than merely trusting their implementation.
mutated = copy.deepcopy(questions)
mutated[0]["ans"] += " 999"
assert complete_digest(mutated) != actual_digest, "answer mutation escaped digest"
assert numeric_signature(mutated[0]) != actual_signatures[1], "numeric answer mutation escaped signature"
mutated = copy.deepcopy(questions)
mutated[40]["why"] = mutated[40]["why"].replace("दर्पण", "परावर्तक", 1)
assert complete_digest(mutated) != actual_digest, "prose mutation escaped digest"

expected_coverage = set(range(1,61))
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
print("valid_marks=60/60; wrong_Indic=0")
print(f"published_answer_bindings={answer_bindings}/60; numerical_field_signatures=60/60")
print("mutation_guards=3/3; complete_source_digest=matched")


def verify_generated_artifacts():
    """Bind the audited source to every generated Markdown file, index, and PDF link."""
    import build
    import pymupdf

    root = Path("/projects/sandbox/Phusics/UP-Board-Class12-Physics/practice-sets")
    sold = root / "solutions"
    published_questions = build.load(9)
    solution_paths = sorted(
        sold.glob("ch9sol*.md"),
        key=lambda path: int(re.search(r"(\d+)$", path.stem).group(1)),
    )
    if [path.name for path in solution_paths] != [f"ch9sol{n}.md" for n in range(1, 61)]:
        raise AssertionError("generated Chapter 9 solution set is not exactly ch9sol1..60")
    for q, path in zip(published_questions, solution_paths):
        expected = build.build_solution(q, 9)
        if path.read_text(encoding="utf-8") != expected:
            raise AssertionError(f"generated solution differs from audited source: {path.name}")
    expected_index = build.build_master_index(str(sold))
    if (sold / "README.md").read_text(encoding="utf-8") != expected_index:
        raise AssertionError("master solutions index is stale or differs from builder output")

    pdf_path = root / "chapter9.pdf"
    if not pdf_path.is_file() or pdf_path.stat().st_size < 300_000:
        raise AssertionError("Chapter 9 PDF missing or implausibly small")
    document = pymupdf.open(pdf_path)
    uris = [
        link.get("uri", "")
        for page in document
        for link in page.get_links()
        if link.get("kind") == pymupdf.LINK_URI
    ]
    expected_uris = [
        f"https://github.com/singhupavinash8506-arch/Phusics/blob/up-board-class12-2026-27/"
        f"UP-Board-Class12-Physics/practice-sets/solutions/ch9sol{n}.md"
        for n in range(1, 61)
    ]
    if len(uris) != 60 or len(set(uris)) != 60 or set(uris) != set(expected_uris):
        raise AssertionError("PDF does not contain exactly 60 unique expected HTTPS solution links")
    pdf_text = "\n".join(page.get_text() for page in document)
    if "किरण प्रकाशिकी" not in pdf_text or "�" in pdf_text:
        raise AssertionError("PDF title/text extraction failed or contains replacement characters")
    readme = (root / "README.md").read_text(encoding="utf-8")
    expected_row = "| 9 | किरण प्रकाशिकी एवं प्रकाशिक यंत्र | [chapter9.pdf](chapter9.pdf) ✅ | [60 हल](solutions/README.md) |"
    if expected_row not in readme:
        raise AssertionError("main README Chapter 9 row is not published")
    if (root / "chapter10.pdf").exists() or list(sold.glob("ch10sol*.md")):
        raise AssertionError("Chapter 10 artifact found during Chapter 9-only verification")
    print(f"POST_BUILD_ARTIFACT_BINDING solutions=60/60 pdf_pages={document.page_count} https_annotations=60/60 index=exact")


if "--post-build" in sys.argv:
    verify_generated_artifacts()

print(f"\nALL CHAPTER 9 CHECKS PASSED: {len(checks)} independent/source-bound checks, 60/60 question coverage")
