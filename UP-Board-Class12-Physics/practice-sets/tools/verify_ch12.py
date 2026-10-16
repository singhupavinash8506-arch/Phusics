# -*- coding: utf-8 -*-
"""अध्याय 12 — परमाणु: fail-closed स्रोत तथा post-build सत्यापन।

पहले स्वतंत्र भौतिक सम्बन्धों से प्रत्येक प्रकाशित संख्यात्मक निष्कर्ष निकाला जाता है,
फिर सभी 60 उत्तरों, exact schema, pedagogical depth, source fingerprints और generated
Markdown/PDF artifacts को audited स्रोत से बाँधा जाता है।
"""

from __future__ import annotations

import copy
import hashlib
import importlib
import math
from pathlib import Path
import re
import sys
import unicodedata

if not __debug__:
    raise RuntimeError("Chapter 12 verifier must run without Python -O")

EXPECTED_KEYS = {
    "n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"
}
H = 6.626e-34
C = 3.00e8
E = 1.602e-19
ME = 9.109e-31
RH = 1.097e7
A0 = 5.29e-11
V1 = 2.188e6
E1 = 13.6
COULOMB_MEV_FM = 1.44
ROOT = Path(__file__).resolve().parent
PRACTICE = ROOT.parent
SOLUTIONS = PRACTICE / "solutions"

parts = []
for part_number in (1, 2, 3):
    module = importlib.import_module(f"ch12_part{part_number}")
    parts.append(getattr(module, f"PART{part_number}"))
questions = sum(parts, [])
by_number = {q.get("n"): q for q in questions}

checks: list[tuple[int, str, bool]] = []
covered: set[int] = set()
answer_bindings = 0


def check(qno, label, got, expected, rel_tol=9e-4, abs_tol=0.0):
    """Magnitude-aware comparison; a tiny nonzero result can never pass as zero."""
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


def wavelength_nm(ni, nf, z=1):
    return 1e9 / (RH * z * z * (1 / nf**2 - 1 / ni**2))


def transition_ev(ni, nf, z=1):
    return E1 * z * z * (1 / nf**2 - 1 / ni**2)


def closest_fm(z, kinetic_mev):
    return 2 * z * COULOMB_MEV_FM / kinetic_mev


print("=== PART 1: प्रत्यक्ष सूत्र Q1–Q20 ===")
check(1, "hydrogen ground-state radius (angstrom)", A0 * 1e10, 0.529)
check(2, "hydrogen n=3 radius (angstrom)", 9 * A0 * 1e10, 4.761)
check(3, "He+ n=2 radius (angstrom)", A0 * 4 / 2 * 1e10, 1.058)
check(4, "hydrogen ground-state speed", V1, 2.188e6)
check(5, "hydrogen n=4 speed", V1 / 4, 5.470e5)
check(6, "Li2+ n=2 speed", V1 * 3 / 2, 3.282e6)
check(7, "hydrogen n=2 energy (eV)", -E1 / 4, -3.40)
check(8, "He+ n=3 energy (eV)", -E1 * 4 / 9, -6.04444)
check(9, "hydrogen ground-state ionisation energy", E1, 13.6)
check(10, "hydrogen n=3 ionisation energy", E1 / 9, 1.51111)
check(11, "hydrogen 1 to 2 excitation energy", E1 * (1 - 1 / 4), 10.20)
check(12, "hydrogen 3 to 2 emitted energy", transition_ev(3, 2), 1.88889)
check(12, "hydrogen 3 to 2 wavelength (nm)", wavelength_nm(3, 2), 656.335)
check(13, "Lyman-alpha wavelength (nm)", wavelength_nm(2, 1), 121.544)
check(14, "Balmer-alpha wavelength (nm)", wavelength_nm(3, 2), 656.335)
check(15, "Paschen-alpha wavelength (nm)", wavelength_nm(4, 3), 1875.24)
check(16, "Lyman series-limit wavelength (nm)", 1e9 / RH, 91.1577)
check(17, "Balmer series-limit wavelength (nm)", 4e9 / RH, 364.631)
check(18, "n=4 angular momentum (J s)", 4 * H / (2 * math.pi), 4.21824e-34)
check(19, "10.2 eV photon frequency", 10.2 * E / H, 2.46610e15)
check(20, "5 MeV alpha-Au closest approach (fm)", closest_fm(79, 5.00), 45.504)

