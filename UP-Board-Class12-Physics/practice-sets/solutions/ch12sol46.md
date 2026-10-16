# प्रश्न 46 — विस्तृत हल

> **अध्याय 12: परमाणु** &nbsp;|&nbsp; श्रेणी: **विविध**
> &nbsp;|&nbsp; अंक: **5** &nbsp;|&nbsp; विषय: **hydrogen-like orbit radius का निगमन**

---

## 📋 प्रश्न

Bohr postulates से +Ze nucleus वाले hydrogen-like atom की nth orbit radius rₙ व्युत्पन्न कीजिए और n तथा Z पर निर्भरता समझाइए।

---

## 🧮 प्रयुक्त सूत्र

```
mₑv²/r=(1/4πε₀)Ze²/r²;    mₑvr=nħ;    r_n=a₀n²/Z
```

## 🤔 यह सूत्र क्यों लगाया?

radius formula Coulomb–centripetal dynamics और quantum angular momentum को एक साथ हल करने से मिलता है। यही derivation continuous classical radii को discrete Bohr radii में बदलता है।

---

## ✍️ चरणबद्ध हल

### चरण 1 — बल-सन्तुलन

circular orbit में कूलॉम attraction केन्द्राभिमुख force है: mₑv²/r=(1/4πε₀)Ze²/r²।

### चरण 2 — quantisation

Bohr condition mₑvr=nħ से v=nħ/(mₑr) मिलता है।

### चरण 3 — substitution

v का यह मान force equation में रखने पर mₑ[n²ħ²/(mₑ²r²)]/r=(1/4πε₀)Ze²/r²।

### चरण 4 — सरलीकरण

common powers cancel करने पर n²ħ²/(mₑr)=(1/4πε₀)Ze²।

### चरण 5 — radius

अतः rₙ=(4πε₀ħ²/mₑe²)(n²/Z)। bracket को Bohr radius a₀ कहते हैं।

### चरण 6 — मानक रूप

a₀=5.29×10⁻¹¹ m=0.529 Å, इसलिए rₙ=a₀n²/Z। hydrogen के लिए Z=1 से rₙ=n²a₀।

### चरण 7 — निर्भरता

n बढ़ने पर radius n² से तेजी से बढ़ती; समान n पर Z बढ़ने से stronger attraction radius 1/Z से घटाती है।

### चरण 8 — consistency

n=1,Z=1 पर r₁=a₀ और He⁺ same n पर hydrogen radius की आधी मिलती है, जो scaling check है।

---

## ✅ उत्तर

> **Coulomb केन्द्राभिमुख balance और mₑvr=nħ से rₙ=a₀n²/Z, जहाँ a₀=4πε₀ħ²/(mₑe²)=0.529 Å मिलता है।**

---

## 🎯 परीक्षा की ट्रिक

force equation में Coulomb denominator r² और centripetal denominator r है। final radius n²/Z है, Z² denominator नहीं।

---

## 🔄 वैकल्पिक विधि / अतिरिक्त ध्यान

force equation से mv²=kZe²/r और quantisation से mvr=nħ लेकर दोनों को algebraically eliminate करना derivation का सबसे छोटा बोर्ड रूप है।

---

<div align="center">

[⬅️ प्रश्न 45](ch12sol45.md) &nbsp;&nbsp;|&nbsp;&nbsp; [📑 सूची](README.md) &nbsp;&nbsp;|&nbsp;&nbsp; [प्रश्न 47 ➡️](ch12sol47.md)

**बनाया गया ❤️ से**

</div>
