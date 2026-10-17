# -*- coding: utf-8 -*-
"""Render the Chapter 10-14 formula sheets to PDF + PNG, fail-closed on overflow.

Pages are served from disk over file:// -- with page.set_content() the document
origin is about:blank and Chromium refuses to load the file:// @font-face
sources, which silently renders every Devanagari glyph blank.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

import engine as E
from content import CHAPTERS, FOOTER

OUT = Path("/projects/sandbox/Phusics/UP-Board-Class12-Physics/formula")
TMP = Path("/projects/sandbox/build/fsheet/tmp")
SCALE = 3

PRINT_CSS = """
@page { size: %dpx %dpx; margin: 0; }
@media print {
  html, body { background:#fff; }
  .board { break-after: page; page-break-after: always; }
  .board:last-child { break-after: auto; page-break-after: auto; }
}
""" % (E.PAGE_W, E.PAGE_H)

# Counts glyph ink drawn by a named font: zero means the face never loaded.
GLYPH_PROBE = """
(() => {
  const out = {};
  for (const [key, spec, text] of [
      ['devRegular', '400 30px Dev',  'तरंग प्रकाशिकी'],
      ['devBold',    '700 30px Dev',  'नाभिक अर्धचालक'],
      ['cmuRoman',   '400 30px CMU',  'Rutherford 1240'],
      ['cmuItalic',  'italic 400 30px CMU', 'nvEIR']]) {
    const c = document.createElement('canvas');
    c.width = 420; c.height = 60;
    const g = c.getContext('2d');
    g.font = spec; g.fillStyle = '#000';
    g.fillText(text, 4, 42);
    const d = g.getImageData(0, 0, c.width, c.height).data;
    let n = 0;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 12) n++;
    out[key] = n;
  }
  out.faces = document.fonts.size;
  out.devOK  = document.fonts.check('400 13px Dev');
  out.devBOK = document.fonts.check('700 13px Dev');
  out.cmuOK  = document.fonts.check('400 13px CMU');
  return out;
})()
"""


def open_doc(browser, html: str, name: str, scale: int = 1):
    """Write the document to disk and navigate, so file:// fonts are allowed."""
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / f"{name}.html"
    path.write_text(html, encoding="utf-8")
    page = browser.new_page(viewport={"width": E.PAGE_W, "height": E.PAGE_H},
                            device_scale_factor=scale)
    page.goto(f"file://{path}", wait_until="load")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(500)
    return page


