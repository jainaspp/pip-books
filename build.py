#!/usr/bin/env python3
"""Build the static Pip books site. Run: python3 build.py (needs Pillow and the book page PNGs on the box).

Everything on the homepage is driven by two lists below:
  BOOKS   – one dict per book. Keys used by the homepage:
            n (book number), season (1, 2, ...), status ("live" | "soon"),
            slug, paid (Gumroad product slug), sample (Gumroad free-sample slug),
            en / zh (titles), theme_en / theme_zh, optional tag_en (shorter theme for the card),
            optional price (default PRICE).
            season defaults to 1 for Books 1–6 and 2 for Books 7–12; status defaults to "live".
            A "soon" book needs only n, season, status, slug, en, zh, theme_en, theme_zh
            (it gets a card with "Coming soon", no links, no detail page).
  BUNDLES – one dict per bundle (Gumroad slug, price, which books). Rendered on the sage band.
Books 7–12 (Season 2) are in BOOKS. The Season 2 bundle entry is already in BUNDLES but hidden until
BUNDLE_S2 is set to its Gumroad URL (one-line change; check BUNDLE_S2_PRICE matches Gumroad).
The Season 2 heading appears automatically once a season-2 book is in BOOKS.
"""
import html, os, json
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path(__file__).parent
SITE = "https://jainaspp.github.io/pip-books"
GR = "https://jainaspark4.gumroad.com/l/"
UTM = "?utm_source=pipsite"
# Books 1–6 bundle, US$9.99 minimum (pay what you want). 6 × US$4.99 = US$29.94 separately.
BUNDLE = "https://jainaspark4.gumroad.com/l/imzzp"
# Books 7–12 bundle: leave "" until it is live on Gumroad, then paste its URL here and rebuild (it then shows
# on the homepage bundles band, the Season 2 heading link, JSON-LD and the Book 7–12 page upsells).
BUNDLE_S2 = ""
BUNDLE_S2_PRICE = "9.99"   # confirm against Gumroad before setting BUNDLE_S2
EMAIL = "jainaspp@gmail.com"
REDBUBBLE = "https://www.redbubble.com/people/jainaspp/shop?collections=4588651"
ETSY = "https://www.etsy.com/shop/PipTheMoleStories"
PRICE = "4.99"   # single book price (US$), unless a book sets price=

