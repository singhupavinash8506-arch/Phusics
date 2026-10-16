# -*- coding: utf-8 -*-
"""अध्याय 7 — प्रत्यावर्ती धारा।

प्रश्न 1–60 में प्रयुक्त प्रत्येक संख्यात्मक परिणाम को प्रश्न-स्रोत से स्वतन्त्र
रूप से मूल AC सम्बन्धों द्वारा पुनः गणना करता है। किसी भी असंगति पर यह स्क्रिप्ट
AssertionError के साथ non-zero exit करती है।
"""

import math


checks = []
covered_questions = set()


def check(qno, label, got, expected, rel_tol=5e-4, abs_tol=5e-7):
    """एक प्रदर्शित मान की स्वतंत्र गणना जाँचें और प्रश्न-कवरेज दर्ज करें।"""
    passed = math.isclose(got, expected, rel_tol=rel_tol, abs_tol=abs_tol)
    checks.append((qno, label, passed, got, expected))
    covered_questions.add(qno)
    status = "PASS" if passed else "FAIL"
    print(f"{status} Q{qno:02d} {label:<43} got={got:.10g} expected={expected:.10g}")


def mean_over_cycle(fn, samples=200_000):
    """मध्य-बिन्दु योग से एक 2π चक्र का स्वतंत्र संख्यात्मक औसत।"""
    return sum(fn((i + 0.5) * 2 * math.pi / samples) for i in range(samples)) / samples


pi = math.pi

print("=== PART 1: प्रत्यक्ष सूत्र (Q1–Q20) ===")
# Q1: v = V_m sin(2πft), V_m=200 V, f=50 Hz, t=1/600 s
phase1 = 2 * pi * 50 * (1 / 600)
check(1, "phase 2πft (rad)", phase1, pi / 6)
check(1, "instantaneous voltage (V)", 200 * math.sin(phase1), 100.0)

# Q2: ω=100π rad/s
f2 = (100 * pi) / (2 * pi)
check(2, "frequency from angular frequency (Hz)", f2, 50.0)
check(2, "period (s)", 1 / f2, 0.020)

# Q3: half-cycle mean for V_m=311 V
check(3, "half-cycle mean voltage (V)", 2 * 311 / pi, 197.99, rel_tol=8e-5)
check(3, "full-cycle mean voltage (V)", 0.0, 0.0)

# Q4: RMS for V_m=325 V
check(4, "RMS voltage (V)", 325 / math.sqrt(2), 229.81, rel_tol=3e-5)

# Q5: peak current for I_rms=5 A
check(5, "peak current (A)", 5 * math.sqrt(2), 7.071, rel_tol=2e-5)

# Q6: pure R, 220 V across 44 Ω
check(6, "resistive current (A)", 220 / 44, 5.0)
check(6, "phase difference (degree)", 0.0, 0.0)

# Q7: X_L for f=50 Hz, L=0.20 H
check(7, "inductive reactance (ohm)", 2 * pi * 50 * 0.20, 62.83, rel_tol=4e-5)

# Q8: pure L, V=220 V, f=50 Hz, L=0.70 H
xl8 = 2 * pi * 50 * 0.70
check(8, "inductive reactance (ohm)", xl8, 219.91, rel_tol=2e-5)
check(8, "inductive current (A)", 220 / xl8, 1.0004, rel_tol=6e-5)

# Q9: X_C for f=50 Hz, C=100 μF
xc9 = 1 / (2 * pi * 50 * 100e-6)
check(9, "capacitive reactance (ohm)", xc9, 31.83, rel_tol=5e-5)

# Q10: pure C, V=220 V, f=50 Hz, C=50 μF
xc10 = 1 / (2 * pi * 50 * 50e-6)
check(10, "capacitive reactance (ohm)", xc10, 63.66, rel_tol=4e-5)
check(10, "capacitive current (A)", 220 / xc10, 3.456, rel_tol=8e-5)

# Q11: series LCR, R=30 Ω, X_L=50 Ω, X_C=10 Ω
x11 = 50 - 10
check(11, "net reactance (ohm)", x11, 40.0)
check(11, "impedance (ohm)", math.hypot(30, x11), 50.0)