print("\n=== PART 2A: एक अज्ञात Q21–Q30 ===")
check(21, "n from hydrogen radius 4a0", math.sqrt(4), 2)
check(22, "n from He+ radius 8a0", math.sqrt(8 * 2), 4)
check(23, "n from hydrogen energy -0.850 eV", math.sqrt(E1 / 0.850), 4)
check(24, "n from hydrogen ionisation energy 1.511 eV", math.sqrt(E1 / 1.511), 3.00011)
check(25, "n from hydrogen speed 7.293e5 m/s", V1 / 7.293e5, 3.00014)
check(26, "initial n from 12.089 eV to ground", math.sqrt(1 / (1 - 12.089 / E1)), 3.00011)
inv_lambda27 = 1 / (486.17e-9 * RH)
check(27, "initial n from 486.17 nm Balmer line", math.sqrt(1 / (1 / 4 - inv_lambda27)), 4.00004)
check(28, "initial n from Balmer wavenumber 1.5236e6", math.sqrt(1 / (1 / 4 - 1.5236e6 / RH)), 3.00002)
check(29, "lower n from 820.42 nm series limit", math.sqrt(RH * 820.42e-9), 3.00000)
check(30, "gold Z from closest approach dataset", 36.40 * 6.25 / (2 * COULOMB_MEV_FM), 78.9931)

print("\n=== PART 2B: दो अज्ञात Q31–Q40 ===")
check(31, "hydrogen n=4 radius (angstrom)", 16 * A0 * 1e10, 8.464)
check(31, "hydrogen n=4 speed", V1 / 4, 5.470e5)
check(32, "He+ n=3 radius (angstrom)", 9 * A0 / 2 * 1e10, 2.3805)
check(32, "He+ n=3 energy (eV)", -E1 * 4 / 9, -6.04444)
check(33, "hydrogen ground to n=3 excitation (eV)", E1 * (1 - 1 / 9), 12.0889)
check(33, "corresponding absorption wavelength (nm)", wavelength_nm(3, 1), 102.552)
check(34, "hydrogen 4 to 2 emitted energy (eV)", transition_ev(4, 2), 2.55)
check(34, "hydrogen 4 to 2 wavelength (nm)", wavelength_nm(4, 2), 486.174)
check(35, "hydrogen 5 to 2 frequency", C / (wavelength_nm(5, 2) * 1e-9), 6.91110e14)
check(35, "hydrogen 5 to 2 wavelength (nm)", wavelength_nm(5, 2), 434.084)
check(36, "Balmer longest wavelength (nm)", wavelength_nm(3, 2), 656.335)
check(36, "Balmer shortest wavelength (nm)", 4e9 / RH, 364.631)
check(37, "Lyman-alpha energy (eV)", transition_ev(2, 1), 10.20)
check(37, "Lyman-alpha frequency from energy", 10.2 * E / H, 2.46610e15)
check(38, "He+ 4 to 2 energy (eV)", transition_ev(4, 2, 2), 10.20)
check(38, "He+ 4 to 2 wavelength (nm)", wavelength_nm(4, 2, 2), 121.544)
check(39, "He+ n=2 radius (angstrom)", 2 * A0 * 1e10, 1.058)
check(39, "He+ n=2 energy (eV)", -E1, -13.6)
check(40, "7.7 MeV alpha-Au closest approach", closest_fm(79, 7.70), 29.5481)
check(40, "closest approach after doubling energy", closest_fm(79, 15.40), 14.7740)

print("\n=== PART 3A: निगमन एवं अवधारणा Q41–Q50 ===")
truth(41, "Rutherford apparatus and all three scattering observations",
      all(x in source_text(41) for x in ("स्वर्ण-पत्र", "जिंक सल्फाइड", "अधिकांश", "अल्प", "बहुत कम")))
truth(42, "Rutherford model conclusions and stated limitations",
      all(x in source_text(42) for x in ("धन आवेश", "रिक्त", "त्वरित", "विकिरण", "रेखा-वर्णक्रम")))
truth(43, "head-on closest-approach derivation uses energy conservation",
      all(x in source_text(43) for x in ("b=0", "Kα", "2Ze²", "गतिज ऊर्जा शून्य", "turning point")))
truth(44, "impact parameter gives qualitative scattering hierarchy",
      all(x in source_text(44) for x in ("impact parameter", "b", "प्रत्यक्ष टक्कर", "विक्षेपण कोण", "प्रतिकर्षण")))
