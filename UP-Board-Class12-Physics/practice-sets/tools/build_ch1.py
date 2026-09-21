# -*- coding: utf-8 -*-
"""अध्याय 1 — chapter1.pdf तथा 60 समाधान फाइलें बनाता है।"""
import os, re, html, sys, shutil
from ch1_part1 import PART1
from ch1_part2 import PART2
from ch1_part3 import PART3

QS = PART1 + PART2 + PART3
assert len(QS) == 60, f"60 प्रश्न चाहिए, मिले {len(QS)}"
assert [q["n"] for q in QS] == list(range(1, 61)), "प्रश्न क्रम टूटा है"

CH_NO    = 1
CH_NAME  = "वैद्युत आवेश तथा क्षेत्र"
CH_EN    = "Electric Charges and Fields"

OWNER, REPO, BRANCH = "singhupavinash8506-arch", "Phusics", "up-board-class12-2026-27"
REPO_SUB = "UP-Board-Class12-Physics/practice-sets"
BLOB = f"https://github.com/{OWNER}/{REPO}/blob/{BRANCH}/{REPO_SUB}"

OUT   = "/projects/sandbox/Phusics/UP-Board-Class12-Physics/practice-sets"
SOLD  = os.path.join(OUT, "solutions")
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


# ───────────────────────────── PDF ─────────────────────────────
def q_card(q):
    url = f"{BLOB}/solutions/ch{CH_NO}sol{q['n']}.md"
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


def build_html():
    blocks = []
    for cat in (1, 2, 3):
        title, desc = CATS[cat]
        items = [x for x in QS if x["cat"] == cat]
        blocks.append(f"""
        <section class="cat">
          <div class="cathead">
            <h2>{title}</h2>
            <p>{desc}</p>
            <div class="catmeta">कुल {len(items)} प्रश्न &nbsp;·&nbsp;
                 प्रश्न {items[0]['n']} से {items[-1]['n']} तक</div>
          </div>
          {''.join(q_card(q) for q in items)}
        </section>""")

    return f"""<!DOCTYPE html>
<html lang="hi"><head><meta charset="utf-8"><title>अध्याय {CH_NO} — अभ्यास सेट</title>
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
  <h1>अध्याय {CH_NO} — {CH_NAME}</h1>
  <div class="en">{CH_EN} &nbsp;|&nbsp; अभ्यास सेट &nbsp;|&nbsp; 60 प्रश्न</div>
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
  <b>दिए गए नियतांक —</b> 1/4πε₀ = 9 × 10⁹ N·m²/C² &nbsp;·&nbsp; ε₀ = 8.85 × 10⁻¹² C²/N·m²
  &nbsp;·&nbsp; e = 1.6 × 10⁻¹⁹ C &nbsp;·&nbsp; mₑ = 9.1 × 10⁻³¹ kg
</div>

{''.join(blocks)}

<div class="foot">
  सभी प्रश्न UPMSP के 2026-27 पाठ्यक्रम तथा 2019, 2021-22, 2025-26 एवं फरवरी 2026 के
  प्रश्नपत्रों के विश्लेषण पर आधारित हैं।<br>
  सभी संख्यात्मक उत्तर स्वतन्त्र रूप से सत्यापित हैं।
</div>
</body></html>"""


def render_pdf():
    from playwright.sync_api import sync_playwright
    src = "/projects/sandbox/build/chapter1.html"
    open(src, "w", encoding="utf-8").write(build_html())
    footer = """
    <div style="width:100%;font-size:7.5pt;color:#6b7280;padding:0 11mm;
                font-family:'Noto Sans Devanagari','DejaVu Sans',sans-serif;
                display:flex;justify-content:space-between;">
      <span>अध्याय 1 &middot; वैद्युत आवेश तथा क्षेत्र</span>
      <span style="color:#dc2626;font-weight:bold;">&#10084;</span>
      <span>पृष्ठ <span class="pageNumber"></span> / <span class="totalPages"></span></span>
    </div>"""
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page()
        pg.goto("file://" + src)
        pg.wait_for_timeout(1500)
        pg.pdf(path=os.path.join(OUT, "chapter1.pdf"), format="A4",
               print_background=True, display_header_footer=True,
               header_template="<div></div>", footer_template=footer,
               margin={"top":"13mm","bottom":"16mm","left":"11mm","right":"11mm"})
        pg.screenshot(path="/projects/sandbox/build/chapter1_preview.png", full_page=False)
        b.close()