# Q12: V_rms=200 V, Z=50 Ω
check(12, "series current (A)", 200 / 50, 4.0)

# Q13: R=40 Ω, X_L=70 Ω, X_C=40 Ω
ratio13 = (70 - 40) / 40
check(13, "tan phase angle", ratio13, 0.75)
check(13, "lagging phase angle (degree)", math.degrees(math.atan(ratio13)), 36.87, rel_tol=2e-5)

# Q14: R=60 Ω, net reactance=80 Ω
z14 = math.hypot(60, 80)
check(14, "impedance (ohm)", z14, 100.0)
check(14, "power factor", 60 / z14, 0.60)

# Q15: V=220 V, I=5 A, cosφ=0.8
check(15, "apparent power (VA)", 220 * 5, 1100.0)
check(15, "real power (W)", 220 * 5 * 0.8, 880.0)

# Q16: resonance for L=0.20 H, C=50 μF
omega16 = 1 / math.sqrt(0.20 * 50e-6)
check(16, "resonant angular frequency (rad/s)", omega16, 316.23, rel_tol=2e-5)
check(16, "resonant frequency (Hz)", omega16 / (2 * pi), 50.33, rel_tol=2e-5)

# Q17: resonance current, V=200 V, R=40 Ω
check(17, "maximum current at resonance (A)", 200 / 40, 5.0)

# Q18: X_L ∝ f, from 40 Ω at 50 Hz to 100 Hz
frequency_ratio18 = 100 / 50
check(18, "frequency ratio", frequency_ratio18, 2.0)
check(18, "new inductive reactance (ohm)", 40 * frequency_ratio18, 80.0)

# Q19: X_C ∝ 1/f, from 60 Ω at 50 Hz to 150 Hz
frequency_ratio19 = 150 / 50
check(19, "frequency ratio", frequency_ratio19, 3.0)
check(19, "new capacitive reactance (ohm)", 60 / frequency_ratio19, 20.0)

# Q20: ideal transformer 220 V, N_p=1000, N_s=100
check(20, "turns ratio N_s/N_p", 100 / 1000, 0.10)
check(20, "secondary voltage (V)", 220 * 100 / 1000, 22.0)

print("\n=== PART 2A: एक अज्ञात (Q21–Q30) ===")
# Q21: V_m from v=100 V at 30°
check(21, "peak voltage (V)", 100 / math.sin(math.radians(30)), 200.0)

# Q22: frequency from ω=100π
check(22, "frequency (Hz)", (100 * pi) / (2 * pi), 50.0)

# Q23: resistance from 220 V, 5 A
check(23, "resistance (ohm)", 220 / 5, 44.0)

# Q24: inductance from X_L=62.8 Ω at 50 Hz
check(24, "inductance (H)", 62.8 / (2 * pi * 50), 0.1999, rel_tol=8e-5)

# Q25: capacitance from X_C=31.8 Ω at 50 Hz
c25 = 1 / (2 * pi * 50 * 31.8)
check(25, "capacitance (microfarad)", c25 * 1e6, 100.10, rel_tol=3e-5)

# Q26: net reactance from Z=50 Ω, R=30 Ω (inductive circuit)
check(26, "net inductive reactance (ohm)", math.sqrt(50**2 - 30**2), 40.0)

# Q27: power factor from P=660 W, V=220 V, I=5 A
check(27, "power factor", 660 / (220 * 5), 0.60)

# Q28: C for resonance with L=0.10 H at f_0=50 Hz
c28 = 1 / ((2 * pi * 50) ** 2 * 0.10)
check(28, "resonant capacitance (microfarad)", c28 * 1e6, 101.32, rel_tol=2e-5)

# Q29: secondary turns, 220:11 V and N_p=1000
check(29, "voltage ratio V_s/V_p", 11 / 220, 0.050)
check(29, "secondary turns", 1000 * 11 / 220, 50.0)

# Q30: efficiency from 500 W input, 450 W output
check(30, "transformer efficiency fraction", 450 / 500, 0.90)
check(30, "transformer efficiency percent", 100 * 450 / 500, 90.0)