BOOKS = [
 dict(n=1, season=1, status="live", slug="pips-big-dig", src="/workspace/pipbook/pages", paid="yulzdr", sample="pips-big-dig-free-sample",
  en="Pip's Big Dig", zh="皮皮的大挖掘", theme_en="teamwork", theme_zh="一起合作",
  kw="teamwork story for kids",
  sum_en="Pip the mole wants to dig the biggest hole… alone. Scratch, scratch, scoop! His paws get tired, and the hole is still small. A robin hops by, then a rabbit, but Pip says, “No! I can do it all by myself!” Will he let his friends help? A warm story about teamwork: the pages start cool and grey while Pip digs alone and turn golden when the friends dig together.",
  sum_zh="皮皮想獨自挖一個最大的洞。可是一個人挖，真的比較好玩嗎？爪子累了，洞還是小小的。知更鳥和兔子來了，皮皮會讓朋友幫忙嗎？一個關於一起合作的溫暖故事。",
  short_en="Pip the mole wants to dig the biggest hole all by himself. Is digging alone really more fun?",
  short_zh="皮皮想獨自挖一個最大的洞，一個人挖真的比較好玩嗎？"),
 dict(n=2, season=1, status="live", tag_en="not giving up, solving it together", slug="pip-and-the-big-rain", src="/workspace/pipbook2/pages", paid="pip-big-rain", sample="pip-big-rain-free-sample",
  en="Pip and the Big Rain", zh="皮皮和大雨天", theme_en="not giving up and solving problems together", theme_zh="不放棄、一起想辦法",
  kw="rainy day picture book",
  sum_en="Pitter, patter! After the big dig, a big rain comes. By morning the big hole is full of water, and Rabbit's burrow is flooded too. Pip sits in the mud and wants to give up. But Robin says, “Don't worry. Let's think together.” Then Pip watches a raindrop slide down a leaf… and has an idea. A gentle story about what to do when things go wrong: don't give up, think it through with your friends, and a bad day can turn into something new and good.",
  sum_zh="皮皮和朋友們的大洞被大雨灌滿了水，兔子的窩也進水了。皮皮想放棄，可是大家一起想辦法，壞事也能變成新的好事！",
  short_en="A big rain floods the hole and Rabbit's burrow. Pip wants to give up, until the friends think together.",
  short_zh="大雨把大洞灌滿了水，皮皮和朋友們一起想辦法。"),
 dict(n=3, season=1, status="live", slug="pip-and-the-night-lights", src="/workspace/pipbook3/pages", paid="pip-night-lights", sample="pip-night-lights-free-sample",
  en="Pip and the Night Lights", zh="皮皮和螢火蟲", theme_en="being brave in the dark, together", theme_zh="有朋友在身邊，不怕黑",
  kw="bedtime story scared of the dark",
  sum_en="The big hole is a little pond now, and Pip, Robin and Rabbit meet there to watch the stars. But when the sky gets dark, Rabbit's ears start to shake: “It's so dark! I'm scared.” Pip lives under the ground and isn't afraid of the dark at all. His secret? Close your eyes and listen. Ribbit, ribbit… chirp, chirp… A calm wind-down story about being brave together. It ends with the three friends snuggling up and saying goodnight.",
  sum_zh="天黑了，兔子好害怕。皮皮教大家閉上眼睛靜靜地聽，知更鳥輕輕地唱。原來有朋友在身邊，黑黑的夜晚也很美。",
  short_en="Night falls by the pond and Rabbit is scared of the dark. A calm bedtime story about being brave together.",
  short_zh="天黑了，兔子好害怕。有朋友在身邊，黑黑的夜晚也很美。"),
 dict(n=4, season=1, status="live", slug="pip-and-the-autumn-leaves", src="/workspace/pipbook4/pages", paid="pip-autumn-leaves", sample="pip-autumn-leaves-free-sample",
  en="Pip and the Autumn Leaves", zh="皮皮和落葉", theme_en="sharing", theme_zh="分享",
  kw="autumn picture book, sharing story for kids",
  sum_en="Flutter, flutter! Summer is over and the leaves on the hill turn orange, red and brown. Winter is coming, so Pip wants a warm leaf bed. Scratch, scratch, scoop! Pip's pile grows higher and higher, taller than Pip! But Robin's beak is small, and Robin can carry only one leaf at a time. As the sun goes down, Robin's nest is still cold… A gentle story about sharing with friends: Pip finds out that sharing makes everyone warm, Pip included.",
  sum_zh="皮皮堆了一大堆落葉，全都想留給自己。可是知更鳥的小窩還是冷冰冰的……皮皮決定分享，才發現分享讓大家都暖暖的、好開心！",
  short_en="Pip piles up autumn leaves for a warm winter bed. Will he share with Robin?",
  short_zh="皮皮堆了一大堆落葉，會分享給知更鳥嗎？"),
 dict(n=5, season=1, status="live", tag_en="saying sorry and fixing things", slug="pip-and-the-windy-day", src="/workspace/pipbook5/pages", paid="pip-windy-day", sample="pip-windy-day-free-sample",
  en="Pip and the Windy Day", zh="皮皮和大風天", theme_en="saying sorry and fixing things together", theme_zh="說對不起、一起修好",
  kw="saying sorry story for kids",
  sum_en="Whoo, whoo! Autumn is almost over and the wind is so strong today. Rabbit builds a leaf house from sticks and fallen leaves. Pip wants to see it too, so he digs a tunnel to get there faster… and pops up right under the leaf house. Down it tumbles! Pip quickly says, “The wind did it!”, but he feels a little stone inside. A gentle story about telling the truth, saying sorry and fixing things together.",
  sum_zh="兔子搭了一間葉子屋，卻被急急忙忙挖地道的皮皮弄倒了。皮皮先說「是大風吹的！」，心裡卻好不舒服……皮皮說了對不起，大家一起搭出更堅固的葉子屋！",
  short_en="Pip pops up under Rabbit's leaf house and knocks it down. A story about saying sorry and fixing it together.",
  short_zh="皮皮不小心弄倒了兔子的葉子屋，說聲對不起，再一起修好。"),
 dict(n=6, season=1, status="live", slug="pip-and-the-first-snow", src="/workspace/pipbook6/pages", paid="pip-first-snow", sample="pip-first-snow-free-sample",
  en="Pip and the First Snow", zh="皮皮和第一場雪", theme_en="caring for others", theme_zh="關心別人",
  kw="winter picture book, kindness story for kids",
  sum_en="Squeak, squeak! Winter is here, and Pip runs out of his underground room: “The first snow!” The three friends play on the white hill, until Robin spots some tiny footprints. Whose are they? The footprints lead to a low bush by the pond, and under it a little round ball is shivering. It's a baby hedgehog named Pom, who can't find the way home. A gentle story about caring for others: Rabbit holds Pom close, Pip digs a path to his warm underground room, and Robin brings soft moss and sweet red berries.",
  sum_zh="冬天的第一場雪，皮皮、兔子和知更鳥跟著小小的腳印，找到了在樹叢下發抖的刺蝟寶寶蓬蓬。皮皮挖小路，兔子抱一抱，知更鳥找青苔，大家一起照顧蓬蓬。",
  short_en="Tiny footprints in the first snow lead the friends to a shivering baby hedgehog named Pom.",
  short_zh="第一場雪，小小的腳印通到樹叢下，找到了發抖的刺蝟寶寶蓬蓬。"),
 dict(n=7, slug="pip-and-the-leaf-nest", src="/workspace/pipbook7/pages", paid="pip-leaf-nest", sample="pip-leaf-nest-free-sample",
  en="Pip and the Leaf Nest", zh="皮皮和葉子窩", theme_en="saying goodbye for now", theme_zh="好好說再見",
  kw="winter picture book, saying goodbye story for kids",
  sum_en="Early winter. Lost little Pom is staying in Pip's underground room, but now Pom gives a big yawn: “I'm so sleepy. I want my leaf nest.” The snow is white everywhere and every bush looks the same. How can they find it? Sniff, sniff! Pom's little nose finds the way, and everyone follows her tiny footprints. A gentle story about saying goodbye for now: Pip doesn't want Pom to go, but he helps dig the snow away from the nest's door. “See you in spring!”",
  sum_zh="入冬了，蓬蓬想回葉子窩睡長長的覺，可是雪地白白的……她用小鼻子找路，皮皮捨不得，卻幫她回家。好好說再見，春天再相見！",
  short_en="Sleepy Pom wants to go home to her leaf nest, but the snow is all white. Pip helps her home and says goodbye for now.",
  short_zh="蓬蓬想回葉子窩睡長長的覺，皮皮捨不得，卻幫她回家。"),
 dict(n=8, slug="pip-and-the-snow-slide", src="/workspace/pipbook8/pages", paid="pip-snow-slide", sample="pip-snow-slide-free-sample",
  en="Pip and the Snow Slide", zh="皮皮和雪滑梯", theme_en="speaking up and listening", theme_zh="說出想法、也聽聽別人",
  kw="winter picture book, speaking up story for kids",
  sum_en="It's winter, and white snow covers the hill. Pip digs a long snow ditch slide, but off they go— plop! The leaves sink into the soft snow and stop. Rabbit has a different idea. Will she say it? “Wait!” Rabbit calls. Thump, thump, thump! She stamps the snow hard with her long feet, everyone stamps together, and… Whoosh! A gentle story about speaking up and listening.",
  sum_zh="冬天，大家想從雪山丘滑下來，可是雪溝一滑就陷進軟雪……兔子心裡有主意，敢說出來嗎？說出想法，也聽聽別人的，滑梯更好玩！",
  short_en="Pip's snow slide sinks into the soft snow. Rabbit has a different idea. Will she say it?",
  short_zh="皮皮的雪滑梯陷進軟雪，兔子心裡有別的主意，敢說出來嗎？"),
 dict(n=9, slug="pip-and-the-spring-nest", src="/workspace/pipbook9/pages", paid="pip-spring-nest", sample="pip-spring-nest-free-sample",
  en='Pip and the Spring Nest', zh="皮皮和春天的鳥窩", theme_en="trying again", theme_zh="再試一次",
  kw="spring picture book, trying again story for kids",
  sum_en="The snow melts and spring is here. Robin's old nest was squashed by the winter snow, so she will build a new one. But flip, flop! The twig falls down, again and again. Pip wants to build it for her, but Robin wants to do it herself: will he stay with her? Then Robin finds wet moss under the melting snow... A gentle story about trying again.",
  sum_zh="春天到了，知更鳥想搭一個新窩，可是樹枝一次又一次掉下來……皮皮陪著她，她自己想到好方法。掉下來不怕，再試一次！",
  short_en="Flip, flop! Robin's twigs keep falling. Pip stays with her, and she finds a way all by herself.",
  short_zh="知更鳥的樹枝一次又一次掉下來，皮皮陪著她，她自己想到好方法。"),
 dict(n=10, slug="pip-and-the-thorny-bush", src="/workspace/pipbook10/pages", paid="pip-thorny-bush", sample="pip-thorny-bush-free-sample",
  en='Pip and the Thorny Bush', zh="皮皮和刺刺叢", theme_en="liking what makes you different", theme_zh="欣賞自己不一樣",
  kw="spring picture book, story about being different for kids",
  sum_en='Spring flowers bloom and Pom wakes up from her long winter sleep. But when everyone rushes to hug her, Pom gets a fright and her spines pop up! Then the picnic basket bumps a stone, rolls down the slope and gets stuck deep inside a thorny bush. Nobody can reach it... except someone with spines. Roll, roll! A gentle story about liking what makes you different.',
  sum_zh="春天，蓬蓬醒來了，可是一受驚，刺就豎起來……野餐籃滾進刺刺叢，誰都拿不到。原來，蓬蓬的刺刺，也有它的好！",
  short_en="Pom's spines pop up when she's scared. Then the picnic basket rolls into a thorny bush, and nobody can reach it...",
  short_zh="蓬蓬一嚇，刺就豎起來。野餐籃滾進刺刺叢，誰都拿不到……"),
 dict(n=11, slug="pip-and-the-hot-day", src="/workspace/pipbook11/pages", paid="pip-hot-day", sample="pip-hot-day-free-sample",
  en='Pip and the Hot Day', zh="皮皮和大熱天", theme_en="stopping when you feel cross", theme_zh="生氣時先停一停",
  kw="summer picture book, calming down story for kids",
  sum_en="Early summer, and it's too hot! Pip digs a cool tunnel for everyone, fast and hard... then crash! The whole tunnel falls in. Bubble, bubble! Pip's tummy feels like a pot of boiling water. Rabbit sits down beside him: “Shh, shh...” and takes a slow, deep breath. Once Pip is calm, he can hear Pom's good idea. A gentle story about stopping when you feel cross.",
  sum_zh="大熱天，皮皮給大家挖涼涼的地道，快挖好時整條塌了！肚子裡咕嘟咕嘟……先停一停，吸一口氣，靜下來，才聽得見朋友的好方法。",
  short_en="Pip's cool tunnel falls in, and his tummy goes bubble, bubble! Stop, take a breath, and listen.",
  short_zh="皮皮的涼涼地道塌了，肚子裡咕嘟咕嘟！先停一停，吸一口氣。"),
 dict(n=12, slug="pip-and-the-friendship-circle", src="/workspace/pipbook12/pages", paid="pip-friendship-circle", sample="pip-friendship-circle-free-sample",
  en='Pip and the Friendship Circle', zh="皮皮和大圓圈", theme_en="saying thank you and making room", theme_zh="感謝，和這裡有你位子",
  kw="friendship picture book, belonging story for kids",
  sum_en="A summer night by the pond. The three old friends remember last summer, when fireflies filled the air. But the grass nest is full, and Pom sits outside, all alone. “Last summer... I wasn't here then.” Pip stands up: “Now, you're here. Let's dig a spot together!” Heave-ho! A gentle story about saying thank you and making room. The finale of Volume 1.",
  sum_zh="夏天晚上，大家在池塘邊等螢火蟲回來。蓬蓬坐在草窩外，靜靜的……「那時候，我不在。」皮皮站起來，大家一起多挖一個位子！第一冊終章。",
  short_en='The nest is full and Pom sits outside. Heave-ho! The friends dig one more spot. The Volume 1 finale.',
  short_zh="草窩擠滿了，蓬蓬坐在外邊。嘿咻嘿咻！大家多挖一個位子。第一冊終章。"),
]

