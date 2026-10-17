# -*- coding: utf-8 -*-
"""Compact black line-art schematics, styled like the reference sheet."""

S = ('stroke="#11100e" fill="none" stroke-width="1" '
     'stroke-linecap="round" stroke-linejoin="round"')
SF = 'fill="#11100e" stroke="none"'
TXT = ('font-family="CMU,serif" font-size="7.4" font-style="italic" '
       'fill="#11100e" stroke="none"')
TXU = ('font-family="CMU,serif" font-size="7.2" fill="#11100e" stroke="none"')
DEV = ('font-family="Dev,sans-serif" font-size="6.6" fill="#11100e" stroke="none"')


def _wrap(w, h, body):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs><marker id="ar" markerWidth="7" markerHeight="7" refX="6" refY="2.3" '
            f'orient="auto"><path d="M0,0 L6,2.3 L0,4.6 z" fill="#11100e"/></marker>'
            f'<marker id="ars" markerWidth="5.5" markerHeight="5.5" refX="4.8" refY="1.8" '
            f'orient="auto"><path d="M0,0 L4.8,1.8 L0,3.6 z" fill="#11100e"/></marker>'
            f'</defs>{body}</svg>')


# ======================================================== Chapter 10 Wave Optics
def huygens():
    b = f'<path d="M14 6 L14 62" {S}/>'
    for cy in (16, 34, 52):
        b += f'<circle cx="14" cy="{cy}" r="13" {S} stroke-dasharray="2.4 2"/>'
        b += f'<circle cx="14" cy="{cy}" r="1.5" {SF}/>'
    b += f'<path d="M27 6 L27 62" {S}/>'
    b += f'<path d="M31 34 L48 34" {S} marker-end="url(#ar)"/>'
    b += f'<text x="4" y="70" {TXU}>AB</text><text x="22" y="70" {TXU}>A&#8242;B&#8242;</text>'
    return _wrap(116, 74, b)


def ydse():
    b = f'<path d="M8 10 L8 62" {S}/>'
    b += f'<path d="M30 10 L30 28 M30 34 L30 38 M30 44 L30 62" {S}/>'
    b += f'<circle cx="30" cy="31" r="1.5" {SF}/><circle cx="30" cy="41" r="1.5" {SF}/>'
    b += f'<path d="M8 36 L28 31 M8 36 L28 41" {S} stroke-width=".85"/>'
    b += f'<path d="M94 8 L94 64" {S}/>'
    for y, w in ((16, 3), (24, 5), (32, 7), (40, 5), (48, 3)):
        b += f'<rect x="91" y="{y}" width="6" height="{w}" {SF}/>'
    b += f'<path d="M30 31 L94 24 M30 41 L94 48" {S} stroke-width=".85"/>'
    b += f'<text x="52" y="60" {TXT}>D</text>'
    b += f'<text x="34" y="39" {TXT}>d</text>'
    b += f'<text x="100" y="35" {TXT}>&#946;</text>'
    return _wrap(118, 72, b)


def single_slit():
    b = f'<path d="M6 8 L6 60" {S}/>'
    b += f'<path d="M26 8 L26 28 M26 40 L26 60" {S}/>'
    b += f'<path d="M6 34 L24 34" {S} stroke-width=".85"/>'
    b += f'<text x="30" y="37" {TXT}>a</text>'
    b += f'<path d="M86 6 L86 62" {S}/>'
    b += f'<path d="M26 34 L86 34" {S} stroke-width=".85"/>'
    b += f'<path d="M26 34 L86 16 M26 34 L86 52" {S} stroke-width=".7" stroke-dasharray="2 1.6"/>'
    # intensity envelope
    b += (f'<path d="M98 34 C101 34 102 12 105 12 C108 12 109 34 112 34 '
          f'C114 34 114 27 116 27 C118 27 118 34 120 34" {S} stroke-width=".9"/>')
    b += f'<text x="60" y="13" {TXT}>&#955;/a</text>'
    return _wrap(124, 70, b)


