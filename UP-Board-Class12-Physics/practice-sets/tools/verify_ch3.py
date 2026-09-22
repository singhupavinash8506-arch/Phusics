"""अध्याय 3 — विद्युत धारा। हर संख्यात्मक उत्तर मूल सिद्धान्तों से पुनः गणना।"""
import math

e  = 1.6e-19
me = 9.1e-31

ok = []
def chk(tag, got, want, tol=0.02):
    rel = abs(got-want)/abs(want) if want else abs(got)
    s = "OK " if rel <= tol else "FAIL"
    ok.append(s == "OK ")
    print(f"{s} {tag:<46} got={got:.6g}  want={want:.6g}")

print("=== SHRENI 1 : direct formula ===")
chk("Q1  I=q/t  30C in 10s",            30/10, 3)
chk("Q2  I=V/R  12V, 4ohm",             12/4, 3)
rho, L, A = 1.7e-8, 2.0, 1e-6
chk("Q3  R=rho*L/A",                    rho*L/A, 0.034)
n_cu = 8.5e28
chk("Q4  v_d=I/(neA)  I=3,A=1e-6",      3/(n_cu*e*1e-6), 2.206e-4)
chk("Q5  P=VI  220V,5A",                220*5, 1100)
chk("Q6  P=I^2R  2A,50ohm",             2**2*50, 200)
chk("Q7  P=V^2/R  220V,44ohm",          220**2/44, 1100)
chk("Q8  series 2+3+5",                 2+3+5, 10)
chk("Q9  parallel 6 & 3",               1/(1/6+1/3), 2)
chk("Q10 I=emf/(R+r) 12V,5,1",          12/(5+1), 2)
chk("Q11 V=emf-Ir  12-2*1",             12-2*1, 10)
chk("Q12 Rt=R0(1+a dT) 100,0.004,50",   100*(1+0.004*50), 120)
chk("Q13 sigma=1/rho  2e-8",            1/2e-8, 5e7)
chk("Q14 J=I/A  5A, 2e-6",              5/2e-6, 2.5e6)
chk("Q15 mu=v_d/E  2e-4 / 2",           2e-4/2, 1e-4)
chk("Q16 Wheatstone S=QR/P  2,4,3",     4*3/2, 6)
chk("Q17 metre bridge S=R(100-l)/l",    4*(100-40)/40, 6)
chk("Q18 k=V/L  2V, 10m",               2/10, 0.2)
chk("Q19 W=Pt  1000W, 2h (kWh)",        1000*2/1000, 2)
nS, emf, r, R = 3, 2.0, 0.5, 4.5
chk("Q20 n cells series I",             nS*emf/(R+nS*r), 1)

print("\n=== SHRENI 2a : one unknown ===")
chk("Q21 t=q/I  30C, 3A",               30/3, 10)
chk("Q22 R=V/I  12V, 3A",               12/3, 4)
chk("Q23 rho=RA/L  0.034,1e-6,2",       0.034*1e-6/2, 1.7e-8)
vd24 = 2.206e-4
chk("Q24 n=I/(e A v_d)",                3/(e*1e-6*vd24), 8.5e28)
chk("Q25 R=V^2/P  220V,1100W",          220**2/1100, 44)
chk("Q26 R3 = 10-2-3",                  10-2-3, 5)
chk("Q27 R2 parallel: tot2, R1=6",      1/(1/2-1/6), 3)
chk("Q28 r=emf/I - R  12/2-5",          12/2-5, 1)
chk("Q29 alpha=(Rt-R0)/(R0 dT)",        (120-100)/(100*50), 0.004)
chk("Q30 l=100R/(R+S)  4,6",            100*4/(4+6), 40)

print("\n=== SHRENI 2b : two unknowns ===")
def roots(S, P):
    d = S*S - 4*P
    return ((S+math.sqrt(d))/2, (S-math.sqrt(d))/2)