print("\n=== PART 2B: दो अज्ञात (Q31–Q40) ===")
# Q31: V_m=311 V, f=50 Hz, t=1/600 s
omega31 = 2 * pi * 50
phase31 = omega31 / 600
check(31, "angular frequency (rad/s)", omega31, 314.16, rel_tol=4e-6)
check(31, "phase at stated time (rad)", phase31, pi / 6)
check(31, "instantaneous voltage (V)", 311 * math.sin(phase31), 155.5)

# Q32: pure L, V=220 V, f=50 Hz, L=0.14 H
xl32 = 2 * pi * 50 * 0.14
check(32, "inductive reactance (ohm)", xl32, 43.98, rel_tol=6e-5)
check(32, "current (A)", 220 / xl32, 5.002, rel_tol=8e-5)

# Q33: pure C, V=220 V, f=50 Hz, C=72 μF
xc33 = 1 / (2 * pi * 50 * 72e-6)
check(33, "capacitive reactance (ohm)", xc33, 44.21, rel_tol=3e-5)
check(33, "current (A)", 220 / xc33, 4.976, rel_tol=6e-5)

# Q34/Q35: same series LCR data, V=220 V, f=50 Hz, R=30 Ω, L=.2 H, C=100 μF
xl34 = 2 * pi * 50 * 0.20
xc34 = 1 / (2 * pi * 50 * 100e-6)
x34 = xl34 - xc34
z34 = math.hypot(30, x34)
i34 = 220 / z34
check(34, "X_L (ohm)", xl34, 62.83, rel_tol=4e-5)
check(34, "X_C (ohm)", xc34, 31.83, rel_tol=5e-5)
check(34, "net reactance (ohm)", x34, 31.00, rel_tol=4e-5)
check(34, "impedance (ohm)", z34, 43.14, rel_tol=3e-5)
check(34, "current (A)", i34, 5.10, rel_tol=5e-4)
check(35, "tan phase angle", x34 / 30, 1.0334, rel_tol=5e-5)
check(35, "phase angle (degree)", math.degrees(math.atan2(x34, 30)), 45.94, rel_tol=2e-4)
check(35, "power factor", 30 / z34, 0.6954, rel_tol=5e-5)

# Q36: R=30 Ω, X_L=50 Ω, X_C=10 Ω, V=200 V
z36 = math.hypot(30, 50 - 10)
i36 = 200 / z36
check(36, "impedance (ohm)", z36, 50.0)
check(36, "current (A)", i36, 4.0)
check(36, "real power (W)", i36**2 * 30, 480.0)
check(36, "inductor RMS voltage (V)", i36 * 50, 200.0)

# Q37: resonance, L=.2 H, C=50 μF, R=20 Ω, V=100 V
omega37 = 1 / math.sqrt(0.20 * 50e-6)
check(37, "resonant angular frequency (rad/s)", omega37, 316.23, rel_tol=2e-5)
check(37, "resonant frequency (Hz)", omega37 / (2 * pi), 50.33, rel_tol=2e-5)
check(37, "maximum current (A)", 100 / 20, 5.0)

# Q38: phasor voltage for I=2 A, R=30 Ω, X_L=50 Ω, X_C=20 Ω
vr38 = 2 * 30
vl38 = 2 * 50
vc38 = 2 * 20
vreact38 = vl38 - vc38
vsource38 = math.hypot(vr38, vreact38)
check(38, "resistor voltage (V)", vr38, 60.0)
check(38, "inductor voltage (V)", vl38, 100.0)
check(38, "capacitor voltage (V)", vc38, 40.0)
check(38, "net reactive voltage (V)", vreact38, 60.0)
check(38, "source RMS voltage (V)", vsource38, 84.85, rel_tol=4e-5)
check(38, "phase angle (degree)", math.degrees(math.atan2(vreact38, vr38)), 45.0)
check(38, "power factor", vr38 / vsource38, 0.7071, rel_tol=2e-5)

# Q39: ideal transformer, 220 to 2200 V, 1100 W output
check(39, "turns/voltage ratio", 2200 / 220, 10.0)
check(39, "secondary current (A)", 1100 / 2200, 0.50)
check(39, "primary current (A)", 1100 / 220, 5.0)

