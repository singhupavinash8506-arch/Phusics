"""अध्याय 2 — हर संख्यात्मक उत्तर स्वतन्त्र रूप से सत्यापित।
कोई भी मान PDF में जाने से पहले यहाँ मूल सिद्धान्तों से पुनः गणना होता है।"""
import math

k = 9e9
eps0 = 8.85e-12
e = 1.6e-19

ok = []
def chk(tag, got, want, tol=0.02):
    rel = abs(got - want)/abs(want) if want else abs(got)
    s = "OK " if rel <= tol else "FAIL"
    ok.append(s == "OK ")
    print(f"{s} {tag:<46} got={got:.6g}  want={want:.6g}")

print("=== SHRENI 1 : direct formula ===")
chk("Q1  V=kq/r  2uC at 30cm",        k*2e-6/0.30, 6e4)
chk("Q2  V=W/q  4e-3 J, 2uC",         4e-3/2e-6, 2e3)
chk("Q3  C=q/V  5uC at 100V",         5e-6/100, 5e-8)
A4, d4 = 0.02, 1e-3
chk("Q4  C=eps0*A/d  0.02m2, 1mm",    eps0*A4/d4, 1.77e-10)
chk("Q5  with K=5",                   5*eps0*A4/d4, 8.85e-10)
chk("Q6  series 6uF & 3uF",           1/(1/6e-6 + 1/3e-6), 2e-6)
chk("Q7  parallel 6uF & 3uF",         6e-6+3e-6, 9e-6)
chk("Q8  U=0.5CV^2  2uF,100V",        0.5*2e-6*100**2, 1e-2)
chk("Q9  U=q^2/2C   4uC,2uF",         (4e-6)**2/(2*2e-6), 4e-6)
chk("Q10 u=0.5eps0E^2  E=1e5",        0.5*eps0*(1e5)**2, 4.425e-2)
chk("Q11 V axial dipole p=2e-8,r=30cm", k*2e-8/0.30**2, 2e3)
# Q12 V equatorial = 0 (exact)
chk("Q13 U=kq1q2/r  2uC,3uC,30cm",    k*2e-6*3e-6/0.30, 0.18)
chk("Q14 U=-pEcos60  p=2e-6,E=1e5",   -2e-6*1e5*math.cos(math.radians(60)), -0.1)
chk("Q15 C sphere R=9cm  (R/k)",      0.09/k, 1e-11)
chk("Q16 E=V/d  100V, 2mm",           100/2e-3, 5e4)
chk("Q17 W=q*dV  2uC, 50V",           2e-6*50, 1e-4)
chk("Q18 V system +4uC@0.2, -2uC@0.3", k*(4e-6/0.20 - 2e-6/0.30), 1.2e5)
chk("Q19 q=CV  10uF, 50V",            10e-6*50, 5e-4)
chk("Q20 common V (2uF@100,3uF@50)",  (2e-6*100+3e-6*50)/(5e-6), 70)

print("\n=== SHRENI 2a : one unknown ===")
chk("Q21 q from V=6e4 at r=0.3",       6e4*0.30/k, 2e-6)
chk("Q22 V from q=5uC, C=0.05uF",      5e-6/5e-8, 100)
chk("Q23 d from C=177pF, A=0.02",      eps0*0.02/1.77e-10, 1e-3)
chk("Q24 V from U=1e-2, C=2uF",        math.sqrt(2*1e-2/2e-6), 100)
chk("Q25 K from 8.85e-10 / 1.77e-10",  8.85e-10/1.77e-10, 5)
chk("Q26 C2 series: tot 2uF, C1 6uF",  1/(1/2e-6 - 1/6e-6), 3e-6)
chk("Q27 E from u=4.425e-2",           math.sqrt(2*4.425e-2/eps0), 1e5)
chk("Q28 r from U=0.18, q1q2=6e-12",   k*6e-12/0.18, 0.30)
chk("Q29 d from E=5e4, V=100",         100/5e4, 2e-3)
chk("Q30 R from C=10pF",               1e-11*k, 0.09)

print("\n=== SHRENI 2b : two unknowns ===")
def roots(S, P):
    disc = S*S - 4*P
    return ((S+math.sqrt(disc))/2, (S-math.sqrt(disc))/2)