E = html.escape

BUNDLES = [b for b in [
 dict(id="season-1", season=1, books=[1, 2, 3, 4, 5, 6], url=BUNDLE, price="9.99", fan=[3, 6, 4],
  en="Pip Books 1–6 in one bundle", zh="皮皮第 1–6 集套裝",
  btn_en="Get Books 1–6 · US$9.99", label_en="Season 1 · Books 1–6", label_zh="第一輯"),
 dict(id="season-2", season=2, books=[7, 8, 9, 10, 11, 12], url=BUNDLE_S2, price=BUNDLE_S2_PRICE, fan=[9, 12, 8],
  en="Pip Books 7–12 in one bundle", zh="皮皮第 7–12 集套裝",
  btn_en=f"Get Books 7–12 · US${BUNDLE_S2_PRICE}", label_en="Season 2 · Books 7–12", label_zh="第二輯"),
] if b["url"]]   # a bundle without a URL is hidden everywhere

ZH_NUM = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"]

def season_of(b):
    return b.get("season") or (1 if b["n"] <= 6 else 2)

def status_of(b):
    return b.get("status", "live")

def live_books():
    return sorted((b for b in BOOKS if status_of(b) == "live"), key=lambda x: x["n"])

def price_of(b):
    return b.get("price", PRICE)

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

# Homepage art. Hero = Book 3 (Night Lights) story page 1 painting, sunset pond, from the 5120x2880 text-free
# illustration (the web page images are only 720px). Spot art = Art direction crops (240px, shown at 44-88px).
HERO_SRC = "/workspace/pipbook3/illustrations/02.png"
SPOT_SRC = "/workspace/pip-web-direction/mockup/img/spot"
HERO_SIZES = (960, 1600)

def make_home_images():
    out = ROOT / "img" / "home"
    out.mkdir(parents=True, exist_ok=True)
    if not (out / "hero-1600.webp").exists() or os.environ.get("REIMG"):
        im = Image.open(HERO_SRC).convert("RGB")
        w, h = im.size
        ch = round(w * 5 / 9)                       # 9:5 crop, keep the sky + the friends at the bottom
        top = h - ch
        im = im.crop((0, top, w, top + ch))
        for tw in HERO_SIZES:
            im.resize((tw, round(tw * 5 / 9)), Image.LANCZOS).save(out / f"hero-{tw}.webp", "WEBP", quality=72, method=6)
    for k in ("together", "calm", "lesson"):
        if not (out / f"spot-{k}.webp").exists():
            Image.open(Path(SPOT_SRC) / f"{k}.webp").save(out / f"spot-{k}.webp", "WEBP", quality=80, method=6)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,600,100'
         '&family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">')

# Shared design tokens (Art direction STYLE-SPEC v1)
ROOT_CSS = """
:root{--paper:#FBF6EC;--surface:#FFFDF8;--sage:#E7EDDF;--hairline:#EADFCB;--ink:#3B2F24;--muted:#6B5A48;
--accent:#B8641C;--accent-hover:#8A4B12;--moss:#5E7A4E;
--font-head:'Fraunces','Noto Sans TC','Noto Sans CJK TC',Georgia,serif;
--font-body:'Noto Sans TC','Noto Sans CJK TC','PingFang TC','Microsoft JhengHei',system-ui,sans-serif;
--maxw:1080px;--textw:620px;--section:96px;--gap:32px;--r-hero:24px;--r-card:16px;--r-img:12px;
--shadow:0 6px 20px rgba(59,47,36,.08);
--wave:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='16' viewBox='0 0 120 16'%3E%3Cpath d='M0 8 Q15 2 30 8 T60 8 T90 8 T120 8' fill='none' stroke='%23EADFCB' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E")}
@media (max-width:720px){:root{--section:56px;--gap:16px}}
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;font:400 17px/28px var(--font-body);color:var(--ink);background:var(--paper)}
img{max-width:100%;height:auto}
a{color:var(--accent)}a:hover{color:var(--accent-hover)}
h1,h2,h3{font-family:var(--font-head);font-weight:600;font-variation-settings:'SOFT' 100;color:var(--ink);letter-spacing:-.005em}
.brand{color:var(--ink);text-decoration:none;display:inline-flex;align-items:baseline;gap:8px}
.brand b{font:600 22px/28px var(--font-head);font-variation-settings:'SOFT' 100}
.brand span{font-size:15px;color:var(--muted)}
.brand:hover{color:var(--ink)}
@media (max-width:720px){body{font-size:16px;line-height:26px}}
"""