# Q40: η=.90, V_p=230 V, I_p=2 A, V_s=115 V
pin40 = 230 * 2
pout40 = 0.90 * pin40
check(40, "input power (W)", pin40, 460.0)
check(40, "output power (W)", pout40, 414.0)
check(40, "secondary current (A)", pout40 / 115, 3.60)

print("\n=== PART 3A: निगमन/अवधारणा पहचान (Q41–Q50) ===")
# Q41: sine mean values
check(41, "half-cycle mean/peak ratio", 2 / pi, 0.63662, rel_tol=4e-6)
check(41, "full-cycle sine mean", mean_over_cycle(math.sin), 0.0, abs_tol=1e-12)

# Q42: RMS derivation
check(42, "mean of sin²", mean_over_cycle(lambda x: math.sin(x) ** 2), 0.50, abs_tol=1e-12)
check(42, "RMS/peak ratio", math.sqrt(mean_over_cycle(lambda x: math.sin(x) ** 2)), 1 / math.sqrt(2), abs_tol=1e-12)

# Q43: pure resistance: v and i in phase, <sin²>=1/2
vm43, im43 = 10.0, 2.0
check(43, "pure-R average power sample (W)", mean_over_cycle(lambda x: vm43 * im43 * math.sin(x) ** 2), 10.0, abs_tol=1e-10)

# Q44: pure inductance: i lags by π/2 and average power is zero
check(44, "inductive phase lag (degree)", math.degrees(pi / 2), 90.0)
check(44, "pure-L average power sample", mean_over_cycle(lambda x: 20 * math.sin(x) * math.sin(x - pi / 2)), 0.0, abs_tol=1e-10)

# Q45: pure capacitance: i leads by π/2 and average power is zero
check(45, "capacitive phase lead (degree)", math.degrees(pi / 2), 90.0)
check(45, "pure-C average power sample", mean_over_cycle(lambda x: 20 * math.sin(x) * math.sin(x + pi / 2)), 0.0, abs_tol=1e-10)

# Q46: LCR phasor identity, 3-4-5 check
check(46, "phasor impedance identity (ohm)", math.hypot(3, 4), 5.0)
check(46, "phasor angle identity (degree)", math.degrees(math.atan2(4, 3)), 53.1301, rel_tol=2e-6)

# Q47: resonance identity for L=2 H, C=.5 F
check(47, "resonance angular frequency identity", 1 / math.sqrt(2 * 0.5), 1.0)
check(47, "equal reactances at resonance", 1 * 2 - 1 / (1 * 0.5), 0.0)

# Q48: average power identity at φ=60°
phi48 = math.radians(60)
check(48, "<sin x sin(x-φ)> at 60 degree", mean_over_cycle(lambda x: math.sin(x) * math.sin(x - phi48)), 0.25, abs_tol=1e-12)
check(48, "power factor at 60 degree", math.cos(phi48), 0.50)

# Q49: raising voltage tenfold lowers I²R loss by 100
check(49, "tenfold-voltage current ratio", 1 / 10, 0.10)
check(49, "tenfold-voltage loss ratio", (1 / 10) ** 2, 0.010)

# Q50: LC energy exchange sample, C=2 F, L=8 H, Q_m=4 C at phase π/4
c50, l50, qm50, theta50 = 2.0, 8.0, 4.0, pi / 4
omega50 = 1 / math.sqrt(l50 * c50)
q50 = qm50 * math.cos(theta50)
i50 = -omega50 * qm50 * math.sin(theta50)
ue50 = q50**2 / (2 * c50)
um50 = 0.5 * l50 * i50**2
check(50, "LC angular frequency sample", omega50, 0.25)
check(50, "electric energy at π/4 (J)", ue50, 2.0)
check(50, "magnetic energy at π/4 (J)", um50, 2.0)
check(50, "constant total LC energy (J)", ue50 + um50, qm50**2 / (2 * c50))

