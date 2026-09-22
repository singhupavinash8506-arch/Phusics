"""अध्याय 4 — गतिमान आवेश और चुम्बकत्व। हर संख्यात्मक उत्तर मूल सिद्धान्तों से पुनः गणना।"""
import math

mu0   = 4*math.pi*1e-7      # T m/A
k_mag = mu0/(4*math.pi)     # = 1e-7
e     = 1.6e-19
me    = 9.1e-31
mp    = 1.67e-27

ok = []
def chk(tag, got, want, tol=0.02):
    rel = abs(got-want)/abs(want) if want else abs(got)
    s = "OK " if rel <= tol else "FAIL"
    ok.append(s == "OK ")
    print(f"{s} {tag:<48} got={got:.6g}  want={want:.6g}")

print("=== SHRENI 1 : direct formula ===")
chk("Q1  B straight wire I=10 r=0.05",     mu0*10/(2*math.pi*0.05), 4e-5)
chk("Q2  B loop centre N=50 I=2 R=0.1",    mu0*50*2/(2*0.1), 6.283e-4)
chk("Q3  B solenoid n=1000 I=5",           mu0*1000*5, 6.283e-3)
chk("Q4  F=qvB  1.6e-19,1e6,0.5",          e*1e6*0.5, 8e-14)
chk("Q5  F=BIL  0.5,4,0.2",                0.5*4*0.2, 0.4)
r6 = me*1e6/(e*0.5)
chk("Q6  r=mv/qB electron v=1e6 B=0.5",    r6, 1.1375e-5)
chk("Q7  T=2 pi m/(qB)",                   2*math.pi*me/(e*0.5), 7.147e-11)
chk("Q8  F/L parallel 10A,10A,d=0.1",      mu0*10*10/(2*math.pi*0.1), 2e-4)
chk("Q9  m=NIA  100,2,0.01",               100*2*0.01, 2)
chk("Q10 tau=mB sin90  m=2 B=0.5",         2*0.5*math.sin(math.radians(90)), 1)
chk("Q11 B toroid N=500 I=2 r=0.1",        mu0*500*2/(2*math.pi*0.1), 2e-3)
chk("Q12 dB Biot-Savart I=5 dl=0.01 r=0.1",k_mag*5*0.01*1/(0.1**2), 5e-7)
chk("Q13 v=E/B  1e4/0.02",                 1e4/0.02, 5e5)
chk("Q14 cyclotron f proton B=1",          e*1/(2*math.pi*mp), 1.525e7)
Ig, G = 0.01, 99.0
chk("Q15 shunt S=IgG/(I-Ig) I=1",          Ig*G/(1-Ig), 1.0)
chk("Q16 voltmeter R=V/Ig - G  V=10",      10/Ig - G, 901)
chk("Q17 current sensitivity NAB/C",       100*0.01*0.5/1e-6, 5e5)
chk("Q18 F/L  5A,10A,d=0.2",               mu0*5*10/(2*math.pi*0.2), 5e-5)
chk("Q19 B semicircular arc I=4 R=0.1",    mu0*4/(4*0.1), 1.2566e-5)
# Q20 work by magnetic force = 0 (exact)

print("\n=== SHRENI 2a : one unknown ===")
chk("Q21 I from B=4e-5 r=0.05",            4e-5*2*math.pi*0.05/mu0, 10)
chk("Q22 n from B=6.283e-3 I=5",           6.283e-3/(mu0*5), 1000)
chk("Q23 B from F=0.4 I=4 L=0.2",          0.4/(4*0.2), 0.5)
chk("Q24 v from r=1.1375e-5 B=0.5",        r6*e*0.5/me, 1e6)
chk("Q25 d from F/L=2e-4 I=10,10",         mu0*10*10/(2*math.pi*2e-4), 0.1)
chk("Q26 sin theta from tau=1 m=2 B=0.5",  math.degrees(math.asin(1/(2*0.5))), 90)
chk("Q27 I from m=2 N=100 A=0.01",         2/(100*0.01), 2)
chk("Q28 I from S=1 G=99 Ig=0.01",         Ig*G/1.0 + Ig, 1.0)
chk("Q29 N from B=6.283e-4 I=2 R=0.1",     6.283e-4*2*0.1/(mu0*2), 50)
chk("Q30 E from v=5e5 B=0.02",             5e5*0.02, 1e4)

print("\n=== SHRENI 2b : two unknowns ===")
def roots(S, P):
    d = S*S - 4*P
    return ((S+math.sqrt(d))/2, (S-math.sqrt(d))/2)

