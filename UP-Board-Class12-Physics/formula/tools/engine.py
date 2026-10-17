# -*- coding: utf-8 -*-
"""Formula-sheet engine: clipboard-style revision sheets with LaTeX-grade math.

Geometry is matched to the reference photograph (572 x 1017 CSS px), math is set
in Computer Modern (the LaTeX family in the reference), Hindi in Noto Sans
Devanagari. Sections are measured in-browser and packed so no sheet overflows.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

FONTS = "/projects/sandbox/fonts"

# ---------------------------------------------------------------- page geometry
PAGE_W, PAGE_H = 572, 1017          # CSS px, 9:16 like the reference photo
PAPER_X, PAPER_W = 30, 513
PAPER_Y, PAPER_H = 95, 893
PAD = 9                              # gap between paper edge and the ink border
BORDER_PAD = 11                      # gap between ink border and text
TITLE_BLOCK = 46                     # title + rule
FOOTER_BLOCK = 30                    # footer line

# usable height for sections inside the ink border
CONTENT_H = PAPER_H - 2 * PAD - 2 * BORDER_PAD - TITLE_BLOCK - FOOTER_BLOCK

# ------------------------------------------------------------------ math markup
GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ", "chi": "χ",
    "psi": "ψ", "omega": "ω", "varphi": "φ", "varepsilon": "ε",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
SYM = {
    "propto": "∝", "Rightarrow": "⟹", "rightarrow": "→", "to": "→",
    "leftarrow": "←", "leftrightarrow": "↔", "longrightarrow": "⟶",
    "times": "×", "cdot": "·", "div": "÷", "pm": "±", "mp": "∓",
    "approx": "≈", "simeq": "≃", "equiv": "≡", "neq": "≠",
    "leq": "≤", "le": "≤", "geq": "≥", "ge": "≥", "ll": "≪", "gg": "≫",
    "infty": "∞", "partial": "∂", "nabla": "∇", "hbar": "ℏ",
    "degree": "°", "angle": "∠", "perp": "⊥", "parallel": "∥",
    "sum": "Σ", "int": "∫", "prime": "′", "ohm": "Ω", "odot": "⊙",
    "uparrow": "↑", "downarrow": "↓", "therefore": "∴", "because": "∵",
    "oplus": "⊕", "ominus": "⊖", "bullet": "•", "star": "★",
    "ldots": "…", "dots": "…", "cdots": "⋯", "vdots": "⋮",
    "sim": "∼", "propto2": "∝",
}
# \left and \right only scale delimiters in LaTeX; the delimiter itself follows
# as an ordinary character, so these are consumed and emit nothing.
SKIP = {"right", "displaystyle", "limits"}
SPACE = {"quad": ".9em", "qquad": "1.8em", "!": "-.08em"}
FUNCS = {"sin", "cos", "tan", "cot", "sec", "cosec", "cosec", "log", "ln",
         "exp", "max", "min", "const", "rms", "dc", "ac", "eff", "net",
         "sinh", "cosh", "tanh", "cot"}


def _grab(s: str, i: int) -> tuple[str, int]:
    """Extract a balanced {...} group starting at s[i] == '{'."""
    if i >= len(s) or s[i] != "{":
        raise ValueError(f"expected '{{' at {i} in {s!r}")
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    raise ValueError(f"unbalanced braces in {s!r}")


# LaTeX sets Latin variables and LOWERCASE Greek in italic, but leaves digits,
# operators, function names and UPPERCASE Greek upright.
_ITALIC_RUN = re.compile(r"[A-Za-z\u03b1-\u03c9\u03d1\u03d5\u03f5]+")


def _leaf(t: str) -> str:
    """Italicise variables; keep digits/operators/function names upright.

    Relations are split out FIRST and the two passes never see each other's
    output: running the relation pass over already-generated markup would match
    the '=' inside attributes like class="op" and shred the HTML.
    """
    t = (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

    def repl(m: re.Match) -> str:
        w = m.group(0)
        if w.lower() in FUNCS:
            return f'<span class="op">{w}</span>'
        return f"<i>{w}</i>"

    # TeX spaces relations and binary operators by atom class; a control word
    # also swallows the space written after it ("\phi = x" loses one side), so
    # literal spaces are collapsed here and the gaps restored with padding.
    out = []
    for i, part in enumerate(_RELATION.split(t)):
        if i % 2:                       # captured relation token
            out.append(f'<span class="rel">{part}</span>')
            continue
        chunks = _BINARY.split(part)
        for j, piece in enumerate(chunks):
            if j % 2:                   # captured binary operator
                op = "\u2212" if piece in "-\u2212" else piece
                # a leading operator is unary (e.g. the minus of 10^-19)
                lead = " lead" if j == 1 and not chunks[0] else ""
                out.append(f'<span class="bin{lead}">{op}</span>')
            elif piece:
                out.append(_ITALIC_RUN.sub(repl, piece))
    return "".join(out)


_BINARY = re.compile(r"\s*([+\-\u2212\u00b1\u2213])\s*")


_RELATION = re.compile(
    r"\s*(&lt;|&gt;|=|\u2248|\u221d|\u223c|\u2243|\u2261|\u2260|\u2264|\u2265"
    r"|\u27f9|\u27f6|\u2192|\u2190|\u2194)\s*")


def mhtml(s: str) -> str:
    """Convert a small LaTeX subset to styled HTML."""
    out: list[str] = []
    buf: list[str] = []
    i, n = 0, len(s)

    def flush() -> None:
        if buf:
            out.append(_leaf("".join(buf)))
            buf.clear()

    while i < n:
        c = s[i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            if m:
                name = m.group(1)
                i += m.end()
                # TeX rule: a control word swallows the whitespace after it, so
                # "\Delta t" sets as a single token rather than "Delta space t".
                while i < n and s[i] == " ":
                    i += 1
                if name == "frac":
                    a, i = _grab(s, i)
                    b, i = _grab(s, i)
                    flush()
                    out.append(
                        f'<span class="frac"><span class="num">{mhtml(a)}</span>'
                        f'<span class="den">{mhtml(b)}</span></span>')
                elif name == "sqrt":
                    a, i = _grab(s, i)
                    flush()
                    out.append(f'<span class="sqrt">&#8730;<span class="rad">'
                               f'{mhtml(a)}</span></span>')
                elif name == "text":
                    a, i = _grab(s, i)
                    flush()
                    out.append(f'<span class="upr">{a}</span>')
                elif name == "nuc":
                    a, i = _grab(s, i)   # mass number A
                    z, i = _grab(s, i)   # atomic number Z
                    x, i = _grab(s, i)   # symbol
                    flush()
                    out.append(f'<span class="nuc"><span>{mhtml(a)}</span>'
                               f'<span>{mhtml(z)}</span></span>'
                               f'<span class="nucsym">{x}</span>')
                elif name == "boxed":
                    a, i = _grab(s, i)
                    flush()
                    out.append(f'<span class="boxed">{mhtml(a)}</span>')
                elif name in ("bar", "vec", "hat", "overline", "dot"):
                    a, i = _grab(s, i)
                    flush()
                    cls = {"bar": "bar", "overline": "bar",
                           "vec": "vec", "hat": "hat", "dot": "dotacc"}[name]
                    out.append(f'<span class="{cls}">{mhtml(a)}</span>')
                elif name == "left":
                    # \left( ... \right) -- stretch the delimiters when the
                    # group wraps a fraction, the way TeX sizes them
                    if i >= n:
                        raise ValueError(f"\\left without a delimiter in {s!r}")
                    open_d, i = s[i], i + 1
                    # depth-aware scan: the first \right may close a NESTED
                    # group, as in \left[\left(..\right)-\left(..\right)\right]
                    depth, j, split = 1, i, -1
                    while j < n:
                        if s.startswith("\\left", j):
                            depth += 1
                            j += 5
                        elif s.startswith("\\right", j):
                            depth -= 1
                            if depth == 0:
                                split = j
                                break
                            j += 6
                        else:
                            j += 1
                    if split < 0 or split + 6 >= n:
                        raise ValueError(f"\\left without matching \\right in {s!r}")
                    inner = mhtml(s[i:split])
                    close_d = s[split + 6]
                    i = split + 7
                    big = " big" if 'class="frac"' in inner else ""
                    flush()
                    out.append(f'<span class="db{big}">{open_d}</span>{inner}'
                               f'<span class="db{big}">{close_d}</span>')
                elif name in SKIP:
                    pass
                elif name in SPACE:
                    flush()
                    out.append(f'<span style="display:inline-block;'
                               f'width:{SPACE[name]}"></span>')
                elif name in GREEK:
                    buf.append(GREEK[name])
                elif name in SYM:
                    flush()
                    out.append(f'<span class="sym">{SYM[name]}</span>')
                elif name in FUNCS:
                    flush()
                    out.append(f'<span class="op">{name}</span>')
                else:
                    raise ValueError(f"unknown macro \\{name} in {s!r}")
            else:
                nxt = s[i + 1] if i + 1 < n else ""
                if nxt == ",":
                    flush(); out.append('<span class="thin"></span>'); i += 2
                elif nxt == ";":
                    flush(); out.append('<span class="med"></span>'); i += 2
                elif nxt == " ":
                    buf.append(" "); i += 2
                else:
                    buf.append(nxt); i += 2
        elif c in "^_":
            i += 1
            if i < n and s[i] == "{":
                a, i = _grab(s, i)
            else:
                a, i = s[i], i + 1
            flush()
            tag = "sup" if c == "^" else "sub"
            out.append(f"<{tag}>{mhtml(a)}</{tag}>")
        else:
            buf.append(c)
            i += 1
    flush()
    return "".join(out)


_B_OPEN, _B_CLOSE = "\x01", "\x02"


def rich(text: str) -> str:
    """Render prose with $math$ spans and **bold** runs.

    Bold delimiters are resolved to sentinels BEFORE the math split, otherwise a
    run that straddles a formula -- "**$\\mu$A**" -- leaves one stray '**' in
    each prose fragment and both render literally.
    """
    segments = text.split("**")
    if len(segments) % 2 == 0:
        raise ValueError(f"unbalanced ** in {text!r}")
    marked = segments[0]
    for i, seg in enumerate(segments[1:]):
        marked += (_B_OPEN if i % 2 == 0 else _B_CLOSE) + seg

    out = []
    for p in re.split(r"(\$[^$]*\$)", marked):
        if p.startswith("$") and p.endswith("$") and len(p) >= 2:
            out.append(f'<span class="m">{mhtml(p[1:-1])}</span>')
        else:
            out.append(p.replace("&", "&amp;")
                        .replace("<", "&lt;").replace(">", "&gt;"))
    html = "".join(out)
    return html.replace(_B_OPEN, "<b>").replace(_B_CLOSE, "</b>")


# ------------------------------------------------------------------------- CSS
CSS = f"""
@font-face {{ font-family:'CMU'; src:url('file://{FONTS}/cmunrm.ttf'); font-weight:400; font-style:normal; }}
@font-face {{ font-family:'CMU'; src:url('file://{FONTS}/cmunti.ttf'); font-weight:400; font-style:italic; }}
@font-face {{ font-family:'CMU'; src:url('file://{FONTS}/cmunbx.ttf'); font-weight:700; font-style:normal; }}
@font-face {{ font-family:'CMU'; src:url('file://{FONTS}/cmunbi.ttf'); font-weight:700; font-style:italic; }}
@font-face {{ font-family:'Dev'; src:url('file://{FONTS}/DevRegular.ttf'); font-weight:400; }}
@font-face {{ font-family:'Dev'; src:url('file://{FONTS}/NotoDevBold.ttf'); font-weight:700; font-variation-settings:'wght' 700; }}
/* Computer Modern lacks a few operators (angle, proportional, approx);
   DejaVu covers them so they never fall through to a notdef box. */
