#!/usr/bin/env python3
"""Build the static Pip books site. Run: python3 build.py (needs Pillow and the book page PNGs on the box)."""
import html, os, json
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).parent
SITE = "https://jainaspp.github.io/pip-books"
GR = "https://jainaspark4.gumroad.com/l/"
UTM = "?utm_source=pipsite"
# All 6 books, US$9.99 minimum (pay what you want). 6 × US$4.99 = US$29.94 separately.
BUNDLE = "https://jainaspark4.gumroad.com/l/imzzp"
EMAIL = "jainaspp@gmail.com"

BOOKS = [
 dict(n=1, slug="pips-big-dig", src="/workspace/pipbook/pages", paid="yulzdr", sample="pips-big-dig-free-sample",
  en="Pip's Big Dig", zh="皮皮的大挖掘", theme_en="teamwork", theme_zh="一起合作",
  kw="teamwork story for kids",
  sum_en="Pip the mole wants to dig the biggest hole… alone. Scratch, scratch, scoop! His paws get tired, and the hole is still small. A robin hops by, then a rabbit, but Pip says, “No! I can do it all by myself!” Will he let his friends help? A warm story about teamwork: the pages start cool and grey while Pip digs alone and turn golden when the friends dig together.",
  sum_zh="皮皮想獨自挖一個最大的洞。可是一個人挖，真的比較好玩嗎？爪子累了，洞還是小小的。知更鳥和兔子來了，皮皮會讓朋友幫忙嗎？一個關於一起合作的溫暖故事。",
  short_en="Pip the mole wants to dig the biggest hole all by himself. Is digging alone really more fun?",
  short_zh="皮皮想獨自挖一個最大的洞，一個人挖真的比較好玩嗎？"),
 dict(n=2, slug="pip-and-the-big-rain", src="/workspace/pipbook2/pages", paid="pip-big-rain", sample="pip-big-rain-free-sample",
  en="Pip and the Big Rain", zh="皮皮和大雨天", theme_en="not giving up and solving problems together", theme_zh="不放棄、一起想辦法",
  kw="rainy day picture book",
  sum_en="Pitter, patter! After the big dig, a big rain comes. By morning the big hole is full of water, and Rabbit's burrow is flooded too. Pip sits in the mud and wants to give up. But Robin says, “Don't worry. Let's think together.” Then Pip watches a raindrop slide down a leaf… and has an idea. A gentle story about what to do when things go wrong: don't give up, think it through with your friends, and a bad day can turn into something new and good.",
  sum_zh="皮皮和朋友們的大洞被大雨灌滿了水，兔子的窩也進水了。皮皮想放棄，可是大家一起想辦法，壞事也能變成新的好事！",
  short_en="A big rain floods the hole and Rabbit's burrow. Pip wants to give up, until the friends think together.",
  short_zh="大雨把大洞灌滿了水，皮皮和朋友們一起想辦法。"),
 dict(n=3, slug="pip-and-the-night-lights", src="/workspace/pipbook3/pages", paid="pip-night-lights", sample="pip-night-lights-free-sample",
  en="Pip and the Night Lights", zh="皮皮和螢火蟲", theme_en="being brave in the dark, together", theme_zh="有朋友在身邊，不怕黑",
  kw="bedtime story scared of the dark",
  sum_en="The big hole is a little pond now, and Pip, Robin and Rabbit meet there to watch the stars. But when the sky gets dark, Rabbit's ears start to shake: “It's so dark! I'm scared.” Pip lives under the ground and isn't afraid of the dark at all. His secret? Close your eyes and listen. Ribbit, ribbit… chirp, chirp… A calm wind-down story about being brave together. It ends with the three friends snuggling up and saying goodnight.",
  sum_zh="天黑了，兔子好害怕。皮皮教大家閉上眼睛靜靜地聽，知更鳥輕輕地唱。原來有朋友在身邊，黑黑的夜晚也很美。",
  short_en="Night falls by the pond and Rabbit is scared of the dark. A calm bedtime story about being brave together.",
  short_zh="天黑了，兔子好害怕。有朋友在身邊，黑黑的夜晚也很美。"),
 dict(n=4, slug="pip-and-the-autumn-leaves", src="/workspace/pipbook4/pages", paid="pip-autumn-leaves", sample="pip-autumn-leaves-free-sample",
  en="Pip and the Autumn Leaves", zh="皮皮和落葉", theme_en="sharing", theme_zh="分享",
  kw="autumn picture book, sharing story for kids",
  sum_en="Flutter, flutter! Summer is over and the leaves on the hill turn orange, red and brown. Winter is coming, so Pip wants a warm leaf bed. Scratch, scratch, scoop! Pip's pile grows higher and higher, taller than Pip! But Robin's beak is small, and Robin can carry only one leaf at a time. As the sun goes down, Robin's nest is still cold… A gentle story about sharing with friends: Pip finds out that sharing makes everyone warm, Pip included.",
  sum_zh="皮皮堆了一大堆落葉，全都想留給自己。可是知更鳥的小窩還是冷冰冰的……皮皮決定分享，才發現分享讓大家都暖暖的、好開心！",
  short_en="Pip piles up autumn leaves for a warm winter bed. Will he share with Robin?",
  short_zh="皮皮堆了一大堆落葉，會分享給知更鳥嗎？"),
 dict(n=5, slug="pip-and-the-windy-day", src="/workspace/pipbook5/pages", paid="pip-windy-day", sample="pip-windy-day-free-sample",
  en="Pip and the Windy Day", zh="皮皮和大風天", theme_en="saying sorry and fixing things together", theme_zh="說對不起、一起修好",
  kw="saying sorry story for kids",
  sum_en="Whoo, whoo! Autumn is almost over and the wind is so strong today. Rabbit builds a leaf house from sticks and fallen leaves. Pip wants to see it too, so he digs a tunnel to get there faster… and pops up right under the leaf house. Down it tumbles! Pip quickly says, “The wind did it!”, but he feels a little stone inside. A gentle story about telling the truth, saying sorry and fixing things together.",
  sum_zh="兔子搭了一間葉子屋，卻被急急忙忙挖地道的皮皮弄倒了。皮皮先說「是大風吹的！」，心裡卻好不舒服……皮皮說了對不起，大家一起搭出更堅固的葉子屋！",
  short_en="Pip pops up under Rabbit's leaf house and knocks it down. A story about saying sorry and fixing it together.",
  short_zh="皮皮不小心弄倒了兔子的葉子屋，說聲對不起，再一起修好。"),
 dict(n=6, slug="pip-and-the-first-snow", src="/workspace/pipbook6/pages", paid="pip-first-snow", sample="pip-first-snow-free-sample",
  en="Pip and the First Snow", zh="皮皮和第一場雪", theme_en="caring for others", theme_zh="關心別人",
  kw="winter picture book, kindness story for kids",
  sum_en="Squeak, squeak! Winter is here, and Pip runs out of his underground room: “The first snow!” The three friends play on the white hill, until Robin spots some tiny footprints. Whose are they? The footprints lead to a low bush by the pond, and under it a little round ball is shivering. It's a baby hedgehog named Pom, who can't find the way home. A gentle story about caring for others: Rabbit holds Pom close, Pip digs a path to his warm underground room, and Robin brings soft moss and sweet red berries.",
  sum_zh="冬天的第一場雪，皮皮、兔子和知更鳥跟著小小的腳印，找到了在樹叢下發抖的刺蝟寶寶蓬蓬。皮皮挖小路，兔子抱一抱，知更鳥找青苔，大家一起照顧蓬蓬。",
  short_en="Tiny footprints in the first snow lead the friends to a shivering baby hedgehog named Pom.",
  short_zh="第一場雪，小小的腳印通到樹叢下，找到了發抖的刺蝟寶寶蓬蓬。"),
]