def polaroid():
    b = f'<path d="M4 30 L22 30" {S} marker-end="url(#ars)"/>'
    for x in (8, 14, 20):
        b += f'<path d="M{x} 24 L{x} 36" {S} stroke-width=".7"/>'
    b += f'<rect x="26" y="10" width="7" height="42" {S}/>'
    for y in range(14, 50, 5):
        b += f'<path d="M27 {y} L32 {y}" {S} stroke-width=".65"/>'
    b += f'<rect x="62" y="10" width="7" height="42" {S} transform="rotate(0 65 31)"/>'
    for y in range(14, 50, 5):
        b += f'<path d="M63 {y} L68 {y}" {S} stroke-width=".65" transform="rotate(22 65 31)"/>'
    b += f'<path d="M36 31 L59 31" {S}/>'
    b += f'<path d="M72 31 L90 31" {S} marker-end="url(#ars)"/>'
    b += f'<text x="24" y="62" {TXU}>P</text><text x="60" y="62" {TXU}>A</text>'
    b += f'<text x="74" y="24" {TXT}>&#952;</text>'
    return _wrap(96, 68, b)


def brewster():
    b = f'<path d="M6 36 L92 36" {S}/>'
    b += f'<path d="M49 6 L49 66" {S} stroke-dasharray="3 2.4" stroke-width=".8"/>'
    b += f'<path d="M14 10 L47 35" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M50 35 L84 11" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M51 37 L72 62" {S} marker-end="url(#ars)" stroke-dasharray="2.6 2"/>'
    b += f'<path d="M49 22 A 15 15 0 0 0 36 28" {S} stroke-width=".75"/>'
    b += f'<text x="30" y="20" {TXT}>i<tspan dy="2" font-size="5.6">p</tspan></text>'
    b += f'<text x="62" y="20" {TXT}>r</text>'
    b += f'<text x="4" y="48" {DEV}>&#2357;&#2366;&#2351;&#2369;</text>'
    b += f'<text x="62" y="48" {DEV}>&#2350;&#2366;&#2343;&#2381;&#2351;&#2350;</text>'
    return _wrap(98, 70, b)


# ================================================== Chapter 11 Dual Nature
def photocell():
    b = f'<path d="M10 14 A 22 22 0 0 0 10 50" {S}/>'
    b += f'<path d="M34 20 L34 44" {S} stroke-width="1.6"/>'
    b += f'<path d="M2 6 L14 18 M2 12 L14 24 M2 18 L14 30" {S} stroke-width=".7"/>'
    b += f'<text x="0" y="60" {DEV}>&#2346;&#2381;&#2352;&#2325;&#2366;&#2358;</text>'
    b += f'<path d="M10 50 L10 64 L52 64" {S}/><path d="M34 44 L34 8 L72 8" {S}/>'
    b += f'<circle cx="62" cy="64" r="8" {S}/><text x="58" y="67" {TXU}>&#956;A</text>'
    b += f'<path d="M72 64 L86 64 L86 30" {S}/>'
    b += f'<path d="M72 8 L86 8 L86 22" {S}/>'
    b += f'<path d="M78 22 L94 22 M80 26 L92 26 M78 30 L94 30" {S} stroke-width=".9"/>'
    b += f'<text x="88" y="44" {TXT}>V</text>'
    return _wrap(104, 72, b)


def v0_vs_nu():
    b = f'<path d="M14 58 L14 8" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M6 48 L96 48" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M36 48 L88 14" {S}/>'
    b += f'<circle cx="36" cy="48" r="1.6" {SF}/>'
    b += f'<path d="M36 48 L36 56" {S} stroke-width=".7" stroke-dasharray="2 1.6"/>'
    b += f'<text x="30" y="65" {TXT}>&#957;<tspan dy="2" font-size="5.6">0</tspan></text>'
    b += f'<text x="90" y="60" {TXT}>&#957;</text><text x="2" y="12" {TXT}>V<tspan dy="2" font-size="5.6">0</tspan></text>'
    b += f'<text x="52" y="26" {TXT}>h/e</text>'
    return _wrap(104, 70, b)


