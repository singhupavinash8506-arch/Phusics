# -*- coding: utf-8 -*-
"""सामान्य बिल्डर — किसी भी अध्याय का chapterN.pdf तथा 60 समाधान फाइलें बनाता है।
प्रयोग:  python3 build.py 2
"""
import os, sys, importlib

CHAPTERS = {
 1:  ("वैद्युत आवेश तथा क्षेत्र", "Electric Charges and Fields"),
 2:  ("स्थिरवैद्युत विभव तथा धारिता", "Electrostatic Potential and Capacitance"),
 3:  ("विद्युत धारा", "Current Electricity"),
 4:  ("गतिमान आवेश और चुम्बकत्व", "Moving Charges and Magnetism"),
 5:  ("चुम्बकत्व एवं द्रव्य", "Magnetism and Matter"),
 6:  ("वैद्युतचुम्बकीय प्रेरण", "Electromagnetic Induction"),
 7:  ("प्रत्यावर्ती धारा", "Alternating Current"),
 8:  ("वैद्युतचुम्बकीय तरंगें", "Electromagnetic Waves"),
 9:  ("किरण प्रकाशिकी एवं प्रकाशिक यंत्र", "Ray Optics and Optical Instruments"),
 10: ("तरंग प्रकाशिकी", "Wave Optics"),
 11: ("विकिरण तथा द्रव्य की द्वैत प्रकृति", "Dual Nature of Radiation and Matter"),
 12: ("परमाणु", "Atoms"),
 13: ("नाभिक", "Nuclei"),
 14: ("अर्धचालक इलेक्ट्रॉनिकी", "Semiconductor Electronics"),
}

CONSTANTS = {
 1: "1/4πε₀ = 9 × 10⁹ N·m²/C² &nbsp;·&nbsp; ε₀ = 8.85 × 10⁻¹² C²/N·m² "
    "&nbsp;·&nbsp; e = 1.6 × 10⁻¹⁹ C &nbsp;·&nbsp; mₑ = 9.1 × 10⁻³¹ kg",
 2: "1/4πε₀ = 9 × 10⁹ N·m²/C² &nbsp;·&nbsp; ε₀ = 8.85 × 10⁻¹² C²/N·m² "
    "&nbsp;·&nbsp; e = 1.6 × 10⁻¹⁹ C &nbsp;·&nbsp; 1 μF = 10⁻⁶ F, 1 pF = 10⁻¹² F",
 3: "e = 1.6 × 10⁻¹⁹ C &nbsp;·&nbsp; mₑ = 9.1 × 10⁻³¹ kg &nbsp;·&nbsp; "
    "ताँबे हेतु n = 8.5 × 10²⁸ प्रति m³ &nbsp;·&nbsp; ρ(ताँबा) = 1.7 × 10⁻⁸ Ω·m",
 4: "μ₀ = 4π × 10⁻⁷ T·m/A &nbsp;·&nbsp; μ₀/4π = 10⁻⁷, μ₀/2π = 2 × 10⁻⁷ "
    "&nbsp;·&nbsp; e = 1.6 × 10⁻¹⁹ C &nbsp;·&nbsp; mₑ = 9.1 × 10⁻³¹ kg "
    "&nbsp;·&nbsp; m<sub>p</sub> = 1.67 × 10⁻²⁷ kg",
}

OWNER, REPO, BRANCH = "singhupavinash8506-arch", "Phusics", "up-board-class12-2026-27"
REPO_SUB = "UP-Board-Class12-Physics/practice-sets"
BLOB  = f"https://github.com/{OWNER}/{REPO}/blob/{BRANCH}/{REPO_SUB}"
OUT   = "/projects/sandbox/Phusics/UP-Board-Class12-Physics/practice-sets"
FONTS = "/projects/sandbox/fonts"