truth(45, "all Bohr postulates and stationary-state radiation rule",
      all(x in source_text(45) for x in ("स्थायी कक्षा", "विकिरण नहीं", "mₑvr=nħ", "संक्रमण", "hν")))
truth(46, "hydrogen-like orbit-radius derivation",
      all(x in source_text(46) for x in ("केन्द्राभिमुख", "कूलॉम", "rₙ", "a₀", "n²/Z")))
truth(47, "speed and angular-momentum derivation",
      all(x in source_text(47) for x in ("vₙ", "Z/n", "Lₙ=nħ", "2.188 × 10⁶", "quantisation")))
truth(48, "total-energy derivation and ionisation/excitation meanings",
      all(x in source_text(48) for x in ("K=−U/2", "Eₙ", "−13.6", "आयनन", "उत्तेजन")))
truth(49, "Bohr transition to Rydberg formula and series assignment",
      all(x in source_text(49) for x in ("1/λ", "R", "nᵢ", "n<sub>f</sub>", "Lyman", "Balmer", "Paschen")))
truth(50, "energy-level diagram, limits, emission and absorption",
      all(x in source_text(50) for x in ("−13.6 eV", "0 eV", "अवशोषण", "उत्सर्जन", "series limit", "ऊर्जा-स्तर")))

print("\n=== PART 3B: कठिन मिश्रित अनुप्रयोग Q51–Q60 ===")
photon51 = H * C / (600e-9 * E)
ionisation51 = E1 / 9
kinetic51 = photon51 - ionisation51
check(51, "600 nm photon energy (eV)", photon51, 2.06804)
check(51, "hydrogen n=3 ionisation threshold (eV)", ionisation51, 1.51111)
check(51, "photo-ionised electron kinetic energy (eV)", kinetic51, 0.556929)
check(51, "photo-ionised electron speed", math.sqrt(2 * kinetic51 * E / ME), 4.42599e5)
check(52, "Li2+ ground ionisation energy (eV)", E1 * 9, 122.4)
check(52, "Li2+ threshold wavelength (nm)", H * C / (E1 * 9 * E) * 1e9, 10.1375)
check(53, "level reached after absorbing 12.75 eV", math.sqrt(1 / (1 - 12.75 / E1)), 4)
check(53, "n=4 ionisation energy (eV)", E1 / 16, 0.850)
check(53, "n=4 ionisation threshold wavelength (nm)", H * C / ((E1 / 16) * E) * 1e9, 1459.79)
check(54, "n=4 cascade distinct lines", 4 * 3 / 2, 6)
check(54, "n=4 cascade shortest wavelength", wavelength_nm(4, 1), 97.2349)
check(54, "n=4 cascade longest wavelength", wavelength_nm(4, 3), 1875.24)
check(55, "hydrogen n=2 radius (angstrom)", 4 * A0 * 1e10, 2.116)
check(55, "He+ n=4 radius (angstrom)", 8 * A0 * 1e10, 4.232)
check(55, "common energy magnitude (eV)", E1 / 4, 3.40)
truth(56, "general Z=k, kn_i to kn_f spectral scaling cancellation",
      all(x in source_text(56) for x in ("Z=k", "1/k²", "cancel", "समान photon energy",
                                          "समान wavelength", "He⁺ 6→4", "H 3→2")))
lambda57 = 656.3e-9
check(57, "656.3 nm line frequency", C / lambda57, 4.57108e14)
check(57, "656.3 nm photon energy (eV)", H * C / (lambda57 * E), 1.89064)
check(58, "5.5 MeV alpha-Au closest approach", closest_fm(79, 5.50), 41.3673)
check(58, "90 degree Rutherford impact parameter", closest_fm(79, 5.50) / 2, 20.6836)
nu_alpha = C / (wavelength_nm(3, 2) * 1e-9)
nu_beta = C / (wavelength_nm(4, 2) * 1e-9)
check(59, "Balmer alpha-beta frequency separation", nu_beta - nu_alpha, 1.59979e14)
check(59, "Balmer alpha-beta energy separation", H * (nu_beta - nu_alpha) / E, 0.66158)
radius_ratio60 = 2.116 / (A0 * 1e10)
energy_ratio60 = 13.6 / E1
z_over_n60 = math.sqrt(energy_ratio60)
n60 = radius_ratio60 * z_over_n60
z60 = n60 * z_over_n60
check(60, "quantum number from measured radius and energy", n60, 4)
check(60, "nuclear charge Z from measured radius and energy", z60, 4)
check(60, "identified ion orbital speed", V1 * z60 / n60, 2.188e6)
check(60, "identified state ionisation energy", E1 * z60**2 / n60**2, 13.6)

