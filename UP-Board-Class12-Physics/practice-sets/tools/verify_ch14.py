# -*- coding: utf-8 -*-
"""अध्याय 14 — अर्धचालक इलेक्ट्रॉनिकी: fail-closed स्रोत तथा post-build सत्यापन।

पहले स्वतंत्र अर्धचालक सम्बन्धों से प्रत्येक प्रकाशित संख्यात्मक निष्कर्ष निकाला जाता है,
फिर सभी 60 उत्तरों, exact schema, pedagogical depth, source fingerprints और generated
Markdown/PDF artifacts को audited स्रोत से बाँधा जाता है।

यह अध्याय पाठ्यक्रम का अन्तिम अध्याय है, अतः 'अगला अध्याय अनुपस्थित रहे' जैसी कोई
एक-बार-की assertion यहाँ नहीं रखी जाती।
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
    raise RuntimeError("Chapter 14 verifier must run without Python -O")

EXPECTED_KEYS = {
    "n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"
}

# बोर्ड परिपाटी के नियतांक — यही मान प्रश्नपत्र के शीर्ष पर प्रकाशित हैं।
E = 1.602e-19          # इलेक्ट्रॉनिक आवेश, C तथा 1 eV का जूल मान
H = 6.626e-34          # प्लांक नियतांक, J·s
C = 3.00e8             # प्रकाश वेग, m/s
HC = H * C             # 1.9878e-25 J·m
NA = 6.022e23          # आवोगाद्रो संख्या, प्रति मोल
PI = 3.1416            # प्रश्नपत्र में प्रकाशित π
ROOT2 = 1.414          # प्रश्नपत्र में प्रकाशित √2
MAINS_HZ = 50.0        # भारतीय मेन्स आवृत्ति

# प्रकाशित परिपाटी स्वयं भी जाँची जाती है, अन्यथा सारी गणनाएँ चुपचाप खिसक जातीं।
assert math.isclose(PI, math.pi, rel_tol=1e-4), "π परिपाटी 3.1416 गलत है"
assert math.isclose(ROOT2, math.sqrt(2.0), rel_tol=1e-3), "√2 परिपाटी 1.414 गलत है"
assert math.isclose(HC, 1.9878e-25, rel_tol=1e-6), "hc = h·c संगत नहीं"
assert math.isclose(HC / E * 1e9, 1240.8, rel_tol=1e-3), \
       "hc का 1240 eV·nm रूप परिपाटी से मेल नहीं खाता"
assert math.isclose(E, 1.602e-19, rel_tol=1e-9), "1 eV = e × 1 V तुल्यता गलत है"

ROOT = Path(__file__).resolve().parent
PRACTICE = ROOT.parent
SOLUTIONS = PRACTICE / "solutions"

parts = []
for part_number in (1, 2, 3):
    module = importlib.import_module(f"ch14_part{part_number}")
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


# ---- स्वतंत्र अर्धचालक सम्बन्ध (किसी स्रोत पाठ से नहीं पढ़े जाते) ----

def ev_to_joule(energy_ev):
    return energy_ev * E


def joule_to_ev(energy_j):
    return energy_j / E


def photon_energy_j(wavelength_m):
    return HC / wavelength_m


def wavelength_from_gap(gap_ev):
    """Eg = hc/λ उलटकर λ; LED के उत्सर्जन तथा फोटोडायोड की सीमा दोनों यही देते हैं।"""
    return HC / ev_to_joule(gap_ev)


def gap_from_wavelength(wavelength_m):
    return joule_to_ev(photon_energy_j(wavelength_m))


def minority_density(intrinsic, majority):
    """द्रव्यमान-क्रिया नियम n_e·n_h = n_i²।"""
    return intrinsic ** 2 / majority


def conductivity(ne, mu_e, nh, mu_h):
    return E * (ne * mu_e + nh * mu_h)


def resistivity(sigma):
    return 1.0 / sigma


def resistance(rho, length_m, area_m2):
    return rho * length_m / area_m2


def atoms_from_mass(mass_g, molar_g):
    return mass_g / molar_g * NA


def half_wave_dc(peak):
    return peak / PI


def full_wave_dc(peak):
    return 2.0 * peak / PI


def peak_from_rms(rms):
    return rms * ROOT2


print("=== PART 1: प्रत्यक्ष सूत्र Q1–Q20 ===")
check(1, "Ge band gap 0.72 eV in joule", ev_to_joule(0.72), 1.153e-19)
check(2, "intrinsic silicon n_i squared (per m^6)", 1.5e16 ** 2, 2.25e32)
check(2, "same n_i expressed per cm^3", 1.5e16 / 1e6, 1.5e10)
check(3, "minority hole density in n-type silicon",
      minority_density(1.5e16, 5.0e22), 4.5e9)
check(4, "intrinsic germanium conductivity (S/m)",
      conductivity(2.4e19, 0.39, 2.4e19, 0.19), 2.230)
check(4, "electron share of germanium conductivity", E * 2.4e19 * 0.39, 1.500)
check(4, "hole share of germanium conductivity", E * 2.4e19 * 0.19, 0.730)
check(5, "resistivity from conductivity 2.5 S/m", resistivity(2.5), 0.40)
check(6, "germanium rod resistance (ohm)", resistance(0.45, 2.0e-2, 1.0e-6), 9.0e3)
check(6, "same rod via conductivity route", resistivity(0.45), 2.222)
check(7, "p-type silicon conductivity (S/m)", conductivity(0.0, 0.135, 4.5e22, 0.048), 346.0)
check(7, "minority electron density justifying the dropped term",
      minority_density(1.5e16, 4.5e22), 5.0e9)
check(7, "p-type silicon resistivity (ohm m)",
      resistivity(conductivity(0.0, 0.135, 4.5e22, 0.048)), 2.890e-3)
check(8, "donor density for 1 in 1e6 doping (per m^3)", 5.0e28 / 1e6, 5.0e22)
check(9, "atoms in 2.0 g of silicon", atoms_from_mass(2.0, 28.0), 4.301e22)
check(9, "atoms in 1.0 g of silicon", atoms_from_mass(1.0, 28.0), 2.151e22)
check(10, "static forward resistance at 0.70 V and 10 mA", 0.70 / 10e-3, 70.0)
check(11, "dynamic resistance for 0.06 V over 20 mA", 0.06 / 20e-3, 3.0)
check(11, "slope of the characteristic (siemens)", 20e-3 / 0.06, 0.3333)
check(12, "reverse resistance at 10 V and 2 microampere", 10.0 / 2e-6, 5.0e6)
check(13, "series diode circuit current (A)", (5.0 - 0.7) / 430.0, 0.01)
check(14, "half-wave dc output for 20 V peak", half_wave_dc(20.0), 6.366)
check(15, "full-wave dc output for 30 V peak", full_wave_dc(30.0), 19.10)
check(15, "half-wave value of the same 30 V peak", half_wave_dc(30.0), 9.549)
check(16, "half-wave ripple frequency from 50 Hz mains", MAINS_HZ, 50.0)
check(16, "full-wave ripple frequency from 50 Hz mains", 2 * MAINS_HZ, 100.0)
check(17, "LED wavelength for 1.9 eV gap (m)", wavelength_from_gap(1.9), 6.531e-7)
check(17, "LED emission frequency (Hz)", ev_to_joule(1.9) / H, 4.594e14)
check(18, "germanium photodiode cutoff wavelength (m)", wavelength_from_gap(0.72), 1.723e-6)
check(18, "silicon cutoff quoted for comparison (m)", wavelength_from_gap(1.1), 1.128e-6)
check(19, "photon energy at 500 nm (J)", photon_energy_j(500e-9), 3.976e-19)
check(19, "photon energy at 500 nm (eV)", gap_from_wavelength(500e-9), 2.482)
check(20, "zener series current (A)", (12.0 - 6.0) / 300.0, 0.02)

print("\n=== PART 2A: एक अज्ञात Q21–Q30 ===")
check(21, "intrinsic density from silicon conductivity (per m^3)",
      4.40e-4 / (E * 0.183), 1.50e16, rel_tol=1e-3)
check(22, "resistivity from resistance and geometry (ohm m)",
      2500.0 * 3.0e-6 / 1.5e-2, 0.50)
check(23, "majority hole density in p-type germanium",
      minority_density(2.4e19, 1.2e15), 4.80e23)
check(24, "doping ratio for 2.5e22 electrons per m^3", 5.0e28 / 2.5e22, 2.0e6)
check(25, "series resistance for 15 mA at 6.0 V (ohm)", (6.0 - 0.7) / 15e-3, 353.3)
check(26, "forward voltage rise for 20 mA at 2.5 ohm (V)", 2.5 * 20e-3, 0.050)
check(27, "band gap of a 560 nm LED (eV)", gap_from_wavelength(560e-9), 2.216)
check(28, "zener branch current (A)", (15.0 - 9.0) / 250.0 - 15e-3, 9.0e-3)
check(29, "peak input from 12.73 V full-wave dc output (V)",
      12.73 * PI / 2.0, 20.0, rel_tol=1e-3)
check(30, "supply frequency from 8.0 ms pulse spacing (Hz)", (1.0 / 8.0e-3) / 2.0, 62.5)

print("\n=== PART 2B: दो अज्ञात Q31–Q40 ===")
check(31, "minority holes in doped n-type silicon",
      minority_density(1.5e16, 2.0e22), 1.125e10)
check(31, "conductivity of that n-type silicon (S/m)",
      conductivity(2.0e22, 0.135, 0.0, 0.048), 432.5)
sigma32 = conductivity(2.4e19, 0.39, 2.4e19, 0.19)
check(32, "intrinsic germanium resistivity (ohm m)", resistivity(sigma32), 0.4484)
check(32, "resistance of that germanium bar (ohm)",
      resistance(resistivity(sigma32), 1.0e-2, 2.0e-6), 2242.0)
check(33, "average field in the depletion layer (V/m)", 0.70 / 5.0e-7, 1.4e6)
check(33, "barrier crossing energy (J)", ev_to_joule(0.70), 1.121e-19)
check(34, "static resistance at the 0.7 V operating point (ohm)", 0.7 / 25e-3, 28.0)
check(34, "dynamic resistance over 0.6 V to 0.7 V (ohm)",
      (0.7 - 0.6) / (25e-3 - 5e-3), 5.0)
check(35, "zener regulator series current (A)", (24.0 - 15.0) / 450.0, 0.02)
check(35, "zener current with a 1.0 kilo-ohm load (A)",
      (24.0 - 15.0) / 450.0 - 15.0 / 1000.0, 5.0e-3)
check(36, "peak of a 24 V rms half-wave input (V)", peak_from_rms(24.0), 33.94)
check(36, "half-wave dc output voltage (V)", half_wave_dc(peak_from_rms(24.0)), 10.80)
check(36, "half-wave dc load current (A)",
      half_wave_dc(peak_from_rms(24.0)) / 1200.0, 9.00e-3, rel_tol=1e-3)
check(37, "full-wave dc output for 40 V peak (V)", full_wave_dc(40.0), 25.46)
check(37, "full-wave dc load current (A)", full_wave_dc(40.0) / 2000.0, 12.73e-3)
check(37, "ripple frequency of that full-wave output (Hz)", 2 * MAINS_HZ, 100.0)
check(38, "wavelength emitted by a 2.5 eV LED (m)", wavelength_from_gap(2.5), 4.963e-7)
check(38, "frequency of that LED light (Hz)", C / wavelength_from_gap(2.5), 6.044e14)
check(39, "solar cell maximum power (W)", 0.48 * 0.125, 0.060)
check(39, "solar cell conversion efficiency", 0.48 * 0.125 / 0.30, 0.20)
check(40, "photon energy at 600 nm (J)", photon_energy_j(600e-9), 3.313e-19)
check(40, "photons arriving per second on the photodiode",
      1.5e-3 / photon_energy_j(600e-9), 4.528e15)

print("\n=== PART 3A: निगमन एवं अवधारणा Q41–Q50 ===")
truth(41, "band formation plus conductor/insulator/semiconductor gap classification",
      all(x in source_text(41) for x in ("ऊर्जा बैण्ड", "संयोजी बैण्ड", "चालन बैण्ड",
                                         "वर्जित ऊर्जा अन्तराल", "चालक", "कुचालक",
                                         "0.72 eV", "1.1 eV")))
check(41, "silicon gap in joule quoted in the classification", ev_to_joule(1.1), 1.762e-19)
truth(42, "intrinsic conduction, pair generation, temperature dependence, mass action",
      all(x in source_text(42) for x in ("निज अर्धचालक", "इलेक्ट्रॉन-होल युग्म",
                                         "nₑ = nₕ = nᵢ", "ताप", "0 K", "ऋणात्मक")))
check(42, "mass-action product quoted for silicon", 1.5e16 ** 2, 2.25e32)
truth(43, "doping, pentavalent/trivalent impurity, donor-acceptor levels, neutrality",
      all(x in source_text(43) for x in ("अपमिश्रण", "पंचसंयोजी", "त्रिसंयोजी",
                                         "n-टाइप", "p-टाइप", "दाता", "ग्राही",
                                         "बहुलांश", "अल्पांश", "वैद्युत उदासीन")))
check(43, "minority density of the worked doped example",
      minority_density(1.5e16, 5.0e22), 4.5e9)
truth(44, "junction formation with diffusion, drift, depletion layer and barrier",
      all(x in source_text(44) for x in ("विसरण", "अपवाह", "ह्रासी परत", "अवरोध विभव",
                                         "p-n संधि", "गतिक साम्य")))
check(44, "average barrier field quoted in the junction derivation (V/m)",
      0.70 / 5.0e-7, 1.4e6)
truth(45, "forward and reverse characteristics with knee, breakdown and resistances",
      all(x in source_text(45) for x in ("अग्र अभिनति", "पश्च अभिनति", "देहली",
                                         "भंजन", "स्थैतिक प्रतिरोध", "गतिक प्रतिरोध")))
check(45, "static resistance quoted on the characteristic (ohm)", 0.70 / 10e-3, 70.0)
check(45, "dynamic resistance quoted on the characteristic (ohm)", 0.06 / 20e-3, 3.0)
truth(46, "half-wave rectifier action, waveforms and ripple frequency",
      all(x in source_text(46) for x in ("अर्ध तरंग", "दिष्टकारी", "तरंगरूप",
                                         "Vdc = Vₘ/π", "तरंगिका", "50 Hz")))
check(46, "half-wave average derived in the answer", half_wave_dc(20.0), 6.366)
truth(47, "full-wave rectifier, centre-tap and bridge, double ripple frequency",
      all(x in source_text(47) for x in ("पूर्ण तरंग", "केन्द्र-नल", "सेतु",
                                         "2Vₘ/π", "100 Hz", "छानक")))
check(47, "full-wave average derived in the answer", full_wave_dc(30.0), 19.10)
truth(48, "zener breakdown characteristic and voltage regulator action",
      all(x in source_text(48) for x in ("जेनर", "भंजन", "नियंत्रक", "श्रेणी प्रतिरोध",
                                         "Is = Iz + IL", "पश्च अभिनति")))
check(48, "regulator series current of the worked example (A)", (12.0 - 6.0) / 300.0, 0.02)
truth(49, "LED structure, working, gap-wavelength condition and advantages",
      all(x in source_text(49) for x in ("प्रकाश उत्सर्जक डायोड", "पुनर्योजन",
                                         "λ = hc/Eg", "अग्र अभिनति", "दृश्य")))
check(49, "LED wavelength worked in the answer (m)", wavelength_from_gap(2.0), 6.204e-7)
truth(50, "photodiode and solar cell working with bias logic and cutoff",
      all(x in source_text(50) for x in ("फोटोडायोड", "सौर सेल", "पश्च अभिनति",
                                         "अभिनति नहीं", "चतुर्थांश", "hc/λ")))
check(50, "solar-cell useful cutoff wavelength for silicon (m)",
      wavelength_from_gap(1.1), 1.128e-6)

print("\n=== PART 3B: कठिन मिश्रित अनुप्रयोग Q51–Q60 ===")
nd51 = 5.0e28 / 1e7
sigma51 = conductivity(nd51, 0.135, minority_density(1.5e16, nd51), 0.048)
sigma51_intrinsic = conductivity(1.5e16, 0.135, 1.5e16, 0.048)
check(51, "donor density for 1 in 1e7 doping (per m^3)", nd51, 5.0e21)
check(51, "minority hole density after that doping", minority_density(1.5e16, nd51), 4.5e10)
check(51, "doped silicon conductivity (S/m)", sigma51, 108.1)
check(51, "intrinsic silicon conductivity (S/m)", sigma51_intrinsic, 4.397e-4)
check(51, "conductivity gain factor from doping", sigma51 / sigma51_intrinsic, 2.459e5)
sigma52 = conductivity(2.5e22, 0.135, 0.0, 0.048)
r52 = resistance(resistivity(sigma52), 2.0e-2, 4.0e-6)
check(52, "n-type rod conductivity (S/m)", sigma52, 540.7)
check(52, "n-type rod resistance (ohm)", r52, 9.248)
check(52, "current at 5.0 V across the rod (A)", 5.0 / r52, 0.5407)
check(52, "field inside the rod (V/m)", 5.0 / 2.0e-2, 250.0)
check(52, "electron drift speed (m/s)", 0.135 * (5.0 / 2.0e-2), 33.75)
i53 = (5.0 - 0.7) / (100.0 + 10.0)
check(53, "current with threshold and dynamic resistance (A)", i53, 0.03909)
check(53, "voltage across the diode (V)", 0.7 + i53 * 10.0, 1.091)
check(53, "voltage across the series resistor (V)", i53 * 100.0, 3.909)
check(53, "power dissipated in the diode (W)", (0.7 + i53 * 10.0) * i53, 0.04264)
check(53, "closure: both drops add to the supply (V)",
      (0.7 + i53 * 10.0) + i53 * 100.0, 5.0)
vm54 = peak_from_rms(18.0)
check(54, "bridge rectifier peak output (V)", vm54, 25.45)
check(54, "bridge rectifier dc output (V)", full_wave_dc(vm54), 16.20)
check(54, "bridge rectifier dc current (A)", full_wave_dc(vm54) / 900.0, 18.00e-3, rel_tol=1e-3)
check(55, "regulator series current for 20 mA load and 5 mA zener (A)",
      20e-3 + 5e-3, 0.025)
check(55, "regulator series resistance (ohm)", (15.0 - 9.0) / 25e-3, 240.0)
check(55, "zener current when the load is removed (A)", (15.0 - 9.0) / 240.0, 0.025)
check(55, "zener power in that worst case (W)", 9.0 * (15.0 - 9.0) / 240.0, 0.225)
check(56, "wavelength of a 2.0 eV LED (m)", wavelength_from_gap(2.0), 6.204e-7)
check(56, "energy of one emitted photon (J)", ev_to_joule(2.0), 3.204e-19)
check(56, "electrical power fed to the LED (W)", 2.0 * 20e-3, 0.040)
check(56, "optical power at 25 percent conversion (W)", 0.25 * 2.0 * 20e-3, 0.010)
check(56, "photons emitted per second",
      0.25 * 2.0 * 20e-3 / ev_to_joule(2.0), 3.121e16)
check(57, "maximum power of one solar cell (W)", 0.50 * 0.080, 0.040)
check(57, "cells needed in series for 12 V", 12.0 / 0.50, 24.0)
check(57, "total cells needed for 4.8 W", 4.8 / (0.50 * 0.080), 120.0)
check(57, "parallel strings required", (4.8 / (0.50 * 0.080)) / (12.0 / 0.50), 5.0)
check(58, "junction field at zero bias (V/m)", 0.72 / 4.0e-7, 1.8e6)
check(58, "effective barrier under 0.30 V forward bias (V)", 0.72 - 0.30, 0.42)
check(58, "junction field under that forward bias (V/m)", (0.72 - 0.30) / 4.0e-7, 1.05e6)
check(58, "effective barrier under 5.0 V reverse bias (V)", 0.72 + 5.0, 5.72)
n59 = atoms_from_mass(5.0, 28.0)
check(59, "silicon atoms in 5.0 g", n59, 1.075e23)
check(59, "donor atoms at 1 in 2.0e6", n59 / 2.0e6, 5.377e16)
check(59, "electron density in a 2.15 cm^3 sample (per m^3)", (n59 / 2.0e6) / 2.15e-6, 2.50e22,
      rel_tol=1e-3)
check(59, "atom density of that sample (per m^3)", n59 / 2.15e-6, 5.0e28, rel_tol=1e-3)
vdc60 = full_wave_dc(20.0)
check(60, "dc voltage feeding the regulator (V)", vdc60, 12.73)
check(60, "ripple frequency of that supply (Hz)", 2 * MAINS_HZ, 100.0)
check(60, "series current of the regulator (A)", (vdc60 - 6.0) / 220.0, 30.60e-3, rel_tol=1e-3)
check(60, "load current of the regulator (A)", 6.0 / 600.0, 10.00e-3)
check(60, "closure: zener current balances the node (A)",
      (vdc60 - 6.0) / 220.0 - 6.0 / 600.0, 20.60e-3, rel_tol=1e-3)

ANSWER_FRAGMENTS = {
 1:("1.153 × 10⁻¹⁹ J",), 2:("1.5 × 10¹⁶", "2.25 × 10³²"),
 3:("4.5 × 10⁹",), 4:("2.230 S/m",), 5:("0.40 Ω·m",),
 6:("9.0 × 10³ Ω",), 7:("346.0 S/m",), 8:("5.0 × 10²²",),
 9:("4.301 × 10²²",), 10:("70 Ω",), 11:("3.0 Ω",),
 12:("5.0 × 10⁶ Ω",), 13:("10 mA",), 14:("6.366 V",),
 15:("19.10 V",), 16:("50 Hz", "100 Hz"), 17:("653.1 nm",),
 18:("1723 nm",), 19:("2.482 eV",), 20:("20 mA",),
 21:("1.50 × 10¹⁶",), 22:("0.50 Ω·m",), 23:("4.80 × 10²³",),
 24:("2.0 × 10⁶",), 25:("353.3 Ω",), 26:("50 mV",),
 27:("2.216 eV",), 28:("9 mA",), 29:("20.0 V",), 30:("62.5 Hz",),
 31:("1.125 × 10¹⁰", "432.5 S/m"),
 32:("0.4484 Ω·m", "2.242 kΩ"),
 33:("1.4 × 10⁶ V/m", "1.121 × 10⁻¹⁹ J"),
 34:("28 Ω", "5.0 Ω"),
 35:("20 mA", "5.0 mA"),
 36:("10.80 V", "9.00 mA"),
 37:("12.73 mA", "100 Hz"),
 38:("496.3 nm", "6.044 × 10¹⁴ Hz"),
 39:("60 mW", "20%"),
 40:("3.313 × 10⁻¹⁹ J", "4.528 × 10¹⁵"),
 41:("वर्जित ऊर्जा अन्तराल", "कुचालक"),
 42:("nᵢ² = nₑnₕ", "ताप बढ़ने"),
 43:("n-टाइप", "p-टाइप", "वैद्युत उदासीन"),
 44:("ह्रासी परत", "अवरोध विभव"),
 45:("देहली वोल्टता", "भंजन"),
 46:("Vₘ/π", "50 Hz"),
 47:("2Vₘ/π", "100 Hz"),
 48:("जेनर", "नियंत्रक"),
 49:("λ = hc/Eg", "620.4 nm"),
 50:("फोटोडायोड", "सौर सेल"),
 51:("108.1 S/m", "2.459 × 10⁵"),
 52:("540.7 S/m", "33.75 m/s"),
 53:("39.09 mA", "42.64 mW"),
 54:("16.20 V", "18.00 mA"),
 55:("240 Ω", "225 mW"),
 56:("620.4 nm", "3.121 × 10¹⁶"),
 57:("0.040 W", "24 सेल", "5 समान्तर पंक्तियाँ"),
 58:("1.8 × 10⁶ V/m", "5.72 V"),
 59:("5.377 × 10¹⁶", "2.50 × 10²²"),
 60:("30.60 mA", "20.60 mA"),
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
    # '<' HTML में टैग खोल देता है; प्रश्न-पत्र सीधे HTML से बनता है, अतः वर्जित है।
    assert "<" not in source_text(q["n"]), f"Q{q['n']} कच्चा '<' वर्ण मिला"

OTHER_INDIC = [(0x0980, 0x09FF), (0x0A00, 0x0A7F), (0x0A80, 0x0AFF),
               (0x0B00, 0x0B7F), (0x0B80, 0x0BFF), (0x0C00, 0x0C7F),
               (0x0C80, 0x0CFF), (0x0D00, 0x0D7F)]
def has_wrong_indic(text):
    return any(lo <= ord(ch) <= hi for ch in text for lo, hi in OTHER_INDIC)
assert not any(has_wrong_indic(source_text(q["n"])) for q in questions), "wrong Indic script मिला"
assert all(not math.isclose(0.0, value, rel_tol=9e-4, abs_tol=0.0)
           for value in (4.5e9, 3.313e-19, 1.121e-19, 4.397e-4)), \
       "tiny nonzero targets को zero से अलग पहचानना आवश्यक है"

all_source = "\n".join(source_text(q["n"]) for q in questions)
# UPMSP 2026-27 का निकाला गया पाठ्यक्रम ट्रांजिस्टर तथा तर्क द्वार नहीं रखता, अतः
# इन विषयों का कोई भी चिह्न scope drift है और बिल्ड से पहले ही रोका जाता है।
for forbidden in ("ट्रांजिस्टर", "ट्रान्जिस्टर", "transistor", "संग्राहक", "उभयनिष्ठ",
                  "प्रवर्धक", "amplifier", "दोलित्र", "oscillator", "तर्क द्वार",
                  "logic gate", "लॉजिक", "गेट", "सत्यमान", "सत्य सारणी", "बूलीय",
                  "boolean", "धारा लाभ"):
    assert forbidden.lower() not in all_source.lower(), f"Chapter 14 scope drift मिला: {forbidden}"
for acronym in ("NAND", "NOR", "XOR"):
    assert acronym not in all_source, f"तर्क द्वार संकेत मिला: {acronym}"
# पिछले अध्यायों का विषय भी यहाँ नहीं घुसना चाहिए।
for stale in ("अर्ध-आयु", "रेडियोसक्रिय", "बन्धन ऊर्जा", "विखण्डन", "संलयन",
              "बोर मॉडल", "फोटोवैद्युत"):
    assert stale.lower() not in all_source.lower(), f"पिछले अध्याय का विषय मिला: {stale}"
assert all(x in all_source for x in ("ऊर्जा बैण्ड", "संयोजी बैण्ड", "चालन बैण्ड",
                                     "वर्जित ऊर्जा अन्तराल", "कुचालक", "निज अर्धचालक",
                                     "इलेक्ट्रॉन-होल युग्म", "अपमिश्रण", "पंचसंयोजी",
                                     "त्रिसंयोजी", "n-टाइप", "p-टाइप", "दाता", "ग्राही",
                                     "बहुलांश", "अल्पांश", "वैद्युत उदासीन", "p-n संधि",
                                     "विसरण", "अपवाह", "ह्रासी परत", "अवरोध विभव",
                                     "अग्र अभिनति", "पश्च अभिनति", "देहली", "भंजन",
                                     "स्थैतिक प्रतिरोध", "गतिक प्रतिरोध", "दिष्टकारी",
                                     "अर्ध तरंग", "पूर्ण तरंग", "सेतु", "तरंगिका",
                                     "जेनर", "नियंत्रक", "प्रकाश उत्सर्जक डायोड",
                                     "फोटोडायोड", "सौर सेल", "गतिशीलता", "चालकता")), \
       "अध्याय 14 का कोई अनिवार्य उपविषय छूट गया"
assert "0.72 eV" in source_text(1) and "0.72 eV" in source_text(18), \
       "जर्मेनियम का अन्तराल मात्रक-परिवर्तन तथा फोटोडायोड दोनों में संगत रहे"
assert "1.5 × 10¹⁶" in source_text(2) and "1.50 × 10¹⁶" in source_text(21), \
       "nᵢ सम्बन्ध forward तथा inverse दोनों दिशाओं में रहे"
assert "4.5 × 10⁹" in source_text(3) and "5.0 × 10⁹" in source_text(7), \
       "अल्पांश वाहक के दोनों datasets भिन्न रहें"
assert "653.1 nm" in source_text(17) and "560 nm" in source_text(27), \
       "LED के forward तथा inverse datasets भिन्न रहें"
assert "430 Ω" in source_text(13) and "353.3 Ω" in source_text(25), \
       "डायोड परिपथ के forward तथा inverse datasets भिन्न रहें"
assert "8.0 ms" in source_text(30) and "तरंगिका" in source_text(30), \
       "Q30 तरंगिका आवृत्ति का inverse प्रश्न रहना चाहिए"
assert "सेतु" in source_text(54) and "18 V" in source_text(54), \
       "Q54 सेतु दिष्टकारी अनुप्रयोग रहना चाहिए"
assert "सौर सेल" in source_text(57) and "श्रेणीक्रम" in source_text(57), \
       "Q57 सौर सेल सरणी अनुप्रयोग रहना चाहिए"
assert "अपवाह वेग" in source_text(52) and "गतिशीलता" in source_text(52), \
       "Q52 में अपवाह वेग तथा गतिशीलता का सम्बन्ध रहे"
assert "2.15 cm³" in source_text(59) and "5.0 g" in source_text(59), \
       "Q59 आवोगाद्रो अनुप्रयोग रहना चाहिए"
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
    1: (24, '54be3255e6f097d3ec7258808f0aeae00fa903966f2fa129d7ad4031e4808a44'),
    2: (18, 'c468a00937f59c88fa3d97a7429ac90d1491b5660913e11e13bbc7a6806b3477'),
    3: (22, 'fbff76ad4654868d38036e1c175dec473ba70a6423820a7f65530c39f183a1eb'),
    4: (21, '3aba484f11fc32b17fb150f193f1d218fc81586c80caf3883914fe8b5fa973f3'),
    5: (15, 'd94dffcbb1fd3eee9bf3402031bb8218d2f0da0ae5f97a52aa1ee728e864671a'),
    6: (36, '1e720b8dd2bb3e11b13badfdc4f8be578679724b53e0410dc3eeb2fe65b51040'),
    7: (21, 'ceeffd0aa6af45578358b2ed9e85b6dd7cff71035085ff90cc63a813eafc6348'),
    8: (22, '338b19f64a03c2ddce877e612d7aa10a5a6288f365598e0c2ba4744a374c102c'),
    9: (25, 'a4e3fe7cb41ee1af54fae4a5db85698aa01c7f880da01c2e0746b56f3b43bbc6'),
    10: (18, 'a023d76ac912b9d426017754ec913b9f41c1ad1b103905c219c178fb562ee152'),
    11: (22, '30d85618100d70d68ad704d65e52965d825d0950e375ccf7d70a48e4eb716dcc'),
    12: (22, '66f6028f803a53f23f3ce0b9cfff3945675a1e27cc404b20fb148fa4f883a3aa'),
    13: (27, 'd1bd066086152a75eb65dc87811fcdd960397fc808165c0a808fa48df1a901b2'),
    14: (24, '24f81964883f716ec61f50752b80afe032f9f39f34397871528115ed71eb327f'),
    15: (23, '8e0741fa3a37ef269ce4fe13b1bfc98a12e4a9ffc557db28ee3892a711af8a9a'),
    16: (16, 'b0b0fe3a6cbb5163fd8d8be9964f629541b13f2e7e063a997ba56bf4e367fa0b'),
    17: (21, '5950edb738c6029a0432c7d49e59c19ed9a546b28cd53b0f60b5c9247fcfab58'),
    18: (16, '4e1c7b1534353223bd3dc81108231f139e52866746844e6b1231932734143bcc'),
    19: (24, '0cca21f2669aca0d336d33babdcaebf666aae87375dd74851653a661c09d5907'),
    20: (23, 'f6567a1fe2e87834e67c9e7948f7fa028022250c23ee674c9d11df50b8824fb3'),
    21: (18, '253b02ec57ff63580b5fe7b8b93b4ea03d41786283b54af08815941acb6d8016'),
    22: (25, '095715c75e007e444810d75327c817b597c6f77195fece0d5ad098cecf4e12fc'),
    23: (20, '35f6124f665c2ec82804e50d7e26a7d12efa1ca5d14e2a1caec4ae2927d2a3bd'),
    24: (20, '74135d8f51469de6cc8527af916c8fece543f05045042609914f1bd3986d691a'),
    25: (24, 'a768f7626f6f20d34d22cd9a448a5f07f6a3a2fa7934ae9a1709819e362b301a'),
    26: (20, '221f96e1fb280f8f7051a16db1f78bdb4a0d464cb045a817071bca5f85b6e468'),
    27: (27, '2b44d516f54d8f7716b48e9776ee0a7eb6daab68e56e530cd4e30476f1b67630'),
    28: (31, 'd9407f8095832c1a0fce70855fd9c46ccf5eecd2e74d1ac6605b56aec35e551d'),
    29: (38, '4cbabe5065f658d0827e65a45dddb65acce11fa3c6bd1a63a5479f8685005b3b'),
    30: (24, '803c6d96837a2bd60d3420b325359737796a84e99a74366a94ace1f45993bb4e'),
    31: (24, '83b7b2f586a0379696fe91e827ef868e2d08b2e7290d549819f07a097aafcc9c'),
    32: (36, '1c171a28d6ac8971c0aa1ed6b320e6aff6971a42b66cf4a325ab629ef2fabfc9'),
    33: (22, '984911420201e04b2a1bbfd5bafc76416140cddd09639cd045e6afd1ce247942'),
    34: (31, '5a4e98b830521cdb181b117872c476c323d767128ee2a587dbed2f9cafcf005a'),
    35: (35, 'a89c64d6878d71bd914006cd0c9bd44c0708ddf80eb534e4106350e100e97582'),
    36: (37, '2940fec320d4ff8fef8bb3405456f4f16533375e8fbcbe96285b968f1c96b51d'),
    37: (40, '7900e4288ef716782310ed9773c6757aabda12eb8325c722f5a6030c6b6362ce'),
    38: (24, '1b9dbcc7f48946a0a28e64e6e13c6ba6fce1014079a5cfec4e6cc5e85818aae1'),
    39: (26, 'f0d240652a611b6741a983c22f1bac1023a623d885f737b03767509cec4bf09b'),
    40: (26, '137be4af7ae76a4524e5a91c5492e14bba926d377bb64ea58a355d37cd3d507a'),
    41: (25, 'db16a0d7b04da17a816722bc957c20298b8b63831298863ac6f06cc080482f11'),
    42: (11, 'dfb602ce98621c8c731ca9828859146842c97262173bcb7747bbcbae67a2cc8a'),
    43: (9, '1cbcc889f713c622953f4981b158bad50f617c399b39eb314b89a50e503dc62e'),
    44: (14, '70edbea6e911dc06d9570a4ad844ad2d4f534846a6d52c0985d939ec8d6dec59'),
    45: (25, '1812bb7ce3d407d35644c43c04879400b81480c27bdf7c74c17ae9b73f06769c'),
    46: (31, '799ec08865942b4c4fee0745da2746f7a646ccab2025564c3a3a3a36d4f0b974'),
    47: (33, '23c937fa655ce784294fc1ab2873d567233362e851e72287e3bfa30123efeb55'),
    48: (20, 'd5595e0f663bd2d53742e778a3f3a877b6462db200dfd378de7ae7c66034598c'),
    49: (31, 'd1b22b2c045c0ccbbdcf6ca8e21f3ed0b77cfbe69b810922b487da42cc33e374'),
    50: (15, '475fcd18ebc8e7a955b449ad4c1621bd9f23f9509770e0eabac98f1bddb4f285'),
    51: (40, '7e9469ec7f5cbf45413b177db4002dbb89a3371905dda9800d6276d0bf5ee155'),
    52: (44, '908dd03e4536a804806ef713dbfe08719233a2c6dbb725853b271a3482bb67cd'),
    53: (46, '20b10663c34e9cbec163c6d69766b11219fd5e32f59a10b4058359a49e10b5da'),
    54: (48, 'd1da99d70d7ab9a7119a92b3d20223fa43a8529521b88f611d8ce0b4605caa01'),
    55: (40, 'f433746b81cee72324df95320cf0aa03568dc3dd502a80f59e4f77cd7d2276ea'),
    56: (38, 'e5044ea36de8bd418ef6298ec1c6cd216a5c16b4e96beb66983dff205e29bb1c'),
    57: (46, 'a6f12c933f7837f65cda8dcd7c479ca83a1cdf0b26e877097298146e367559a2'),
    58: (28, '82f2a51d935e3ecaa16b8fa9d187e6f2e51fb7aed6eedacec9389d0e60b0f8d6'),
    59: (33, 'fea8036277cb4969e123a83c70ff21766bee1f75ec569a3421004087e68b0549'),
    60: (61, '71e84f54569d99c3906bf38727244d787cb1559c847b210bd82ff782c66f701f'),
}
EXPECTED_COMPLETE_DIGEST = '08b6d9274e101b1a5b795adbfccc8303ac87bfbc87850a70289d6428dbd89cd9'

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
mutated_digit[16]["ans"] = mutated_digit[16]["ans"].replace("653.1", "653")
assert numeric_signature(mutated_digit[16]) != EXPECTED_NUMERIC_SIGNATURES[17]
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
            match = re.search(r"/ch14sol(\d+)\.md$", uri)
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
    published = build.load(14)
    assert 14 in build.CONSTANTS and all(
        token in build.CONSTANTS[14]
        for token in ("1.602 × 10⁻¹⁹", "6.626 × 10⁻³⁴", "1240 eV·nm",
                      "N<sub>A</sub>", "3.1416", "0.72 eV")
    ), "Chapter 14 के नियतांक शीर्ष में प्रकाशित नहीं"
    assert build.CHAPTERS[14] == ("अर्धचालक इलेक्ट्रॉनिकी", "Semiconductor Electronics")
    expected_names = {f"ch14sol{n}.md" for n in range(1, 61)}
    actual = {p.name for p in SOLUTIONS.glob("ch14sol*.md")}
    assert actual == expected_names, f"Chapter 14 समाधान set गलत: missing={expected_names-actual}, extra={actual-expected_names}"

    required_sections = ("## 📋 प्रश्न", "## 🧮 प्रयुक्त सूत्र", "## 🤔 यह सूत्र क्यों लगाया?",
                         "## ✍️ चरणबद्ध हल", "## ✅ उत्तर", "## 🎯 परीक्षा की ट्रिक",
                         "## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान")
    nav_count = 0
    all_local_links = 0
    for q in published:
        n = q["n"]
        path = SOLUTIONS / f"ch14sol{n}.md"
        text = path.read_text(encoding="utf-8")
        assert text == build.build_solution(q, 14), f"{path.name} audited source से byte-exact नहीं"
        assert all(section in text for section in required_sections), f"{path.name} section अधूरा"
        assert "�" not in text and not has_wrong_indic(text), f"{path.name} script/tofu text दोष"
        assert not raw_subscript.search(strip_code_fences(text)), f"{path.name} raw prose underscore"
        # prev/next navigation को स्पष्ट रूप से बाँधिए, केवल गिनती पर्याप्त नहीं।
        if n > 1:
            assert f"[⬅️ प्रश्न {n-1}](ch14sol{n-1}.md)" in text, f"{path.name} prev link गलत"
        else:
            assert "⬅️ *पहला प्रश्न*" in text and "ch14sol0.md" not in text
        if n < 60:
            assert f"[प्रश्न {n+1} ➡️](ch14sol{n+1}.md)" in text, f"{path.name} next link गलत"
        else:
            assert "*अन्तिम प्रश्न* ➡️" in text and "ch14sol61.md" not in text
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
    assert len(master_links) == 854, f"14 अध्यायों के master local links 854 चाहिए, मिले {len(master_links)}"
    assert "| 14 | अर्धचालक इलेक्ट्रॉनिकी |" in master
    assert "## अध्याय 14 — अर्धचालक इलेक्ट्रॉनिकी" in master
    assert "— आना शेष" not in master, "मास्टर सूची में कोई अध्याय शेष नहीं रहना चाहिए"

    changed = build.build_solution(dict(published[0], ans=published[0]["ans"] + " बदला"), 14)
    assert changed != (SOLUTIONS / "ch14sol1.md").read_text(encoding="utf-8")
    print(f"PASS 60 byte-exact solutions; navigation={nav_count}; all local links checked={all_local_links}")

    import pymupdf
    pdf_path = PRACTICE / "chapter14.pdf"
    assert pdf_path.exists() and pdf_path.stat().st_size >= 300_000, "chapter14.pdf missing/बहुत छोटा"
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
        f"UP-Board-Class12-Physics/practice-sets/solutions/ch14sol{n}.md"
        for n in range(1, 61)
    }
    assert len(uris) == 60 and len(set(uris)) == 60, \
        f"PDF URI links unique 60 चाहिए, मिले {len(uris)}/{len(set(uris))}"
    assert set(uris) == expected_uris, "PDF links exact ch14sol1..60 HTTPS set नहीं"
    assert all(uri.startswith("https://") for uri in uris), "सभी PDF links HTTPS होने चाहिए"
    assert pdf_prompt_manifest_matches(doc, published), "PDF के 60 rendered prompts/topics audited source से bound नहीं"
    pdf_mutations = (
        (1, "1.5 × 10¹⁶", "15 × 10¹⁶"),   # removed decimal point
        (32, "5.0 × 10⁻⁷", "5.0 × 10⁻⁶"), # shifted a significant exponent
        (53, "18 V", "80 V"),             # changed the physical dataset
    )
    for record_index, old, new in pdf_mutations:
        mutated_pdf_source = copy.deepcopy(published)
        assert old in mutated_pdf_source[record_index]["q"], \
            f"mutation probe का आधार Q{record_index + 1} में नहीं मिला: {old!r}"
        mutated_pdf_source[record_index]["q"] = mutated_pdf_source[record_index]["q"].replace(old, new, 1)
        assert not pdf_prompt_manifest_matches(doc, mutated_pdf_source), \
            f"PDF numeric mutation guard ने Q{record_index + 1} का {old!r}->{new!r} स्वीकार किया"
    joined_pdf_text = "\n".join(pdf_text)
    assert all(token in joined_pdf_text for token in ("अध्याय 14", "60 प्रश्न"))
    assert "�" not in joined_pdf_text and "\x00" not in joined_pdf_text and not has_wrong_indic(joined_pdf_text)
    # पादलेख प्रत्येक पृष्ठ पर पूर्ण, एकल तथा नीचे की पट्टी में सीमित रहे। देवनागरी संयुक्ताक्षरों
    # का ToUnicode मानचित्र पादलेख में हानिपूर्ण है (अध्याय 9–13 में भी वही), अतः पाठ के स्थान पर
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
        assert "14" in footer_text and "\u2764" in footer_text, \
            f"पृष्ठ {page_number} के पादलेख में अध्याय क्रमांक अथवा हृदय-चिह्न नहीं: {footer_text!r}"
        assert y1 <= band_bottom, f"पृष्ठ {page_number} का पादलेख पृष्ठ से बाहर जा रहा है"
        assert x0 >= 10 * mm and x1 <= width - 10 * mm, \
            f"पृष्ठ {page_number} का पादलेख पार्श्व हाशिये से बाहर है"
        body = [b for b in blocks if b[1] <= band_top]
        assert body, f"पृष्ठ {page_number} पर मुख्य सामग्री नहीं मिली"
        assert max(b[3] for b in body) < y0, \
            f"पृष्ठ {page_number} पर मुख्य सामग्री पादलेख से टकरा रही है"
    assert 8 <= doc.page_count <= 10, f"PDF पृष्ठ संख्या असामान्य: {doc.page_count}"
    assert doc.page_count == EXPECTED_PDF_PAGES, \
        f"अध्याय 14 का PDF {EXPECTED_PDF_PAGES} पृष्ठ का होना चाहिए, मिला {doc.page_count}"
    pages = doc.page_count
    doc.close()

    public_readme = (PRACTICE / "README.md").read_text(encoding="utf-8")
    expected_row = ("| 14 | अर्धचालक इलेक्ट्रॉनिकी | [chapter14.pdf](chapter14.pdf) ✅ "
                    "| [60 हल](solutions/README.md) |")
    assert expected_row in public_readme, "Chapter 14 README row प्रकाशित नहीं"
    assert "| 13 | नाभिक | [chapter13.pdf](chapter13.pdf) ✅ | [60 हल](solutions/README.md) |" \
           in public_readme, "Chapter 13 की पंक्ति अछूती रहनी चाहिए"
    assert "| 14 | अर्धचालक इलेक्ट्रॉनिकी | — | — |" not in public_readme, \
           "Chapter 14 की पुरानी रिक्त पंक्ति हटनी चाहिए"
    readme_links = list(local_markdown_links(PRACTICE / "README.md", public_readme))
    for target in readme_links:
        assert target.exists(), f"README का टूटा link: {target}"
    print(f"PASS PDF pages={pages}, bytes={pdf_path.stat().st_size}, exact unique HTTPS links=60")
    print("PASS 60 rendered PDF prompts/topics bound; decimal/exponent/dataset mutations rejected")
    print(f"PASS footers, master index, README publication row, README links={len(readme_links)}")


EXPECTED_PDF_PAGES = 9

if "--post-build" in sys.argv:
    verify_generated_artifacts()