def photocurrent():
    b = f'<path d="M34 56 L34 6" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M4 44 L98 44" {S} marker-end="url(#ars)"/>'
    b += (f'<path d="M10 44 C18 44 24 40 34 30 C44 20 56 14 90 14" {S}/>')
    b += (f'<path d="M18 44 C24 44 28 42 34 36 C44 27 56 23 90 23" {S} '
          f'stroke-dasharray="2.6 2"/>')
    b += f'<circle cx="10" cy="44" r="1.5" {SF}/>'
    b += f'<text x="0" y="56" {TXT}>&#8722;V<tspan dy="2" font-size="5.6">0</tspan></text>'
    b += f'<text x="88" y="56" {TXT}>V</text><text x="18" y="12" {TXT}>I</text>'
    b += f'<text x="62" y="11" {DEV}>&#2360;&#2306;&#2340;&#2371;&#2346;&#2381;&#2340;</text>'
    return _wrap(104, 64, b)


def davisson():
    b = f'<path d="M6 10 L30 30" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M10 54 L74 54" {S} stroke-width="1.4"/>'
    for x in range(14, 72, 7):
        b += f'<circle cx="{x}" cy="58" r="1.5" {SF}/>'
        b += f'<circle cx="{x}" cy="64" r="1.5" {SF}/>'
    b += f'<path d="M34 32 L62 12" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M32 31 A 20 20 0 0 0 46 20" {S} stroke-width=".7"/>'
    b += f'<text x="44" y="30" {TXT}>&#966;</text>'
    b += f'<text x="2" y="24" {TXT}>e<tspan dy="-3" font-size="5.6">&#8722;</tspan></text>'
    b += f'<text x="74" y="66" {TXT}>d</text>'
    b += f'<text x="62" y="46" {TXU}>Ni</text>'
    return _wrap(92, 72, b)


# ====================================================== Chapter 12 Atoms
def rutherford():
    b = f'<circle cx="52" cy="36" r="3.2" {SF}/>'
    b += f'<circle cx="52" cy="36" r="11" {S} stroke-dasharray="2 2" stroke-width=".7"/>'
    b += f'<path d="M4 58 L36 46" {S}/>'
    b += (f'<path d="M36 46 C46 42 54 30 50 14" {S} marker-end="url(#ars)"/>')
    b += f'<path d="M4 44 L34 38" {S}/>'
    b += (f'<path d="M34 38 C48 34 62 30 86 24" {S} marker-end="url(#ars)"/>')
    b += f'<path d="M4 30 L86 14" {S} stroke-dasharray="2.6 2" stroke-width=".8"/>'
    b += f'<path d="M4 66 L86 62" {S} stroke-width=".8"/>'
    b += f'<text x="56" y="30" {TXU}>+Ze</text>'
    b += f'<text x="62" y="40" {TXT}>&#952;</text>'
    b += f'<text x="20" y="34" {TXT}>b</text>'
    b += f'<text x="0" y="22" {TXT}>&#945;</text>'
    return _wrap(96, 74, b)


def bohr_orbits():
    b = f'<circle cx="40" cy="36" r="2.8" {SF}/>'
    for r, n in ((10, "1"), (19, "2"), (28, "3")):
        b += f'<circle cx="40" cy="36" r="{r}" {S} stroke-width=".85"/>'
        b += f'<text x="{40+r-3}" y="{36-r+9}" {TXT}>{n}</text>'
    b += f'<circle cx="50" cy="36" r="1.8" {SF}/>'
    b += f'<circle cx="40" cy="17" r="1.8" {SF}/>'
    b += (f'<path d="M48 30 L42 20" {S} stroke-width=".8" marker-end="url(#ars)"/>')
    b += f'<text x="70" y="24" {TXT}>r<tspan dy="2" font-size="5.6">n</tspan></text>'
    b += f'<text x="68" y="36" {TXU}>=</text>'
    b += f'<text x="76" y="36" {TXT}>a<tspan dy="2" font-size="5.6">0</tspan>'
    b += f'<tspan dy="-2">n</tspan><tspan dy="-3" font-size="5.6">2</tspan></text>'
    return _wrap(104, 74, b)