# ─────────────────────────── solutions ───────────────────────────
def md_escape_keep_html(s):
    """HTML tags we use (<b> <i> <br> <sub> <sup>) render fine on GitHub — keep as-is."""
    return s


def build_solution(q):
    n = q["n"]
    prev_l = (f"[⬅️ प्रश्न {n-1}](ch{CH_NO}sol{n-1}.md)" if n > 1 else "⬅️ *पहला प्रश्न*")
    next_l = (f"[प्रश्न {n+1} ➡️](ch{CH_NO}sol{n+1}.md)" if n < 60 else "*अन्तिम प्रश्न* ➡️")

    steps = []
    for i, (head, body) in enumerate(q["steps"], 1):
        steps.append(f"### चरण {i} — {head}\n\n{md_escape_keep_html(body)}\n")

    return f"""# प्रश्न {n} — विस्तृत हल

> **अध्याय {CH_NO}: {CH_NAME}** &nbsp;|&nbsp; श्रेणी: **{CATBADGE[q['cat']]}**
> &nbsp;|&nbsp; अंक: **{q['marks']}** &nbsp;|&nbsp; विषय: **{q['topic']}**

---

## 📋 प्रश्न

{md_escape_keep_html(q['q'])}

---

## 🧮 प्रयुक्त सूत्र

```
{q['formula']}
```

## 🤔 यह सूत्र क्यों लगाया?

{md_escape_keep_html(q['why'])}

---

## ✍️ चरणबद्ध हल

{chr(10).join(steps)}
---

## ✅ उत्तर

> **{md_escape_keep_html(q['ans'])}**

---

## 🎯 परीक्षा की ट्रिक

{md_escape_keep_html(q['trick'])}

---

## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान

{md_escape_keep_html(q['alt'])}

---

<div align="center">

{prev_l} &nbsp;&nbsp;|&nbsp;&nbsp; [📑 सूची](README.md) &nbsp;&nbsp;|&nbsp;&nbsp; {next_l}

**बनाया गया ❤️ से**

</div>
"""


def build_index():
    rows = []
    for cat in (1, 2, 3):
        title, _ = CATS[cat]
        rows.append(f"\n### {title}\n")
        rows.append("| प्रश्न | विषय | अंक | हल |")
        rows.append("|---|---|---|---|")
        for q in [x for x in QS if x["cat"] == cat]:
            rows.append(f"| {q['n']} | {q['topic']} | {q['marks']} | "
                        f"[हल देखें](ch{CH_NO}sol{q['n']}.md) |")
    return f"""# अध्याय {CH_NO} — {CH_NAME} : समाधान सूची

कक्षा 12 भौतिक विज्ञान · UP बोर्ड · सत्र 2026-27 · कुल **60 प्रश्न**

प्रश्नपत्र: [chapter1.pdf](../chapter1.pdf)
{chr(10).join(rows)}

---

<div align="center">

**बनाया गया ❤️ से**

</div>
"""


if __name__ == "__main__":
    os.makedirs(SOLD, exist_ok=True)
    for q in QS:
        open(os.path.join(SOLD, f"ch{CH_NO}sol{q['n']}.md"), "w",
             encoding="utf-8").write(build_solution(q))
    open(os.path.join(SOLD, "README.md"), "w", encoding="utf-8").write(build_index())
    print(f"{len(QS)} समाधान फाइलें + सूची बनीं")
    render_pdf()
    print("chapter1.pdf बन गया")