ANSWER_FRAGMENTS = {
 1:("0.529 Å",), 2:("4.761 Å",), 3:("1.058 Å",), 4:("2.188 × 10⁶ m/s",),
 5:("5.470 × 10⁵ m/s",), 6:("3.282 × 10⁶ m/s",), 7:("−3.40 eV",),
 8:("−6.044 eV",), 9:("13.6 eV",), 10:("1.511 eV",), 11:("10.20 eV",),
 12:("1.889 eV", "656.34 nm"), 13:("121.54 nm",), 14:("656.34 nm",),
 15:("1875.24 nm",), 16:("91.16 nm",), 17:("364.63 nm",),
 18:("4.218 × 10⁻³⁴ J·s",), 19:("2.466 × 10¹⁵ Hz",), 20:("45.50 fm",),
 21:("n = 2",), 22:("n = 4",), 23:("n = 4",), 24:("n = 3",), 25:("n = 3",),
 26:("nᵢ = 3",), 27:("nᵢ = 4",), 28:("nᵢ = 3",), 29:("n<sub>f</sub> = 3",), 30:("Z = 79",),
 31:("8.464 Å", "5.470 × 10⁵ m/s"), 32:("2.3805 Å", "−6.044 eV"),
 33:("12.089 eV", "102.55 nm"), 34:("2.550 eV", "486.17 nm"),
 35:("6.911 × 10¹⁴ Hz", "434.08 nm"), 36:("656.34 nm", "364.63 nm"),
 37:("10.20 eV", "2.466 × 10¹⁵ Hz"), 38:("10.20 eV", "121.54 nm"),
 39:("1.058 Å", "−13.6 eV"), 40:("29.55 fm", "14.77 fm"),
 41:("रदरफोर्ड", "स्वर्ण-पत्र"), 42:("नाभिकीय परमाणु मॉडल", "रेखा-वर्णक्रम"),
 43:("d = (1/4πε₀)(2Ze²/Kα)",), 44:("b घटने पर", "विक्षेपण कोण बढ़ता"),
 45:("स्थायी कक्षाएँ", "mₑvr=nħ"), 46:("rₙ=a₀n²/Z",),
 47:("vₙ=2.188 × 10⁶(Z/n) m/s", "Lₙ=nħ"),
 48:("Eₙ=−13.6Z²/n² eV",), 49:("1/λ=RZ²(1/n<sub>f</sub>²−1/nᵢ²)",),
 50:("Lyman", "Balmer", "Paschen", "अवशोषण", "उत्सर्जन"),
 51:("ionisation होगा", "2.068 eV", "1.511 eV", "0.557 eV", "4.426 × 10⁵ m/s"),
 52:("122.4 eV", "10.14 nm"), 53:("n = 4", "0.850 eV", "1459.79 nm"),
 54:("6", "97.23 nm", "1875.24 nm"),
 55:("2.116 Å", "4.232 Å", "−3.40 eV"),
 56:("Z=k", "समान photon energy", "समान wavelength", "He⁺ 6→4", "H 3→2"),
 57:("nᵢ=3 से n<sub>f</sub>=2", "4.571 × 10¹⁴ Hz", "1.891 eV"),
 58:("41.37 fm", "20.68 fm"),
 59:("3→2", "4→2", "1.600 × 10¹⁴ Hz", "0.662 eV"),
 60:("Z = 4", "n = 4", "Be³⁺", "2.188 × 10⁶ m/s", "13.6 eV"),
}
for qno in range(1, 61):
    claim(qno, "ans", *ANSWER_FRAGMENTS[qno])

assert all(len(ANSWER_FRAGMENTS[qno]) == 1 for qno in range(21, 31)), \
       "Q21–Q30 में एक ही bound unknown चाहिए"
assert all(len(ANSWER_FRAGMENTS[qno]) == 2 for qno in range(31, 41)), \
       "Q31–Q40 में ठीक दो bound outputs चाहिए"
assert set(by_number) == set(range(1, 61)), "प्रश्न coverage 1–60 नहीं है"
assert covered == set(range(1, 61)), f"physics coverage अधूरा: {sorted(set(range(1,61))-covered)}"
assert all(ok for _, _, ok in checks), "स्वतंत्र physics अथवा published-answer binding विफल"
assert answer_bindings == 60, f"60 answer bindings चाहिए, मिले {answer_bindings}"