def energy_levels():
    b = ""
    ys = {1: 62, 2: 36, 3: 24, 4: 17, 5: 12}
    for n, y in ys.items():
        b += f'<path d="M22 {y} L86 {y}" {S} stroke-width=".9"/>'
        b += f'<text x="90" y="{y+2.6}" {TXT}>{n}</text>'
    b += f'<path d="M22 7 L86 7" {S} stroke-dasharray="2.4 2" stroke-width=".8"/>'
    b += f'<text x="88" y="9.6" {TXT}>&#8734;</text>'
    # Lyman, Balmer, Paschen
    b += f'<path d="M30 36 L30 62" {S} stroke-width=".9" marker-end="url(#ars)"/>'
    b += f'<path d="M40 24 L40 62" {S} stroke-width=".9" marker-end="url(#ars)"/>'
    b += f'<path d="M56 24 L56 36" {S} stroke-width=".9" marker-end="url(#ars)"/>'
    b += f'<path d="M68 17 L68 36" {S} stroke-width=".9" marker-end="url(#ars)"/>'
    b += f'<path d="M78 17 L78 24" {S} stroke-width=".9" marker-end="url(#ars)"/>'
    b += f'<text x="0" y="65" {TXT}>n</text>'
    b += f'<text x="0" y="40" {TXU}>E</text>'
    b += f'<text x="24" y="72" {TXU}>Ly</text><text x="48" y="72" {TXU}>Ba</text>'
    b += f'<text x="70" y="72" {TXU}>Pa</text>'
    return _wrap(100, 76, b)


# ======================================================= Chapter 13 Nuclei
def be_curve():
    b = f'<path d="M16 60 L16 6" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M12 56 L100 56" {S} marker-end="url(#ars)"/>'
    b += (f'<path d="M19 50 C22 30 26 18 34 15 C44 11 52 13 62 18 '
          f'C74 24 86 30 96 34" {S}/>')
    b += f'<circle cx="38" cy="13.4" r="1.5" {SF}/>'
    b += f'<path d="M38 13.4 L38 56" {S} stroke-width=".65" stroke-dasharray="2 1.7"/>'
    b += f'<text x="30" y="66" {TXU}>56</text>'
    b += f'<text x="94" y="66" {TXT}>A</text>'
    b += f'<text x="0" y="12" {TXT}>E<tspan dy="2" font-size="5.6">b</tspan>/A</text>'
    b += f'<text x="42" y="11" {TXU}>8.8</text>'
    return _wrap(106, 70, b)


def decay_curve():
    b = f'<path d="M16 58 L16 6" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M12 54 L98 54" {S} marker-end="url(#ars)"/>'
    b += (f'<path d="M16 10 C34 10 40 30 52 40 C64 50 76 52 94 53" {S}/>')
    b += f'<path d="M16 32 L40 32" {S} stroke-width=".65" stroke-dasharray="2 1.7"/>'
    b += f'<path d="M40 32 L40 54" {S} stroke-width=".65" stroke-dasharray="2 1.7"/>'
    b += f'<path d="M16 43 L58 43" {S} stroke-width=".65" stroke-dasharray="2 1.7"/>'
    b += f'<path d="M58 43 L58 54" {S} stroke-width=".65" stroke-dasharray="2 1.7"/>'
    b += f'<text x="0" y="13" {TXT}>N<tspan dy="2" font-size="5.6">0</tspan></text>'
    b += f'<text x="0" y="35" {TXU}>N<tspan dy="2" font-size="5.6">0</tspan>/2</text>'
    b += f'<text x="34" y="64" {TXT}>T<tspan dy="2" font-size="5.6">1/2</tspan></text>'
    b += f'<text x="90" y="64" {TXT}>t</text>'
    return _wrap(104, 70, b)