CATS = {
 1: ("श्रेणी 1 — सूत्र आधारित प्रश्न",
     "सूत्र सीधे लगाकर हल कीजिए। लक्ष्य — सूत्र पहचानना, मात्रक बदलना तथा घातों की गणना।"),
 2: ("श्रेणी 2 — मान ज्ञात करना",
     "यहाँ उत्तर दिया है और कोई राशि अज्ञात है। प्रश्न 21–30 में एक अज्ञात, "
     "प्रश्न 31–40 में दो अज्ञात राशियाँ हैं।"),
 3: ("श्रेणी 3 — विविध (बोर्ड स्तर, कठिन)",
     "निगमन, वैचारिक तथा बहुचरणीय प्रश्न — जैसे बोर्ड परीक्षा के 3 व 5 अंक वाले खण्डों में आते हैं।"),
}
CATBADGE = {1: "सूत्र आधारित", 2: "मान ज्ञात करना", 3: "विविध"}


import re as _re

# X_सबस्क्रिप्ट  ->  X<sub>सबस्क्रिप्ट</sub>
# केवल गद्य क्षेत्रों पर लगाइए; 'formula' कोड ब्लॉक में है, अतः उसे अछूता छोड़ा जाता है।
_SUB = _re.compile(r'([A-Za-zΑ-Ωα-ω])_([A-Za-z0-9]+|[\u0900-\u097F]+)')

def subs(text):
    """अधोलेख (subscript) को सही HTML में बदलता है।"""
    return _SUB.sub(r'\1<sub>\2</sub>', text)


def apply_subs(q):
    """प्रश्न के गद्य क्षेत्रों में अधोलेख लगाइए ('formula' को छोड़कर)।"""
    q = dict(q)
    for f in ("q", "ans", "trick", "alt", "why", "topic"):
        q[f] = subs(q[f])
    q["steps"] = [(subs(h), subs(b)) for h, b in q["steps"]]
    return q


# देवनागरी U+0900-097F है। अन्य किसी भारतीय लिपि का वर्ण गलती से आ जाना
# फॉन्ट में खाली डिब्बा (tofu) दिखाता है, अतः बिल्ड के समय ही पकड़ा जाता है।
_OTHER_INDIC = [(0x0980, 0x09FF, "Bengali"), (0x0A00, 0x0A7F, "Gurmukhi"),
                (0x0A80, 0x0AFF, "Gujarati"), (0x0B00, 0x0B7F, "Oriya"),
                (0x0B80, 0x0BFF, "Tamil"),    (0x0C00, 0x0C7F, "Telugu"),
                (0x0C80, 0x0CFF, "Kannada"),  (0x0D00, 0x0D7F, "Malayalam")]


def check_script(q, ch):
    """गलत लिपि के वर्ण मिलने पर बिल्ड रोक दीजिए।"""
    fields = {f: q[f] for f in ("q", "ans", "trick", "alt", "why", "topic", "formula")}
    for i, (h, b) in enumerate(q["steps"], 1):
        fields[f"step{i}-शीर्षक"] = h
        fields[f"step{i}"] = b
    for name, text in fields.items():
        for c in text:
            for lo, hi, script in _OTHER_INDIC:
                if lo <= ord(c) <= hi:
                    raise ValueError(
                        f"अध्याय {ch} प्रश्न {q['n']} [{name}]: {script} वर्ण "
                        f"U+{ord(c):04X} ({c!r}) मिला — देवनागरी होना चाहिए")


def load(ch):
    qs = []
    for p in (1, 2, 3):
        mod = importlib.import_module(f"ch{ch}_part{p}")
        qs += getattr(mod, f"PART{p}")
    assert len(qs) == 60, f"60 प्रश्न चाहिए, मिले {len(qs)}"
    assert [q["n"] for q in qs] == list(range(1, 61)), "प्रश्न क्रम टूटा है"
    for q in qs:
        check_script(q, ch)
    return [apply_subs(q) for q in qs]