# Book detail pages: same structure as before, new palette and type.
BOOK_CSS = """
header,main,footer{max-width:960px;margin:0 auto;padding:0 20px}
header{padding-top:20px;padding-bottom:8px}
h1{font-size:2.1rem;line-height:1.2;margin:.3em 0 .3em}
h1 .zh{display:block;font:400 1.6rem/1.4 var(--font-body);color:var(--muted);margin-top:6px}
h2{font-size:1.5rem;line-height:1.3;margin:1.8em 0 .6em}
h2 span[lang]{font:400 1.1rem var(--font-body);color:var(--muted)}
.lead{margin:.3em 0 1em}
.lead[lang="zh-Hant"]{color:var(--muted)}
.book{display:grid;grid-template-columns:minmax(0,300px) 1fr;gap:32px;align-items:start;margin-top:12px}
.book .cover img{width:100%;height:auto;border-radius:var(--r-img);box-shadow:var(--shadow);aspect-ratio:3/4;display:block}
dl.facts{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;font-size:.94rem;margin:16px 0;background:var(--surface);border-radius:var(--r-card);box-shadow:var(--shadow);padding:16px 20px}
dl.facts dt{font-weight:700}dl.facts dd{margin:0}
.pages{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.pages img{width:100%;height:auto;border-radius:var(--r-img);box-shadow:var(--shadow);aspect-ratio:3/4;background:var(--surface);display:block}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0 8px}
.btn{display:inline-block;padding:13px 22px;border-radius:16px;font-weight:700;text-decoration:none;text-align:center;flex:1 1 240px;transition:background .2s}
.btn small{display:block;font-weight:400;font-size:.85em}
.btn.buy{background:var(--accent);color:#FFFDF8}.btn.buy:hover{background:var(--accent-hover);color:#FFFDF8}
.btn.free{background:var(--surface);color:var(--accent);box-shadow:var(--shadow)}.btn.free:hover{color:var(--accent-hover)}
.upsell{font-size:.94rem;color:var(--muted)}
.note{font-size:.88rem;color:var(--muted)}
footer{margin-top:48px;padding-top:24px;padding-bottom:40px;font-size:14px;line-height:22px;color:var(--muted);background:var(--wave) repeat-x top/120px 16px}
@media (max-width:640px){.book{grid-template-columns:1fr}.book .cover{max-width:280px}.pages{grid-template-columns:repeat(2,1fr)}h1{font-size:1.6rem}h1 .zh{font-size:1.3rem}}
@media (max-width:600px){.book{grid-template-columns:minmax(0,38%) minmax(0,1fr);gap:14px;align-items:start}.book .cover{max-width:none}.cta.top{margin:8px 0 4px;gap:8px}.cta.top .btn{flex:1 1 100%;min-width:0;padding:10px 8px}}
"""
CSS = ROOT_CSS + BOOK_CSS

BOOK_HEADER = f'<header><a class="brand" href="{SITE}/"><b>Pip the Mole</b><span lang="zh-Hant">皮皮繪本</span></a></header>'