# Q31 series 2uF, parallel 9uF  (in uF)
P31 = 2*9            # C1C2 = Cs*(C1+C2)
chk("Q31 product (uF^2)", P31, 18)
a,b = roots(9, P31); chk("Q31 root A", a, 6); chk("Q31 root B", b, 3)

# Q32 parallel 5uF, series 1.2uF
P32 = 1.2*5
chk("Q32 product (uF^2)", P32, 6)
a,b = roots(5, P32); chk("Q32 root A", a, 3); chk("Q32 root B", b, 2)

# Q33 C=2uF, U=0.01 J -> V and q
V33 = math.sqrt(2*0.01/2e-6); chk("Q33 V", V33, 100)
chk("Q33 q", 2e-6*V33, 2e-4)

# Q34 C=177pF, E=5e4 at V=100 -> d and A
d34 = 100/5e4; chk("Q34 d", d34, 2e-3)
chk("Q34 A", 1.77e-10*d34/eps0, 0.04)

# Q35 sum 5uC, U=0.18 J at r=0.3 -> both charges
P35 = (0.18*0.30/k)/1e-12
chk("Q35 product (uC^2)", P35, 6)
a,b = roots(5, P35); chk("Q35 root A", a, 3); chk("Q35 root B", b, 2)

# Q36 q=2e-4, U=1e-2 -> V and C
V36 = 2*1e-2/2e-4; chk("Q36 V", V36, 100)
chk("Q36 C", 2e-4/V36, 2e-6)

# Q37 common potential and energy loss
C1, C2, V1, V2 = 2e-6, 3e-6, 100, 50
chk("Q37 common V", (C1*V1+C2*V2)/(C1+C2), 70)
chk("Q37 energy loss", C1*C2*(V1-V2)**2/(2*(C1+C2)), 1.5e-3)

# Q38 partially filled dielectric: d=4mm, t=2mm, K=2, A=0.02
d38, t38, K38, A38 = 4e-3, 2e-3, 2, 0.02
chk("Q38 C air",  eps0*A38/d38, 4.425e-11)
chk("Q38 C slab", eps0*A38/(d38 - t38 + t38/K38), 5.9e-11)

# Q39 C=10pF, V=900V -> R and q
chk("Q39 R", 1e-11*k, 0.09)
chk("Q39 q", 1e-11*900, 9e-9)

# Q40 dipole p=2e-6, E=1e5 : U at 0 deg, W for 0->90
chk("Q40 U(0)",     -2e-6*1e5, -0.2)
chk("Q40 W(0->90)",  2e-6*1e5*(math.cos(0)-math.cos(math.radians(90))), 0.2)

print("\n=== SHRENI 3 : hard numericals ===")
# Q50/Q56 three-charge systems, equilateral side 10 cm
a_tri = 0.10
chk("Q50 U 3 equal 2uC at 10cm", 3*k*(2e-6)**2/a_tri, 1.08)
q1,q2,q3 = 1e-6, 2e-6, -3e-6
chk("Q56 U mixed +1,+2,-3 uC",
    (k/a_tri)*(q1*q2 + q2*q3 + q1*q3), -0.63)
# Q57 network: 2uF in series with (3uF || 3uF)
chk("Q57 network 2 series (3||3)", 1/(1/2e-6 + 1/6e-6), 1.5e-6)
# Q58 connected spheres R1=2cm R2=6cm total 8uC
R1s, R2s, Qtot = 0.02, 0.06, 8e-6
q1s = Qtot*R1s/(R1s+R2s); q2s = Qtot - q1s
chk("Q58 q on 2cm sphere", q1s, 2e-6)
chk("Q58 q on 6cm sphere", q2s, 6e-6)
chk("Q58 sigma ratio = R2/R1",
    (q1s/R1s**2)/(q2s/R2s**2), 3)
# Q59 work across potentials
chk("Q59 W = q(V1-V2) 2uC, 100->40", 2e-6*(100-40), 1.2e-4)

print(f"\n{'='*62}\n{sum(ok)}/{len(ok)} checks passed"
      f"{'  -- ALL GOOD' if all(ok) else '  -- FIX NEEDED'}")