print("\n=== SCHEMA, SPLIT, SCOPE और PEDAGOGICAL QUALITY ===")
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
assert all(4 <= len(q["steps"]) <= 5 and q["marks"] in (3, 5) for q in questions[50:60])
normalized_prompts = [re.sub(r"\s+", " ", q["q"].strip().lower()) for q in questions]
assert len(set(normalized_prompts)) == 60, "duplicate prompts मिले"
# First-sentence/topic collision guard catches superficial number-swap templates.
prompt_stems = [re.sub(r"\d+(?:\.\d+)?|[⁰¹²³⁴⁵⁶⁷⁸⁹]+", "#", q["q"].split("।", 1)[0].lower())
                for q in questions]
assert max(prompt_stems.count(stem) for stem in set(prompt_stems)) <= 2, "superficial number-swap prompt family मिली"
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
assert all(not math.isclose(0.0, value, rel_tol=9e-4, abs_tol=0.0)
           for value in (5.29e-11, 4.218e-34, 1.097e7, 1.602e-19)), \
       "tiny nonzero targets को zero से अलग पहचानना आवश्यक है"

all_source = "\n".join(source_text(q["n"]) for q in questions)
for forbidden in ("द्रव्यमान दोष", "नाभिकीय बन्धन ऊर्जा", "रेडियोधर्मिता", "अर्ध-आयु",
                  "नाभिकीय विखण्डन", "नाभिकीय संलयन", "fission", "fusion", "radioactivity"):
    assert forbidden.lower() not in all_source.lower(), f"Chapter 13 scope drift मिला: {forbidden}"
assert all(x in all_source for x in ("रदरफोर्ड", "Bohr", "Lyman", "Balmer", "Paschen", "Rydberg"))
assert "impact parameter" in source_text(44) and "impact parameter" in source_text(58)
assert "nᵢ = 4" in source_text(27) and "nᵢ = 3" in source_text(28), "inverse spectrum datasets अलग रहें"
assert "7.70 MeV" in source_text(40) and "5.50 MeV" in source_text(58), "Rutherford datasets अलग रहें"
assert all(token in source_text(51) for token in ("600 nm", "n=3", "ionisation", "kinetic energy", "speed")), \
       "Q51 distinct excited-state photo-ionisation application रहना चाहिए"
assert all(token in source_text(56) for token in ("Z=k", "knᵢ", "1/k²", "He⁺ 6→4")), \
       "Q56 general spectral-scaling theorem रहना चाहिए"
assert "complete cascade" in source_text(54) and "threshold maximum wavelength" in source_text(53), \
       "Q53 excitation-threshold और Q54 cascade purposes अलग रहें"
assert all(token in source_text(60) for token in ("2.116 Å", "−13.6 eV", "Z = 4", "Be³⁺")), \
       "Q60 measured radius-energy inverse identification रहना चाहिए"
print("PASS exact schema, numbering, 20/20/20 split, depth, uniqueness, scope and script hygiene")


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