def q_card(q, ch):
    url = f"{BLOB}/solutions/ch{ch}sol{q['n']}.md"
    return f"""
    <div class="q">
      <div class="qhead">
        <span class="qn">{q['n']}</span>
        <span class="tag tag-topic">{q['topic']}</span>
        <span class="tag tag-marks">{q['marks']} अंक</span>
        <span class="tag tag-cat">{CATBADGE[q['cat']]}</span>
      </div>
      <div class="qbody">{q['q']}</div>
      <a class="sol" href="{url}">हल देखें &#9656;</a>
    </div>"""


def build_html(ch, qs):
    name, en = CHAPTERS[ch]
    blocks = []
    for cat in (1, 2, 3):
        title, desc = CATS[cat]
        items = [x for x in qs if x["cat"] == cat]
        blocks.append(f"""
        <section class="cat">
          <div class="cathead">
            <h2>{title}</h2>
            <p>{desc}</p>
            <div class="catmeta">कुल {len(items)} प्रश्न &nbsp;·&nbsp;
                 प्रश्न {items[0]['n']} से {items[-1]['n']} तक</div>
          </div>
          {''.join(q_card(q, ch) for q in items)}
        </section>""")

    return f"""<!DOCTYPE html>
<html lang="hi"><head><meta charset="utf-8"><title>अध्याय {ch} — अभ्यास सेट</title>
<style>
@font-face {{ font-family:'Dev'; src:url('file://{FONTS}/DevRegular.ttf'); font-weight:400; }}
@font-face {{ font-family:'Dev'; src:url('file://{FONTS}/DevBold.ttf');    font-weight:700; }}
@page {{ size:A4; margin:13mm 11mm 16mm 11mm; }}
* {{ box-sizing:border-box; }}
body {{ font-family:'Dev','DejaVu Sans',sans-serif; font-size:10pt; line-height:1.6;
        color:#16182b; margin:0; }}
.hero {{ background:linear-gradient(135deg,#1e3a8a 0%,#6d28d9 55%,#be185d 100%);
         color:#fff; padding:20px 22px; border-radius:14px; margin-bottom:6px; }}
.hero .kicker {{ font-size:9pt; letter-spacing:.5px; opacity:.92; }}
.hero h1 {{ margin:6px 0 2px; font-size:24pt; line-height:1.25; }}
.hero .en {{ font-size:10.5pt; opacity:.9; }}
.hero .strip {{ margin-top:12px; display:flex; gap:7px; flex-wrap:wrap; }}
.hero .chip {{ background:rgba(255,255,255,.18); border:1px solid rgba(255,255,255,.34);
               padding:3px 10px; border-radius:20px; font-size:8.5pt; }}
.howto {{ background:#f5f3ff; border:1px solid #ddd6fe; border-left:5px solid #6d28d9;
          border-radius:9px; padding:11px 14px; margin:12px 0 4px; font-size:9.3pt; }}
.howto b {{ color:#5b21b6; }}
.cat {{ margin-top:16px; }}
.cathead {{ background:#1e293b; color:#fff; border-radius:11px; padding:12px 16px; margin-bottom:11px; }}
.cathead h2 {{ margin:0 0 4px; font-size:14.5pt; }}
.cathead p  {{ margin:0; font-size:9.2pt; opacity:.9; }}
.catmeta {{ margin-top:7px; font-size:8.3pt; background:rgba(255,255,255,.14);
            display:inline-block; padding:2px 9px; border-radius:12px; }}
.q {{ border:1px solid #e3e1f0; border-left:4px solid #6d28d9; background:#fcfbff;
      border-radius:0 10px 10px 0; padding:9px 13px 11px; margin-bottom:9px;
      break-inside:avoid; page-break-inside:avoid; }}
.qhead {{ margin-bottom:5px; }}
.qn {{ display:inline-block; background:#6d28d9; color:#fff; width:21px; height:21px;
       border-radius:50%; text-align:center; font-weight:700; font-size:9pt;
       line-height:21px; margin-right:6px; }}
.tag {{ display:inline-block; font-size:7.6pt; padding:2px 8px; border-radius:11px; margin-right:4px; }}
.tag-topic {{ background:#ede9fe; color:#5b21b6; border:1px solid #ddd6fe; }}
.tag-marks {{ background:#fef3c7; color:#92400e; border:1px solid #fde68a; }}
.tag-cat   {{ background:#e0f2fe; color:#075985; border:1px solid #bae6fd; }}
.qbody {{ margin:3px 0 7px; }}
.sol {{ display:inline-block; background:#dc2626; color:#fff !important; text-decoration:none;
        padding:3px 12px; border-radius:13px; font-size:8.4pt; font-weight:700; }}
.foot {{ margin-top:20px; border-top:2px dashed #c7c7d9; padding-top:11px;
         font-size:8.8pt; color:#4b5563; text-align:center; }}
</style></head><body>

<div class="hero">
  <div class="kicker">उत्तर प्रदेश माध्यमिक शिक्षा परिषद् &nbsp;·&nbsp; कक्षा 12 भौतिक विज्ञान &nbsp;·&nbsp; सत्र 2026-27</div>
  <h1>अध्याय {ch} — {name}</h1>
  <div class="en">{en} &nbsp;|&nbsp; अभ्यास सेट &nbsp;|&nbsp; 60 प्रश्न</div>
  <div class="strip">
    <span class="chip">20 सूत्र आधारित</span>
    <span class="chip">20 मान ज्ञात करना</span>
    <span class="chip">20 विविध (कठिन)</span>
    <span class="chip">प्रत्येक प्रश्न का विस्तृत हल</span>
  </div>
</div>

<div class="howto">
  <b>प्रयोग कैसे करें —</b> पहले स्वयं प्रश्न हल कीजिए, उसके बाद ही
  <b style="color:#dc2626">हल देखें &#9656;</b> पर क्लिक कीजिए। हर हल में सूत्र चुनने का कारण,
  चरणबद्ध गणना, परीक्षा की ट्रिक तथा वैकल्पिक विधि दी गई है।<br>
  <b>दिए गए नियतांक —</b> {CONSTANTS.get(ch, CONSTANTS[1])}
</div>

{''.join(blocks)}

<div class="foot">
  सभी प्रश्न UPMSP के 2026-27 पाठ्यक्रम तथा 2019, 2021-22, 2025-26 एवं फरवरी 2026 के
  प्रश्नपत्रों के विश्लेषण पर आधारित हैं।<br>
  सभी संख्यात्मक उत्तर स्वतन्त्र रूप से सत्यापित हैं।
</div>
</body></html>"""


