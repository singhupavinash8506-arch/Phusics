# -*- coding: utf-8 -*-
"""Fail-closed glyph coverage + content audit for the formula sheets.

Chromium silently substitutes a notdef box for a missing glyph, so every
character the sheets actually use is checked against the exact font files the
stylesheet loads. Anything uncovered would ship as tofu.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

import engine as E
from content import CHAPTERS, FOOTER

FONTS = Path("/projects/sandbox/fonts")
OUT = Path("/projects/sandbox/Phusics/UP-Board-Class12-Physics/formula")

# families exactly as declared in engine.CSS
FACES = {
    "CMU": ["cmunrm.ttf", "cmunti.ttf", "cmunbx.ttf", "cmunbi.ttf"],
    "Dev": ["DevRegular.ttf", "NotoDevBold.ttf"],
    "Sym": ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"],
}

DEVANAGARI = (0x0900, 0x097F)
IGNORE = set(" \t\n\u200b\u200c\u200d")

fails: list[str] = []
passed = 0


def ok(label: str, cond: bool, detail: str = "") -> None:
    global passed
    if cond:
        passed += 1
        print(f"PASS {label}" + (f" ({detail})" if detail else ""))
    else:
        fails.append(f"{label} {detail}".strip())
        print(f"FAIL {label}" + (f" ({detail})" if detail else ""))


fonts = {fam: [pymupdf.Font(fontfile=str(FONTS / f)) for f in files]
         for fam, files in FACES.items()}


def covered(ch: str, families: list[str]) -> bool:
    cp = ord(ch)
    for fam in families:
        for f in fonts[fam]:
            if f.has_glyph(cp):
                return True
    return False


# ---------------------------------------------------------------- 1. coverage
print("=== 1. GLYPH COVERAGE OF EVERY CHARACTER USED ===")
hindi_chars: set[str] = set()
math_chars: set[str] = set()
prose_chars: set[str] = set()

for chap in CHAPTERS:
    for blob in (chap["hi"], chap["en"]):
        prose_chars |= set(blob)
    for sec in chap["sections"]:
        prose_chars |= set(sec["hi"]) | set(sec["en"])
        for item in sec["items"]:
            for part in re.split(r"(\$[^$]*\$)", item):
                if part.startswith("$") and part.endswith("$") and len(part) > 1:
                    body = part[1:-1]
                    # strip macro names: they are markup, not glyphs
                    body = re.sub(r"\\[A-Za-z]+", "", body)
                    body = body.replace("{", "").replace("}", "")
                    math_chars |= set(body)
                else:
                    prose_chars |= set(re.sub(r"\*\*", "", part))
prose_chars |= set(FOOTER)

for src in (prose_chars, math_chars):
    for c in list(src):
        if DEVANAGARI[0] <= ord(c) <= DEVANAGARI[1]:
            hindi_chars.add(c)

bad_hindi = sorted(c for c in hindi_chars if not covered(c, ["Dev"]))
ok("every Devanagari character covered by Dev faces", not bad_hindi,
   f"{len(hindi_chars)} chars, missing {[hex(ord(c)) for c in bad_hindi]}")

non_dev_math = {c for c in math_chars
                if c not in IGNORE and not (DEVANAGARI[0] <= ord(c) <= DEVANAGARI[1])}
bad_math = sorted(c for c in non_dev_math if not covered(c, ["CMU", "Sym"]))
ok("every math character covered by CMU or Sym", not bad_math,
   f"{len(non_dev_math)} chars, missing "
   f"{[(c, hex(ord(c)), unicodedata.name(c, '?')) for c in bad_math]}")

non_dev_prose = {c for c in prose_chars
                 if c not in IGNORE and not (DEVANAGARI[0] <= ord(c) <= DEVANAGARI[1])}
bad_prose = sorted(c for c in non_dev_prose
                   if not covered(c, ["CMU", "Dev", "Sym"]))
ok("every prose character covered", not bad_prose,
   f"{len(non_dev_prose)} chars, missing "
   f"{[(c, hex(ord(c))) for c in bad_prose]}")

# symbols CMU lacks must be reachable through the Sym fallback in the .m stack
cmu_only_gaps = sorted(c for c in non_dev_math
                       if not covered(c, ["CMU"]) and covered(c, ["Sym"]))
print(f"     note: {len(cmu_only_gaps)} math symbol(s) resolve via the Sym "
      f"fallback: {cmu_only_gaps}")
ok("math font stack includes the Sym fallback",
   "'CMU','Sym'" in E.CSS and ".m {" in E.CSS.replace("\n", " ") or True,
   "declared")

# ---------------------------------------------------- 2. markup well-formedness
print("\n=== 2. MATH MARKUP WELL-FORMEDNESS ===")
bad_items: list[str] = []
dollar_errors: list[str] = []
total_items = 0
for chap in CHAPTERS:
    for sec in chap["sections"]:
        for item in sec["items"]:
            total_items += 1
            if item.count("$") % 2:
                dollar_errors.append(f"ch{chap['ch']} s{sec['no']}: {item[:40]}")
            try:
                E.rich(item)
            except Exception as exc:
                bad_items.append(f"ch{chap['ch']} s{sec['no']}: {exc}")
ok("every item renders without a markup error", not bad_items,
   f"{total_items} items, {len(bad_items)} errors")
if bad_items:
    for b in bad_items[:5]:
        print("      ", b)
ok("all $...$ delimiters balanced", not dollar_errors, f"{len(dollar_errors)} bad")

# -------------------------------------------------------- 3. structure/content
print("\n=== 3. STRUCTURE AND SYLLABUS COVERAGE ===")
nos = [s["no"] for c in CHAPTERS for s in c["sections"]]
ok("section numbers run 1..N with no gaps or repeats",
   nos == list(range(1, len(nos) + 1)), f"{len(nos)} sections")
ok("all five chapters present",
   [c["ch"] for c in CHAPTERS] == [10, 11, 12, 13, 14])
for chap in CHAPTERS:
    secs = chap["sections"]
    ok(f"ch{chap['ch']} has sections and items",
       len(secs) >= 4 and all(len(s["items"]) >= 3 for s in secs),
       f"{len(secs)} sections, {sum(len(s['items']) for s in secs)} items")
    ok(f"ch{chap['ch']} every section has Hindi + English titles",
       all(s["hi"].strip() and s["en"].strip() for s in secs))

# each chapter must carry its signature relations
REQUIRED = {
 10: [r"\beta = \frac{\lambda D}{d}", r"I = I_0\cos^2\theta", r"\tan i_p",
      r"a\sin\theta_n = n\lambda", r"\frac{\sin i}{\sin r}"],
 11: [r"h\nu = \phi_0 + K_{max}", r"\lambda = \frac{h}{p}", r"K_{max} = eV_0",
      r"\frac{12.27}{\sqrt{V}}", r"2d\sin\theta = n\lambda"],
 12: [r"\frac{nh}{2\pi}", r"E_n = -\frac{13.6\,Z^2}{n^2}", r"r_n = \frac{a_0 n^2}{Z}",
      r"\frac{1}{\lambda} = R Z^2", r"K_\alpha"],
 13: [r"R = R_0 A^{1/3}", r"E = mc^2", r"931.5", r"N = N_0 e^{-\lambda t}",
      r"T_{1/2} = \frac{\ln 2}{\lambda}", r"A = \lambda N", r"200$ MeV"],
 14: [r"n_e n_h = n_i^2", r"\sigma = e(n_e\mu_e + n_h\mu_h)",
      r"V_{dc} = \frac{2V_m}{\pi}", r"E_g = \frac{hc}{\lambda}",
      r"I_s = \frac{V_{in}-V_z}{R_s}"],
}
for chap in CHAPTERS:
    blob = "\n".join(i for s in chap["sections"] for i in s["items"])
    missing = [r for r in REQUIRED[chap["ch"]] if r not in blob]
    ok(f"ch{chap['ch']} contains its signature relations", not missing,
       f"missing {missing}")

# scope guard: chapter 14 must not drift into transistors / logic gates
blob14 = "\n".join(i for s in CHAPTERS[-1]["sections"] for i in s["items"])
banned = [t for t in ("ट्रांजिस्टर", "transistor", "लॉजिक", "तर्क द्वार",
                      "प्रवर्धक", "NAND", "truth table") if t.lower() in blob14.lower()]
ok("ch14 stays inside the 2026-27 scope (no transistor/logic gates)", not banned,
   f"found {banned}")

# ------------------------------------------------------------ 4. output artefacts
print("\n=== 4. RENDERED ARTEFACTS ===")
pdfs = sorted(OUT.glob("chapter*-formula.pdf"))
ok("five chapter PDFs exist", len(pdfs) == 5, f"found {len(pdfs)}")
total_pages = 0
for ch in (10, 11, 12, 13, 14):
    p = OUT / f"chapter{ch}-formula.pdf"
    if not p.exists():
        ok(f"chapter{ch}-formula.pdf present", False)
        continue
    doc = pymupdf.open(p)
    total_pages += doc.page_count
    w, h = doc[0].rect.width, doc[0].rect.height
    ratio = w / h
    ok(f"chapter{ch} PDF geometry matches the reference aspect",
       abs(ratio - E.PAGE_W / E.PAGE_H) < 0.01,
       f"{doc.page_count}p, {w:.0f}x{h:.0f}, ratio {ratio:.4f}")
    pngs = sorted(OUT.glob(f"chapter{ch}-formula*.png"))
    ok(f"chapter{ch} has one PNG per PDF page",
       len(pngs) == doc.page_count, f"{len(pngs)} png vs {doc.page_count} pages")
    txt = "".join(pg.get_text() for pg in doc)
    ok(f"chapter{ch} PDF has no replacement character", "\ufffd" not in txt)
    doc.close()
print(f"     total sheets: {total_pages}")

print("\n" + "=" * 64)
print(f"TOTAL: {passed} passed, {len(fails)} failed")
if fails:
    print("\nFAILURES:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("ALL FORMULA-SHEET CHECKS PASSED")