def build() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    # drop artefacts from previous runs so a reduced sheet count cannot leave
    # an orphaned PNG behind
    for old in list(OUT.glob("chapter*-formula*.png")) + \
               list(OUT.glob("chapter*-formula.pdf")):
        old.unlink()
    problems: list[str] = []
    made: list[tuple[int, int]] = []
    font_checked = False

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--font-render-hinting=none"])

        for chap in CHAPTERS:
            ch = chap["ch"]
            secs = chap["sections"]

            # ---- 1. measure every section at final width
            page = open_doc(browser, E.measure_doc(secs), f"measure{ch}")

            if not font_checked:
                g = page.evaluate(GLYPH_PROBE)
                print(f"font probe: {g}")
                for key, label in (("devRegular", "Devanagari regular"),
                                   ("devBold", "Devanagari bold"),
                                   ("cmuRoman", "CMU roman"),
                                   ("cmuItalic", "CMU italic")):
                    if g[key] < 150:
                        problems.append(
                            f"font {label} drew only {g[key]} ink px "
                            f"-- face did not load")
                for flag, label in (("devOK", "Dev 400"), ("devBOK", "Dev 700"),
                                    ("cmuOK", "CMU 400")):
                    if not g[flag]:
                        problems.append(f"font {label} not available")
                font_checked = True

            meas = page.evaluate("""
            Array.from(document.querySelectorAll('.sec')).map(sec=>{
              const dg = sec.querySelector('.dg');
              return {
                head: sec.querySelector('.sh').getBoundingClientRect().height,
                items: Array.from(sec.querySelectorAll('.it'))
                         .map(e=>e.getBoundingClientRect().height),
                dg: dg ? dg.getBoundingClientRect().height : 0
              };
            })
            """)
            page.close()
            if len(meas) != len(secs):
                problems.append(f"ch{ch}: measured {len(meas)} of {len(secs)}")
                continue
            bad = [s["no"] for s, m in zip(secs, meas)
                   if len(m["items"]) != len(s["items"])]
            if bad:
                problems.append(f"ch{ch}: item count mismatch in sections {bad}")
                continue

            # ---- 1b. true usable height for this chapter's (possibly wrapping) title
            page = open_doc(browser, E.probe_doc(chap["hi"], chap["en"], FOOTER),
                            f"probe{ch}")
            budget = page.evaluate(
                "document.querySelector('.flow').getBoundingClientRect().height")
            page.close()

            # ---- 2. flow item-by-item into sheets that cannot overflow
            # a few px of slack absorbs sub-pixel rounding between the
            # measuring pass and the final render
            groups = E.balanced_flow(secs, meas, budget - 6)

            sheets = []
            for idx, grp in enumerate(groups, 1):
                part = (f"भाग {idx}/{len(groups)}" if len(groups) > 1 else None)
                sheets.append({"hi": chap["hi"], "en": chap["en"],
                               "part": part, "chunks": grp})

            # ---- 3. render
            html = E.sheets_doc(sheets, FOOTER).replace(
                "</style>", PRINT_CSS + "</style>")
            page = open_doc(browser, html, f"sheet{ch}", scale=SCALE)

            # ---- 4. fail-closed layout verification
            report = page.evaluate("""
            Array.from(document.querySelectorAll('.board')).map((b,i)=>{
              const ink  = b.querySelector('.ink');
              const flow = b.querySelector('.flow');
              const foot = b.querySelector('.foot');
              const paper= b.querySelector('.paper');
              const ir = ink.getBoundingClientRect();
              const fr = flow.getBoundingClientRect();
              const ftr= foot.getBoundingClientRect();
              const pr = paper.getBoundingClientRect();
              let worst = 0;
              ink.querySelectorAll('.it,.sh,.title,.dg').forEach(el=>{
                const r = el.getBoundingClientRect();
                worst = Math.max(worst, r.right-ir.right, r.bottom-ir.bottom);
              });
              let used = 0;
              b.querySelectorAll('.sec').forEach(s=>{
                used += s.getBoundingClientRect().height
                      + parseFloat(getComputedStyle(s).marginBottom||0);
              });
              // Headings and maths are white-space:nowrap, so unlike ordinary
              // text they do not reflow around a floated diagram -- they just
              // run underneath it. Flag any that actually overlap.
              const clash = [];
              b.querySelectorAll('.sec').forEach(sec=>{
                const dg = sec.querySelector('.dg');
                if (!dg) return;
                const d = dg.getBoundingClientRect();
                sec.querySelectorAll('.sh, .m').forEach(el=>{
                  // A heading is a block, so its own rect spans the full
                  // content width regardless of how short the text is. Measure
                  // the inline text boxes via a Range instead.
                  const rng = document.createRange();
                  rng.selectNodeContents(el);
                  for (const r of rng.getClientRects()) {
                    const vOver = Math.min(r.bottom,d.bottom) - Math.max(r.top,d.top);
                    if (vOver > 2 && r.right > d.left + 1) {
                      clash.push(el.textContent.trim().slice(0,42));
                      break;
                    }
                  }
                });
              });
              return {
                page: i+1,
                inkScroll: ink.scrollHeight, inkClient: ink.clientHeight,
                flowH: fr.height, usedH: used,
                footInside: (ftr.bottom <= pr.bottom + 0.6),
                footBelowFlow: (ftr.top >= fr.bottom - 0.6),
                overflowPx: Math.round(worst*100)/100,
                wrappedHeads: Array.from(b.querySelectorAll('.sh'))
                   .filter(h=>h.getBoundingClientRect().height > 26)
                   .map(h=>h.textContent.trim().slice(0,58)),
                titleWrapped: (b.querySelector('.title')
                   .getBoundingClientRect().height > 26),
                fillPct: Math.round(100*used/fr.height),
                diagramClash: clash.slice(0,4),
                // any of these in the *rendered text* means markup escaped
                rawHtml: (ink.innerText.match(
                   /class=|<span|<\\/|&lt;span|"op"|&amp;lt;|&amp;gt;/g) || [])
                   .slice(0,4),
                sections: b.querySelectorAll('.sec').length,
                mathSpans: b.querySelectorAll('.m').length,
                // a nuclide prescript is exactly two stacked lines; more means
                // an inner span was promoted to a block
                tallNuc: Array.from(b.querySelectorAll('.nuc'))
                   .filter(e=>e.getBoundingClientRect().height > 22).length,
                nucs: b.querySelectorAll('.nuc').length,
                fracs: b.querySelectorAll('.frac').length,
                boxed: b.querySelectorAll('.boxed').length,
                svgs: b.querySelectorAll('.dg svg').length
              };
            })
            """)

            for r in report:
                tag = f"ch{ch} p{r['page']}"
                if r["inkScroll"] > r["inkClient"] + 1:
                    problems.append(f"{tag}: ink overflow "
                                    f"{r['inkScroll']} > {r['inkClient']}")
                if r["overflowPx"] > 0.75:
                    problems.append(f"{tag}: element escapes border "
                                    f"by {r['overflowPx']}px")
                if not r["footInside"]:
                    problems.append(f"{tag}: footer outside paper")
                if not r["footBelowFlow"]:
                    problems.append(f"{tag}: footer collides with content")
                if r["usedH"] > r["flowH"] + 1:
                    problems.append(f"{tag}: content {r['usedH']:.0f}px exceeds "
                                    f"usable {r['flowH']:.0f}px")
                for head in r["wrappedHeads"]:
                    problems.append(f"{tag}: heading wraps -> {head!r}")
                if r["titleWrapped"]:
                    problems.append(f"{tag}: chapter title wraps to two lines")
                if r["rawHtml"]:
                    problems.append(f"{tag}: raw markup leaked into text -> "
                                    f"{r['rawHtml']}")
                if r["tallNuc"]:
                    problems.append(f"{tag}: {r['tallNuc']} nuclide prescript(s) "
                                    f"taller than two lines")
                for c in r["diagramClash"]:
                    problems.append(f"{tag}: runs into its diagram -> {c!r}")

            pdf_path = OUT / f"chapter{ch}-formula.pdf"
            page.emulate_media(media="print")
            page.pdf(path=str(pdf_path), width=f"{E.PAGE_W}px",
                     height=f"{E.PAGE_H}px", print_background=True,
                     margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            page.emulate_media(media="screen")

            boards = page.query_selector_all(".board")
            for i, b in enumerate(boards, 1):
                suffix = f"-{i}" if len(boards) > 1 else ""
                b.screenshot(path=str(OUT / f"chapter{ch}-formula{suffix}.png"))
            page.close()

            made.append((ch, len(boards)))
            print(f"ch{ch}: {len(boards)} sheet(s), {len(secs)} sections, "
                  f"fill {[r['fillPct'] for r in report]}%, "
                  f"{sum(r['mathSpans'] for r in report)} math, "
                  f"{sum(r['fracs'] for r in report)} fractions, "
                  f"{sum(r['boxed'] for r in report)} boxed, "
                  f"{sum(r['svgs'] for r in report)} diagrams")

        browser.close()

    print("\n" + "=" * 62)
    if problems:
        print(f"VERIFICATION FAILED ({len(problems)} problems)")
        for p in problems:
            print("  -", p)
        return 1
    print(f"LAYOUT OK: {len(made)} chapters, {sum(n for _, n in made)} sheets, "
          f"fonts loaded, no overflow")
    return 0


if __name__ == "__main__":
    sys.exit(build())