# Q31 galvanometer G=99, Ig=0.01 -> ammeter 1A and voltmeter 10V
chk("Q31 shunt for 1 A",     Ig*G/(1-Ig), 1.0)
chk("Q31 series for 10 V",   10/Ig - G, 901)

# Q32 two wires: sum 15 A, F/L = 5e-5 at d=0.2
P32 = 5e-5*2*math.pi*0.2/mu0
chk("Q32 product I1*I2", P32, 50)
a,b = roots(15, P32); chk("Q32 root A", a, 10); chk("Q32 root B", b, 5)

# Q33 electron v=1e6 B=0.5 -> r and T
chk("Q33 r", me*1e6/(e*0.5), 1.1375e-5)
chk("Q33 T", 2*math.pi*me/(e*0.5), 7.147e-11)

# Q34 coil N=50 R=0.1 B=6.283e-4 -> I and m
I34 = 6.283e-4*2*0.1/(mu0*50); chk("Q34 I", I34, 2)
A34 = math.pi*0.1**2
chk("Q34 m = NIA", 50*I34*A34, 3.1416)

# Q35 solenoid L=0.5 m, B=6.283e-3, I=5 -> n and N
n35 = 6.283e-3/(mu0*5); chk("Q35 n", n35, 1000)
chk("Q35 N = n L", n35*0.5, 500)

# Q36 velocity selector E=1e4 B=0.02 -> v ; then r for electron
v36 = 1e4/0.02; chk("Q36 v", v36, 5e5)
chk("Q36 r", me*v36/(e*0.02), 1.4219e-4)

# Q37 cyclotron proton B=1 R=0.5 -> f and KE_max
chk("Q37 f", e*1/(2*math.pi*mp), 1.525e7)
vmax = e*1*0.5/mp; chk("Q37 v_max", vmax, 4.7904e7)
KE = 0.5*mp*vmax**2
chk("Q37 KE (J)",   KE, 1.9157e-12)
chk("Q37 KE (MeV)", KE/1.6e-13, 11.973)

# Q38 galvanometer sensitivities N=100 A=0.01 B=0.5 C=1e-6 R=100
chk("Q38 current sensitivity", 100*0.01*0.5/1e-6, 5e5)
chk("Q38 voltage sensitivity", 100*0.01*0.5/(1e-6*100), 5e3)

# Q39 wire length 6.28 m bent into N=10 turns, I=2 -> R and B
R39 = 6.28/(10*2*math.pi); chk("Q39 R", R39, 0.09995)
chk("Q39 B centre", mu0*10*2/(2*R39), 1.2566e-4)

# Q40 tau_max=1, B=0.5, N=100, A=0.01 -> m and I
m40 = 1/0.5; chk("Q40 m", m40, 2)
chk("Q40 I", m40/(100*0.01), 2)

print("\n=== SHRENI 3 : hard numericals ===")
# Q53 two parallel wires 10 A and 20 A, d=0.1, same direction, B at midpoint
B1 = mu0*10/(2*math.pi*0.05); B2 = mu0*20/(2*math.pi*0.05)
chk("Q53 B1 at midpoint", B1, 4e-5)
chk("Q53 B2 at midpoint", B2, 8e-5)
chk("Q53 net (opposite at midpoint)", abs(B2-B1), 4e-5)

# Q54 helical path: v=1e6 at 30 deg to B=0.5 (electron)
vperp = 1e6*math.sin(math.radians(30)); vpar = 1e6*math.cos(math.radians(30))
chk("Q54 v_perp", vperp, 5e5)
chk("Q54 v_par",  vpar, 8.6603e5)
chk("Q54 r",      me*vperp/(e*0.5), 5.6875e-6)
T54 = 2*math.pi*me/(e*0.5)
chk("Q54 T",      T54, 7.147e-11)
chk("Q54 pitch",  vpar*T54, 6.1898e-5)

# Q56 F = BIL sin30
chk("Q56 F at 30 deg", 0.5*4*0.2*math.sin(math.radians(30)), 0.2)

# Q58 galvanometer G=100, Ig=1mA -> ammeter 10 A
chk("Q58 shunt", 0.001*100/(10-0.001), 0.010001)

# Q59 loop N=100 I=2 r=0.05 -> m and torque at 30 deg in B=0.4
A59 = math.pi*0.05**2
m59 = 100*2*A59
chk("Q59 A", A59, 7.854e-3)
chk("Q59 m", m59, 1.5708)
chk("Q59 tau at 30", m59*0.4*math.sin(math.radians(30)), 0.31416)

print(f"\n{'='*66}\n{sum(ok)}/{len(ok)} checks passed"
      f"{'  -- ALL GOOD' if all(ok) else '  -- FIX NEEDED'}")