def fission():
    b = f'<circle cx="8" cy="30" r="2.2" {SF}/>'
    b += f'<path d="M12 30 L26 30" {S} marker-end="url(#ars)"/>'
    b += f'<circle cx="38" cy="30" r="10" {S}/>'
    b += f'<text x="30" y="33" {TXU}>U</text>'
    b += f'<circle cx="68" cy="14" r="7" {S}/><text x="62" y="17" {TXU}>Ba</text>'
    b += f'<circle cx="68" cy="48" r="7" {S}/><text x="62" y="51" {TXU}>Kr</text>'
    b += f'<path d="M48 26 L60 17" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M48 34 L60 45" {S} marker-end="url(#ars)"/>'
    for dy in (-7, 0, 7):
        b += f'<path d="M78 {31+dy*1.1} L92 {31+dy*1.6}" {S} stroke-width=".8" marker-end="url(#ars)"/>'
    b += f'<text x="84" y="12" {TXT}>n</text>'
    b += f'<text x="20" y="62" {TXU}>+ 200 MeV</text>'
    return _wrap(104, 68, b)


def nuclear_well():
    b = f'<path d="M8 14 L8 58" {S} marker-end="url(#ars)" transform="translate(0,-4)"/>'
    b += f'<path d="M4 36 L96 36" {S} marker-end="url(#ars)"/>'
    b += (f'<path d="M20 10 L20 36 L30 36 L30 58 L54 58 '
          f'C70 58 78 42 92 38" {S}/>')
    b += f'<text x="30" y="68" {TXT}>r<tspan dy="2" font-size="5.6">0</tspan> &#8776; 0.8 fm</text>'
    b += f'<text x="0" y="12" {TXT}>U</text>'
    b += f'<text x="56" y="52" {TXU}>&#8722;100 MeV</text>'
    return _wrap(102, 72, b)


# ============================================ Chapter 14 Semiconductor
def bands():
    out = ""
    labels = ("\u0a1a", "", "")
    xs = (4, 40, 76)
    gaps = ((22, 30), (18, 34), (10, 44))
    names = ("&#2330;&#2366;&#2354;&#2325;", "&#2309;&#2352;&#2381;&#2343;&#2330;&#2366;&#2354;&#2325;",
             "&#2325;&#2369;&#2330;&#2366;&#2354;&#2325;")
    for x, (top, bot), nm in zip(xs, gaps, names):
        out += f'<rect x="{x}" y="{top-14}" width="26" height="14" {S} fill="#d8d8d8"/>'
        out += f'<rect x="{x}" y="{bot}" width="26" height="14" {S} fill="#8f8f8f"/>'
        if bot > top:
            out += (f'<path d="M{x+13} {top} L{x+13} {bot}" {S} stroke-width=".7" '
                    f'stroke-dasharray="2 1.6"/>')
        out += f'<text x="{x-1}" y="70" {DEV}>{nm}</text>'
    out += f'<text x="30" y="20" {TXT}>E<tspan dy="2" font-size="5.6">g</tspan></text>'
    return _wrap(108, 74, out)


def pn_junction():
    b = f'<rect x="8" y="16" width="38" height="30" {S} fill="#eeeeee"/>'
    b += f'<rect x="46" y="16" width="38" height="30" {S} fill="#dcdcdc"/>'
    b += f'<rect x="38" y="16" width="16" height="30" {S} fill="#ffffff"/>'
    for i, x in enumerate((16, 26, 34)):
        b += f'<text x="{x}" y="28" {TXU}>+</text>'
    for x in (58, 68, 76):
        b += f'<text x="{x}" y="28" {TXU}>&#8722;</text>'
    for x in (40, 46):
        b += f'<text x="{x}" y="41" {TXU}>&#8722;</text>'
    for x in (48, 52):
        b += f'<text x="{x}" y="41" {TXU}>+</text>'
    b += f'<text x="20" y="12" {TXT}>p</text><text x="64" y="12" {TXT}>n</text>'
    b += f'<path d="M38 50 L38 58 M54 50 L54 58" {S} stroke-width=".7"/>'
    b += f'<path d="M38 55 L54 55" {S} stroke-width=".8"/>'
    b += f'<text x="30" y="70" {DEV}>&#2361;&#2381;&#2352;&#2366;&#2360;&#2404; &#2360;&#2306;&#2343;&#2367;</text>'
    return _wrap(96, 74, b)