@font-face {{ font-family:'Sym'; src:url('file://{FONTS}/DejaVuSans.ttf'); font-weight:400; }}
@font-face {{ font-family:'Sym'; src:url('file://{FONTS}/DejaVuSans-Bold.ttf'); font-weight:700; }}

* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ background:#555; }}
body {{ font-family:'CMU','Dev','Sym',serif; -webkit-font-smoothing:antialiased; }}

/* ---------- wooden clipboard ---------- */
.board {{
  position:relative; width:{PAGE_W}px; height:{PAGE_H}px; overflow:hidden;
  background:
    radial-gradient(ellipse 60px 220px at 14% 30%, rgba(142,92,44,.13), rgba(0,0,0,0) 70%),
    radial-gradient(ellipse 48px 180px at 76% 66%, rgba(142,92,44,.11), rgba(0,0,0,0) 70%),
    radial-gradient(ellipse 30px 120px at 45% 85%, rgba(120,76,34,.09), rgba(0,0,0,0) 70%),
    repeating-linear-gradient(91deg, rgba(126,80,36,.085) 0 1px, rgba(0,0,0,0) 1px 6px),
    repeating-linear-gradient(89.4deg, rgba(150,102,52,.06) 0 2px, rgba(0,0,0,0) 2px 11px),
    repeating-linear-gradient(90.6deg, rgba(104,64,26,.05) 0 1px, rgba(0,0,0,0) 1px 17px),
    linear-gradient(92deg,#d2a068 0%,#e4bd86 15%,#d8ab71 33%,#e8c795 52%,
                    #dab077 70%,#e6c28d 86%,#cf9d64 100%);
}}
.board::after {{ /* soft vignette so the board reads as a photographed object */
  content:''; position:absolute; inset:0; pointer-events:none; z-index:1;
  background:radial-gradient(ellipse 120% 90% at 50% 42%, rgba(0,0,0,0) 55%, rgba(60,32,8,.18) 100%);
}}
/* clipboard bottom-right corner notch, as in the reference */
.corner {{ position:absolute; right:0; bottom:0; width:30px; height:30px;
  background:linear-gradient(135deg, rgba(0,0,0,0) 50%, #6d5336 50%); opacity:.75; }}

/* ---------- metal clip ---------- */
.clip {{ position:absolute; left:50%; top:6px; transform:translateX(-50%); z-index:5; }}

/* ---------- paper ---------- */
/* z-index keeps the sheet above the board vignette, which would otherwise
   wash a grey gradient across the lower half of the paper. */
.paper {{
  position:absolute; left:{PAPER_X}px; top:{PAPER_Y}px; z-index:3;
  width:{PAPER_W}px; height:{PAPER_H}px; background:#fdfdfb;
  box-shadow:0 1px 3px rgba(0,0,0,.34), 0 7px 16px rgba(0,0,0,.20);
}}
.ink {{ position:absolute; inset:{PAD}px; border:1.1px solid #11100e;
  padding:{BORDER_PAD}px {BORDER_PAD}px 0; display:flex; flex-direction:column; }}

/* ---------- title ---------- */
.title {{ text-align:center; font-weight:700; font-size:16.6px; letter-spacing:.1px;
  line-height:1.3; color:#000; }}
.title .hi {{ font-family:'Dev','CMU',sans-serif; font-weight:700; }}
.title .pt {{ font-size:13.4px; font-weight:700; }}
.rule {{ border-bottom:1.1px solid #11100e; margin:4.5px 0 7px; }}

/* ---------- sections ---------- */
.flow {{ flex:1 1 auto; }}
/* flow-root contains the floated diagram, so a section's measured height is
   its true height -- otherwise a float leaks into the next section and the
   page-packing budget is computed from wrong numbers. */
.sec {{ margin-bottom:7.5px; display:flow-root; }}
.sec:last-child {{ margin-bottom:0; }}
.sh {{ font-weight:700; font-size:13.6px; line-height:1.34; color:#000;
  margin-bottom:1.5px; white-space:nowrap; }}
.sh .hi {{ font-family:'Dev','CMU',sans-serif; font-weight:700; }}
.sh .no {{ font-weight:700; }}
.sh .cont {{ font-family:'Dev','CMU',sans-serif; font-weight:400; font-size:11px; }}

.it {{ display:flex; align-items:baseline; font-size:12.35px; line-height:1.56;
  color:#000; padding-left:3px; }}
.it .mk {{ flex:0 0 11px; text-align:left; }}
.it .mk.dot {{ font-size:10px; line-height:1.9; }}
.it .bd {{ flex:1 1 auto; }}
.it.sub {{ padding-left:20px; font-size:11.95px; }}
.it .hi, .it {{ }}
.bd {{ font-family:'Dev','CMU',sans-serif; }}
.bd b {{ font-family:'Dev','CMU',sans-serif; font-weight:700; }}

/* ---------- maths ---------- */
.m {{ font-family:'CMU','Sym',serif; font-size:13.1px; white-space:nowrap; }}
.m i {{ font-style:italic; }}
.m .op {{ font-style:normal; }}
.m .upr {{ font-family:'Dev','CMU',sans-serif; font-style:normal; font-size:11.9px; }}
.m sup, .m sub {{ font-size:70%; line-height:0; position:relative; }}
.m sup {{ top:-.52em; }}
.m sub {{ bottom:-.26em; }}
.m .sym {{ font-style:normal; padding:0 .13em; }}
.m .rel {{ font-style:normal; padding:0 .19em; }}
.m .bin {{ font-style:normal; padding:0 .13em; }}
.m .bin.lead {{ padding-left:0; padding-right:.02em; }}
.m .db {{ display:inline-block; font-style:normal; }}
.m .db.big {{ transform:scaleY(1.95); transform-origin:50% 48%; padding:0 .05em; }}
.m .thin {{ display:inline-block; width:.17em; }}
.m .med {{ display:inline-block; width:.42em; }}

.frac {{ display:inline-block; vertical-align:-.47em; text-align:center;
  margin:0 .14em; }}
.frac .num {{ display:block; border-bottom:1.05px solid #000; padding:0 .2em 0.3px;
  line-height:1.26; }}
.frac .den {{ display:block; padding:0.6px .2em 0; line-height:1.26; }}

.sqrt {{ display:inline-block; }}
.sqrt .rad {{ border-top:1.05px solid #000; padding:0.6px .14em 0; margin-left:-.055em; }}

.boxed {{ display:inline-block; border:1.05px solid #11100e; padding:1.1px 5px 1.6px;
  margin:0 .1em; }}
.nuc {{ display:inline-block; vertical-align:-.03em; text-align:right; font-size:63%;
  line-height:1.04; margin-right:.06em; }}
/* Direct children only. A descendant selector also caught the .bin span of
   the minus sign inside a nuclide prescript and stacked it on its own line. */
.nuc > span {{ display:block; font-style:normal; }}
.nuc .bin, .nuc .rel {{ display:inline; padding:0 .04em; }}
.nucsym {{ font-style:normal; }}
.bar, .vec, .hat, .dotacc {{ position:relative; display:inline-block; }}
.dotacc::before {{ content:'\\02D9'; position:absolute; left:50%; top:-.62em;
  transform:translateX(-50%); font-size:1em; font-style:normal; }}
.bar::before {{ content:''; position:absolute; left:0; right:0; top:-.08em;
  border-top:1px solid #000; }}
.vec::before {{ content:'\\2192'; position:absolute; left:50%; top:-.78em;
  transform:translateX(-50%); font-size:.72em; }}
.hat::before {{ content:'\\005E'; position:absolute; left:50%; top:-.52em;
  transform:translateX(-50%); font-size:.8em; }}

/* ---------- diagrams ---------- */
.dg {{ float:right; margin:1px 0 2px 7px; }}
.dg svg {{ display:block; }}

/* ---------- footer ---------- */
.foot {{ flex:0 0 auto; text-align:center; font-weight:700; font-style:italic;
  font-size:12.1px; padding:5px 0 7px; color:#000; }}
.foot .hi {{ font-family:'Dev','CMU',sans-serif; font-weight:700; font-style:normal; }}

/* Measuring page. The .ink box MUST keep the exact width it has on a real
   sheet (paper width minus both insets); if it is wider, text wraps less while
   measuring and the packed page then overflows when actually rendered. */
body.measure .board {{ height:auto; }}
body.measure .paper {{ position:static; width:{PAPER_W}px; height:auto; }}
body.measure .ink {{ position:static; inset:auto; width:{PAPER_W - 2 * PAD}px; }}
"""

CLIP_SVG = """
<svg class="clip" width="150" height="88" viewBox="0 0 150 88">
  <defs>
    <linearGradient id="mtl" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0"  stop-color="#f4f5f6"/><stop offset=".3" stop-color="#c8cbcf"/>
      <stop offset=".55" stop-color="#9aa0a5"/><stop offset=".8" stop-color="#c2c6ca"/>
      <stop offset="1"   stop-color="#80868b"/>
    </linearGradient>
    <linearGradient id="blk" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#55565a"/><stop offset=".22" stop-color="#26272a"/>
      <stop offset=".75" stop-color="#17181a"/><stop offset="1" stop-color="#0d0e0f"/>
    </linearGradient>
    <linearGradient id="plate" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8f9499"/><stop offset=".22" stop-color="#e6e9ec"/>
      <stop offset=".5" stop-color="#b9bec3"/><stop offset=".78" stop-color="#e6e9ec"/>
      <stop offset="1" stop-color="#8f9499"/>
    </linearGradient>
  </defs>
  <!-- hanging hole -->
  <ellipse cx="75" cy="11" rx="13" ry="8" fill="#3a3b3e"/>
  <ellipse cx="75" cy="10.2" rx="10" ry="5.6" fill="#cfd3d7"/>
  <ellipse cx="75" cy="10.8" rx="6.6" ry="3.3" fill="#4e5155"/>
  <!-- spring arms rising from the bar -->
  <path d="M32 50 L52 23 L60 27 L41 52 Z" fill="url(#mtl)"/>
  <path d="M118 50 L98 23 L90 27 L109 52 Z" fill="url(#mtl)"/>
  <!-- metal cross bar -->
  <rect x="20" y="45" width="110" height="9" rx="4.5" fill="url(#plate)"/>
  <!-- black clip body -->
  <path d="M30 40 Q75 30 120 40 L124 66 Q75 57 26 66 Z" fill="url(#blk)"/>
  <rect x="26" y="62" width="98" height="16" rx="5" fill="url(#blk)"/>
  <rect x="31" y="42.5" width="88" height="2.4" rx="1.2" fill="#71737a" opacity=".45"/>
  <rect x="32" y="66" width="86" height="2.8" rx="1.4" fill="#404246" opacity=".8"/>
  <!-- pressure plate biting the paper -->
  <rect x="38" y="77" width="74" height="5.5" rx="2.2" fill="url(#plate)"/>
</svg>
"""


# --------------------------------------------------------------- HTML assembly
def _title_html(hi: str, en: str, part: str | None) -> str:
    p = f' <span class="pt">({part})</span>' if part else ""
    return (f'<div class="title"><span class="hi">{hi}</span> '
            f'<span class="pt">({en})</span>{p}</div><div class="rule"></div>')


def _item_html(raw: str, ii: int | None = None) -> str:
    if raw.startswith("•• "):
        mk, cls, body = "•", "dot sub", raw[3:]
    elif raw.startswith("• "):
        mk, cls, body = "•", "dot", raw[2:]
    elif raw.startswith("-- "):
        mk, cls, body = "–", "sub", raw[3:]
    elif raw.startswith("- "):
        mk, cls, body = "–", "", raw[2:]
    else:
        mk, cls, body = "", "nomk", raw
    attr = f' data-ii="{ii}"' if ii is not None else ""
    return (f'<div class="it {cls}"{attr}><span class="mk '
            f'{"dot" if mk == "•" else ""}">{mk}</span>'
            f'<span class="bd">{rich(body)}</span></div>')


def _head_html(sec: dict, cont: bool = False) -> str:
    tail = ' <span class="cont">(क्रमशः)</span>' if cont else ""
    return (f'<div class="sh"><span class="no">{sec["no"]}.</span> '
            f'<span class="hi">{sec["hi"]}</span> ({sec["en"]}){tail}</div>')


def _sec_html(sec: dict, si: int | None = None) -> str:
    """Whole section -- used by the measuring pass."""
    dg = f'<div class="dg">{sec["svg"]}</div>' if sec.get("svg") else ""
    attr = f' data-si="{si}"' if si is not None else ""
    rows = "".join(_item_html(r, i) for i, r in enumerate(sec["items"]))
    return f'<div class="sec"{attr}>{dg}{_head_html(sec)}{rows}</div>'


def _chunk_html(sec: dict, start: int, end: int, first: bool) -> str:
    """One section, or a contiguous slice of it continued on a later sheet."""
    dg = (f'<div class="dg">{sec["svg"]}</div>'
          if first and sec.get("svg") else "")
    rows = "".join(_item_html(r) for r in sec["items"][start:end])
    return (f'<div class="sec">{dg}{_head_html(sec, cont=not first)}'
            f'{rows}</div>')


def _board(inner: str) -> str:
    return (f'<div class="board">{CLIP_SVG}<div class="paper"><div class="ink">'
            f'{inner}</div></div><div class="corner"></div></div>')


def measure_doc(sections: list[dict]) -> str:
    body = "".join(_sec_html(s, i) for i, s in enumerate(sections))
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style>'
            f'</head><body class="measure">{_board(body)}</body></html>')


def probe_doc(hi: str, en: str, footer: str) -> str:
    """A sheet with a real title/footer but no sections.

    `.flow` is flex:1, so its measured height is exactly the usable content
    height for this chapter -- which depends on whether the title wraps.
    """
    inner = (_title_html(hi, en, "भाग 1/9")
             + '<div class="flow"></div>'
             + f'<div class="foot"><span class="hi">{footer}</span></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style>'
            f'</head><body>{_board(inner)}</body></html>')


def sheets_doc(sheets: list[dict], footer: str) -> str:
    boards = []
    for sh in sheets:
        inner = (_title_html(sh["hi"], sh["en"], sh.get("part"))
                 + '<div class="flow">'
                 + "".join(_chunk_html(c["sec"], c["start"], c["end"], c["first"])
                           for c in sh["chunks"])
                 + "</div>"
                 + f'<div class="foot"><span class="hi">{footer}</span></div>')
        boards.append(_board(inner))
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style>'
            f'</head><body>{"".join(boards)}</body></html>')


SEC_GAP = 7.5          # must match .sec margin-bottom


def flow_pages(sections: list[dict], meas: list[dict], budget: float,
               avoid_split_above: float = 0.82) -> list[list[dict]]:
    """Flow sections item-by-item so every sheet fills like the reference.

    `meas[i]` holds {'head':px, 'items':[px...], 'dg':px} measured at the final
    content width. A section may continue onto the next sheet, in which case its
    heading is repeated and marked (क्रमशः). A section is only split when it
    cannot fit whole on a sheet that is still mostly empty, so short sections are
    kept together.
    """
    pages: list[list[dict]] = []
    cur: list[dict] = []
    used = 0.0

    def flush() -> None:
        nonlocal cur, used
        if cur:
            pages.append(cur)
            cur, used = [], 0.0

    for si, sec in enumerate(sections):
        m = meas[si]
        n = len(sec["items"])
        idx, first = 0, True

        while idx < n:
            head = m["head"]
            dg = m["dg"] if first else 0.0
            remaining = sum(m["items"][idx:])
            whole = head + max(remaining, dg) + SEC_GAP

            # Prefer not to split: if the rest of the section fits on a fresh
            # sheet and this sheet is already well filled, break the page.
            if (cur and used + whole > budget and whole <= budget
                    and used / budget > avoid_split_above):
                flush()
                continue

            smallest = head + max(m["items"][idx], dg) + SEC_GAP
            if cur and used + smallest > budget:
                flush()
                continue

            start, items_h = idx, 0.0
            while idx < n:
                cand = head + max(items_h + m["items"][idx], dg) + SEC_GAP
                if used + cand > budget and idx > start:
                    break
                items_h += m["items"][idx]
                idx += 1

            chunk_h = head + max(items_h, dg) + SEC_GAP
            cur.append({"sec": sec, "start": start, "end": idx,
                        "first": first, "h": chunk_h})
            used += chunk_h
            first = False

            if idx < n:          # section continues on the next sheet
                flush()

    flush()
    return pages


def page_height(page: list[dict]) -> float:
    return sum(c["h"] for c in page)


def balanced_flow(sections: list[dict], meas: list[dict],
                  budget: float) -> list[list[dict]]:
    """Flow into the fewest sheets, then even out how full those sheets are.

    Filling greedily to the brim packs the early sheets and leaves the last one
    nearly blank. The sheet count is fixed first, then the smallest working
    budget that still yields that many sheets is found by bisection, which
    spreads the content evenly without ever exceeding the real budget.
    """
    # Fewest sheets wins, so try both a split-shy and a split-friendly flow.
    base = min(flow_pages(sections, meas, budget, 0.82),
               flow_pages(sections, meas, budget, 0.99), key=len)
    target_pages = len(base)
    if target_pages <= 1:
        return base

    # Bisect with splitting allowed, otherwise the anti-split rule keeps
    # bouncing the page count and no even distribution is ever found.
    lo, hi, best = 1.0, budget, base
    for _ in range(44):
        mid = (lo + hi) / 2
        cand = flow_pages(sections, meas, mid, 0.99)
        if (len(cand) <= target_pages
                and all(page_height(p) <= budget + 0.01 for p in cand)):
            best, hi = cand, mid
        else:
            lo = mid
    return best


def pack(sections: list[dict], heights: list[float], budget: float) -> list[list[dict]]:
    """Split sections into the fewest sheets, then balance their fill.

    A plain greedy fill leaves the last sheet nearly empty, which looks wrong
    next to the densely packed reference. So the minimum page count is found
    greedily (optimal for an ordered split) and the sections are then
    redistributed by DP to even out how full each sheet is.
    """
    n = len(heights)
    for sec, h in zip(sections, heights):
        if h > budget:
            raise ValueError(
                f"section {sec['no']} alone is {h:.0f}px > budget {budget:.0f}px")

    pages_needed, used = 1, 0.0
    for h in heights:
        if used + h > budget:
            pages_needed += 1
            used = h
        else:
            used += h

    prefix = [0.0]
    for h in heights:
        prefix.append(prefix[-1] + h)
    target = prefix[n] / pages_needed

    INF = float("inf")
    dp = [[INF] * (pages_needed + 1) for _ in range(n + 1)]
    cut = [[-1] * (pages_needed + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for p in range(1, pages_needed + 1):
        for i in range(1, n + 1):
            for j in range(p - 1, i):
                seg = prefix[i] - prefix[j]
                if seg > budget or dp[j][p - 1] == INF:
                    continue
                cost = dp[j][p - 1] + (target - seg) ** 2
                if cost < dp[i][p]:
                    dp[i][p] = cost
                    cut[i][p] = j

    if dp[n][pages_needed] == INF:          # DP infeasible -> plain greedy
        pages, cur, used = [], [], 0.0
        for sec, h in zip(sections, heights):
            if cur and used + h > budget:
                pages.append(cur)
                cur, used = [], 0.0
            cur.append(sec)
            used += h
        if cur:
            pages.append(cur)
        return pages

    bounds, i = [n], n
    for p in range(pages_needed, 0, -1):
        i = cut[i][p]
        bounds.append(i)
    bounds.reverse()
    return [sections[bounds[k]:bounds[k + 1]] for k in range(pages_needed)]