# Q31 series 10, parallel 2.4
P31 = 2.4*10
chk("Q31 product", P31, 24)
a,b = roots(10, P31); chk("Q31 root A", a, 6); chk("Q31 root B", b, 4)

# Q32 series 9, parallel 2
P32 = 2*9
chk("Q32 product", P32, 18)
a,b = roots(9, P32); chk("Q32 root A", a, 6); chk("Q32 root B", b, 3)

# Q33 emf,r from two (I,R) readings: 2A@5ohm, 1.5A@7ohm
# emf = I(R+r) -> 2(5+r) = 1.5(7+r)
r33 = (1.5*7 - 2*5)/(2-1.5); chk("Q33 r", r33, 1)
chk("Q33 emf", 2*(5+r33), 12)

# Q34 emf,r from terminal PD: V=10 at I=2 ; V=11 at I=1
# 10 = e-2r ; 11 = e-r
r34 = (11-10)/(2-1); chk("Q34 r", r34, 1)
chk("Q34 emf", 11 + r34*1, 12)

# Q35 wire 10 ohm cut 1:4, parts in parallel
p1, p2 = 10*1/5, 10*4/5
chk("Q35 part 1", p1, 2); chk("Q35 part 2", p2, 8)
chk("Q35 parallel of parts", 1/(1/p1+1/p2), 1.6)

# Q36 bulb 1100 W at 220 V
chk("Q36 R", 220**2/1100, 44); chk("Q36 I", 1100/220, 5)

# Q37 potentiometer: l1=60,l2=40, emf sum 5
# e1/e2 = 60/40
e2_37 = 5/(1 + 60/40); e1_37 = 5 - e2_37
chk("Q37 emf1", e1_37, 3); chk("Q37 emf2", e2_37, 2)

# Q38 internal resistance by potentiometer: l1=60,l2=50,R=5 ; k=0.02 V/cm
chk("Q38 r = R(l1-l2)/l2", 5*(60-50)/50, 1)
chk("Q38 emf = k*l1", 0.02*60, 1.2)

# Q39 n cells series: I=1 with R=4.5, emf=2, r=0.5
# 1 = 2n/(4.5+0.5n)
n39 = 4.5/(2-0.5); chk("Q39 n", n39, 3)
chk("Q39 total emf", n39*2, 6); chk("Q39 total r", n39*0.5, 1.5)

# Q40 J and v_d for I=5, A=2e-6
J40 = 5/2e-6; chk("Q40 J", J40, 2.5e6)
chk("Q40 v_d = J/(ne)", J40/(n_cu*e), 1.838e-4)

print("\n=== SHRENI 3 : hard numericals ===")
# Q53 two cells in parallel driving R=3 : 10V/1ohm and 4V/1ohm
emf_eq = (10/1 + 4/1)/(1/1 + 1/1); r_eq = 1/(1/1 + 1/1)
chk("Q53 equivalent emf", emf_eq, 7)
chk("Q53 equivalent r",   r_eq, 0.5)
chk("Q53 current through 3ohm", emf_eq/(3+r_eq), 2)

# Q54 network: (8 || 8) + 2 , across 12 V
Rnet = 1/(1/8+1/8) + 2
chk("Q54 network R", Rnet, 6)
chk("Q54 current", 12/Rnet, 2)

# Q55 wire stretched to double length (volume constant)
chk("Q55 R' = 4R  (R=4)", 4*4, 16)

# Q57 max power transfer: emf 12, r 1
chk("Q57 R for max power", 1, 1)
chk("Q57 P_max = emf^2/(4r)", 12**2/(4*1), 36)

# Q59 metre bridge: R=4, S replaced by 4 -> new balance length
chk("Q59 new l = 100R/(R+S')", 100*4/(4+4), 50)

print(f"\n{'='*62}\n{sum(ok)}/{len(ok)} checks passed"
      f"{'  -- ALL GOOD' if all(ok) else '  -- FIX NEEDED'}")