# Audited source पूरा होने पर --print-fingerprints से निकले मान यहाँ स्थिर किए जाते हैं।
EXPECTED_NUMERIC_SIGNATURES = {
    1: (21, 'ce79a70c6b97afd4200a68d30e22e653296baf664ffa5966f3f80994f1819c82'),
    2: (23, 'b98bae31818cc853cc860241b23d74df8bb5ed131adf02d3683115048d0dc671'),
    3: (26, '326014d4020d94c4a1ed0ed8f44138922e941b3c409797c94083269bef8acafc'),
    4: (16, '6f4fdd86a3a571ab4daa59aede0727ea77a365eebf19a4c0984bc707275e8f24'),
    5: (21, '720a877b436d05ba3c2b34e3183988d505a427b99242c7f9c3ddbc1eda3b3514'),
    6: (25, '7b9553f30046a649632df375e095c20d1138a6f0caa1eb699f60cffbb4709b73'),
    7: (21, 'd64558393580f175d7a93777ef4d8d8ddd3b48ce7b9dbc58ddb0f9ecdb5475d5'),
    8: (25, '798bb4d35d8941a7e5d22d63480f939f70b1dff58468ca33dc635d179124caae'),
    9: (18, '271ac6879a06a21f7f8bdd780dfc61d888c91ba1109fa2cbb1f26b2fb8d9d278'),
    10: (25, 'ad8e59069f6937642b70f785ab2442d3e4ad1caac3fddeaee898c33d84c5754c'),
    11: (29, '01cb5f2d675450fd49a7bdbe6948e5cb26367a649b69686f32fc39f20ab10528'),
    12: (40, '7a7da5930ad18b3e280b422c25cb8f5a7d689ac951cfd8816edbdd6e451c1007'),
    13: (35, '36aac24ceded724eacbd3bd982a3ede88dd368202ccf6bdce70569732d03e111'),
    14: (37, '4ed2b05570ed6d4dcde6672a247a2894e59460c14f49107790bebafce504509a'),
    15: (44, '60ea7bd7fd06b6f86a3db93ed57f28cd502677cb72918f46be12b93a71d79198'),
    16: (23, '5d2c5469476d6e97beaa2f0432e87573077e336c24a476996acc6b95eaa3c40d'),
    17: (29, 'c02bd5ad60b136683ae4aac46bb387603084053451eededfff8cd540f80eca79'),
    18: (30, 'b436ae058c6727e650e3de3ea2dcbcbed963102a49c10e1cb40f86a2a6784c59'),
    19: (15, '29caf8ecc1dd3bc10ce3943499dafaebdfd8da717ada1b84b13d679809bf5626'),
    20: (32, '613b6e3a757ed99f8387df15bf51977b3e417c3c6808fdae151c869f8ced4621'),
    21: (20, 'bd19e8f9d03c745f80ffae0a69abdf43908bc5d5bdb698a735074363498c778a'),
    22: (20, '215deba42c8e08f1f17eac44d3a802e104ecd1a2407bc6609d499e83ca123900'),
    23: (23, 'e25b7f4d4bdeadbce27ff951dce930ab7e4aed4811f9398866975cbd268c2845'),
    24: (23, 'fcce4d5df59aa437f7414b7fb65cbc4e3f0edd4797255714b16af0b1c471866e'),
    25: (12, '697e3a8874c3c1dfc023bb5f5c1c06b68480a5972356835da098f338d224cd4a'),
    26: (31, '32586a54fbc5cb420d2ba5a2f2b6595dd9e6a1ab43203e8a3e06adf424298a7f'),
    27: (39, 'b91a6b92f5a8872a1b31e0d04a0943b3d65133beb0281bbb6c280410f6c7fed6'),
    28: (30, 'a0e8cf1faad4e9179439e914bc29ba27576f18eccfd4f8b92ac9b6b278629fde'),
    29: (15, '6bcf362d8dfb95b60902596084fa0cd10093594f0ef25b9dcff1fb093a103059'),
    30: (28, '46d8f25b63e41f444dc8276cdcdb11857e2fc915bf1a6ef68e439be722e055c4'),
    31: (20, 'b64f8a2519482ec03b3fd1bb89a02cc19cf0b0faa2b600c61b0e4c7110197f61'),
    32: (22, '4038d2513dfcb1a0039632428abb1d7d2e22b412a60fc4b0ece8be591bad5a56'),
    33: (41, '93157dca5cf46750f08593d8d12d46b4080cb07b82bdc8fcc269a697300c7fe0'),
    34: (44, 'cca501a50d9ff8c29096ce5fb60c18a9c4fe81b59a3cccaaa7e3893e0b89d5b3'),
    35: (33, '11b5d698005cf39596ac180ba4ac855f100c13c89946b6568a007a9baff3acd1'),
    36: (34, 'd29b8e996ff604dcca0992275107042d1a575661bfaf9dc9aa0ada738afb9125'),
    37: (24, '06a58e5f2ef6ce6b66a2b410984dfc421ebc81926f2670d329e8e0107631beb2'),
    38: (42, '81a90dcbe35d207a1cd960303cd935c9636e9dc71039877464b540735218e5d6'),
    39: (19, 'f0f8ec9292f0e8339f32e801c480d11580e28cab0a76390c00c58fd157f5417e'),
    40: (29, 'c9052caab373835c9598a808c2fa77a4da6457b32fdac153c1e626bdbe4c1b63'),
    41: (9, '14cbc3e3484b67b540f2d31c1da88c5f4fc697b0cce4108aac43a2aaecfe69f0'),
    42: (6, 'e135b90967cc060b90c16d733de2c04f8348964761a3719c25dc5d455ce33557'),
    43: (46, 'd527856a9ceac91256af4061dd7c45d3faec98c9974b527741958844844a80e1'),
    44: (9, 'aae35b8145b3d89bd4ee9ba3750c5e282192bb3b5ce7ad87a1f895b53d0b67c9'),
    45: (14, 'aa5959f699a41d896ba58a1a24d5380cd4e4990c22a8e583bac53934d9db1b82'),
    46: (26, '139141fe4a60c28f480d1c3b2654e359c19adf07641a1a28a9b79bcd414cbece'),
    47: (8, 'd71fbd549a98f541551cb2d338f0e17969cb6a603bd1af2b1ff98752614ee53e'),
    48: (24, 'b0dc1601f6444dac5e5e1f71b41725cbdc920524c2503dd402615a57231f8ebc'),
    49: (31, '517d20b1d2bef33dd2bcff509eb01f9c1df922800438c5bcb682a2cefb11d0c9'),
    50: (50, '1abc5adaffb09c5a0c434f07f7cd565b3100e187bf27b0452288e16eebc39b5d'),
    51: (36, 'a86ddb2d5284c793c6c5ff2b0859e870739e2080d7234c8badc7e9627baf621c'),
    52: (28, '4177d41485d6023a5b22b6b3fbc60c64a44054a2bb9bdd6b7c49fe10667afa54'),
    53: (39, 'af30b705020d974e7d9b9e86db65af21b2449f42be60ec0330179117d263cf07'),
    54: (47, '52ff53826858f2f275826b03185bb8984c4de09fa4dd5108b805b203f34cfb22'),
    55: (36, 'ce7316d87d2c1db6c48fcafd555ac9e543a44dd1fa7d291a13bf4bbbdc91a151'),
    56: (26, '3f0d1829928b9cd2f226c522bedda14edea21c92349d6964b69ec1a8b06f5e0c'),
    57: (37, '6ad45576c0f0bac5e8fd8ff523bb279ceb13031a6de992b4eff2445f2cf49338'),
    58: (40, '67944f642872d3d5cd24d66e1c2b4f0dec2f395d98eff5d2d02ac69e1c758c15'),
    59: (51, '83ce2aae0878df3729ba5d932289c2a2f086ef33a34a4126ee29709d6810c484'),
    60: (37, 'e61e30fe7b383d8788365875233bdb46b6f647790ae810aa19d97ad7ce198939'),
}
EXPECTED_COMPLETE_DIGEST = "df34016513191cbd142cf12e05bfa33472ade33d7833f7b6faba1996db3941be"

