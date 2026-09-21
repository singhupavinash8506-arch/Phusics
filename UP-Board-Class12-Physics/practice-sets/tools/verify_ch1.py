"""Chapter 1 — verify every numerical answer independently before authoring.
Nothing goes into the PDF unless it is reproduced here from first principles."""
import math

k = 9e9            # 1/(4*pi*eps0)  N m^2 C^-2
eps0 = 8.85e-12    # C^2 N^-1 m^-2
e = 1.6e-19        # C
me = 9.1e-31       # kg
G = 6.67e-11

ok = []
def chk(tag, got, want, tol=0.02):
    rel = abs(got - want) / abs(want) if want else abs(got)
    status = "OK " if rel <= tol else "FAIL"
    ok.append(status == "OK ")
    print(f"{status} {tag:<44} got={got:.6g}  want={want:.6g}")

print("=== SHRENI 1 : direct formula ===")
chk("Q1  F Coulomb 2uC,3uC,30cm",      k*2e-6*3e-6/0.30**2, 0.6)
chk("Q2  n electrons in 1.6e-17 C",    1.6e-17/e, 100)
chk("Q3  F in medium K=2 from 8e-4",   8e-4/2, 4e-4)
chk("Q4  E=F/q 4e-3/2e-6",             4e-3/2e-6, 2e3)
chk("Q5  E point 4uC at 20cm",         k*4e-6/0.20**2, 9e5)
chk("Q6  p = q*2a 2uC x 5cm",          2e-6*0.05, 1e-7)
chk("Q7  E axial p=4e-8 r=20cm",       2*k*4e-8/0.20**3, 9e4)
chk("Q8  E equatorial same",           k*4e-8/0.20**3, 4.5e4)
chk("Q9  torque p=3e-6 E=2e5 th=30",   3e-6*2e5*math.sin(math.radians(30)), 0.3)
chk("Q10 flux E=5e3 A=0.02 th=60",     5e3*0.02*math.cos(math.radians(60)), 50)
chk("Q11 flux Gauss q=8.85e-8",        8.85e-8/eps0, 1e4)
chk("Q12 E wire lam=2e-6 r=10cm",      2*k*2e-6/0.10, 3.6e5)
chk("Q13 E sheet sig=1.77e-6",         1.77e-6/(2*eps0), 1e5)
chk("Q14 E shell q=5uC at r=50cm",     k*5e-6/0.50**2, 1.8e5)
# Q15 inside shell = 0 (exact, no arithmetic)
chk("Q16 lambda 6uC over 3m",          6e-6/3, 2e-6)
chk("Q17 sigma 4uC sphere R=10cm",     4e-6/(4*math.pi*0.10**2), 3.183e-5)
chk("Q18 F at r/2 from 10N",           10*4, 40)
chk("Q19 E between sheets sig=8.85e-12", 8.85e-12/eps0, 1.0)
chk("Q20 F on electron E=1e4",         e*1e4, 1.6e-15)

print("\n=== SHRENI 2a : one unknown ===")
chk("Q21 r from F=0.6 2uC,3uC",        math.sqrt(k*2e-6*3e-6/0.6), 0.30)
chk("Q22 q from E=9e5 at 20cm",        9e5*0.20**2/k, 4e-6)
chk("Q23 q from flux 1e4",             1e4*eps0, 8.85e-8)
chk("Q24 theta from tau=0.3 pE=0.6",   math.degrees(math.asin(0.3/(3e-6*2e5))), 30)
chk("Q25 lambda from E=3.6e5 r=10cm",  3.6e5*0.10/(2*k), 2e-6)
chk("Q26 sigma from E=1e5",            2*eps0*1e5, 1.77e-6)
chk("Q27 p from E_ax=9e4 r=20cm",      9e4*0.20**3/(2*k), 4e-8)
chk("Q28 n from q=0.8uC",              0.8e-6/e, 5e12)
chk("Q29 K from Fvac=6e-3 Fmed=2e-3",  6e-3/2e-3, 3)
chk("Q30 q shell from E=1.8e5 r=50cm", 1.8e5*0.50**2/k, 5e-6)