def diode_iv():
    b = f'<path d="M48 62 L48 4" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M4 36 L96 36" {S} marker-end="url(#ars)"/>'
    b += (f'<path d="M64 36 C70 36 72 26 74 14 C75 9 76 7 77 6" {S}/>')
    b += f'<path d="M48 36 L64 36" {S}/>'
    b += f'<path d="M48 37.6 L18 38.6" {S}/>'
    b += f'<path d="M18 38.6 L14 38.8 L14 58" {S}/>'
    b += f'<text x="58" y="48" {DEV}>&#2309;&#2327;&#2381;&#2352;</text>'
    b += f'<text x="16" y="22" {DEV}>&#2346;&#2358;&#2381;&#2330;</text>'
    b += f'<text x="80" y="20" {TXT}>I</text>'
    b += f'<text x="86" y="48" {TXT}>V</text>'
    b += f'<text x="4" y="62" {DEV}>&#2349;&#2306;&#2332;&#2344;</text>'
    return _wrap(100, 68, b)


def half_wave():
    b = f'<path d="M6 20 L22 20" {S}/>'
    b += f'<path d="M22 14 L22 44" {S}/><path d="M6 44 L22 44" {S}/>'
    b += f'<circle cx="14" cy="32" r="9" {S}/>'
    b += f'<path d="M9 32 C11 27 13 37 15 32 C17 27 19 37 21 32" {S} stroke-width=".8"/>'
    b += f'<path d="M22 14 L46 14" {S}/>'
    # diode symbol
    b += f'<path d="M46 8 L46 20 L58 14 Z" {SF}/><path d="M58 8 L58 20" {S} stroke-width="1.4"/>'
    b += f'<path d="M58 14 L80 14 L80 30" {S}/>'
    b += f'<path d="M74 30 L86 30 L86 40 L74 40 Z" {S}/>'
    b += f'<path d="M80 40 L80 50 L22 50 L22 44" {S}/>'
    b += f'<text x="88" y="38" {TXT}>R<tspan dy="2" font-size="5.6">L</tspan></text>'
    b += f'<text x="2" y="62" {DEV}>&#2309;&#2352;&#2381;&#2343; &#2340;&#2352;&#2306;&#2327;</text>'
    return _wrap(100, 66, b)


def bridge():
    cx, cy, r = 44, 32, 20
    b = f'<path d="M{cx} {cy-r} L{cx+r} {cy} L{cx} {cy+r} L{cx-r} {cy} Z" {S}/>'
    # four diodes as filled triangles on the arms
    b += f'<path d="M50 20 L58 26 L50 28 Z" {SF}/>'
    b += f'<path d="M58 38 L50 44 L50 36 Z" {SF}/>'
    b += f'<path d="M38 44 L30 38 L38 36 Z" {SF}/>'
    b += f'<path d="M30 26 L38 20 L38 28 Z" {SF}/>'
    b += f'<path d="M{cx-r} {cy} L14 {cy}" {S}/><path d="M{cx+r} {cy} L80 {cy}" {S}/>'
    b += f'<path d="M{cx} {cy-r} L{cx} 6" {S}/><path d="M{cx} {cy+r} L{cx} 58" {S}/>'
    # ac source
    b += f'<circle cx="8" cy="32" r="7" {S}/>'
    b += f'<path d="M4 32 C5.5 29 7 35 8.5 32 C10 29 11.5 35 13 32" {S} stroke-width=".8"/>'
    b += f'<text x="82" y="30" {TXT}>R<tspan dy="2" font-size="5.6">L</tspan></text>'
    b += f'<text x="20" y="64" {DEV}>&#2360;&#2375;&#2340;&#2369; &#2346;&#2370;&#2352;&#2381;&#2339; &#2340;&#2352;&#2306;&#2327;</text>'
    return _wrap(104, 70, b)