if "--print-fingerprints" in sys.argv:
    print("\nEXPECTED_NUMERIC_SIGNATURES = {")
    for q in questions:
        count, digest = numeric_signature(q)
        print(f"    {q['n']}: ({count}, {digest!r}),")
    print("}")
    print(f"EXPECTED_COMPLETE_DIGEST = {complete_digest(questions)!r}")
    print("Fingerprint bootstrap complete; audit and freeze these values before normal verification.")
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
mutated_prose[40]["why"] += " परिवर्तित"
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


def canonical_rendered_text(text):
    """Normalize layout artifacts while preserving every numeric distinction."""
    text = re.sub(r"<[^>]+>", "", text)
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    # Chromium extraction can duplicate a shaped Devanagari vowel mark (ज्ञात→ज्ञाात).
    # Repair only those marks; never collapse digits or Latin/Devanagari letters.
    for mark in "ािीुूृॄॅेैॉोौॢॣंःँ":
        text = re.sub(re.escape(mark) + r"{2,}", mark, text)
    # Keep decimal points, signs, equality, ratios and transition arrows significant.
    return "".join(char for char in text if char.isalnum() or char in ".-+=×/→")


def pdf_prompt_manifest_matches(doc, records):
    """Bind each solution annotation's page to its complete audited prompt and topic."""
    page_by_question = {}
    for page in doc:
        for link in page.get_links():
            uri = link.get("uri") or ""
            match = re.search(r"/ch12sol(\d+)\.md$", uri)
            if match:
                qno = int(match.group(1))
                if qno in page_by_question:
                    return False
                page_by_question[qno] = page.get_text()
    if set(page_by_question) != set(range(1, 61)):
        return False
    for q in records:
        rendered = canonical_rendered_text(page_by_question[q["n"]])
        if canonical_rendered_text(q["q"]) not in rendered:
            return False
        if canonical_rendered_text(q["topic"]) not in rendered:
            return False
    return True