print("\n=== PART 3B: बहुचरणीय संख्यात्मक (Q51–Q60) ===")
# Q51: V=230 V, f=50 Hz, R=40 Ω, L=.2 H, C=80 μF
v51, f51, r51, l51, c51 = 230.0, 50.0, 40.0, 0.20, 80e-6
xl51 = 2 * pi * f51 * l51
xc51 = 1 / (2 * pi * f51 * c51)
x51 = xl51 - xc51
z51 = math.hypot(r51, x51)
i51 = v51 / z51
phi51 = math.degrees(math.atan2(x51, r51))
pf51 = r51 / z51
p51 = i51**2 * r51
check(51, "X_L (ohm)", xl51, 62.83, rel_tol=4e-5)
check(51, "X_C (ohm)", xc51, 39.79, rel_tol=4e-5)
check(51, "net reactance (ohm)", x51, 23.04, rel_tol=2e-4)
check(51, "impedance (ohm)", z51, 46.16, rel_tol=8e-5)
check(51, "current (A)", i51, 4.982, rel_tol=1e-4)
check(51, "phase angle (degree)", phi51, 29.95, rel_tol=2e-4)
check(51, "power factor", pf51, 0.8665, rel_tol=4e-5)
check(51, "real power (W)", p51, 993.0, rel_tol=5e-5)

# Q52: same circuit at resonance and 100 Hz; L=.1 H,C=100 μF,R=20 Ω,V=200 V
l52, c52, r52, v52 = 0.10, 100e-6, 20.0, 200.0
omega052 = 1 / math.sqrt(l52 * c52)
f052 = omega052 / (2 * pi)
ires52 = v52 / r52
f52 = 100.0
xl52 = 2 * pi * f52 * l52
xc52 = 1 / (2 * pi * f52 * c52)
x52 = xl52 - xc52
z52 = math.hypot(r52, x52)
i52 = v52 / z52
pf52 = r52 / z52
p52 = i52**2 * r52
check(52, "resonant frequency (Hz)", f052, 50.33, rel_tol=2e-5)
check(52, "resonant current (A)", ires52, 10.0)
check(52, "X_L at 100 Hz (ohm)", xl52, 62.83, rel_tol=4e-5)
check(52, "X_C at 100 Hz (ohm)", xc52, 15.92, rel_tol=3e-4)
check(52, "net reactance at 100 Hz (ohm)", x52, 46.92, rel_tol=8e-5)
check(52, "impedance at 100 Hz (ohm)", z52, 51.00, rel_tol=5e-5)
check(52, "current at 100 Hz (A)", i52, 3.9215, rel_tol=6e-5)
check(52, "power factor at 100 Hz", pf52, 0.39215, rel_tol=6e-5)
check(52, "power at 100 Hz (W)", p52, 307.6, rel_tol=2e-4)

# Q53: phasor voltages, I=3 A, R=40 Ω, X_L=70 Ω, X_C=20 Ω
current53, r53, xl53, xc53 = 3.0, 40.0, 70.0, 20.0
vr53 = current53 * r53
vl53 = current53 * xl53
vc53 = current53 * xc53
vreact53 = vl53 - vc53
vsource53 = math.hypot(vr53, vreact53)
z53 = vsource53 / current53
phi53 = math.degrees(math.atan2(xl53 - xc53, r53))
pf53 = r53 / z53
p53 = current53**2 * r53
check(53, "resistor voltage (V)", vr53, 120.0)
check(53, "inductor voltage (V)", vl53, 210.0)
check(53, "capacitor voltage (V)", vc53, 60.0)
check(53, "net reactive voltage (V)", vreact53, 150.0)
check(53, "source RMS voltage (V)", vsource53, 192.09, rel_tol=3e-5)
check(53, "impedance (ohm)", z53, 64.03, rel_tol=3e-5)
check(53, "phase angle (degree)", phi53, 51.34, rel_tol=4e-5)
check(53, "power factor", pf53, 0.6247, rel_tol=2e-5)
check(53, "real power (W)", p53, 360.0)

# Q54: current components for 2 kW, 220 V, 0.8 lagging power factor
p54, v54, pf54 = 2000.0, 220.0, 0.80
i54 = p54 / (v54 * pf54)
phi54 = math.acos(pf54)
active54 = i54 * pf54
wattless54 = i54 * math.sin(phi54)
apparent54 = v54 * i54
reactive54 = v54 * wattless54
check(54, "load current (A)", i54, 11.3636, rel_tol=4e-5)
check(54, "phase angle (degree)", math.degrees(phi54), 36.87, rel_tol=2e-5)
check(54, "active current component (A)", active54, 9.0909, rel_tol=3e-5)
check(54, "wattless current component (A)", wattless54, 6.8182, rel_tol=3e-5)
check(54, "apparent power (VA)", apparent54, 2500.0)
check(54, "reactive power (var)", reactive54, 1500.0)