def zener():
    # series resistor along the top, zener (reverse biased) and load in parallel
    b = f'<path d="M8 12 L20 12" {S}/>'
    b += f'<rect x="20" y="7" width="22" height="10" {S}/>'
    b += f'<text x="24" y="5" {TXT}>R<tspan dy="2" font-size="5.6">s</tspan></text>'
    b += f'<path d="M42 12 L78 12" {S}/>'
    # zener branch: cathode bar on top, anode triangle pointing up -> reverse bias
    b += f'<path d="M56 12 L56 26" {S}/>'
    b += f'<path d="M49 26 L63 26" {S} stroke-width="1.5"/>'
    b += f'<path d="M49 26 L46 30 M63 26 L66 22" {S} stroke-width="1.1"/>'
    b += f'<path d="M49 38 L63 38 L56 26 Z" {SF}/>'
    b += f'<path d="M56 38 L56 52" {S}/>'
    b += f'<text x="30" y="36" {TXT}>V<tspan dy="2" font-size="5.6">z</tspan></text>'
    # load branch
    b += f'<path d="M78 12 L78 22" {S}/>'
    b += f'<rect x="72" y="22" width="12" height="16" {S}/>'
    b += f'<path d="M78 38 L78 52" {S}/>'
    b += f'<text x="86" y="33" {TXT}>R<tspan dy="2" font-size="5.6">L</tspan></text>'
    # return path
    b += f'<path d="M8 52 L78 52" {S}/><path d="M8 12 L8 52" {S}/>'
    b += f'<text x="0" y="34" {TXU}>V<tspan dy="2" font-size="5.6">in</tspan></text>'
    return _wrap(98, 60, b)


def solar_iv():
    b = f'<path d="M30 56 L30 4" {S} marker-end="url(#ars)"/>'
    b += f'<path d="M6 30 L94 30" {S} marker-end="url(#ars)"/>'
    b += (f'<path d="M30 46 C56 46 66 44 72 38 C76 33 77 31 78 30" {S}/>')
    b += f'<rect x="30" y="30" width="42" height="16" fill="#e8e8e8" stroke="none" opacity=".75"/>'
    b += (f'<path d="M30 46 C56 46 66 44 72 38 C76 33 77 31 78 30" {S}/>')
    b += f'<text x="34" y="40" {TXU}>P = VI</text>'
    b += f'<text x="80" y="42" {TXT}>V<tspan dy="2" font-size="5.6">oc</tspan></text>'
    b += f'<text x="4" y="48" {TXT}>I<tspan dy="2" font-size="5.6">sc</tspan></text>'
    b += f'<text x="84" y="26" {TXT}>V</text>'
    return _wrap(100, 62, b)


def ntype_ptype():
    b = ""
    for ox, core, extra, lbl in ((4, "Si", "+", "n"), (56, "Si", "&#8722;", "p")):
        b += f'<circle cx="{ox+20}" cy="30" r="8" {S}/>'
        b += f'<text x="{ox+13}" y="33" {TXU}>{"As" if lbl=="n" else "In"}</text>'
        for dx, dy in ((-18, 0), (18, 0), (0, -18), (0, 18)):
            b += (f'<circle cx="{ox+20+dx}" cy="{30+dy}" r="6.5" {S} stroke-width=".8"/>')
            b += f'<text x="{ox+20+dx-5}" y="{30+dy+2.6}" {TXU}>{core}</text>'
        b += f'<circle cx="{ox+32}" cy="18" r="2" {SF}/>'
        b += f'<text x="{ox+16}" y="62" {TXT}>{lbl}</text>'
    b += f'<text x="26" y="10" {TXU}>e&#8722;</text><text x="76" y="10" {TXU}>h+</text>'
    return _wrap(104, 68, b)