def render_pdf(ch, qs):
    from playwright.sync_api import sync_playwright
    name, _ = CHAPTERS[ch]
    src = f"/projects/sandbox/build/chapter{ch}.html"
    open(src, "w", encoding="utf-8").write(build_html(ch, qs))
    footer = f"""
    <div style="width:100%;font-size:7.5pt;color:#6b7280;padding:0 11mm;
                font-family:'Noto Sans Devanagari','DejaVu Sans',sans-serif;
                display:flex;justify-content:space-between;">
      <span>अध्याय {ch} &middot; {name}</span>
      <span style="color:#dc2626;font-weight:bold;">&#10084;</span>
      <span>पृष्ठ <span class="pageNumber"></span> / <span class="totalPages"></span></span>
    </div>"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page()
        pg.goto("file://" + src)
        pg.wait_for_timeout(1500)
        pg.pdf(path=os.path.join(OUT, f"chapter{ch}.pdf"), format="A4",
               print_background=True, display_header_footer=True,
               header_template="<div></div>", footer_template=footer,
               margin={"top":"13mm","bottom":"16mm","left":"11mm","right":"11mm"})
        b.close()


def build_solution(q, ch):
    n, name = q["n"], CHAPTERS[ch][0]
    prev_l = (f"[⬅️ प्रश्न {n-1}](ch{ch}sol{n-1}.md)" if n > 1 else "⬅️ *पहला प्रश्न*")
    next_l = (f"[प्रश्न {n+1} ➡️](ch{ch}sol{n+1}.md)" if n < 60 else "*अन्तिम प्रश्न* ➡️")
    steps = [f"### चरण {i} — {h}\n\n{b}\n" for i, (h, b) in enumerate(q["steps"], 1)]
    return f"""# प्रश्न {n} — विस्तृत हल

