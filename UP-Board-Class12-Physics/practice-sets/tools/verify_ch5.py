"""अध्याय 5 — चुम्बकत्व एवं द्रव्य। हर संख्यात्मक उत्तर मूल सिद्धान्तों से पुनः गणना।"""
import math

mu0 = 4*math.pi*1e-7
k   = 1e-7          # mu0/4pi

ok = []
def chk(tag, got, want, tol=0.02):
    rel = abs(got-want)/abs(want) if want else abs(got)
    s = "OK " if rel <= tol else "FAIL"
    ok.append(s == "OK ")
    print(f"{s} {tag:<48} got={got:.6g}  want={want:.6g}")

print("=== SHRENI 1 : direct formula ===")
pole, length = 5.0, 0.10
M = pole*length
chk("Q1  M = m x 2l  (5 A.m, 0.1 m)",        M, 0.5)
chk("Q2  B axial  M=0.5 r=0.1",              k*2*M/0.10**3, 1e-4)
chk("Q3  B equatorial same",                 k*M/0.10**3, 5e-5)
chk("Q4  tau = MB sin30  B=0.4",             M*0.4*math.sin(math.radians(30)), 0.1)
chk("Q5  U = -MB cos60",                    -M*0.4*math.cos(math.radians(60)), -0.1)
chk("Q6  W(0->90) = MB(1-0)",                M*0.4*(1-0), 0.2)
I_moi = 2e-5
chk("Q7  T = 2pi sqrt(I/MB)",                2*math.pi*math.sqrt(I_moi/(M*0.4)), 0.06283)
B_earth, dip = 5e-5, 60.0
chk("Q8  B_H = B cos(dip)",                  B_earth*math.cos(math.radians(dip)), 2.5e-5)
chk("Q9  B_V = B sin(dip)",                  B_earth*math.sin(math.radians(dip)), 4.3301e-5)
chk("Q10 tan(dip) = B_V/B_H",
    math.degrees(math.atan((B_earth*math.sin(math.radians(dip)))/(B_earth*math.cos(math.radians(dip))))), 60)
chk("Q11 B = sqrt(BH^2+BV^2)  3e-5,4e-5",    math.hypot(3e-5, 4e-5), 5e-5)
chk("Q12 magnetisation M=m_net/V  6, 2e-5",  6/2e-5, 3e5)
chk("Q13 H = nI  n=1000 I=2",                1000*2, 2000)
chk("Q14 chi = M/H  6e-2 / 2e3",             6e-2/2e3, 3e-5)
chk("Q15 mu_r = 1 + chi  (chi=499)",         1+499, 500)
chk("Q16 mu = mu0 mu_r  (500)",              mu0*500, 6.2832e-4)
chk("Q17 Curie: chi2 = chi1 T1/T2 300->600", 3e-5*300/600, 1.5e-5)
chk("Q18 cut perpendicular: M' = M/2",       M/2, 0.25)
chk("Q19 two magnets at 90 deg",             math.hypot(M, M), 0.70711)
# Q20 dip at equator 0, poles 90 (exact)

print("\n=== SHRENI 2a : one unknown ===")
chk("Q21 M from B_ax=1e-4 r=0.1",            1e-4*0.10**3/(2*k), 0.5)
chk("Q22 theta from tau=0.1 MB=0.2",         math.degrees(math.asin(0.1/0.2)), 30)
T7 = 2*math.pi*math.sqrt(I_moi/(M*0.4))
chk("Q23 M from T, I, B",                    4*math.pi**2*I_moi/(T7**2*0.4), 0.5)
chk("Q24 B_V from dip=60, B_H=2.5e-5",       2.5e-5*math.tan(math.radians(60)), 4.3301e-5)
chk("Q25 B from B_H=2.5e-5, dip=60",         2.5e-5/math.cos(math.radians(60)), 5e-5)
chk("Q26 pole strength from M=0.5, 2l=0.1",  0.5/0.10, 5)
chk("Q27 M(magnetisation) from chi,H",       3e-5*2e3, 6e-2)
chk("Q28 chi from mu_r=500",                 500-1, 499)
chk("Q29 theta from U=-0.1, MB=0.2",         math.degrees(math.acos(0.1/0.2)), 60)
chk("Q30 m_net from Mag=3e5, V=2e-5",        3e5*2e-5, 6)