def verify_generated_artifacts():
    print("\n=== POST-BUILD GENERATED ARTIFACTS ===")
    build = importlib.import_module("build")
    published = build.load(12)
    assert 12 in build.CONSTANTS and all(token in build.CONSTANTS[12] for token in ("R", "a<sub>0</sub>", "13.6"))
    expected_names = {f"ch12sol{n}.md" for n in range(1, 61)}
    actual = {p.name for p in SOLUTIONS.glob("ch12sol*.md")}
    assert actual == expected_names, f"Chapter 12 समाधान set गलत: missing={expected_names-actual}, extra={actual-expected_names}"

    required_sections = ("## 📋 प्रश्न", "## 🧮 प्रयुक्त सूत्र", "## 🤔 यह सूत्र क्यों लगाया?",
                         "## ✍️ चरणबद्ध हल", "## ✅ उत्तर", "## 🎯 परीक्षा की ट्रिक",
                         "## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान")
    nav_count = 0
    all_local_links = 0
    for q in published:
        path = SOLUTIONS / f"ch12sol{q['n']}.md"
        text = path.read_text(encoding="utf-8")
        assert text == build.build_solution(q, 12), f"{path.name} audited source से byte-exact नहीं"
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
    assert len(master_links) == 732, f"12 अध्यायों के master local links 732 चाहिए, मिले {len(master_links)}"
    assert "| 12 | परमाणु |" in master and "## अध्याय 12 — परमाणु" in master

    changed = build.build_solution(dict(published[0], ans=published[0]["ans"] + " बदला"), 12)
    assert changed != (SOLUTIONS / "ch12sol1.md").read_text(encoding="utf-8")
    print(f"PASS 60 byte-exact solutions; navigation={nav_count}; all local links checked={all_local_links}")

    import pymupdf
    pdf_path = PRACTICE / "chapter12.pdf"
    assert pdf_path.exists() and pdf_path.stat().st_size >= 300_000, "chapter12.pdf missing/बहुत छोटा"
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
        f"UP-Board-Class12-Physics/practice-sets/solutions/ch12sol{n}.md"
        for n in range(1, 61)
    }
    assert len(uris) == 60 and len(set(uris)) == 60, \
        f"PDF URI links unique 60 चाहिए, मिले {len(uris)}/{len(set(uris))}"
    assert set(uris) == expected_uris, "PDF links exact ch12sol1..60 HTTPS set नहीं"
    assert pdf_prompt_manifest_matches(doc, published), "PDF के 60 rendered prompts/topics audited source से bound नहीं"
    pdf_mutations = (
        (0, "5.29", "529"),           # removed decimal point
        (22, "−0.850", "0.850"),      # removed physical sign
        (50, "600 nm", "60 nm"),      # changed repeated-digit magnitude
    )
    for record_index, old, new in pdf_mutations:
        mutated_pdf_source = copy.deepcopy(published)
        assert old in mutated_pdf_source[record_index]["q"]
        mutated_pdf_source[record_index]["q"] = mutated_pdf_source[record_index]["q"].replace(old, new, 1)
        assert not pdf_prompt_manifest_matches(doc, mutated_pdf_source), \
            f"PDF numeric mutation guard ने Q{record_index + 1} का {old!r}->{new!r} स्वीकार किया"
    joined_pdf_text = "\n".join(pdf_text)
    assert all(token in joined_pdf_text for token in ("अध्याय 12", "परमाणु", "60 प्रश्न"))
    assert "�" not in joined_pdf_text and "\x00" not in joined_pdf_text and not has_wrong_indic(joined_pdf_text)
    assert doc.page_count >= 8
    pages = doc.page_count
    doc.close()

    public_readme = (PRACTICE / "README.md").read_text(encoding="utf-8")
    expected_row = "| 12 | परमाणु | [chapter12.pdf](chapter12.pdf) ✅ | [60 हल](solutions/README.md) |"
    assert expected_row in public_readme, "Chapter 12 README row प्रकाशित नहीं"
    assert not (PRACTICE / "chapter13.pdf").exists(), "Chapter 13 को इस task में नहीं बनाना था"
    assert not any(SOLUTIONS.glob("ch13sol*.md")), "Chapter 13 समाधान इस task में नहीं बनने थे"
    print(f"PASS PDF pages={pages}, bytes={pdf_path.stat().st_size}, exact unique HTTPS links=60")
    print("PASS 60 rendered PDF prompts/topics bound; decimal/sign/repeated-digit mutations rejected")
    print("PASS master index, README publication row, and Chapter 13 absence")


if "--post-build" in sys.argv:
    verify_generated_artifacts()