> **अध्याय {ch}: {name}** &nbsp;|&nbsp; श्रेणी: **{CATBADGE[q['cat']]}**
> &nbsp;|&nbsp; अंक: **{q['marks']}** &nbsp;|&nbsp; विषय: **{q['topic']}**

---

## 📋 प्रश्न

{q['q']}

---

## 🧮 प्रयुक्त सूत्र

```
{q['formula']}
```

## 🤔 यह सूत्र क्यों लगाया?

{q['why']}

---

## ✍️ चरणबद्ध हल

{chr(10).join(steps)}
---

## ✅ उत्तर

> **{q['ans']}**

---

## 🎯 परीक्षा की ट्रिक

{q['trick']}

---

## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान

{q['alt']}

---

<div align="center">

{prev_l} &nbsp;&nbsp;|&nbsp;&nbsp; [📑 सूची](README.md) &nbsp;&nbsp;|&nbsp;&nbsp; {next_l}

**बनाया गया ❤️ से**

</div>
"""


def chapter_section(ch, qs):
    """एक अध्याय का खण्ड — मास्टर सूची में जोड़ने हेतु।"""
    name, en = CHAPTERS[ch]
    out = [f"\n## अध्याय {ch} — {name}\n",
           f"*{en}* · प्रश्नपत्र: [chapter{ch}.pdf](../chapter{ch}.pdf)\n"]
    for cat in (1, 2, 3):
        title, _ = CATS[cat]
        out.append(f"\n**{title}**\n")
        out.append("| प्रश्न | विषय | अंक | हल |")
        out.append("|---|---|---|---|")
        for q in [x for x in qs if x["cat"] == cat]:
            out.append(f"| {q['n']} | {q['topic']} | {q['marks']} | "
                       f"[हल देखें](ch{ch}sol{q['n']}.md) |")
    return "\n".join(out)


def build_master_index(sold):
    """सभी उपलब्ध अध्यायों की एक मास्टर सूची (solutions/README.md)।
    अध्याय 1 की फाइलें पहले से README.md से जुड़ी हैं, अतः यही एक सूची रखी जाती है।"""
    built = [c for c in sorted(CHAPTERS)
             if os.path.exists(os.path.join(sold, f"ch{c}sol1.md"))]
    parts = ["# समाधान सूची — कक्षा 12 भौतिक विज्ञान\n",
             "UP बोर्ड · सत्र 2026-27 · प्रत्येक अध्याय में 60 प्रश्न\n",
             "| अध्याय | नाम | स्थिति |", "|---|---|---|"]
    for c in sorted(CHAPTERS):
        nm = CHAPTERS[c][0]
        parts.append(f"| {c} | {nm} | " +
                     (f"[सूची देखें](#अध्याय-{c}--{nm.replace(' ', '-')}) ✅" if c in built
                      else "— आना शेष") + " |")
    for c in built:
        parts.append(chapter_section(c, load(c)))
    parts += ["\n---\n", '<div align="center">\n',
              "**बनाया गया ❤️ से**\n", "</div>\n"]
    return "\n".join(parts)


if __name__ == "__main__":
    ch = int(sys.argv[1])
    qs = load(ch)
    sold = os.path.join(OUT, "solutions")
    os.makedirs(sold, exist_ok=True)
    for q in qs:
        open(os.path.join(sold, f"ch{ch}sol{q['n']}.md"), "w",
             encoding="utf-8").write(build_solution(q, ch))
    open(os.path.join(sold, "README.md"), "w",
         encoding="utf-8").write(build_master_index(sold))
    print(f"अध्याय {ch}: {len(qs)} समाधान फाइलें बनीं + मास्टर सूची अद्यतन")
    render_pdf(ch, qs)
    print(f"chapter{ch}.pdf बन गया")