print("\n=== SHRENI 2b : two unknowns ===")
# Q31 B=5e-5 dip=60 -> BH, BV
chk("Q31 B_H", B_earth*math.cos(math.radians(60)), 2.5e-5)
chk("Q31 B_V", B_earth*math.sin(math.radians(60)), 4.3301e-5)

# Q32 BH=3e-5 BV=4e-5 -> B and dip
chk("Q32 B",   math.hypot(3e-5,4e-5), 5e-5)
chk("Q32 dip", math.degrees(math.atan(4e-5/3e-5)), 53.13)

# Q33 axial B=1e-4 at r=0.1, 2l=0.1 -> M and pole strength
M33 = 1e-4*0.10**3/(2*k); chk("Q33 M", M33, 0.5)
chk("Q33 pole strength", M33/0.10, 5)

# Q34 M=0.5 B=0.4 theta=60 -> tau and U
chk("Q34 tau", M*0.4*math.sin(math.radians(60)), 0.17321)
chk("Q34 U",  -M*0.4*math.cos(math.radians(60)), -0.1)

# Q35 work 0->60 and 0->180
chk("Q35 W(0->60)",  M*0.4*(1-math.cos(math.radians(60))), 0.1)
chk("Q35 W(0->180)", M*0.4*(1-math.cos(math.radians(180))), 0.4)

# Q36 chi=499 -> mu_r and mu
chk("Q36 mu_r", 1+499, 500)
chk("Q36 mu",   mu0*500, 6.2832e-4)

# Q37 m_net=6, V=2e-5, H=2e5 -> Magnetisation and chi
Mag37 = 6/2e-5; chk("Q37 magnetisation", Mag37, 3e5)
chk("Q37 chi", Mag37/2e5, 1.5)

# Q38 T1=0.06283 at B1=0.4 -> T2 at B2=0.1 and ratio
chk("Q38 T2", T7*math.sqrt(0.4/0.1), 0.12566)
chk("Q38 ratio T2/T1", math.sqrt(0.4/0.1), 2)

# Q39 Curie at 450 K and 600 K from 3e-5 at 300 K
chk("Q39 chi(450)", 3e-5*300/450, 2e-5)
chk("Q39 chi(600)", 3e-5*300/600, 1.5e-5)

# Q40 cut perpendicular and parallel -> both M/2
chk("Q40 perpendicular cut M'", pole*(length/2), 0.25)
chk("Q40 parallel cut M'",      (pole/2)*length, 0.25)

print("\n=== SHRENI 3 : hard numericals ===")
# Q53 neutral point on equatorial line: k*M/r^3 = B_H
M53, BH53 = 0.25, 2.5e-5
r53 = (k*M53/BH53)**(1/3)
chk("Q53 neutral point r", r53, 0.10)
chk("Q53 check B_eq at r",  k*M53/r53**3, 2.5e-5)

# Q54 axial field along B_H : resultant when aligned / opposed
chk("Q54 B_axial M=0.5 r=0.2", k*2*0.5/0.20**3, 1.25e-5)
chk("Q54 sum with B_H",  k*2*0.5/0.20**3 + 2.5e-5, 3.75e-5)
chk("Q54 diff with B_H", abs(k*2*0.5/0.20**3 - 2.5e-5), 1.25e-5)

# Q56 cut into 4 equal parts perpendicular
chk("Q56 M' = M/4", M/4, 0.125)

# Q58 chi=1.5 -> mu_r and mu
chk("Q58 mu_r", 1+1.5, 2.5)
chk("Q58 mu",   mu0*2.5, 3.1416e-6)

# Q59 W(0->90) and tau at 90
chk("Q59 W(0->90)",  M*0.4*(1-0), 0.2)
chk("Q59 tau at 90", M*0.4*1, 0.2)

print(f"\n{'='*66}\n{sum(ok)}/{len(ok)} checks passed"
      f"{'  -- ALL GOOD' if all(ok) else '  -- FIX NEEDED'}")
