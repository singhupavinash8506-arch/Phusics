"""अध्याय 6 — वैद्युतचुम्बकीय प्रेरण। हर संख्यात्मक उत्तर मूल सिद्धान्तों से पुनः गणना।"""
import math

mu0 = 4*math.pi*1e-7

ok = []
def chk(tag, got, want, tol=0.02):
    rel = abs(got-want)/abs(want) if want else abs(got)
    s = "OK " if rel <= tol else "FAIL"
    ok.append(s == "OK ")
    print(f"{s} {tag:<48} got={got:.6g}  want={want:.6g}")

print("=== SHRENI 1 : direct formula ===")
B, A, th = 0.5, 0.02, 60.0
chk("Q1  phi = BA cos60",                 B*A*math.cos(math.radians(th)), 5e-3)
chk("Q2  emf = N dphi/dt 100,2e-3,0.1",   100*2e-3/0.1, 2)
chk("Q3  motional emf Blv 0.5,0.2,10",    0.5*0.2*10, 1)
chk("Q4  phi = LI  L=0.5 I=4",            0.5*4, 2)
chk("Q5  emf = L dI/dt 10mH,10A,5ms",     0.01*10/0.005, 20)
N6, A6, l6 = 1000, 0.001, 0.5
L6 = mu0*N6**2*A6/l6
chk("Q6  L solenoid mu0 N^2 A/l",         L6, 2.5133e-3)
chk("Q7  emf2 = M dI1/dt 0.2,5,0.1",      0.2*5/0.1, 10)
chk("Q8  U = 0.5 L I^2  0.5,4",           0.5*0.5*4**2, 4)
chk("Q9  u = B^2/(2 mu0)  B=0.5",         0.5**2/(2*mu0), 9.9472e4)
chk("Q10 q = N dphi/R  100,2e-3,10",      100*2e-3/10, 0.02)
Br, lr, vr, Rr = 0.5, 0.2, 10.0, 2.0
chk("Q11 F = B^2 l^2 v/R",                Br**2*lr**2*vr/Rr, 0.05)
chk("Q12 P = B^2 l^2 v^2/R",              Br**2*lr**2*vr**2/Rr, 0.5)
chk("Q13 I = Blv/R",                      Br*lr*vr/Rr, 0.5)
chk("Q14 dphi/dt from emf=2, N=1",        2/1, 2)
N1, N2 = 1000, 500
chk("Q15 M = mu0 N1 N2 A/l",              mu0*N1*N2*A6/l6, 1.2566e-3)
chk("Q16 phi at theta=0  BA",             B*A, 0.01)
chk("Q17 peak emf NBA omega 100,.5,.02,100", 100*0.5*0.02*100, 100)
chk("Q18 time constant L/R  0.5,10",      0.5/10, 0.05)
chk("Q19 L = N phi / I  200,5e-3,2",      200*5e-3/2, 0.5)
# Q20 Lenz direction (conceptual)

print("\n=== SHRENI 2a : one unknown ===")
chk("Q21 B from phi=5e-3 A=0.02 th=60",   5e-3/(A*math.cos(math.radians(60))), 0.5)
chk("Q22 dphi from emf=2 N=100 dt=0.1",   2*0.1/100, 2e-3)
chk("Q23 v from emf=1 B=0.5 l=0.2",       1/(0.5*0.2), 10)
chk("Q24 L from emf=20 dI=10 dt=5ms",     20*0.005/10, 0.01)
chk("Q25 I from U=4 L=0.5",               math.sqrt(2*4/0.5), 4)
chk("Q26 R from q=0.02 N=100 dphi=2e-3",  100*2e-3/0.02, 10)
chk("Q27 M from emf2=10 dI1=5 dt=0.1",    10*0.1/5, 0.2)
chk("Q28 B from u=9.9472e4",              math.sqrt(2*mu0*9.9472e4), 0.5)
chk("Q29 N from L=2.5133e-3 A=1e-3 l=0.5",math.sqrt(2.5133e-3*l6/(mu0*A6)), 1000)
chk("Q30 L from tau=0.05 R=10",           0.05*10, 0.5)

print("\n=== SHRENI 2b : two unknowns ===")
# Q31 rod: emf and I
chk("Q31 emf", Br*lr*vr, 1.0)
chk("Q31 I",   Br*lr*vr/Rr, 0.5)

# Q32 rod: F and P
chk("Q32 F", Br**2*lr**2*vr/Rr, 0.05)
chk("Q32 P", Br**2*lr**2*vr**2/Rr, 0.5)

# Q33 solenoid L and U at I=2
chk("Q33 L", L6, 2.5133e-3)
chk("Q33 U", 0.5*L6*2**2, 5.0265e-3)

# Q34 two solenoids: M and emf2 at dI1/dt = 100
M34 = mu0*N1*N2*A6/l6
chk("Q34 M",    M34, 1.2566e-3)
chk("Q34 emf2", M34*100, 0.12566)

# Q35 coil: L and flux linkage
chk("Q35 L",            200*5e-3/2, 0.5)
chk("Q35 flux linkage", 200*5e-3, 1.0)

# Q36 induced charge and average current
q36 = 100*2e-3/10
chk("Q36 q",     q36, 0.02)
chk("Q36 I_avg", q36/0.1, 0.2)

# Q37 energy density and total energy in solenoid volume
V37 = A6*l6
u37 = 0.5**2/(2*mu0)
chk("Q37 u", u37, 9.9472e4)
chk("Q37 V", V37, 5e-4)
chk("Q37 U = u V", u37*V37, 49.736)

# Q38 AC generator peak and rms
e0 = 100*0.5*0.02*100
chk("Q38 peak emf", e0, 100)
chk("Q38 rms emf",  e0/math.sqrt(2), 70.711)

# Q39 time constant and max current
chk("Q39 tau",   0.5/10, 0.05)
chk("Q39 I_max", 20/10, 2)

# Q40 flux at 0 and 60 deg
chk("Q40 phi(0)",  B*A, 0.01)
chk("Q40 phi(60)", B*A*math.cos(math.radians(60)), 5e-3)

print("\n=== SHRENI 3 : hard numericals ===")
# Q52 rod complete analysis
chk("Q52 emf",       Br*lr*vr, 1.0)
chk("Q52 I",         Br*lr*vr/Rr, 0.5)
chk("Q52 F",         Br**2*lr**2*vr/Rr, 0.05)
chk("Q52 P_elec",    (Br*lr*vr/Rr)**2*Rr, 0.5)
chk("Q52 P_mech",    Br**2*lr**2*vr**2/Rr, 0.5)

# Q54 rotating coil
chk("Q54 peak emf", e0, 100)
chk("Q54 rms emf",  e0/math.sqrt(2), 70.711)
chk("Q54 frequency", 100/(2*math.pi), 15.915)

# Q56 induced charge independent of time (same q for two durations)
chk("Q56 q (dt=0.1)", 100*2e-3/10, 0.02)
chk("Q56 q (dt=2.0)", 100*2e-3/10, 0.02)

# Q58 mutual inductance with coupling k=1
chk("Q58 M = sqrt(L1 L2)", math.sqrt(0.5*0.2), 0.31623)
chk("Q58 M at k=0.5",  0.5*math.sqrt(0.5*0.2), 0.15811)

print(f"\n{'='*66}\n{sum(ok)}/{len(ok)} checks passed"
      f"{'  -- ALL GOOD' if all(ok) else '  -- FIX NEEDED'}")