print("\n=== SHRENI 2b : two unknowns ===")
def pair_from_sum(S, P):
    """S, P in microcoulomb units; returns the two roots."""
    d = S*S - 4*P
    return ((S+math.sqrt(d))/2, (S-math.sqrt(d))/2)

# Q31 sum 5uC, r=30cm, F=0.6N
P31 = 0.6*0.30**2/k / 1e-12
chk("Q31 product (uC^2)", P31, 6)
a, b = pair_from_sum(5, P31); chk("Q31 root A", a, 3); chk("Q31 root B", b, 2)

# Q32 sum 9uC, r=30cm, F=2N
P32 = 2*0.30**2/k / 1e-12
chk("Q32 product (uC^2)", P32, 20)
a, b = pair_from_sum(9, P32); chk("Q32 root A", a, 5); chk("Q32 root B", b, 4)

# Q33 difference 3uC, r=20cm, F=0.9N
P33 = 0.9*0.20**2/k / 1e-12
chk("Q33 product (uC^2)", P33, 4)
# q1 - q2 = 3, q1*q2 = 4  ->  q1=4, q2=1
D = 3; disc = D*D + 4*P33
q1 = (D+math.sqrt(disc))/2; q2 = q1 - D
chk("Q33 q1", q1, 4); chk("Q33 q2", q2, 1)

# Q34 E1=9e5, E2=1e5 at r1+0.4 ; find q, r1
ratio = math.sqrt(9e5/1e5)             # r2/r1 = 3
r1 = 0.4/(ratio-1); chk("Q34 r1", r1, 0.20)
chk("Q34 q", 9e5*r1**2/k, 4e-6)

# Q35 wire E1=3.6e5 at 10cm, E2=1.2e5 ; find lambda, r2
chk("Q35 lambda", 3.6e5*0.10/(2*k), 2e-6)
chk("Q35 r2", 0.10*(3.6e5/1.2e5), 0.30)

# Q36 2a=4cm, E=2e5, tau_max=0.4 ; find p, q
p36 = 0.4/2e5; chk("Q36 p", p36, 2e-6)
chk("Q36 q", p36/0.04, 5e-5)

# Q37 Fvac=0.9 at 20cm, Fmed=0.3 ; find K, q1q2
chk("Q37 K", 0.9/0.3, 3)
chk("Q37 q1q2", 0.9*0.20**2/k, 4e-12)

# Q38 total flux 1e4 ; find q and per-face flux
chk("Q38 q", 1e4*eps0, 8.85e-8)
chk("Q38 face flux", 1e4/6, 1666.67)

# Q39 a=1.76e15 ; find F and E
F39 = me*1.76e15; chk("Q39 F", F39, 1.602e-15)
chk("Q39 E", F39/e, 1.001e4)

# Q40 null point between 9uC and 4uC, d=1m
x = 1/(1+math.sqrt(4/9)); chk("Q40 x from 9uC", x, 0.60)
chk("Q40 from 4uC", 1-x, 0.40)

print("\n=== SHRENI 3 : selected hard numericals ===")
Fpair = k*2e-6*2e-6/0.10**2
chk("Q47 pair force equilateral 2uC 10cm", Fpair, 3.6)
chk("Q47 net = sqrt3 * F",                 math.sqrt(3)*Fpair, 6.235)
chk("Q49 flux one face of cube q/6eps0",   1e-6/(6*eps0), 1.883e4)
chk("Q52 F before +6uC,-2uC at 20cm",      k*6e-6*2e-6/0.20**2, 2.7)
chk("Q52 F after touching (+2uC each)",    k*2e-6*2e-6/0.20**2, 0.9)
chk("Q56 Fe/Fg two electrons",             (k*e*e)/(G*me*me), 4.17e42)

print(f"\n{'='*60}\n{sum(ok)}/{len(ok)} checks passed"
      f"{'  -- ALL GOOD' if all(ok) else '  -- FIX NEEDED'}")