# Q55: transformer, Vp=220,Np=500,Ns=2000,η=.9,Is=2 A
vp55, np55, ns55, eta55, is55 = 220.0, 500.0, 2000.0, 0.90, 2.0
vs55 = vp55 * ns55 / np55
pout55 = vs55 * is55
pin55 = pout55 / eta55
ip55 = pin55 / vp55
loss55 = pin55 - pout55
check(55, "secondary voltage (V)", vs55, 880.0)
check(55, "output power (W)", pout55, 1760.0)
check(55, "input power (W)", pin55, 1955.56, rel_tol=3e-6)
check(55, "primary current (A)", ip55, 8.889, rel_tol=2e-5)
check(55, "transformer loss (W)", loss55, 195.56, rel_tol=3e-5)

# Q56: transmit 100 kW through 2 Ω at 2 kV and 20 kV, unity PF
p56, rline56 = 100_000.0, 2.0
i_low56 = p56 / 2000
loss_low56 = i_low56**2 * rline56
i_high56 = p56 / 20_000
loss_high56 = i_high56**2 * rline56
check(56, "current at 2 kV (A)", i_low56, 50.0)
check(56, "line loss at 2 kV (W)", loss_low56, 5000.0)
check(56, "loss percentage at 2 kV", 100 * loss_low56 / p56, 5.0)
check(56, "current at 20 kV (A)", i_high56, 5.0)
check(56, "line loss at 20 kV (W)", loss_high56, 50.0)
check(56, "loss percentage at 20 kV", 100 * loss_high56 / p56, 0.050)
check(56, "loss reduction factor", loss_low56 / loss_high56, 100.0)

# Q57: R=20 Ω,L=.2 H,C=50 μF,V=100 V at 40 Hz and 80 Hz
r57, l57, c57, v57 = 20.0, 0.20, 50e-6, 100.0
for f, expected in (
    (40.0, (50.27, 79.58, -29.31, 35.49, 2.818, -55.69, 0.5636)),
    (80.0, (100.53, 39.79, 60.74, 63.95, 1.5637, 71.78, 0.3127)),
):
    xl = 2 * pi * f * l57
    xc = 1 / (2 * pi * f * c57)
    x = xl - xc
    z = math.hypot(r57, x)
    current = v57 / z
    angle = math.degrees(math.atan2(x, r57))
    pf = r57 / z
    ex_xl, ex_xc, ex_x, ex_z, ex_i, ex_angle, ex_pf = expected
    suffix = f"at {int(f)} Hz"
    check(57, f"X_L {suffix} (ohm)", xl, ex_xl, rel_tol=2e-4)
    check(57, f"X_C {suffix} (ohm)", xc, ex_xc, rel_tol=2e-4)
    check(57, f"net X {suffix} (ohm)", x, ex_x, rel_tol=2e-4)
    check(57, f"Z {suffix} (ohm)", z, ex_z, rel_tol=2e-4)
    check(57, f"I {suffix} (A)", current, ex_i, rel_tol=1e-4)
    check(57, f"phase {suffix} (degree)", angle, ex_angle, rel_tol=2e-4)
    check(57, f"power factor {suffix}", pf, ex_pf, rel_tol=2e-4)

# Q58: v=200 sin(100πt), R=50 Ω
vm58, omega58, r58 = 200.0, 100 * pi, 50.0
im58 = vm58 / r58
vrms58 = vm58 / math.sqrt(2)
irms58 = im58 / math.sqrt(2)
pmax58 = vm58 * im58
pavg58 = vrms58 * irms58
check(58, "frequency (Hz)", omega58 / (2 * pi), 50.0)
check(58, "peak current (A)", im58, 4.0)
check(58, "RMS voltage (V)", vrms58, 141.42, rel_tol=2e-5)
check(58, "RMS current (A)", irms58, 2.8284, rel_tol=6e-5)
check(58, "maximum instantaneous power (W)", pmax58, 800.0)
check(58, "average power (W)", pavg58, 400.0)

