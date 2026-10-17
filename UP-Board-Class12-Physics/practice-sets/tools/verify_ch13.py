# -*- coding: utf-8 -*-
"""अध्याय 13 — नाभिक: fail-closed स्रोत तथा post-build सत्यापन।

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
    raise RuntimeError("Chapter 13 verifier must run without Python -O")

EXPECTED_KEYS = {
    "n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"
}

# बोर्ड परिपाटी के नियतांक — यही मान प्रश्नपत्र के शीर्ष पर प्रकाशित हैं।
U_KG = 1.660539e-27
U_MEV = 931.5
C = 3.00e8
MEV_J = 1.602e-13
R0 = 1.2e-15
NA = 6.022e23
LN2 = 0.693
CI_BQ = 3.7e10
YEAR_S = 3.156e7
M_H = 1.007825
M_N = 1.008665
M_P = 1.007276
M_E_U = 0.000549
ME_KG = 9.109e-31
DAY_S = 86400.0

# प्रकाशित परिपाटी स्वयं भी जाँची जाती है: 0.693 वास्तविक ln 2 के पास होना चाहिए और
# 931.5 MeV/u वास्तविक u·c² के पास, अन्यथा सारी गणनाएँ चुपचाप खिसक जातीं।
assert math.isclose(LN2, math.log(2), rel_tol=1e-3), "ln 2 परिपाटी 0.693 गलत है"
assert math.isclose(U_MEV, U_KG * (2.99792458e8) ** 2 / MEV_J, rel_tol=2e-3), \
       "931.5 MeV/u तुल्यता गलत है"

ROOT = Path(__file__).resolve().parent
PRACTICE = ROOT.parent
SOLUTIONS = PRACTICE / "solutions"

parts = []
for part_number in (1, 2, 3):
    module = importlib.import_module(f"ch13_part{part_number}")
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


# ---- स्वतंत्र नाभिकीय सम्बन्ध (किसी स्रोत पाठ से नहीं पढ़े जाते) ----

def radius_fm(a):
    return R0 * a ** (1 / 3) * 1e15


def nuclear_density():
    return U_KG / (4 / 3 * math.pi * R0 ** 3)


def mass_defect_u(z, a, atomic_mass):
    return z * M_H + (a - z) * M_N - atomic_mass


def binding_mev(z, a, atomic_mass):
    return mass_defect_u(z, a, atomic_mass) * U_MEV


def lam_from_half(half_life):
    return LN2 / half_life


def remaining_fraction(t, half_life):
    return 0.5 ** (t / half_life)


def half_from_ratio(t, ratio):
    return t / (math.log(ratio) / math.log(2))


def nuclei_in_mass(mass_g, molar_g):
    return mass_g / molar_g * NA


print("=== PART 1: प्रत्यक्ष सूत्र Q1–Q20 ===")
check(1, "neutron count of U-235", 235 - 92, 143)
check(1, "proton count of U-235", 92, 92)
check(2, "radius of Al-27 (fm)", radius_fm(27), 3.6)
check(3, "radius ratio Cu-64 to Al-27", (64 / 27) ** (1 / 3), 4 / 3)
check(4, "nuclear matter density (kg/m^3)", nuclear_density(), 2.294e17)
check(5, "electron rest energy (MeV)", ME_KG * C * C / MEV_J, 0.5117)
check(6, "deuteron mass defect (u)", mass_defect_u(1, 2, 2.014102), 0.002388)
check(7, "deuteron binding energy (MeV)", 0.002388 * U_MEV, 2.224)
check(7, "deuteron binding energy per nucleon", 0.002388 * U_MEV / 2, 1.112)
check(8, "He-4 binding energy (MeV)", 0.030377 * U_MEV, 28.296)
check(8, "He-4 binding energy per nucleon", 0.030377 * U_MEV / 4, 7.074)
check(9, "Fe-56 total binding energy (MeV)", 56 * 8.79, 492.2, rel_tol=2e-3)
check(10, "alpha-decay daughter mass number", 238 - 4, 234)
check(10, "alpha-decay daughter atomic number", 92 - 2, 90)
check(11, "beta-minus daughter mass number", 234, 234)
check(11, "beta-minus daughter atomic number", 90 + 1, 91)
check(12, "remaining fraction after 60 min at T=20 min", remaining_fraction(60, 20), 0.125)
check(13, "radon decay constant (per s)", lam_from_half(3.8 * DAY_S), 2.111e-6)
check(14, "radium mean life (years)", 1600 / LN2, 2308.8)
check(15, "activity of 1e20 nuclei, T=10 h (Bq)", lam_from_half(10 * 3600) * 1.0e20, 1.925e15)
check(16, "5.0 mCi in becquerel", 5.0e-3 * CI_BQ, 1.85e8)
check(17, "energy from 0.02 u defect (MeV)", 0.02 * U_MEV, 18.63)
check(18, "d-d to He-3 reaction Q (MeV)",
      (2 * 2.014102 - 3.016029 - M_N) * U_MEV, 3.270)
check(19, "energy equivalent of 1 mg (J)", 1e-6 * C * C, 9.0e10)
check(20, "energy of 2.5e21 fissions at 200 MeV (J)", 2.5e21 * 200 * MEV_J, 8.01e10)

print("\n=== PART 2A: एक अज्ञात Q21–Q30 ===")
check(21, "mass number from radius 4.8 fm", (4.8 / 1.2) ** 3, 64)
check(22, "mass number from radius ratio 2 with A=27", 27 * 2 ** 3, 216)
check(23, "mass number from 160.6 MeV and 8.03 MeV", 160.6 / 8.03, 20)
check(24, "tritium mass defect from 8.482 MeV (u)", 8.482 / U_MEV, 0.009106)
check(24, "tritium mass defect from component masses (u)",
      mass_defect_u(1, 3, 3.016049), 0.009106)
check(25, "fissions per second for 200 MW", 200e6 / (200 * MEV_J), 6.242e18)
check(26, "half-life from lambda 1.44e-3 (s)", LN2 / 1.44e-3, 481.25)
check(27, "half-life when 25 percent remains in 10 yr", half_from_ratio(10, 1 / 0.25), 5)
check(28, "time for 1/16 remaining with T=8 d", 8 * math.log(16) / math.log(2), 32)
check(29, "half-life when activity falls to one fifth in 20 min", half_from_ratio(20, 5), 8.614)
check(30, "half-life from mean life 14.4 d", LN2 * 14.4, 9.979)

print("\n=== PART 2B: दो अज्ञात Q31–Q40 ===")
check(31, "radius of A=125 nucleus (fm)", radius_fm(125), 6.0)
check(31, "volume of A=125 nucleus (m^3)", 4 / 3 * math.pi * (6.0e-15) ** 3, 9.048e-43)
check(32, "Li-7 mass defect (u)", mass_defect_u(3, 7, 7.016004), 0.042131)
check(32, "Li-7 binding energy (MeV)", binding_mev(3, 7, 7.016004), 39.245)
check(32, "Li-7 binding energy per nucleon", binding_mev(3, 7, 7.016004) / 7, 5.606)
check(33, "O-16 binding energy (MeV)", binding_mev(8, 16, 15.994915), 127.62)
check(33, "O-16 binding energy per nucleon", binding_mev(8, 16, 15.994915) / 16, 7.976)
check(34, "U-238 mass defect (u)", mass_defect_u(92, 238, 238.050788), 1.934202)
check(34, "U-238 binding energy (MeV)", binding_mev(92, 238, 238.050788), 1801.71)
check(34, "U-238 binding energy per nucleon", binding_mev(92, 238, 238.050788) / 238, 7.570)
check(35, "decay constant for T=10 d (per s)", lam_from_half(10 * DAY_S), 8.021e-7)
check(35, "mean life for T=10 d (days)", 10 / LN2, 14.43)
check(36, "nuclei in 1 g of Ra-226", nuclei_in_mass(1.0, 226), 2.665e21)
check(36, "Ra-226 decay constant (per s)", lam_from_half(1600 * YEAR_S), 1.3724e-11)
check(36, "activity of 1 g Ra-226 (Bq)",
      lam_from_half(1600 * YEAR_S) * nuclei_in_mass(1.0, 226), 3.657e10)
check(36, "activity of 1 g Ra-226 (Ci)",
      lam_from_half(1600 * YEAR_S) * nuclei_in_mass(1.0, 226) / CI_BQ, 0.99, rel_tol=6e-3)
check(37, "nuclei in 1 kg of U-235", nuclei_in_mass(1000.0, 235), 2.563e24)
check(37, "fission energy of 1 kg U-235 (J)",
      nuclei_in_mass(1000.0, 235) * 200 * MEV_J, 8.210e13)
check(38, "Ra-226 alpha daughter mass number", 226 - 4, 222)
check(38, "Ra-226 alpha daughter atomic number", 88 - 2, 86)
check(38, "Ra-226 alpha decay Q (MeV)",
      (226.025410 - 222.017578 - 4.002603) * U_MEV, 4.871)
check(39, "decay constant for T=8 h (per s)", lam_from_half(8 * 3600), 2.406e-5)
check(39, "activity after 24 h from 10 mCi", 10 * remaining_fraction(24, 8), 1.25)
check(40, "half-life from 6000 to 750 Bq in 27 d", half_from_ratio(27, 8), 9)
check(40, "mean life from that half-life (days)", half_from_ratio(27, 8) / LN2, 12.99)

print("\n=== PART 3A: निगमन एवं अवधारणा Q41–Q50 ===")
truth(41, "nucleon notation plus isotope/isobar/isotone definitions and examples",
      all(x in source_text(41) for x in ("न्यूक्लिऑन", "A=Z+N", "समस्थानिक", "समभारिक",
                                         "समन्यूट्रॉनिक", "³₁H", "³₂He")))
check(42, "density independence: A=27 versus A=216 give one value",
      (27 * U_KG) / (4 / 3 * math.pi * (R0 * 27 ** (1 / 3)) ** 3),
      (216 * U_KG) / (4 / 3 * math.pi * (R0 * 216 ** (1 / 3)) ** 3))
check(42, "published nuclear density value", nuclear_density(), 2.294e17)
check(42, "nuclear to water density ratio", nuclear_density() / 1000.0, 2.3e14, rel_tol=3e-2)
truth(42, "size relation and cancellation of A are both derived",
      all(x in source_text(42) for x in ("R=R₀A^(1/3)", "(4/3)πR₀³A", "कट जाता",
                                         "असंपीड्य", "संतृप्त")))
check(43, "1 u energy equivalent with c = 3.00e8 (MeV)", U_KG * C * C / MEV_J, 932.9)
check(43, "1 u energy equivalent with precise c (MeV)",
      U_KG * (2.9979e8) ** 2 / MEV_J, 931.5, rel_tol=2e-3)
truth(43, "amu definition, E = mc squared and 931.5 MeV conversion",
      all(x in source_text(43) for x in ("कार्बन-12", "बारहवें भाग", "E=mc²",
                                         "1.660539×10⁻²⁷", "931.5")))
truth(44, "mass defect, binding energy, relation and per-nucleon significance",
      all(x in source_text(44) for x in ("द्रव्यमान क्षति", "बन्धन ऊर्जा", "Eb=Δm·c²",
                                         "प्रति न्यूक्लिऑन", "स्थायित्व")))
check(44, "worked example quoted for U-238 total binding energy",
      binding_mev(92, 238, 238.050788), 1801.7, rel_tol=2e-3)
truth(45, "binding-energy curve peak, flat region and both energy-release routes",
      all(x in source_text(45) for x in ("शिखर", "8.79", "समतल", "कूलॉम प्रतिकर्षण",
                                         "विखण्डन", "संलयन")))
check(45, "curve-based fission estimate quoted (MeV)", 235 * (8.5 - 7.6), 211.5)
check(45, "curve-based fusion estimate quoted (MeV)", 4 * (7.074 - 1.112), 23.85, rel_tol=2e-3)
truth(46, "nuclear force strength, range, charge independence, saturation, repulsive core",
      all(x in source_text(46) for x in ("प्रबल", "लघु परास", "आवेश", "संतृप्त",
                                         "0.8 fm", "प्रतिकर्षी", "मेसॉन")))
truth(47, "alpha/beta/gamma nature plus both displacement laws and inverted orders",
      all(x in source_text(47) for x in ("⁴₂He", "इलेक्ट्रॉन", "फोटॉन", "भेदन क्षमता",
                                         "आयनन क्षमता", "(A−4, Z−2)", "(A, Z+1)")))
truth(48, "decay-law derivation with separation, limits and activity law",
      all(x in source_text(48) for x in ("−dN/dt=λN", "dN/N=−λdt", "ln(N/N₀)=−λt",
                                         "N=N₀e^(−λt)", "A=A₀e^(−λt)")))
truth(49, "half-life and mean-life derivation with their ratio",
      all(x in source_text(49) for x in ("N₀/2", "T₁/₂=ln 2/λ", "τ=1/λ",
                                         "1.443", "N₀/e")))
check(49, "half-life to mean-life conversion factor", 1 / LN2, 1.443, rel_tol=2e-3)
check(49, "radium mean life quoted in the derivation (years)", 1600 / LN2, 2308.8)
truth(50, "fission example, chain reaction, critical mass, reactor parts and fusion",
      all(x in source_text(50) for x in ("¹⁴¹₅₆Ba", "⁹²₃₆Kr", "श्रृंखला", "क्रांतिक द्रव्यमान",
                                         "मंदक", "नियंत्रक छड़", "शीतलक", "संलयन", "10⁷ K")))
check(50, "deuterium-tritium fusion Q quoted (MeV)",
      (2.014102 + 3.016049 - 4.002603 - M_N) * U_MEV, 17.6, rel_tol=4e-3)

print("\n=== PART 3B: कठिन मिश्रित अनुप्रयोग Q51–Q60 ===")
solar_dm = 4 * M_H - 4.002603
check(51, "solar pp-chain mass defect (u)", solar_dm, 0.028697)
check(51, "solar pp-chain Q value (MeV)", solar_dm * U_MEV, 26.73)
check(51, "solar pp-chain energy per nucleon (MeV)", solar_dm * U_MEV / 4, 6.683)
check(51, "same Q from nuclear masses and two electrons (MeV)",
      (4 * M_P + 2 * M_E_U - (4.002603 - 2 * M_E_U)) * U_MEV, 26.73, rel_tol=2e-3)
thermal_w = 1000e6 / 0.25
daily_j = thermal_w * DAY_S
fissions_day = daily_j / (200 * MEV_J)
check(52, "required thermal power (W)", thermal_w, 4.00e9)
check(52, "daily thermal energy (J)", daily_j, 3.456e14)
check(52, "daily fission count", fissions_day, 1.079e25, rel_tol=1e-3)
check(52, "daily U-235 consumption (kg)", fissions_day / NA * 235 / 1000, 4.209)
q53 = (238.050788 - 234.043601 - 4.002603) * U_MEV
check(53, "U-238 alpha decay Q (MeV)", q53, 4.270)
check(53, "alpha kinetic energy after momentum sharing (MeV)", q53 * 234 / 238, 4.198)
check(53, "thorium recoil energy (MeV)", q53 * 4 / 238, 0.072, rel_tol=4e-3)
check(54, "carbon-14 half-lives elapsed at 30 percent", math.log(1 / 0.30) / math.log(2), 1.737)
check(54, "carbon-14 sample age (years)", 5730 * math.log(1 / 0.30) / math.log(2), 9953)
lam55 = lam_from_half(5.27 * YEAR_S)
act55 = 8.0e-3 * CI_BQ
check(55, "cobalt-60 activity in becquerel", act55, 2.96e8)
check(55, "cobalt-60 decay constant (per s)", lam55, 4.167e-9)
check(55, "cobalt-60 nuclei present", act55 / lam55, 7.104e16)
check(55, "cobalt-60 source mass (g)", act55 / lam55 / NA * 60, 7.077e-6)
check(56, "remaining fraction after 80 min at T=20 min", remaining_fraction(80, 20), 0.0625)
check(56, "decayed percentage after 80 min", (1 - remaining_fraction(80, 20)) * 100, 93.75)
check(57, "deuteron total binding energy from per-nucleon value (MeV)", 2 * 1.112, 2.224)
check(57, "helium total binding energy from per-nucleon value (MeV)", 4 * 7.074, 28.296)
check(57, "fusion energy released by two deuterons (MeV)", 4 * 7.074 - 2 * (2 * 1.112), 23.85,
      rel_tol=2e-3)
check(58, "per-nucleon binding gain in fission (MeV)", 8.5 - 7.6, 0.9)
check(58, "estimated energy per fission (MeV)", 235 * (8.5 - 7.6), 211.5)
check(58, "products total binding energy (MeV)", 235 * 8.5, 1997.5)
sep59 = (15.003065 + M_N - 15.994915) * U_MEV
check(59, "O-16 neutron separation mass difference (u)",
      15.003065 + M_N - 15.994915, 0.016815)
check(59, "O-16 neutron separation energy (MeV)", sep59, 15.66, rel_tol=2e-3)
check(59, "same result from binding-energy difference (MeV)",
      binding_mev(8, 16, 15.994915) - binding_mev(8, 15, 15.003065), 15.66, rel_tol=2e-3)
check(60, "half-lives elapsed for 1600 to 100 per s", math.log(16) / math.log(2), 4)
check(60, "half-life in seconds", 7200 / 4, 1800)
check(60, "decay constant (per s)", LN2 / 1800, 3.850e-4)
check(60, "initial nuclei from activity", 1600 / (LN2 / 1800), 4.156e6)
check(60, "closure: activity of remaining nuclei after 2 h",
      (LN2 / 1800) * (1600 / (LN2 / 1800)) / 16, 100)

ANSWER_FRAGMENTS = {
 1:("92 प्रोटॉन", "143 न्यूट्रॉन"), 2:("3.6 fm",), 3:("4/3 = 1.333",),
 4:("2.294 × 10¹⁷ kg/m³",), 5:("0.5117 MeV",), 6:("0.002388 u",),
 7:("2.224 MeV",), 8:("7.074 MeV",), 9:("492.2 MeV",),
 10:("²³⁴₉₀Th", "234", "90"), 11:("²³⁴₉₁Pa", "234", "91"),
 12:("1/8 = 12.5%",), 13:("2.111 × 10⁻⁶ s⁻¹",), 14:("2308.8 वर्ष",),
 15:("1.925 × 10¹⁵ Bq",), 16:("1.85 × 10⁸ Bq",), 17:("18.63 MeV",),
 18:("3.270 MeV",), 19:("9.0 × 10¹⁰ J",), 20:("8.01 × 10¹⁰ J",),
 21:("A = 64",), 22:("A = 216",), 23:("A = 20",), 24:("0.009106 u",),
 25:("6.242 × 10¹⁸",), 26:("481.25 s",), 27:("5 वर्ष",), 28:("32 दिन",),
 29:("8.614 मिनट",), 30:("9.979 दिन",),
 31:("6.0 fm", "9.048 × 10⁻⁴³ m³"),
 32:("0.042131 u", "39.245 MeV"),
 33:("127.62 MeV", "7.976 MeV"),
 34:("1801.71 MeV", "7.570 MeV"),
 35:("8.021 × 10⁻⁷ s⁻¹", "14.43 दिन"),
 36:("2.665 × 10²¹", "3.657 × 10¹⁰ Bq"),
 37:("2.563 × 10²⁴", "8.210 × 10¹³ J"),
 38:("²²²₈₆Rn", "4.871 MeV"),
 39:("2.406 × 10⁻⁵ s⁻¹", "1.25 mCi"),
 40:("9 दिन", "12.99 दिन"),
 41:("समस्थानिक", "समभारिक", "समन्यूट्रॉनिक"),
 42:("2.294 × 10¹⁷ kg/m³", "द्रव्यमान संख्या से स्वतन्त्र"),
 43:("1.660539 × 10⁻²⁷ kg", "931.5 MeV"),
 44:("Eb = Δm × 931.5 MeV", "प्रति न्यूक्लिऑन"),
 45:("8.8 MeV", "विखण्डन", "संलयन"),
 46:("लघु परास", "प्रतिकर्षी"),
 47:("गामा > बीटा > अल्फा", "अल्फा > बीटा > गामा"),
 48:("N = N₀e^(−λt)", "A = A₀e^(−λt)"),
 49:("T₁/₂ = 0.693/λ", "τ = 1.443T₁/₂"),
 50:("200 MeV", "क्रांतिक द्रव्यमान", "मंदक", "संलयन"),
 51:("26.73 MeV", "6.683 MeV"),
 52:("4.209 kg",),
 53:("4.270 MeV", "4.198 MeV", "0.072 MeV"),
 54:("9953 वर्ष",),
 55:("7.104 × 10¹⁶", "7.077 × 10⁻⁶ g"),
 56:("6.25%", "93.75%", "1/16"),
 57:("23.85 MeV",),
 58:("211.5 MeV", "200 MeV"),
 59:("15.66 MeV",),
 60:("30 मिनट", "3.850 × 10⁻⁴ s⁻¹", "4.156 × 10⁶"),
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
assert len(set(q["topic"] for q in questions)) == 60, "प्रत्येक प्रश्न का topic भिन्न होना चाहिए"
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
           for value in (1.660539e-27, 1.3724e-11, 4.167e-9, 9.048e-43)), \
       "tiny nonzero targets को zero से अलग पहचानना आवश्यक है"

all_source = "\n".join(source_text(q["n"]) for q in questions)
for forbidden in ("अर्धचालक", "semiconductor", "ट्रांजिस्टर", "transistor", "डायोड", "diode",
                  "zener", "जेनर", "दिष्टकारी", "rectifier", "संधि", "p-n", "ऊर्जा बैण्ड"):
    assert forbidden.lower() not in all_source.lower(), f"Chapter 14 scope drift मिला: {forbidden}"
assert all(x in all_source for x in ("समस्थानिक", "समभारिक", "समन्यूट्रॉनिक", "बन्धन ऊर्जा",
                                     "नाभिकीय बल", "अर्ध-आयु", "औसत आयु", "सक्रियता",
                                     "विखण्डन", "संलयन", "क्रांतिक द्रव्यमान", "मंदक")), \
       "अध्याय 13 का कोई अनिवार्य उपविषय छूट गया"
assert "1.2 fm" in source_text(2) and "R₀" in source_text(21), "R₀ सम्बन्ध दोनों दिशाओं में रहे"
assert "4.8 fm" in source_text(21) and "4.8 fm" in source_text(3), \
       "Cu-64 की त्रिज्या forward तथा inverse दोनों में संगत रहे"
assert "3.8 दिन" in source_text(13) and "1600 वर्ष" in source_text(14), "decay datasets अलग रहें"
assert "14.4" in source_text(30) and "14.43" in source_text(35), \
       "Q30 inverse तथा Q35 forward mean-life datasets अलग रहें"
assert "30%" in source_text(54) and "5730" in source_text(54), \
       "Q54 कार्बन डेटिंग अनुप्रयोग रहना चाहिए"
assert "1000 MW" in source_text(52) and "25%" in source_text(52), \
       "Q52 रिएक्टर दक्षता अनुप्रयोग रहना चाहिए"
assert "प्रतिक्षेप" in source_text(53) and "संवेग" in source_text(53), \
       "Q53 में संवेग विभाजन रहना चाहिए"
assert "पृथक्करण" in source_text(59) and "¹⁵₈O" in source_text(59), \
       "Q59 न्यूट्रॉन पृथक्करण ऊर्जा रहना चाहिए"
assert "6000" in source_text(40) and "1600 विघटन" in source_text(60), \
       "Q40 तथा Q60 के activity datasets भिन्न रहें"
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
    1: (16, 'e0a4d2b50766714f480c734b688ff76c20742d7014706433c0737d8b769bba85'),
    2: (38, 'a8d26d0a421c069bb113cb09a21cc40eadc73d4594b52b5f33d54bf4afecd2bb'),
    3: (38, '1e9f9209a0a6e21c24006b00d5798988e1ae093c53cc1a6b334e065b7d023a38'),
    4: (36, '987b35e6b55a0f65216b16ec4061573baf805f31408a811d99652ce661ad568b'),
    5: (23, 'c12e257d2254181607fe941095977c503440893a267cfbbbd171af2ae6f89d2e'),
    6: (19, 'be74303df82cd4a1ac57d52f9e242cde9e027a64d6f79822182f69aa40dff186'),
    7: (25, 'ea084d6d44f911e8cc1b9b8a69bc38296b6bc8c687143bee5e9802bbd0f37c80'),
    8: (22, 'dab3746c919f8cb2189d5cefa1827416d84aeaf53ea8a226dce67f79cd57144f'),
    9: (16, '10079361e737f0ef46a71c390320be671f8d0e9da3446ff8897898628acbc5b3'),
    10: (22, '0e4d216c4d36d5b77e0a2b886b4140004fd53325e0480098dce3c446ee8930e2'),
    11: (15, '79f194e52131f3ee80242e5bca037ee197b3a6fed2d159a6384661410b5e9f2a'),
    12: (41, '2e43163f9970e5702bd697334b1e7fa89d0fb52b16559e4a2f728c09f11fcd5a'),
    13: (22, 'aba22c9e4489c86e932593885ae3478765f4aa5a318e9d12ed60d0605cf02d6a'),
    14: (26, 'fe826087d9c27355d4623cc090c5674e554f472cc23b7ab5c918474dbb22be8c'),
    15: (25, '3f3b05ea308cf7a1317566b9106b504685f73cf48deea82e3d8470d4be5016ed'),
    16: (24, '356886641bf676600ba74e0cde6e142871779bf2e3ea9b8ef0eecd558c60d16a'),
    17: (21, '4c0d7a4a960dd7de3256f2e86b246fdc3f264aa31ccb05adf645348a746d0e4b'),
    18: (26, 'ffaa82a9c03fa9487bf45a2f8bad587be07fc517999e0a0e0722e63e5e698d96'),
    19: (23, 'ad5f1defbfbbcdcd6698abcc34b2a201159a2ef28e056743403b1649c7734cfb'),
    20: (25, 'aa6bd6b29758dda1f82f5ca15a89c06264c9bf0b4799f1ede577c0bb1895a585'),
    21: (31, 'c833e1bf865b439c65dec6e303eddb8233bc804bc2e4d80354b5cdb7f760c888'),
    22: (30, 'da3d6d931cefc19dd3e021602615f2b3c749aab47f3e4d2f886fae1b14ddf337'),
    23: (16, 'cd7c5893b21e68def8fbd2b9c585517ff7d593d1c63049a1f210932ff628e373'),
    24: (24, '54c4bfcc27b2a9fd71d09d8fbbd427eeda954664c4efd8eb5175f92e16cbc819'),
    25: (20, 'c6d327e5f6767ada1130edc2c423f014157fcd65cf7c7a7a01c6c606392cb006'),
    26: (24, '18c5b5f0799b71edea8dc2c8637d8e5edf2d03862aafa34ef12c647880fa5b37'),
    27: (30, '3e5a407464280515fc582cbcfdea650458809dc0806fd86958d553af97a4cb88'),
    28: (43, '2733014995b52f25efc0e01f93e741fd43dc233a1977db478ae19d68ca4e0a14'),
    29: (36, '093a3bfafcaddab39ab8bdc28d99bf2b166e3dc06f46988f8478f3e967a7392a'),
    30: (23, '3d0050d93cc9989a3f52cb168e0084050afb698ad37518b2c86456bd41bdc4bd'),
    31: (35, '6c7cc6f195457ec981518f5ab7b0551e8aff379d79612a4ca9fbed5f40c79592'),
    32: (33, '118681cee0c00ea60552dfaaa8db12c41969d4a1b914b125fb7e9112651ede5d'),
    33: (32, '4498a7dfcb83ba6fcd32e8d9d2d866cddfd261a383a556f22fb60c705193ac0d'),
    34: (33, 'e7f27d249558ddd6c5ec250f4096f86b87d7ca111bae62db6122452580f12fdf'),
    35: (25, 'ee11ed0b793ff27f4b42c733cae8422e2811a7f8a00a2c84d7084fa05f24c91f'),
    36: (32, '0c6e242e62bfb16c52b36259348333393c546cd8ec5422652da6fc49b851bcbd'),
    37: (27, '3323845353f3f94d7d19811fda573f9d9e0208e8760dc4d3c8245a89ca96fa1f'),
    38: (26, '8267417b31569352e8fd85507ed7cf3fe5c4c51b26a7b20225afc5d6daf0afb0'),
    39: (35, 'f6133943d40ea86d49279f0e0bccb5bc3735053cbc81c88778b168ee2e144881'),
    40: (35, '33c7cc441d2e9487a4b9f617cf469354663e062e023b049adc7cbdee739cf019'),
    41: (7, 'ebb7169964bef756b8b89fea56737881d3c9c8202d7006d3e13b36f5222fc5c4'),
    42: (42, '7a1593a90e15bcd2cff8423c8ca1fd64ce1008ec5f5412efcecc75f317d7a4b6'),
    43: (47, '01d2f25d90de9d50d4537821057c0ee930c42c6517f8c9de734873a4e5fe2463'),
    44: (10, '37102f42257c61e7d8fcda4b75d3f72c054cb2de3486bdfa4a5b2e61232ec9d0'),
    45: (22, '779738fae3661e4e7697fb9fe8dfca33f189041eebae41f53752e203f6e5fec3'),
    46: (12, '25a7498364e7de6cb59a36bf819444e1e2f364be9aab03525846d16ff4640938'),
    47: (12, '4cff5c7a6748d9e547e2335fbc0584994d998c3c90adc145b2f6943eea2eb7ec'),
    48: (4, '8435f62085b13ca7ba19d93725be2a9bc78c916393efa7ef58219af156a30212'),
    49: (34, 'dfc7180ce52d12ecafea50554bd7d8fe325e255f58e4c5348454ff9a63a9809b'),
    50: (10, 'b3629a5f36252a6b6a55755ce2d9acf945837700830c59835580d2857adb90a1'),
    51: (38, '0222db2bf1f5b390b4572c5f60249e07280fa3c9c969aa3d3397dcc103ba470a'),
    52: (35, 'd0cb190e0b459c3a16ea38165e1b6a031b5784696eb229a858709f2f82d806d3'),
    53: (34, '377dfa23abf1a58c8ce8d8e1643bf30858b46772c44fd5ad0100c29e9f59b023'),
    54: (41, '4c196f13890d33a02b1f5567a26b899eb30782c81a1509e59ee5bf31b4fab873'),
    55: (38, 'cc8981ca2e8811a92b015bbae27c580b08111e6236cdf9c7fff4255d99f40666'),
    56: (37, 'f50a88e7bb7f1dac3167555b5a90bb10c3a92962f8ba71580e33deaa5128a6ec'),
    57: (27, '2af4094ec51ead47512ff8c1750af4475d0915945ce9c55ba950db2009c8d112'),
    58: (25, 'b4ac756bc2d5ba0b307059cfff348d2cd37ad5ab0069f1d0bbc4e615a5fb9053'),
    59: (21, '5a3889cbe5d3808bb423f9a511335de9ce3bc3f6fc18c5490485312b8b29d162'),
    60: (41, 'd8059d6dc5dfa931082ddf18f484b85393dc9ec1975474b72ca429c8d53485fc'),
}
EXPECTED_COMPLETE_DIGEST = '1510b3db86a3234f71c03547663549982ca3dd00fe2bc795a4f2a82b9a1127c7'

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
mutated_digit = copy.deepcopy(questions)
mutated_digit[12]["ans"] = mutated_digit[12]["ans"].replace("2.111", "2.11")
assert numeric_signature(mutated_digit[12]) != EXPECTED_NUMERIC_SIGNATURES[13]
print("PASS answer, numeric, prose, structure and digit-drop mutation guards")


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
            match = re.search(r"/ch13sol(\d+)\.md$", uri)
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
    published = build.load(13)
    assert 13 in build.CONSTANTS and all(
        token in build.CONSTANTS[13]
        for token in ("931.5", "R<sub>0</sub>", "1.007825", "3.7 × 10¹⁰", "ln 2 = 0.693")
    ), "Chapter 13 के नियतांक शीर्ष में प्रकाशित नहीं"
    assert build.CHAPTERS[13] == ("नाभिक", "Nuclei")
    expected_names = {f"ch13sol{n}.md" for n in range(1, 61)}
    actual = {p.name for p in SOLUTIONS.glob("ch13sol*.md")}
    assert actual == expected_names, f"Chapter 13 समाधान set गलत: missing={expected_names-actual}, extra={actual-expected_names}"

    required_sections = ("## 📋 प्रश्न", "## 🧮 प्रयुक्त सूत्र", "## 🤔 यह सूत्र क्यों लगाया?",
                         "## ✍️ चरणबद्ध हल", "## ✅ उत्तर", "## 🎯 परीक्षा की ट्रिक",
                         "## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान")
    nav_count = 0
    all_local_links = 0
    for q in published:
        n = q["n"]
        path = SOLUTIONS / f"ch13sol{n}.md"
        text = path.read_text(encoding="utf-8")
        assert text == build.build_solution(q, 13), f"{path.name} audited source से byte-exact नहीं"
        assert all(section in text for section in required_sections), f"{path.name} section अधूरा"
        assert "�" not in text and not has_wrong_indic(text), f"{path.name} script/tofu text दोष"
        assert not raw_subscript.search(strip_code_fences(text)), f"{path.name} raw prose underscore"
        # prev/next navigation को स्पष्ट रूप से बाँधिए, केवल गिनती पर्याप्त नहीं।
        if n > 1:
            assert f"[⬅️ प्रश्न {n-1}](ch13sol{n-1}.md)" in text, f"{path.name} prev link गलत"
        else:
            assert "⬅️ *पहला प्रश्न*" in text and "ch13sol0.md" not in text
        if n < 60:
            assert f"[प्रश्न {n+1} ➡️](ch13sol{n+1}.md)" in text, f"{path.name} next link गलत"
        else:
            assert "*अन्तिम प्रश्न* ➡️" in text and "ch13sol61.md" not in text
        assert "[📑 सूची](README.md)" in text, f"{path.name} index link अनुपस्थित"
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
    # master index प्रत्येक निर्मित अध्याय के लिए 61 local links देता है (60 हल + 1 PDF)।
    # पहले यह गणना 13 अध्यायों पर स्थिर थी; अब निर्मित अध्यायों से व्युत्पन्न होती है।
    built_chapters = len(list(PRACTICE.glob("chapter*.pdf")))
    assert len(master_links) == 61 * built_chapters, \
        f"{built_chapters} अध्यायों के master local links {61 * built_chapters} चाहिए, मिले {len(master_links)}"
    assert "| 13 | नाभिक |" in master and "## अध्याय 13 — नाभिक" in master

    changed = build.build_solution(dict(published[0], ans=published[0]["ans"] + " बदला"), 13)
    assert changed != (SOLUTIONS / "ch13sol1.md").read_text(encoding="utf-8")
    print(f"PASS 60 byte-exact solutions; navigation={nav_count}; all local links checked={all_local_links}")

    import pymupdf
    pdf_path = PRACTICE / "chapter13.pdf"
    assert pdf_path.exists() and pdf_path.stat().st_size >= 300_000, "chapter13.pdf missing/बहुत छोटा"
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
        f"UP-Board-Class12-Physics/practice-sets/solutions/ch13sol{n}.md"
        for n in range(1, 61)
    }
    assert len(uris) == 60 and len(set(uris)) == 60, \
        f"PDF URI links unique 60 चाहिए, मिले {len(uris)}/{len(set(uris))}"
    assert set(uris) == expected_uris, "PDF links exact ch13sol1..60 HTTPS set नहीं"
    assert all(uri.startswith("https://") for uri in uris), "सभी PDF links HTTPS होने चाहिए"
    assert pdf_prompt_manifest_matches(doc, published), "PDF के 60 rendered prompts/topics audited source से bound नहीं"
    pdf_mutations = (
        (1, "1.2 fm", "12 fm"),          # removed decimal point
        (33, "238.050788", "238.05078"), # dropped a significant digit
        (53, "30%", "80%"),              # changed the physical dataset
    )
    for record_index, old, new in pdf_mutations:
        mutated_pdf_source = copy.deepcopy(published)
        assert old in mutated_pdf_source[record_index]["q"], \
            f"mutation probe का आधार Q{record_index + 1} में नहीं मिला: {old!r}"
        mutated_pdf_source[record_index]["q"] = mutated_pdf_source[record_index]["q"].replace(old, new, 1)
        assert not pdf_prompt_manifest_matches(doc, mutated_pdf_source), \
            f"PDF numeric mutation guard ने Q{record_index + 1} का {old!r}->{new!r} स्वीकार किया"
    joined_pdf_text = "\n".join(pdf_text)
    assert all(token in joined_pdf_text for token in ("अध्याय 13", "नाभिक", "60 प्रश्न"))
    assert "�" not in joined_pdf_text and "\x00" not in joined_pdf_text and not has_wrong_indic(joined_pdf_text)
    # पादलेख प्रत्येक पृष्ठ पर पूर्ण, एकल तथा नीचे की पट्टी में सीमित रहे। देवनागरी संयुक्ताक्षरों
    # का ToUnicode मानचित्र पादलेख में हानिपूर्ण है (अध्याय 9–12 में भी वही), अतः पाठ के स्थान पर
    # पृष्ठ-क्रमांक, हृदय-चिह्न तथा ज्यामिति बाँधी जाती है; दृश्य जाँच अलग से की जाती है।
    mm = 72 / 25.4
    for page_number in range(1, doc.page_count + 1):
        page = doc[page_number - 1]
        height, width = page.rect.height, page.rect.width
        band_top, band_bottom = height - 13 * mm, height - 3 * mm
        blocks = page.get_text("blocks")
        footers = [b for b in blocks if b[1] > band_top]
        assert len(footers) == 1, \
            f"पृष्ठ {page_number} पर पादलेख खण्ड {len(footers)} मिले, एक चाहिए"
        x0, y0, x1, y1, footer_text = footers[0][:5]
        assert f"{page_number} / {doc.page_count}" in footer_text, \
            f"पृष्ठ {page_number} का पादलेख क्रमांक दोषपूर्ण: {footer_text!r}"
        assert "13" in footer_text and "\u2764" in footer_text, \
            f"पृष्ठ {page_number} के पादलेख में अध्याय क्रमांक अथवा हृदय-चिह्न नहीं: {footer_text!r}"
        assert y1 <= band_bottom, f"पृष्ठ {page_number} का पादलेख पृष्ठ से बाहर जा रहा है"
        assert x0 >= 10 * mm and x1 <= width - 10 * mm, \
            f"पृष्ठ {page_number} का पादलेख पार्श्व हाशिये से बाहर है"
        body = [b for b in blocks if b[1] <= band_top]
        assert body, f"पृष्ठ {page_number} पर मुख्य सामग्री नहीं मिली"
        assert max(b[3] for b in body) < y0, \
            f"पृष्ठ {page_number} पर मुख्य सामग्री पादलेख से टकरा रही है"
    assert 8 <= doc.page_count <= 10, f"PDF पृष्ठ संख्या असामान्य: {doc.page_count}"
    assert doc.page_count == 9, f"अध्याय 13 का PDF 9 पृष्ठ का होना चाहिए, मिला {doc.page_count}"
    pages = doc.page_count
    doc.close()

    public_readme = (PRACTICE / "README.md").read_text(encoding="utf-8")
    expected_row = "| 13 | नाभिक | [chapter13.pdf](chapter13.pdf) ✅ | [60 हल](solutions/README.md) |"
    assert expected_row in public_readme, "Chapter 13 README row प्रकाशित नहीं"
    # पहले अध्याय 14 की पंक्ति placeholder रहनी आवश्यक थी; अब वह बन चुका है, अतः पंक्ति
    # या placeholder हो या अपना PDF link करती हो — दोनों में से ठीक एक रूप मान्य है।
    ch14_placeholder = "| 14 | अर्धचालक इलेक्ट्रॉनिकी | — | — |" in public_readme
    ch14_published = "| 14 | अर्धचालक इलेक्ट्रॉनिकी | [chapter14.pdf](chapter14.pdf) ✅ | [60 हल](solutions/README.md) |" in public_readme
    assert ch14_placeholder != ch14_published, "Chapter 14 की README पंक्ति का रूप अमान्य है"
    # पहले यह guard अध्याय 14 की अनुपस्थिति माँगता था (task-isolation)। सभी अध्याय पूर्ण
    # होने पर अब केवल आंशिक build पकड़ा जाता है।
    if (PRACTICE / "chapter14.pdf").exists() or any(SOLUTIONS.glob("ch14sol*.md")):
        assert (PRACTICE / "chapter14.pdf").exists(), "Chapter 14 समाधान बिना chapter14.pdf (आंशिक build)"
        assert not [n for n in range(1, 61) if not (SOLUTIONS / f"ch14sol{n}.md").exists()], \
            "Chapter 14 आंशिक रूप से बना है"
    # अध्याय 14 के स्रोत मॉड्यूल अब वैध रूप से उपस्थित हैं; यदि हों तो तीनों पूर्ण होने चाहिए।
    ch14_parts = sorted(p.name for p in ROOT.glob("ch14_part*.py"))
    if ch14_parts:
        assert ch14_parts == ["ch14_part1.py", "ch14_part2.py", "ch14_part3.py"], \
            f"Chapter 14 स्रोत मॉड्यूल अपूर्ण: {ch14_parts}"
    print(f"PASS PDF pages={pages}, bytes={pdf_path.stat().st_size}, exact unique HTTPS links=60")
    print("PASS 60 rendered PDF prompts/topics bound; decimal/digit/dataset mutations rejected")
    print("PASS footers, master index, README publication row, and sibling-build integrity")


if "--post-build" in sys.argv:
    verify_generated_artifacts()