def head(title, desc, kw, url, img, ogtype="website", ogtitle=None, css=None, header=None, bodycls=None, extra_head=""):
    if ogtitle is None:
        ogtitle = title
    if css is None:
        css = CSS
    if header is None:
        header = BOOK_HEADER
    body = f'<body class="{bodycls}">' if bodycls else "<body>"
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
{FONTS}
{extra_head}<style>{css}</style>
</head>
{body}
{header}
"""

# Footer: About + AI disclosure wording unchanged.
UTM_JS = """<script>
(function(){
  var K=["utm_source","utm_medium","utm_campaign","utm_content","utm_term"], got={}, has=false;
  var q=new URLSearchParams(location.search);
  K.forEach(function(k){var v=q.get(k); if(v){got[k]=v.slice(0,100); has=true;}});
  try{
    if(has) sessionStorage.setItem("pip_utm", JSON.stringify(got));
    else got=JSON.parse(sessionStorage.getItem("pip_utm")||"{}");
  }catch(e){}
  if(!Object.keys(got).length) return;
  document.querySelectorAll('a[href*="gumroad.com/"]').forEach(function(a){
    var u=new URL(a.href);
    K.forEach(function(k){u.searchParams.delete(k);});
    K.forEach(function(k){if(got[k]) u.searchParams.set(k, got[k]);});
    a.href=u.toString();
  });
})();
</script>"""

FOOT_BODY = f"""<p><strong>About · <span lang="zh-Hant">關於</span>:</strong> Stories written by PP O in Hong Kong. Illustrations are AI-generated. <span lang="zh-Hant">故事由香港的 PP O 創作，插圖由 AI 生成。</span></p>
<p>Books are sold as PDF ebooks on Gumroad (Gumroad handles checkout). <span lang="zh-Hant">電子書（PDF）經 Gumroad 發售。</span></p>
<p>Contact · <span lang="zh-Hant">聯絡</span>: <a href="mailto:{EMAIL}">{EMAIL}</a></p>"""

FOOT = f"""<footer>
{FOOT_BODY}
</footer>
{UTM_JS}
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
    others = [o for o in sorted(live_books(), key=lambda x: -x["n"]) if o is not b]
    more = " · ".join(f'<a href="../{o["slug"]}/">{E(o["en"])} <span lang="zh-Hant">{o["zh"]}</span></a>' for o in others)
    own = next((x for x in BUNDLES if b["n"] in x["books"]), None)
    if own:   # this book is in a live bundle
        r = f'{own["books"][0]}–{own["books"][-1]}'
        upsell = (f'<p class="upsell">Want the set? <a href="{own["url"]}{UTM}">Get Pip Books {r} in one bundle for US${own["price"]}</a> '
                  f'· <span lang="zh-Hant">想要套裝？<a href="{own["url"]}{UTM}">皮皮第 {r} 集套裝 US${own["price"]}</a></span></p>')
    else:     # Books 7–12 until their bundle is live: point to the Books 1–6 bundle
        upsell = (f'<p class="upsell">Also available: <a href="{BUNDLE}{UTM}">the Pip bundle of Books 1–6 for US$9.99</a> '
                  f'· <span lang="zh-Hant">另有<a href="{BUNDLE}{UTM}">皮皮第 1–6 集套裝 US$9.99</a></span></p>')
    s = head(title, desc, kw, url, img, "book")
    s += f"""<main>
<div class="book">
<div class="cover"><img src="../img/{b['slug']}/cover.webp" width="600" height="800" alt="Cover of {E(b['en'])} / {b['zh']}: Pip the mole and friends"></div>
<div>
<p class="note">Book {b['n']} · <span lang="zh-Hant">第{["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"][b['n']-1]}集</span></p>
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

HOME_CSS = """
p{margin:0}h1,h2,h3{margin:0}
.zh{color:var(--muted);font-weight:400;font-family:var(--font-body)}
h1+.zh{font-size:26px;line-height:36px;margin-top:8px}
h2+.zh{font-size:22px;line-height:32px;margin-top:4px}
h3+.zh{font-size:17px;line-height:26px;margin-top:2px}
h1{font-size:46px;line-height:54px}h2{font-size:30px;line-height:38px}h3{font-size:20px;line-height:28px}
a{text-decoration:none}a:hover{text-decoration:underline;text-underline-offset:3px}
.wrap{max-width:calc(var(--maxw) + 48px);margin:0 auto;padding:0 24px}
.section{padding:var(--section) 0}
.section-head{max-width:var(--textw);margin-bottom:48px}
.section-head .lede{margin-top:16px;color:var(--ink)}
.section-head .lede .zh{display:block;font-size:15px;line-height:24px}
.wave{height:16px;max-width:var(--maxw);margin:0 auto;background:var(--wave) repeat-x center/120px 16px}
/* slim header */
.nav{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:20px 0}
.nav ul{display:flex;gap:28px;list-style:none;margin:0;padding:0;font-size:15px}
.nav ul a{color:var(--ink)}
/* hero */
.hero{padding:32px 0 var(--section)}
.hero-text{max-width:var(--textw);margin-bottom:48px}
.hero-text .body{margin-top:24px}
.hero-text .body .zh{display:block;font-size:15px;line-height:24px;margin-top:4px}
.actions{display:flex;align-items:center;flex-wrap:wrap;gap:16px 32px;margin-top:32px}
.btn{display:inline-block;background:var(--accent);color:#FFFDF8;font:700 17px/24px var(--font-body);padding:16px 28px;border-radius:999px;transition:background .2s}
.btn:hover{background:var(--accent-hover);color:#FFFDF8;text-decoration:none}
.textlink{font-weight:700}
.hero-art{border-radius:var(--r-hero);overflow:hidden;aspect-ratio:9/5;background:#e9d9c4}
.hero-art img{display:block;width:100%;height:100%;object-fit:cover}
.why{list-style:none;margin:48px 0 0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:32px}
.why li{display:grid;grid-template-columns:88px 1fr;column-gap:20px;align-items:center}
.spot{width:88px;height:88px;border-radius:50%;object-fit:cover;grid-row:span 3}
.why h3{font-size:18px;line-height:26px}.why h3+.zh{font-size:15px;line-height:22px}
.why .body{font-size:15px;line-height:24px;margin-top:4px}
/* books */
.season{margin:0 0 24px;display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 24px}
.season h3{font-size:22px;line-height:30px}.season h3 .zh{font-size:17px;margin-left:8px}
.season a{font-weight:700;font-size:15px}
.season-block+.season-block{margin-top:64px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--gap)}
.card{background:var(--surface);border-radius:var(--r-card);box-shadow:var(--shadow);padding:16px;display:flex;flex-direction:column;transition:transform .2s ease,box-shadow .2s ease}
.card:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(59,47,36,.10)}
.card .cover img{display:block;border-radius:var(--r-img);aspect-ratio:3/4;object-fit:cover;width:100%;background:#efe6d4}
.card-body{padding:20px 8px 4px;display:flex;flex-direction:column;flex:1}
.eyebrow{font-size:14px;line-height:22px;color:var(--muted);margin-bottom:4px;display:flex;align-items:center;gap:8px}
.tag{font-size:12px;line-height:18px;color:var(--moss);background:rgba(94,122,78,.10);padding:1px 8px;border-radius:999px;font-weight:700}
.card h3 a{color:var(--ink)}.card h3 a:hover{color:var(--ink);text-decoration:none}
.theme{margin-top:12px;font-size:15px;line-height:24px}
.theme .zh{display:block;font-size:14px;line-height:22px}
.card-foot{margin-top:auto;padding-top:16px;display:flex;justify-content:space-between;align-items:flex-start;gap:8px;font-size:15px;line-height:22px}
.card-foot a{font-weight:700}
.card-foot .zh{display:block;font-size:13px;line-height:20px;font-weight:400}
.price{color:var(--ink);font-weight:700;white-space:nowrap}.price:hover{color:var(--ink)}
.soon .card-foot{color:var(--muted)}
/* look inside */
.strip{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:24px}
.strip img{display:block;width:100%;border-radius:var(--r-img);box-shadow:var(--shadow);background:var(--surface);aspect-ratio:3/4}
.strip-more{margin-top:24px;font-weight:700}
/* bundles */
.band{background:var(--sage)}
.bundle{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}
.bundle+.bundle{margin-top:var(--section)}
.bundle .label{font-size:14px;line-height:22px;color:var(--muted);margin-bottom:8px}
.fan{position:relative;height:340px}
.fan img{position:absolute;width:190px;border-radius:var(--r-img);box-shadow:var(--shadow);top:30px}
.fan img:nth-child(1){left:8%;transform:rotate(-6deg)}
.fan img:nth-child(2){left:50%;margin-left:-95px;top:0;z-index:2}
.fan img:nth-child(3){right:8%;transform:rotate(6deg)}
.price-big{font:600 46px/54px var(--font-head);font-variation-settings:'SOFT' 100;margin-top:24px}
.price-note{color:var(--ink);font-size:15px;line-height:24px;margin-top:8px}
.price-note .zh{display:block}
.bundle .btn{margin-top:32px}
/* faq */
.faq{max-width:760px}
details{border-top:1px solid var(--hairline)}
details:last-child{border-bottom:1px solid var(--hairline)}
summary{list-style:none;cursor:pointer;padding:24px 48px 24px 0;position:relative}
summary::-webkit-details-marker{display:none}
summary::after{content:'';position:absolute;right:8px;top:34px;width:10px;height:10px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg);transition:transform .2s}
details[open] summary::after{transform:rotate(-135deg);top:40px}
summary .q{display:block;font-weight:700}
summary .zh{display:block;font-size:15px;line-height:24px}
.a{padding:0 48px 24px 0;max-width:var(--textw)}
.a .zh{font-size:15px;line-height:24px;margin-top:8px}
/* more ways */
.more-ways{padding:0 0 var(--section)}
.more-ways h2{font-size:22px;line-height:30px}.more-ways h2+.zh{font-size:17px;line-height:26px}
.chips{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}
.chip{display:inline-block;padding:8px 16px;border:1px solid var(--hairline);border-radius:999px;color:var(--ink);font-size:15px;line-height:22px;background:transparent}
.chip:hover{border-color:var(--muted);color:var(--ink);text-decoration:none}
.chip .zh{font-size:14px}
.more-ways .note{margin-top:12px;font-size:14px;line-height:22px;color:var(--muted)}
/* footer */
footer{padding:40px 0 72px;font-size:14px;line-height:22px;color:var(--muted)}
footer p{margin:8px 0 0}
footer .brand b{font-size:18px}
/* sticky mobile CTA */
.sticky{position:fixed;left:0;right:0;bottom:0;z-index:9;padding:10px 16px calc(10px + env(safe-area-inset-bottom));background:rgba(251,246,236,.96);box-shadow:0 -4px 16px rgba(59,47,36,.08);display:none;transform:translateY(110%);transition:transform .25s}
.sticky .btn{display:block;text-align:center;padding:12px 20px;font-size:16px}
.sticky.show{transform:none}
@media (max-width:900px){.why{grid-template-columns:1fr;gap:16px}}
@media (max-width:720px){
 h1{font-size:30px;line-height:38px}h1+.zh{font-size:20px;line-height:28px;margin-top:6px}
 h2{font-size:24px;line-height:32px}h2+.zh{font-size:18px;line-height:28px}
 .wrap{padding:0 20px}
 .nav{padding:14px 0}.nav ul{gap:16px;font-size:14px}.nav .brand span{display:none}.brand b{font-size:20px}
 .hero{padding:8px 0 24px}
 .hero-text{margin-bottom:16px}
 .hero-text .body{margin-top:12px;font-size:15px;line-height:24px}
 .hero-text .body .zh{font-size:14px;line-height:22px;margin-top:2px}
 .actions{margin-top:16px;gap:12px 24px}
 .btn{padding:14px 24px;font-size:16px}
 .hero-art{aspect-ratio:2/1;border-radius:20px}
 .why{margin-top:12px;grid-template-columns:repeat(3,1fr);gap:8px}
 .why li{display:block;text-align:center}
 .spot{display:block;width:40px;height:40px;margin:0 auto 4px}
 .why h3{font-size:13px;line-height:18px}.why h3+.zh{font-size:12px;line-height:18px;margin:2px 0 0}
 .why .body{display:none}
 #books{padding-top:24px}
 .season a{display:none}
 .section-head{margin-bottom:16px}
 .section-head .lede{margin-top:8px;font-size:15px;line-height:24px}
 .season{margin-bottom:16px}.season h3{font-size:19px;line-height:26px}.season h3 .zh{font-size:15px}
 .grid{grid-template-columns:repeat(2,1fr)}
 .card{padding:8px}
 .card-body{padding:10px 4px 2px}
 .card h3{font-size:17px;line-height:24px}.card h3+.zh{font-size:14px;line-height:22px}
 .theme{font-size:14px;line-height:22px;margin-top:6px}.theme .zh{font-size:13px;line-height:20px}
 .card-foot{font-size:14px;gap:4px;padding-top:10px}.card-foot a{white-space:nowrap}
 .season a{font-size:14px}
 .strip{display:flex;overflow-x:auto;gap:16px;margin:0 -20px;padding:0 20px 12px;scroll-snap-type:x mandatory}
 .strip li{flex:0 0 62%;scroll-snap-align:start}
 .bundle{grid-template-columns:1fr;gap:24px}
 .fan{height:220px;order:-1}.fan img{width:124px}.fan img:nth-child(2){margin-left:-62px}
 .price-big{font-size:36px;line-height:44px}
 summary{padding:20px 40px 20px 0}summary::after{top:28px}details[open] summary::after{top:34px}
 .a{padding-right:0}
 .sticky{display:block}
}
@media (max-width:400px){.card-foot{font-size:13px}.card-foot .zh{font-size:12px}
 body.lp{padding-bottom:76px}
}
"""

FAQ = [
 ("How do I get the books after paying?", "付款後怎樣收到書？",
  "Gumroad shows a download button right after checkout and also emails you the link. The files stay in your Gumroad library, so you can download them again later.",
  "付款後 Gumroad 會即時顯示下載按鈕，同時把下載連結電郵給你。檔案會保留在你的 Gumroad 帳戶，之後可以再下載。"),
 ("Can we read them on a phone or tablet?", "手機、平板可以看嗎？",
  "Yes. They are PDF files, so they open on phones, tablets and computers. Once downloaded, you can read them anywhere, even offline.",
  "可以。全部是 PDF，手機、平板、電腦都能打開；下載後隨時隨地都可以看，不用上網。"),
 ("Can I print them?", "可以列印嗎？",
  "Yes. Each book comes with a print-ready 300 dpi PDF as well as the screen version, so you can print it at home or at a print shop.",
  "可以。每本除了螢幕版，還有 300 dpi 印刷版 PDF，可以在家或到印刷店列印。"),
 ("Is the Chinese Traditional or Simplified?", "中文是繁體還是簡體？",
  "Traditional Chinese, with the English text on the same page.",
  "繁體中文，同一頁有英文對照。"),
 ("What age is it for? Do they need to be read in order?", "適合多少歲？需要按順序讀嗎？",
  "Ages 3–6. The sentences are short and repeat, so they work for reading aloud at bedtime and for early readers. The stories follow the same friends through the seasons, but each book reads fine on its own.",
  "3 至 6 歲。句子短、有重複，適合睡前唸給孩子聽，也適合剛開始認字的孩子。故事是皮皮和好朋友們在不同季節的經歷，但每本都可以單獨閱讀。"),
]

WHY = [
 ("together", "Two languages, one page", "同一頁中英對照", "English and Traditional Chinese together on every page. Read either one, or both."),
 ("calm", "Short and calm", "短而平靜", "16 story pages with short, repeating lines and a read-aloud refrain. Made for winding down."),
 ("lesson", "One small lesson per book", "每本一個小道理", "Teamwork, sharing, saying sorry, trying again, speaking up, saying thank you."),
]

def make_og_collage():
    from PIL import ImageDraw, ImageFont
    out = ROOT / "img" / "og-collage.jpg"
    if out.exists() and not os.environ.get("REIMG"):
        return
    bg = Image.new("RGB", (1200, 630), (251, 246, 236))
    w, h = 144, 192   # up to 12 covers, 4 × 3 grid
    for i, b in enumerate(live_books()[:12]):
        c = Image.open(ROOT / "img" / b["slug"] / "cover.webp").convert("RGB").resize((w, h), Image.LANCZOS)
        bg.paste(c, (36 + (i % 4) * (w + 12), 21 + (i // 4) * (h + 12)))
    d = ImageDraw.Draw(bg)
    fp = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    f1 = ImageFont.truetype(fp, 50, index=2); f2 = ImageFont.truetype(fp, 30, index=2); f3 = ImageFont.truetype(fp, 34, index=2)
    x = 690
    d.text((x, 120), "Pip the Mole", font=f1, fill=(90, 61, 34))
    d.text((x, 185), "皮皮繪本", font=f1, fill=(138, 75, 18))
    d.text((x, 280), f"{len(live_books())} bilingual picture books", font=f2, fill=(59, 47, 36))
    d.text((x, 322), "中英對照 · Ages 3–6", font=f2, fill=(59, 47, 36))
    d.rounded_rectangle((x, 400, x + 440, 470), radius=16, fill=(184, 100, 28))
    d.text((x + 24, 412), "6-book set · US$9.99", font=f3, fill=(255, 255, 255))
    bg.save(out, "JPEG", quality=84, optimize=True, progressive=True)

def book_card(b, newest):
    slug = b["slug"]
    theme_en = (b.get("tag_en") or b["theme_en"])
    theme = f'<p class="theme">{E(theme_en[:1].upper() + theme_en[1:])}<span class="zh" lang="zh-Hant">{b["theme_zh"]}</span></p>'
    img = (f'<img src="img/{slug}/cover-sm.webp" srcset="img/{slug}/cover-sm.webp 360w, img/{slug}/cover.webp 600w" '
           f'sizes="(max-width:720px) 45vw, 330px" width="360" height="480" loading="lazy" decoding="async" '
           f'alt="Cover of {E(b["en"])} / {b["zh"]}">')
    if status_of(b) != "live":
        return f"""<article class="card soon">
<div class="cover">{img}</div>
<div class="card-body">
<p class="eyebrow">Book {b['n']}</p>
<h3>{E(b['en'])}</h3>
<p class="zh" lang="zh-Hant">{b['zh']}</p>
{theme}
<div class="card-foot"><span>Coming soon<span class="zh" lang="zh-Hant">即將推出</span></span></div>
</div>
</article>"""
    tag = ' <span class="tag">New <span lang="zh-Hant">新</span></span>' if b is newest else ""
    return f"""<article class="card">
<a class="cover" href="{slug}/">{img}</a>
<div class="card-body">
<p class="eyebrow">Book {b['n']}{tag}</p>
<h3><a href="{slug}/">{E(b['en'])}</a></h3>
<p class="zh" lang="zh-Hant">{b['zh']}</p>
{theme}
<div class="card-foot">
<a href="{GR}{b['sample']}{UTM}">Free sample<span class="zh" lang="zh-Hant">免費試讀</span></a>
<a class="price" href="{GR}{b['paid']}{UTM}" aria-label="Buy {E(b['en'])}, US${price_of(b)}">US${price_of(b)}</a>
</div>
</div>
</article>"""

def index_page():
    live = live_books()
    n_live = len(live)
    newest = live[-1]
    min_bundle = min(BUNDLES, key=lambda x: float(x["price"]))["price"]
    title = "Pip the Mole 皮皮繪本 · Bilingual Chinese English Picture Books, Ages 3–6 · Free Samples & Bundle"
    ogtitle = f"Pip the Mole 皮皮繪本 · {n_live} bilingual picture books for ages 3–6 · 6-book set from US${min_bundle}"
    desc = (f"{n_live} bilingual picture books for kids aged 3–6, English + Traditional Chinese on every page. "
            f"Read a free sample of any book, or get a 6-book set from US${min_bundle}. 中英對照雙語繪本，共 {n_live} 本：每本免費試讀，或者買六本套裝。")

    # Books grid: one grid per season, series order, each book once
    seasons = sorted({season_of(b) for b in BOOKS})
    blocks = []
    for sn in seasons:
        bs = sorted((b for b in BOOKS if season_of(b) == sn), key=lambda x: x["n"])
        rng = f"Books {bs[0]['n']}–{bs[-1]['n']}" if len(bs) > 1 else f"Book {bs[0]['n']}"
        zh_s = f"第{ZH_NUM[sn - 1]}輯"
        bund = next((x for x in BUNDLES if x["season"] == sn), None)
        blink = (f'<a href="#bundle-{bund["id"]}">Books {bund["books"][0]}–{bund["books"][-1]} in one bundle · US${bund["price"]} →</a>' if bund else "")
        cards = "\n".join(book_card(b, newest) for b in bs)
        blocks.append(f"""<div class="season-block" id="season-{sn}">
<div class="season"><h3>Season {sn} · {rng}<span class="zh" lang="zh-Hant">{zh_s}</span></h3>{blink}</div>
<div class="grid">
{cards}
</div>
</div>""")

    # Look inside: 4 pages from the newest live book (all inside its free sample)
    peek = newest
    zh_peek = f"以下是第{ZH_NUM[peek['n'] - 1]}集《{peek['zh']}》其中四頁。"
    strip = "".join(
        f'<li><img src="img/{peek["slug"]}/page-{i}.webp" width="720" height="960" loading="lazy" decoding="async" '
        f'alt="{E(peek["en"])}, story page {i}: illustration with Traditional Chinese and English text"></li>' for i in range(1, 5))

    # Bundles (sage band)
    bl = []
    for x in BUNDLES:
        each = sum(float(price_of(b)) for b in BOOKS if b["n"] in x["books"])
        fan = "".join(f'<img src="img/{b["slug"]}/cover.webp" width="600" height="800" loading="lazy" decoding="async" alt="">'
                      for k in x.get("fan", x["books"][:3]) for b in BOOKS if b["n"] == k)
        n = len(x["books"])
        bl.append(f"""<div class="bundle" id="bundle-{x['id']}">
<div>
<p class="label">{E(x['label_en'])} · <span lang="zh-Hant">{x['label_zh']}</span></p>
<h2>{E(x['en'])}</h2>
<p class="zh" lang="zh-Hant">{x['zh']}</p>
<p class="price-big">US${x['price']}</p>
<p class="price-note">Instead of US${each:.2f} one by one ({n} × US${PRICE}). Pay what you want from US${x['price']}; paying more helps us make the next Pip book. Instant PDF download via Gumroad.<span class="zh" lang="zh-Hant">逐本買要 US${each:.2f}。US${x['price']} 起自訂價錢，多付一點可以支持我們出下一本；經 Gumroad 即時下載 PDF。</span></p>
<a class="btn" href="{x['url']}{UTM}">{E(x['btn_en'])}</a>
</div>
<div class="fan" aria-hidden="true">{fan}</div>
</div>""")

    faq = "\n".join(
        f'<details{" open" if i == 0 else ""}><summary><span class="q">{E(q)}</span><span class="zh" lang="zh-Hant">{qz}</span></summary>'
        f'<div class="a"><p>{E(a)}</p><p class="zh" lang="zh-Hant">{az}</p></div></details>'
        for i, (q, qz, a, az) in enumerate(FAQ))

    why = "\n".join(
        f'<li><img class="spot" src="img/home/spot-{k}.webp" width="240" height="240" loading="lazy" decoding="async" alt="">'
        f'<h3>{E(t)}</h3><p class="zh" lang="zh-Hant">{tz}</p><p class="body">{E(body)}</p></li>' for k, t, tz, body in WHY)

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            *[{"@type": "Product", "name": f"Pip the Mole {x['label_en']} bundle · {x['zh']}",
               "description": f"{len(x['books'])} bilingual English + Traditional Chinese picture books (PDF) for ages 3–6.",
               "image": f"{SITE}/img/og-collage.jpg", "brand": {"@type": "Brand", "name": "Pip the Mole Books"},
               "offers": {"@type": "Offer", "price": x["price"], "priceCurrency": "USD", "availability": "https://schema.org/InStock", "url": x["url"]}}
              for x in BUNDLES],
            {"@type": "ItemList", "name": "Pip the Mole picture books",
             "itemListElement": [{"@type": "ListItem", "position": b["n"], "url": f"{SITE}/{b['slug']}/", "name": b["en"]} for b in live]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, qz, a, az in FAQ]},
        ]}
    header = f"""<div class="wrap"><header class="nav">
<a class="brand" href="{SITE}/"><b>Pip the Mole</b><span lang="zh-Hant">皮皮繪本</span></a>
<nav aria-label="Sections"><ul><li><a href="#books">Books</a></li><li><a href="#bundles">Bundles</a></li><li><a href="#free">Free</a></li><li><a href="#faq">FAQ</a></li></ul></nav>
</header></div>"""
    hero_pre = (f'<link rel="preload" as="image" href="img/home/hero-960.webp" '
                f'imagesrcset="img/home/hero-960.webp 960w, img/home/hero-1600.webp 1600w" imagesizes="(max-width:1128px) 100vw, 1080px">\n')
    s = head(title, desc, BASE_KW + ", teamwork, sharing, kindness", f"{SITE}/", f"{SITE}/img/og-collage.jpg",
             ogtitle=ogtitle, css=ROOT_CSS + HOME_CSS, header=header, bodycls="lp", extra_head=hero_pre)
    s += f"""<main>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<div class="wrap">
<section class="hero">
<div class="hero-text">
<h1>Gentle bedtime stories in English and Chinese</h1>
<p class="zh" lang="zh-Hant">中英對照睡前繪本：小鼴鼠皮皮</p>
<p class="body">Picture books about Pip the mole and friends, with English and Traditional Chinese on every page. Ages 3–6.<span class="zh" lang="zh-Hant">小鼴鼠皮皮的短篇繪本，每頁中英對照，3–6 歲。</span></p>
<div class="actions">
<a class="btn" id="hero-cta" href="#bundles">Get a 6-book set · <span lang="zh-Hant">六本套裝</span> US${min_bundle}+</a>
<a class="textlink" href="#books">Read a free sample · <span lang="zh-Hant">免費試讀</span> →</a>
</div>
</div>
<div class="hero-art"><img src="img/home/hero-960.webp" srcset="img/home/hero-960.webp 960w, img/home/hero-1600.webp 1600w" sizes="(max-width:1128px) 100vw, 1080px" width="1600" height="889" fetchpriority="high" decoding="async" alt="Pip, Robin and Rabbit watching the sunset over the pond"></div>
<ul class="why">
{why}
</ul>
</section>
</div>

<div class="wave" aria-hidden="true"></div>

<section class="section" id="books">
<div class="wrap">
<div class="section-head"><h2>The books</h2><p class="zh" lang="zh-Hant">全部繪本</p>
<p class="lede" id="free">Every book has a free PDF sample.<span class="zh" lang="zh-Hant">每本都有免費試讀。</span></p></div>
{chr(10).join(blocks)}
</div>
</section>

<div class="wave" aria-hidden="true"></div>

<section class="section" id="inside">
<div class="wrap">
<div class="section-head"><h2>Look inside</h2><p class="zh" lang="zh-Hant">內頁預覽</p>
<p class="lede">Four pages from Book {peek['n']}, <i>{E(peek['en'])}</i>.<span class="zh" lang="zh-Hant">{zh_peek}</span></p></div>
<ul class="strip">{strip}</ul>
<p class="strip-more"><a href="{peek['slug']}/">More about this book · <span lang="zh-Hant">看看這本書</span> →</a></p>
</div>
</section>

<section class="section band" id="bundles">
<div class="wrap">
{chr(10).join(bl)}
</div>
</section>

<section class="section" id="faq">
<div class="wrap">
<div class="section-head"><h2>Questions</h2><p class="zh" lang="zh-Hant">常見問題</p></div>
<div class="faq">
{faq}
</div>
</div>
</section>

<section class="more-ways" id="more-ways">
<div class="wrap">
<h2>More ways to get Pip</h2>
<p class="zh" lang="zh-Hant">其他購買渠道</p>
<p class="chips">
<a class="chip" href="{REDBUBBLE}" target="_blank" rel="noopener">Redbubble <span class="zh" lang="zh-Hant">周邊產品</span></a>
<a class="chip" href="{ETSY}" target="_blank" rel="noopener">Etsy <span class="zh" lang="zh-Hant">PDF 電子書</span></a>
</p>
<p class="note">Redbubble: stickers, mugs and other merch. Etsy: the same PDF ebooks. <span lang="zh-Hant">Redbubble：貼紙、杯子等周邊產品；Etsy：同樣的 PDF 電子書。</span></p>
</div>
</section>
</main>

<div class="wave" aria-hidden="true"></div>
<footer>
<div class="wrap">
<a class="brand" href="{SITE}/"><b>Pip the Mole</b><span lang="zh-Hant">皮皮繪本</span></a>
{FOOT_BODY}
</div>
</footer>

<div class="sticky" id="sticky" aria-hidden="true">
<a class="btn" href="#bundles" tabindex="-1">Get a 6-book set · <span lang="zh-Hant">六本套裝</span> US${min_bundle}+</a>
</div>
<script>
(function(){{
  // Sticky mobile CTA: only after the hero button scrolls away, hidden while the bundle band is on screen,
  // so there is never more than one orange button in view.
  var st=document.getElementById("sticky"), hero=document.getElementById("hero-cta"), band=document.getElementById("bundles");
  if(!st||!hero||!band||!("IntersectionObserver" in window)) return;
  var heroVis=true, bandVis=false;
  function upd(){{ var on=!heroVis&&!bandVis; st.classList.toggle("show",on); st.setAttribute("aria-hidden",on?"false":"true");
    st.querySelector("a").tabIndex=on?0:-1; }}
  new IntersectionObserver(function(e){{heroVis=e[0].isIntersecting;upd();}}).observe(hero);
  new IntersectionObserver(function(e){{bandVis=e[0].isIntersecting;upd();}}).observe(band);
}})();
</script>
{UTM_JS}
</body>
</html>
"""
    return s

def main():
    for b in live_books():
        if not (ROOT / "img" / b["slug"] / "page-4.webp").exists() or os.environ.get("REIMG"):
            make_images(b)
        d = ROOT / b["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(book_page(b), encoding="utf-8")
    make_home_images()
    make_og_collage()
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    urls = [f"{SITE}/"] + [f"{SITE}/{b['slug']}/" for b in sorted(live_books(), key=lambda x: -x["n"])]
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>2026-10-01</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("")
    json.dump([{**{k: b[k] for k in ("n", "slug", "en", "zh", "paid", "sample")}, "season": season_of(b), "status": status_of(b),
                "theme_en": b["theme_en"], "theme_zh": b["theme_zh"], "price": price_of(b)} for b in live_books()],
              open(ROOT / "books.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