# Q59: 220 V to 12 V, 60 W load, η=.8
vp59, vs59, pout59, eta59 = 220.0, 12.0, 60.0, 0.80
ratio59 = vs59 / vp59
is59 = pout59 / vs59
pin59 = pout59 / eta59
ip59 = pin59 / vp59
loss59 = pin59 - pout59
check(59, "turns ratio N_s/N_p", ratio59, 0.05455, rel_tol=9e-5)
check(59, "secondary current (A)", is59, 5.0)
check(59, "input power (W)", pin59, 75.0)
check(59, "primary current (A)", ip59, 0.3409, rel_tol=5e-5)
check(59, "loss (W)", loss59, 15.0)

# Q60: design resonance at 50 Hz; R=30 Ω,L=.2 H,V=120 V
f60, r60, l60, v60 = 50.0, 30.0, 0.20, 120.0
omega60 = 2 * pi * f60
c60 = 1 / (omega60**2 * l60)
i60 = v60 / r60
x60 = omega60 * l60
vl60 = i60 * x60
p60 = i60**2 * r60
check(60, "required capacitance (microfarad)", c60 * 1e6, 50.66, rel_tol=8e-5)
check(60, "resonant current (A)", i60, 4.0)
check(60, "X_L=X_C (ohm)", x60, 62.83, rel_tol=4e-5)
check(60, "V_L=V_C magnitude (V)", vl60, 251.33, rel_tol=2e-5)
check(60, "real power (W)", p60, 480.0)

expected_questions = set(range(1, 61))
missing = sorted(expected_questions - covered_questions)
extra = sorted(covered_questions - expected_questions)
failed = [(q, label, got, expected) for q, label, passed, got, expected in checks if not passed]
passed_count = len(checks) - len(failed)

print("\n" + "=" * 86)
print(f"PASS TOTAL: {passed_count}/{len(checks)} numerical checks")
print(f"QUESTION COVERAGE: {len(covered_questions)}/60")

assert not missing, f"इन प्रश्नों की स्वतंत्र जाँच नहीं हुई: {missing}"
assert not extra, f"अमान्य प्रश्न क्रमांक जाँचे गए: {extra}"
assert not failed, "असफल संख्यात्मक जाँचें: " + "; ".join(
    f"Q{q} {label}: got={got}, expected={expected}" for q, label, got, expected in failed
)

# संख्यात्मक गणना ऊपर स्रोत से स्वतन्त्र है। उसके बाद अलग से स्रोत-संरचना जाँचें,
# ताकि सही गणना किसी अधूरे अथवा गलत क्रम वाले प्रश्न-संग्रह को न छिपा सके।
import ch7_part1
import ch7_part2
import ch7_part3

parts = (ch7_part1.PART1, ch7_part2.PART2, ch7_part3.PART3)
questions = [question for part in parts for question in part]
required_keys = {"n", "cat", "marks", "topic", "q", "formula", "why", "steps", "ans", "trick", "alt"}
assert [len(part) for part in parts] == [20, 20, 20], "तीनों भागों में 20-20 प्रश्न चाहिए"
assert [question["n"] for question in questions] == list(range(1, 61)), "प्रश्न क्रम 1–60 नहीं है"
assert all(set(question) == required_keys for question in questions), "11-key schema टूटा है"
assert all(question["cat"] == (question["n"] - 1) // 20 + 1 for question in questions), "श्रेणी-विभाजन टूटा है"
assert len({question["q"] for question in questions}) == 60, "दो प्रश्नों का कथन समान है"
assert all(
    len(question["steps"]) >= 3
    and all(len(step) == 2 and all(isinstance(value, str) and value.strip() for value in step) for step in question["steps"])
    for question in questions
), "किसी प्रश्न का चरणबद्ध हल अधूरा है"
assert all(question["marks"] in (3, 5) for question in ch7_part3.PART3[:10]), "Q41–Q50 दीर्घ-उत्तरीय होने चाहिए"
print("STRUCTURE VERIFIED: exact schema, 20/20/20 split, 10 long derivations")
print("ALL CHAPTER 7 NUMERICAL RESULTS VERIFIED")