E = html.escape

def make_images(b):
    out = ROOT / "img" / b["slug"]
    out.mkdir(parents=True, exist_ok=True)
    src = Path(b["src"])
    cover = Image.open(src / "page-01.png").convert("RGB")
    cover.resize((600, 800), Image.LANCZOS).save(out / "cover.webp", "WEBP", quality=80, method=6)
    cover.resize((360, 480), Image.LANCZOS).save(out / "cover-sm.webp", "WEBP", quality=78, method=6)
    # Open Graph image 1200x630: cover centred on a blurred copy of itself
    bg = cover.resize((1200, 1600), Image.LANCZOS).crop((0, 485, 1200, 1115)).filter(ImageFilter.GaussianBlur(28))
    fg = cover.resize((472, 630), Image.LANCZOS)
    bg.paste(fg, ((1200 - 472) // 2, 0))
    bg.save(out / "og.jpg", "JPEG", quality=82, optimize=True, progressive=True)
    # Preview: story pages 1-4 (all inside the free sample: cover + first 5 story pages)
    for i, p in enumerate([2, 3, 4, 5], 1):
        Image.open(src / f"page-{p:02d}.png").convert("RGB").resize((720, 960), Image.LANCZOS).save(out / f"page-{i}.webp", "WEBP", quality=78, method=6)

CSS = """
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;color:#3b2f24;background:#fbf6ec;line-height:1.6}
a{color:#8a4b12}
header,main,footer{max-width:960px;margin:0 auto;padding:0 18px}
header{padding-top:18px;padding-bottom:6px}
header .brand{font-weight:700;font-size:1.1rem;text-decoration:none;color:#5a3d22}
h1{font-size:1.7rem;line-height:1.25;margin:.6em 0 .2em}h1 .zh{display:block;font-size:1.35rem;color:#6d4c2e}
h2{font-size:1.2rem;margin:1.6em 0 .5em}
.lead{font-size:1.02rem;margin:.3em 0 1em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:18px;margin:18px 0 28px}
.card{background:#fff;border-radius:14px;box-shadow:0 1px 4px rgba(80,50,20,.12);overflow:hidden;display:flex;flex-direction:column}
.card a.cov{display:block;background:#efe6d4}.card img{width:100%;height:auto;display:block;aspect-ratio:3/4}
.card .body{padding:12px 14px 16px;flex:1;display:flex;flex-direction:column}
.card h3{margin:0 0 .3em;font-size:1.05rem;line-height:1.3}.card h3 a{text-decoration:none;color:#3b2f24}
.card p{margin:.2em 0;font-size:.93rem}.card .more{margin-top:auto;padding-top:8px;font-weight:600}
.tag{display:inline-block;font-size:.78rem;background:#f2e3c6;border-radius:99px;padding:1px 9px;margin:0 4px 4px 0}
.book{display:grid;grid-template-columns:minmax(0,300px) 1fr;gap:24px;align-items:start;margin-top:10px}
.book .cover img{width:100%;height:auto;border-radius:10px;box-shadow:0 2px 10px rgba(80,50,20,.2);aspect-ratio:3/4}
dl.facts{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;font-size:.95rem;margin:12px 0}dl.facts dt{font-weight:600}dl.facts dd{margin:0}
.pages{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.pages img{width:100%;height:auto;border-radius:8px;box-shadow:0 1px 5px rgba(80,50,20,.15);aspect-ratio:3/4;background:#efe6d4}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin:26px 0 8px}
.cta.hero{margin:14px 0 6px}
.cta.hero .btn{flex:1 1 220px;min-width:min(100%,220px)}
.bundlebox{background:#fff;border-radius:14px;box-shadow:0 1px 4px rgba(80,50,20,.12);padding:14px 18px 18px;margin:18px 0}
.btn{display:inline-block;padding:13px 20px;border-radius:12px;font-weight:700;text-decoration:none;text-align:center;flex:1 1 240px}
.btn small{display:block;font-weight:500}
.btn.free{background:#fff;border:2px solid #b8641c;color:#8a4b12}.btn.buy{background:#b8641c;color:#fff;border:2px solid #b8641c}
.btn.sm{flex:1 1 0;padding:9px 10px;font-size:.92rem}
.cardbtns{display:flex;gap:8px;margin-top:10px}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-block;padding:8px 12px;border:2px solid #b8641c;border-radius:99px;text-decoration:none;font-weight:600;font-size:.92rem;background:#fff}
.note{font-size:.85rem;color:#6b5a48}
footer{border-top:1px solid #e6d8bf;margin-top:36px;padding-top:14px;padding-bottom:30px;font-size:.88rem;color:#6b5a48}
@media (max-width:640px){.book{grid-template-columns:1fr}.book .cover{max-width:280px}.pages{grid-template-columns:repeat(2,1fr)}h1{font-size:1.45rem}}
@media (max-width:600px){.book{grid-template-columns:minmax(0,38%) minmax(0,1fr);gap:12px;align-items:start}.book .cover{max-width:none}.cta.top{margin:8px 0 4px;gap:8px}.cta.top .btn{flex:1 1 100%;min-width:0;padding:10px 8px}}
"""

def head(title, desc, kw, url, img, ogtype="website", ogtitle=None):
    if ogtitle is None:
        ogtitle = title
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="keywords" content="{E(kw)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Pip the Mole Books 皮皮繪本">
<meta property="og:title" content="{E(ogtitle)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta property="og:locale:alternate" content="zh_HK">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{img}">
<style>{CSS}</style>
</head>
<body>
<header><a class="brand" href="{SITE}/">Pip the Mole Books · <span lang="zh-Hant">皮皮繪本</span></a></header>
"""

FOOT = f"""<footer>
<p><strong>About · <span lang="zh-Hant">關於</span>:</strong> Stories written by PP O in Hong Kong. Illustrations are AI-generated. <span lang="zh-Hant">故事由香港的 PP O 創作，插圖由 AI 生成。</span></p>
<p>Books are sold as PDF ebooks on Gumroad (Gumroad handles checkout). <span lang="zh-Hant">電子書（PDF）經 Gumroad 發售。</span></p>
<p>Contact · <span lang="zh-Hant">聯絡</span>: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</footer>
<script>
(function(){{
  var K=["utm_source","utm_medium","utm_campaign","utm_content","utm_term"], got={{}}, has=false;
  var q=new URLSearchParams(location.search);
  K.forEach(function(k){{var v=q.get(k); if(v){{got[k]=v.slice(0,100); has=true;}}}});
  try{{
    if(has) sessionStorage.setItem("pip_utm", JSON.stringify(got));
    else got=JSON.parse(sessionStorage.getItem("pip_utm")||"{{}}");
  }}catch(e){{}}
  if(!Object.keys(got).length) return;
  document.querySelectorAll('a[href*="gumroad.com/"]').forEach(function(a){{
    var u=new URL(a.href);
    K.forEach(function(k){{u.searchParams.delete(k);}});
    K.forEach(function(k){{if(got[k]) u.searchParams.set(k, got[k]);}});
    a.href=u.toString();
  }});
}})();
</script>
</body>
</html>
"""

BASE_KW = "children's picture book, bilingual Chinese English picture book, Traditional Chinese, 中英雙語繪本, bedtime story, toddler, preschool, ages 3-6, read aloud, PDF ebook, Pip the mole"

def book_page(b):
    url = f"{SITE}/{b['slug']}/"
    img = f"{SITE}/img/{b['slug']}/og.jpg"
    title = f"{b['en']} {b['zh']} · Bilingual Chinese English Picture Book, Ages 3–6"
    desc = (f"Book {b['n']} of Pip the mole's stories: a bilingual English + Traditional Chinese children's picture book "
            f"(PDF) about {b['theme_en']}, for toddlers and preschoolers aged 3–6. {b['short_en']} Free sample available.")
    kw = f"{b['en']}, {b['zh']}, {b['kw']}, " + BASE_KW
    pages = "\n".join(
        f'<img src="../img/{b["slug"]}/page-{i}.webp" width="720" height="960" loading="lazy" decoding="async" '
        f'alt="{E(b["en"])}, story page {i}: illustration with Traditional Chinese and English text">' for i in range(1, 5))
    others = [o for o in sorted(BOOKS, key=lambda x: -x["n"]) if o is not b]
    more = " · ".join(f'<a href="../{o["slug"]}/">{E(o["en"])} <span lang="zh-Hant">{o["zh"]}</span></a>' for o in others)
    upsell = (f'<p class="upsell">Want all six? <a href="{BUNDLE}{UTM}">Get the Pip bundle, all 6 books for US$9.99</a> '
              f'· <span lang="zh-Hant">想要全套？<a href="{BUNDLE}{UTM}">皮皮全套 6 本 US$9.99</a></span></p>')
    s = head(title, desc, kw, url, img, "book")
    s += f"""<main>
<div class="book">
<div class="cover"><img src="../img/{b['slug']}/cover.webp" width="600" height="800" alt="Cover of {E(b['en'])} / {b['zh']}: Pip the mole and friends"></div>
<div>
<p class="note">Book {b['n']} · <span lang="zh-Hant">第{"一二三四五六"[b['n']-1]}集</span></p>
<h1>{E(b['en'])}<span class="zh" lang="zh-Hant">{b['zh']}</span></h1>
<div class="cta top">
<a class="btn free" href="{GR}{b['sample']}{UTM}">Read the free sample<small lang="zh-Hant">免費試讀（封面＋頭 5 頁）</small></a>
<a class="btn buy" href="{GR}{b['paid']}{UTM}">Get the full book US$4.99<small lang="zh-Hant">購買完整版 US$4.99</small></a>
</div>
{upsell}
<p class="lead">{E(b['sum_en'])}</p>
<p class="lead" lang="zh-Hant">{b['sum_zh']}</p>
<dl class="facts">
<dt>Ages · <span lang="zh-Hant">年齡</span></dt><dd>3–6 · <span lang="zh-Hant">適合 3–6 歲</span></dd>
<dt>Language · <span lang="zh-Hant">語言</span></dt><dd>English + Traditional Chinese on every page · <span lang="zh-Hant">每頁中英對照（繁體中文）</span></dd>
<dt>Theme · <span lang="zh-Hant">主題</span></dt><dd>{E(b['theme_en'].capitalize())} · <span lang="zh-Hant">{b['theme_zh']}</span></dd>
<dt>Format · <span lang="zh-Hant">格式</span></dt><dd>PDF ebook, 19 pages (cover, 16 story pages, a read-aloud refrain page, back cover); screen and print-ready 300 dpi versions · <span lang="zh-Hant">PDF 電子書，共 19 頁</span></dd>
<dt>Story · <span lang="zh-Hant">故事</span></dt><dd>PP O (Hong Kong); illustrations AI-generated · <span lang="zh-Hant">插圖由 AI 生成</span></dd>
</dl>
</div>
</div>
<h2>Look inside · <span lang="zh-Hant">內頁預覽</span></h2>
<div class="pages">
{pages}
</div>
<p class="note">The free sample has the cover and the first 5 story pages. Book {b['n']} also reads fine on its own. <span lang="zh-Hant">免費試讀版包括封面和故事的頭 5 頁。</span></p>
<div class="cta">
<a class="btn free" href="{GR}{b['sample']}{UTM}">Read the free sample<small lang="zh-Hant">免費試讀</small></a>
<a class="btn buy" href="{GR}{b['paid']}{UTM}">Get the full book US$4.99<small lang="zh-Hant">購買完整版 US$4.99</small></a>
</div>
{upsell}
<h2>More Pip books · <span lang="zh-Hant">更多皮皮繪本</span></h2>
<p>{more}</p>
<p><a href="../">← All books · <span lang="zh-Hant">所有繪本</span></a></p>
</main>
"""
    return s + FOOT

LP_CSS = """
.hero{display:grid;grid-template-columns:1.1fr 1fr;gap:26px;align-items:center;margin:8px 0 10px}
.hero h1{font-size:2rem;margin:.2em 0 .3em}.hero h1 .zh{font-size:1.45rem}
.hero .kicker{display:inline-block;background:#f2e3c6;border-radius:99px;padding:3px 12px;font-size:.85rem;font-weight:600}
.hero .price{font-size:.95rem;margin:.4em 0 0}
.hero .price s{color:#8b7a66}
.covers{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.covers img{width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(80,50,20,.22);aspect-ratio:3/4;display:block}
.covers img:nth-child(odd){transform:rotate(-2deg)}.covers img:nth-child(even){transform:rotate(2deg)}
.why{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px;margin:12px 0}
.why div{background:#fff;border-radius:14px;box-shadow:0 1px 4px rgba(80,50,20,.12);padding:14px 16px}
.why h3{margin:0 0 .3em;font-size:1rem}.why p{margin:.2em 0;font-size:.92rem}
.themes{width:100%;border-collapse:collapse;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 1px 4px rgba(80,50,20,.12);font-size:.93rem}
.themes td{padding:9px 12px;border-bottom:1px solid #f0e4cc;vertical-align:top}.themes tr:last-child td{border-bottom:0}
.themes td:first-child{font-weight:700;white-space:nowrap;color:#8a4b12}
.compare{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0 14px}
.compare div{border-radius:12px;padding:12px 14px;background:#fbf6ec;border:1px solid #ead9b9}
.compare .best{border:2px solid #b8641c;background:#fff7ec}
.compare b{display:block;font-size:1.35rem}
details{background:#fff;border-radius:12px;box-shadow:0 1px 3px rgba(80,50,20,.1);padding:10px 14px;margin:8px 0}
summary{font-weight:700;cursor:pointer}details p{margin:.5em 0 .2em;font-size:.94rem}
.sticky{position:fixed;left:0;right:0;bottom:0;background:#fffaf1;border-top:1px solid #e6d8bf;padding:8px 12px;display:none;gap:8px;z-index:9}
.sticky .btn{padding:9px 8px;font-size:.92rem;flex:1 1 0}
@media (max-width:720px){.hero{grid-template-columns:1fr}.hero h1{font-size:1.6rem}.covers{max-width:420px}.compare{grid-template-columns:1fr}
 .sticky{display:flex}body.lp{padding-bottom:72px}}
"""
CSS += LP_CSS

FAQ = [
 ("How do I get the books after paying?", "付款後怎樣收到書？",
  "Gumroad shows a download button right after checkout and also emails you the link. The files stay in your Gumroad library, so you can download them again later.",
  "付款後 Gumroad 會即時顯示下載按鈕，同時把下載連結電郵給你。檔案會保留在你的 Gumroad 帳戶，之後可以再下載。"),
 ("Can we read them on a phone or tablet? Can I print them?", "手機、平板可以看嗎？可以列印嗎？",
  "Yes. They are PDF files, so they open on phones, tablets and computers. Each book also comes with a print-ready 300 dpi version for printing at home.",
  "可以。全部是 PDF，手機、平板、電腦都能打開。每本還有 300 dpi 印刷版，可以在家列印。"),
 ("Is the Chinese Traditional or Simplified?", "中文是繁體還是簡體？",
  "Traditional Chinese, with the English text on the same page.",
  "繁體中文，同一頁有英文對照。"),
 ("What age is it for?", "適合多少歲？",
  "Ages 3–6. The sentences are short and repeat, so they work for reading aloud at bedtime and for early readers.",
  "3 至 6 歲。句子短、有重複，適合睡前唸給孩子聽，也適合剛開始認字的孩子。"),
 ("Do the books need to be read in order?", "需要按順序讀嗎？",
  "No. The six stories follow the same friends through the seasons, but each book reads fine on its own.",
  "不用。六個故事是皮皮和好朋友們在不同季節的經歷，但每本都可以單獨閱讀。"),
 ("How do I pay?", "怎樣付款？",
  "Checkout is handled by Gumroad, which shows the payment options available to you. You can also pay more than US$9.99 if you want to support new books.",
  "結帳由 Gumroad 處理，會顯示你可以使用的付款方法。如果想支持新書，可以自訂高於 US$9.99 的價錢。"),
]

def make_og_collage():
    from PIL import ImageDraw, ImageFont
    out = ROOT / "img" / "og-collage.jpg"
    if out.exists() and not os.environ.get("REIMG"):
        return
    bg = Image.new("RGB", (1200, 630), (251, 246, 236))
    w, h = 204, 272
    for i, b in enumerate(sorted(BOOKS, key=lambda x: x["n"])):
        c = Image.open(ROOT / "img" / b["slug"] / "cover.webp").convert("RGB").resize((w, h), Image.LANCZOS)
        bg.paste(c, (36 + (i % 3) * (w + 14), 36 + (i // 3) * (h + 14)))
    d = ImageDraw.Draw(bg)
    fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    f1 = ImageFont.truetype(fp, 50, index=2); f2 = ImageFont.truetype(fp, 30, index=2); f3 = ImageFont.truetype(fp, 34, index=2)
    x = 730
    d.text((x, 120), "Pip the Mole", font=f1, fill=(90, 61, 34))
    d.text((x, 185), "皮皮繪本", font=f1, fill=(138, 75, 18))
    d.text((x, 280), "6 bilingual picture books", font=f2, fill=(59, 47, 36))
    d.text((x, 322), "中英對照 · Ages 3–6", font=f2, fill=(59, 47, 36))
    d.rounded_rectangle((x, 400, x + 400, 470), radius=16, fill=(184, 100, 28))
    d.text((x + 24, 412), "All 6 · US$9.99", font=f3, fill=(255, 255, 255))
    bg.save(out, "JPEG", quality=84, optimize=True, progressive=True)

def index_page():
    title = "Pip the Mole 皮皮繪本 · Bilingual Chinese English Picture Books, Ages 3–6 · Free Samples & 6-Book Bundle"
    ogtitle = "Pip the Mole 皮皮繪本 · 6 bilingual picture books for ages 3–6 · all 6 for US$9.99"
    desc = ("Six bilingual picture books for kids aged 3–6, English + Traditional Chinese on every page. "
            "Read a free sample of any book, or get all 6 in one bundle. 中英對照雙語繪本：每本免費試讀，或者一次過買全套 6 本。")
    order = sorted(BOOKS, key=lambda x: x["n"])
    covers = "\n".join(
        f'<img src="img/{b["slug"]}/cover-sm.webp" width="360" height="480" alt="Cover of {E(b["en"])} / {b["zh"]}"'
        + (' fetchpriority="high"' if b["n"] <= 3 else ' loading="lazy"') + '>' for b in order)
    themes = "\n".join(
        f'<tr><td>Book {b["n"]}</td><td><a href="{b["slug"]}/">{E(b["en"])}</a> <span lang="zh-Hant">{b["zh"]}</span><br>'
        f'{E(b["theme_en"].capitalize())} · <span lang="zh-Hant">{b["theme_zh"]}</span></td></tr>' for b in order)
    samples = " ".join(
        f'<a class="chip" href="{GR}{b["sample"]}{UTM}">{E(b["en"])} <span lang="zh-Hant">{b["zh"]}</span></a>' for b in order)
    peek = "img/pip-and-the-first-snow"
    pages = "\n".join(
        f'<img src="{peek}/page-{i}.webp" width="720" height="960" loading="lazy" decoding="async" '
        f'alt="Pip and the First Snow, story page {i}: illustration with Traditional Chinese and English text">' for i in range(1, 5))
    faq = "\n".join(
        f'<details><summary>{E(q)} · <span lang="zh-Hant">{qz}</span></summary><p>{E(a)}</p><p lang="zh-Hant">{az}</p></details>'
        for q, qz, a, az in FAQ)
    cards = []
    for b in sorted(BOOKS, key=lambda x: -x["n"]):
        cards.append(f"""<article class="card">
<a class="cov" href="{b['slug']}/"><img src="img/{b['slug']}/cover-sm.webp" width="360" height="480" loading="lazy" decoding="async" alt="Cover of {E(b['en'])} / {b['zh']}"></a>
<div class="body">
<h3><a href="{b['slug']}/">{E(b['en'])}<br><span lang="zh-Hant">{b['zh']}</span></a></h3>
<p><span class="tag">Book {b['n']}</span><span class="tag">Ages 3–6</span><span class="tag">EN + <span lang="zh-Hant">繁中</span></span></p>
<p>{E(b['short_en'])}</p>
<p lang="zh-Hant">{b['short_zh']}</p>
<a class="more" href="{b['slug']}/">Look inside · <span lang="zh-Hant">看看內頁</span> →</a>
<div class="cardbtns">
<a class="btn free sm" href="{GR}{b['sample']}{UTM}">Free sample<small lang="zh-Hant">免費試讀</small></a>
<a class="btn buy sm" href="{GR}{b['paid']}{UTM}">US$4.99<small lang="zh-Hant">購買</small></a>
</div>
</div>
</article>""")
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Product", "name": "Pip the Mole 6-Book Bundle 皮皮全套 6 本",
             "description": "Six bilingual English + Traditional Chinese picture books (PDF) for ages 3–6.",
             "image": f"{SITE}/img/og-collage.jpg", "brand": {"@type": "Brand", "name": "Pip the Mole Books"},
             "offers": {"@type": "Offer", "price": "9.99", "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": BUNDLE}},
            {"@type": "ItemList", "name": "Pip the Mole picture books",
             "itemListElement": [{"@type": "ListItem", "position": b["n"], "url": f"{SITE}/{b['slug']}/", "name": b["en"]} for b in order]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, qz, a, az in FAQ]},
        ]}
    s = head(title, desc, BASE_KW + ", teamwork, sharing, kindness", f"{SITE}/", f"{SITE}/img/og-collage.jpg", ogtitle=ogtitle)
    s = s.replace("<body>", '<body class="lp">', 1)
    s += f"""<main>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<section class="hero">
<div>
<span class="kicker">Ages 3–6 · EN + <span lang="zh-Hant">繁中</span></span>
<h1>Gentle bedtime stories in English and Chinese<span class="zh" lang="zh-Hant">中英對照睡前繪本：小鼴鼠皮皮</span></h1>
<p class="lead">Six short picture books about Pip the mole and his friends Robin and Rabbit. Every page has English and Traditional Chinese together, so you can read in either language, or both.</p>
<p class="lead" lang="zh-Hant">六本關於小鼴鼠皮皮和知更鳥、兔子的短篇繪本。每頁都有英文和繁體中文，可以讀其中一種語言，也可以兩種一起讀。</p>
<div class="cta hero">
<a class="btn buy" href="{BUNDLE}{UTM}">Get all 6 books · US$9.99<small lang="zh-Hant">購買全套 6 本 US$9.99</small></a>
<a class="btn free" href="#free-samples">Read a free sample first<small lang="zh-Hant">先免費試讀</small></a>
</div>
<p class="price">Instant PDF download via Gumroad. One by one the six books cost <s>US$29.94</s>. <span lang="zh-Hant">經 Gumroad 即時下載 PDF；逐本買要 US$29.94。</span></p>
</div>
<div class="covers">
{covers}
</div>
</section>

<h2>Why parents pick Pip · <span lang="zh-Hant">為甚麼選皮皮</span></h2>
<div class="why">
<div><h3>Two languages, one page · <span lang="zh-Hant">同一頁中英對照</span></h3><p>English and Traditional Chinese side by side on every page.</p><p lang="zh-Hant">每頁英文和繁體中文並列，不用拿兩本書對照。</p></div>
<div><h3>Short and calm · <span lang="zh-Hant">短而平靜</span></h3><p>16 story pages each, with short repeating lines and a read-aloud refrain page. Good for winding down at bedtime.</p><p lang="zh-Hant">每本 16 頁故事，句子短又有重複，還有一頁朗讀兒歌，很適合睡前。</p></div>
<div><h3>One small lesson per book · <span lang="zh-Hant">每本一個小道理</span></h3><p>Teamwork, not giving up, being brave, sharing, saying sorry and caring for others.</p><p lang="zh-Hant">合作、不放棄、勇敢、分享、說對不起、關心別人。</p></div>
<div><h3>Read anywhere, print at home · <span lang="zh-Hant">隨時看，也可以印</span></h3><p>PDFs for phone, tablet or computer, plus print-ready 300 dpi files.</p><p lang="zh-Hant">手機、平板、電腦都能看，另有 300 dpi 印刷版。</p></div>
</div>

<h2>Six stories, six themes · <span lang="zh-Hant">六個故事，六個主題</span></h2>
<table class="themes">
{themes}
</table>

<h2>Look inside · <span lang="zh-Hant">內頁預覽</span></h2>
<p class="note">Four pages from Book 6, Pip and the First Snow. <span lang="zh-Hant">以下是第六集《皮皮和第一場雪》其中四頁。</span></p>
<div class="pages">
{pages}
</div>

<section id="bundle" class="bundlebox">
<h2>All 6 Pip books in one bundle · <span lang="zh-Hant">皮皮全套 6 本</span></h2>
<div class="compare">
<div>One by one · <span lang="zh-Hant">逐本買</span><b>US$29.94</b>6 × US$4.99</div>
<div class="best">Bundle · <span lang="zh-Hant">全套</span><b>US$9.99</b>All 6 PDF books · <span lang="zh-Hant">6 本 PDF</span></div>
</div>
<p>Pay what you want from US$9.99. Paying more helps us make the next Pip book. <span lang="zh-Hant">US$9.99 起自訂價錢；多付一點可以支持我們出下一本。</span></p>
<a class="btn buy" href="{BUNDLE}{UTM}">Get all 6 books · US$9.99<small lang="zh-Hant">購買全套 6 本 US$9.99</small></a>
</section>

<section id="free-samples">
<h2>Not sure yet? Start free · <span lang="zh-Hant">還沒決定？先免費試讀</span></h2>
<p>Every book has a free PDF sample: the cover and the first 5 story pages. Pick one and read it together tonight. <span lang="zh-Hant">每本都有免費試讀（PDF）：封面和故事的頭 5 頁。選一本，今晚一起讀。</span></p>
<p class="chips">{samples}</p>
</section>

<h2>Questions · <span lang="zh-Hant">常見問題</span></h2>
{faq}

<h2>All books, newest first · <span lang="zh-Hant">全部繪本（最新在前）</span></h2>
<div class="grid">
{chr(10).join(cards)}
</div>
</main>
<div class="sticky">
<a class="btn free" href="#free-samples">Free sample<small lang="zh-Hant">免費試讀</small></a>
<a class="btn buy" href="{BUNDLE}{UTM}">All 6 · US$9.99<small lang="zh-Hant">全套 6 本</small></a>
</div>
"""
    return s + FOOT

def main():
    for b in BOOKS:
        if not (ROOT / "img" / b["slug"] / "page-4.webp").exists() or os.environ.get("REIMG"):
            make_images(b)
        d = ROOT / b["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(book_page(b), encoding="utf-8")
    make_og_collage()
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    urls = [f"{SITE}/"] + [f"{SITE}/{b['slug']}/" for b in sorted(BOOKS, key=lambda x: -x["n"])]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>2026-09-29</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("")
    json.dump([{k: b[k] for k in ("n", "slug", "en", "zh", "paid", "sample")} for b in BOOKS], open(ROOT / "books.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
