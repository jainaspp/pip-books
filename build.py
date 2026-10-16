#!/usr/bin/env python3
"""Build the static Pip books site. Run: python3 build.py (needs Pillow and the book page PNGs on the box).

Pages are driven by BOOKS and BUNDLES:
  /                homepage shelf — featured (latest) season only, three season entry cards, 3 FAQs
  /season-N/       that season's story, six book cards, its bundle, links to the other seasons
  /shop/           all singles + three bundles; checkout links go to Gumroad
  /about/          PP O, how the books are read, AI illustration note, ages 3–6, contact
  /{slug}/         book page: season badge, prev/next inside the season, 本季其餘, then other seasons
FAQ stays on the homepage (#faq). This build does not write /faq/ or /books/.

  BOOKS   – n, season, status ("live" | "soon"), slug, paid, sample, en/zh, theme_en/theme_zh,
            optional tag_en, optional price (default PRICE).
            season defaults to 1 for Books 1–6 and 2 for Books 7–12; status defaults to "live".
            A "soon" book needs only n, season, status, slug, en, zh, theme_en, theme_zh
            (a card with "Coming soon", no links, no detail page).
  BUNDLES – Gumroad URL, price, which books. A bundle with url "" is hidden everywhere.
A book with sample="" gets no free-sample link until its Gumroad slug is filled in.
Every Gumroad href keeps ?utm_source=pipsite. AdSense auto ads stay in each page <head>.
"""
import html, os, json
from datetime import date
from pathlib import Path
from PIL import Image, ImageFilter
from PIL import Image, ImageFilter

ROOT = Path(__file__).parent
SITE = "https://jainaspp.github.io/pip-books"
GR = "https://jainaspark4.gumroad.com/l/"
UTM = "?utm_source=pipsite"
# Books 1–6 bundle, US$9.99 minimum (pay what you want). 6 × US$4.99 = US$29.94 separately.
BUNDLE = "https://jainaspark4.gumroad.com/l/imzzp"
# Books 7–12 bundle: leave "" until it is live on Gumroad, then paste its URL here and rebuild (it then shows
# on the homepage bundles band, the Season 2 heading link, JSON-LD and the Book 7–12 page upsells).
BUNDLE_S2 = "https://jainaspark4.gumroad.com/l/puwhe"
BUNDLE_S2_PRICE = "9.99"   # confirm against Gumroad before setting BUNDLE_S2
# Books 13–18 bundle (Season 3): leave "" until it is live on Gumroad, then paste its URL here and rebuild.
BUNDLE_S3 = "https://jainaspark4.gumroad.com/l/nnjxnb"
BUNDLE_S3_PRICE = "9.99"   # confirm against Gumroad before setting BUNDLE_S3
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
  sum_zh="夏天晚上，大家在池塘邊等螢火蟲回來。蓬蓬坐在草窩外，靜靜的……「那時候，我不在。」皮皮站起來，大家一起多挖一個位子！第二輯終章。",
  short_en='The nest is full and Pom sits outside. Heave-ho! The friends dig one more spot. The Season 2 finale.',
  short_zh="草窩擠滿了，蓬蓬坐在外邊。嘿咻嘿咻！大家多挖一個位子。第二輯終章。"),
 dict(n=13, season=3, slug="pip-and-the-steady-light", src="/workspace/pipbook13/pages", paid="pip-steady-light", sample="pip-steady-light-free-sample",
  en="Pip and the Steady Light", zh="皮皮和遠處的光", theme_en="being curious and brave together", theme_zh="好奇、一起勇敢去看看",
  kw="adventure picture book, being brave story for kids",
  sum_en="Beyond the hill, one light never blinks. Pip tells Mum and Dad where they're going, and the four friends set off. At the top of the hill is a big, big valley, and it's getting dark. Pip's heart goes thump, thump. He wants to go home… until he sees Pom, curled up tight. He holds her little paw: “Let's look together.” Robin flies up to the tallest pine: “I see it! By the stream. It doesn't blink or move. That's our light!” A gentle story about being curious and brave together. The first book of Season 3.",
  sum_zh="山丘那邊，有一點光不閃也不動。皮皮跟爸媽說好去哪裡，就和好朋友出發了。河谷好大，皮皮好怕，可是他看見蓬蓬縮成一團，就牽起她的小爪子：「我們一起看。」第三輯第一本。",
  short_en="A steady light shines beyond the hill. The valley is big and Pip is scared, but he holds Pom's paw: “Let's look together.”",
  short_zh="山丘那邊有一點不閃也不動的光。皮皮好怕，可是他牽起蓬蓬的小爪子：「我們一起看。」"),
 dict(n=14, season=3, slug="pip-and-the-old-badger", src="/workspace/pipbook14/pages", paid="pip-old-badger", sample="pip-old-badger-free-sample",
  en="Pip and the Old Badger", zh="皮皮和獾婆婆", theme_en="saying hello first", theme_zh="主動打招呼",
  kw="making friends picture book, saying hello story for kids",
  sum_en="The next morning, the four friends cross the hill again and come to the door by the little window. The door is big and tall. Pip lifts his paw to knock… then puts it down. “Who will knock first?” Nobody dares. Only little Pom stands on tiptoe and peeks in: one chair, one cup. “Someone is all alone.” Knock, knock, knock! The door opens, and an old badger smiles: “It's been a long, long time since anyone knocked.” A gentle story about saying hello first.",
  sum_zh="第二天，四個好朋友來到小窗前的門口。門好高好大，誰也不敢敲。最小的蓬蓬踮起腳尖往窗裡看：「這裡只有一個人呢。」叩叩叩！門開了，獾婆婆笑了：「好久好久，沒有人來敲門了。」",
  short_en="The door is so big. Who dares to knock? Little Pom peeks in the window, then knock, knock, knock!",
  short_zh="門好高好大，誰敢敲？最小的蓬蓬踮起腳尖往窗裡看，叩叩叩！"),
 dict(n=15, season=3, tag_en="asking before helping", slug="pip-and-the-apple-tree", src="/workspace/pipbook15/pages", paid="pip-apple-tree", sample="pip-apple-tree-free-sample",
  en="Pip and the Apple Tree", zh="皮皮和蘋果樹", theme_en="asking before helping", theme_zh="幫忙前先問對方需要甚麼",
  kw="summer picture book, helping others story for kids",
  sum_en="It's summer, and the apple tree by Old Badger's house is full of red apples. Thud! An apple drops into the grass. “Old Badger can't climb. I'll pick them all!” says Pip, and he hugs the trunk. Rabbit gently touches his arm: “Wait. It's Old Badger's tree. Let's ask her first.” Old Badger has her own way to pick the high apples, and she asks the friends to gather the fallen ones. Robin spots, Rabbit hops, Pom rolls. Scratch, scratch, scoop! A gentle story about asking before helping.",
  sum_zh="獾婆婆的蘋果熟了，咚！皮皮想爬上樹，全部摘下來。兔子說：「先問問她吧。」原來獾婆婆想要的，是大家幫她撿掉下來的蘋果。先問再來幫！",
  short_en="Pip wants to climb up and pick all of Old Badger's apples. “Let's ask her first,” says Rabbit.",
  short_zh="皮皮想把獾婆婆的蘋果全部摘下來。兔子說：「先問問她吧。」"),
 dict(n=16, season=3, slug="pip-and-the-little-lantern", src="/workspace/pipbook16/pages", paid="pip-little-lantern", sample="pip-little-lantern-free-sample",
  en="Pip and the Little Lantern", zh="皮皮和小燈籠", theme_en="keeping a promise", theme_zh="守承諾",
  kw="autumn picture book, keeping a promise story for kids",
  sum_en="It's autumn in the valley. Old Badger walks very slowly, and she needs her little lantern in her window to find her way home after dark. “Me! I promise!” says Pip. “I'll get it there before dark!” Around the bend is a big pile of crunchy gold leaves. “Let's jump in!” Pip's feet itch to jump too… but he hugs the lantern close and walks past, step by step. “I promised Old Badger. After we deliver the lantern, we'll come back and jump!” A gentle story about keeping a promise.",
  sum_zh="獾婆婆請皮皮送小燈籠回家。皮皮答應了：「天黑前一定送到！」路邊有一大堆金黃落葉，嚓嚓嚓……好想跳！皮皮把燈籠抱緊：「送完燈籠，我們再回來跳！」",
  short_en="Pip promises to take Old Badger's lantern home before dark. Then he sees a big pile of crunchy leaves…",
  short_zh="皮皮答應天黑前把小燈籠送到。路邊的落葉堆嚓嚓嚓，好想跳！"),
 dict(n=17, season=3, slug="pip-and-the-fog", src="/workspace/pipbook17/pages", paid="pip-fog", sample="pip-fog-free-sample",
  en="Pip and the Fog", zh="皮皮和大霧", theme_en="staying close to friends", theme_zh="跟緊同伴",
  kw="autumn picture book, staying safe story for kids",
  sum_en="One autumn morning, thick fog rolls over the hill, white and soft like a big cotton ball. Sniff, sniff! Rabbit smells clover and hops off into the white fog. “Me too!” says Pip. “Stop!” shouts Pom. She remembers the snowy day when she couldn't find her home. “Let's hold each other's tails as we walk. Then nobody gets lost.” Step by step, nobody lets go, until the fog lifts over a big patch of green clover. A gentle story about staying close to friends.",
  sum_zh="秋天的山丘，忽然起了大霧。兔子聞到三葉草的香味，一跳，就跳進了白霧裡……蓬蓬大聲喊：「停！」大家一個拉著一個的尾巴走，誰也不會走丟。",
  short_en="Thick fog covers the hill and Rabbit hops off after the smell of clover. “Stop!” shouts Pom.",
  short_zh="大霧裡，兔子一跳就跳進白霧裡。蓬蓬大聲喊：「停！」"),
 dict(n=18, season=3, slug="pip-and-the-wobbly-bridge", src="/workspace/pipbook18/pages", paid="pip-wobbly-bridge", sample="pip-wobbly-bridge-free-sample",
  en="Pip and the Wobbly Bridge", zh="皮皮和搖晃的橋", theme_en="saying what worries you", theme_zh="說出擔心",
  kw="autumn picture book, worries and feelings story for kids",
  sum_en="It's autumn, and chestnuts cover the ground across the stream. “I'll go first!” says Pip, jumping onto the log bridge. Creak! The log wobbles, and Rabbit's ears slowly droop. “I… I'm not in a hurry.” Robin flies back to her: “Rabbit, are you a little worried?” “The bridge wobbles. I'm scared I'll fall.” Pip steps down: “Then I don't need to be first.” Together, step by step, they cross, and the first chestnut goes to Rabbit. A gentle story about saying what worries you.",
  sum_zh="秋天，小溪對岸掉滿了栗子。皮皮跳上獨木橋，吱呀——兔子的耳朵卻垂了下來。知更鳥輕輕問：「兔子，你是不是有一點擔心？」說出擔心，朋友就會陪著你。",
  short_en="The log bridge wobbles, and Rabbit's ears droop. “Are you a little worried?” Say you're scared, and a friend stays.",
  short_zh="獨木橋吱呀吱呀地晃，兔子的耳朵垂了下來。說出擔心，就不慌！"),
]

E = html.escape

BUNDLES = [b for b in [
 dict(id="season-1", season=1, books=[1, 2, 3, 4, 5, 6], url=BUNDLE, price="9.99", fan=[3, 6, 4],
  en="Pip Books 1–6 in one bundle", zh="皮皮第 1–6 集套裝",
  btn_en="Get Books 1–6 · US$9.99", label_en="Season 1 · Books 1–6", label_zh="第一輯"),
 dict(id="season-2", season=2, books=[7, 8, 9, 10, 11, 12], url=BUNDLE_S2, price=BUNDLE_S2_PRICE, fan=[9, 12, 8],
  en="Pip Books 7–12 in one bundle", zh="皮皮第 7–12 集套裝",
  btn_en=f"Get Books 7–12 · US${BUNDLE_S2_PRICE}", label_en="Season 2 · Books 7–12", label_zh="第二輯"),
 dict(id="season-3", season=3, books=[13, 14, 15, 16, 17, 18], url=BUNDLE_S3, price=BUNDLE_S3_PRICE, fan=[14, 13, 16],
  en="Pip Books 13–18 in one bundle", zh="皮皮第 13–18 集套裝",
  btn_en=f"Get Books 13–18 · US${BUNDLE_S3_PRICE}", label_en="Season 3 · Books 13–18", label_zh="第三輯"),
] if b["url"]]   # a bundle without a URL is hidden everywhere

ZH_NUM = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八"]

def season_of(b):
    return b.get("season") or (1 if b["n"] <= 6 else 2 if b["n"] <= 12 else 3)

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
    # Header mark: Pip centred in the calm spot, circled in CSS.
    avatar = out / "pip-avatar.webp"
    if not avatar.exists() or os.environ.get("REIMG"):
        src = Image.open(out / "spot-calm.webp").convert("RGBA")
        bg = Image.new("RGB", src.size, (251, 246, 236))
        bg.paste(src, mask=src.split()[-1])
        w, h = bg.size
        side = min(w, h)
        left, top = (w - side) // 2, (h - side) // 2
        bg.crop((left, top, left + side, top + side)).resize((160, 160), Image.LANCZOS).save(avatar, "WEBP", quality=84, method=6)

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,600,100'
         '&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">')

# Google AdSense Auto ads. One script in <head>; no manual <ins> units.
ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8392975944327076"\n'
           '     crossorigin="anonymous"></script>')
ADS_TXT = "google.com, pub-8392975944327076, DIRECT, f08c47fec0942fa0\n"

# Short season lines for entry cards; the longer pair is the season-page narrative.
# Copy stays in the site's written Traditional voice (not a rewrite of the book texts).
SEASON_META = {
 1: dict(
   tone_en="From the big dig to the first snow.",
   tone_zh="從大挖掘到第一場雪。",
   story_en="Pip, Robin and Rabbit share a hill: a hole that becomes a pond, then the first snow. Six calm bedtime stories about teamwork, sharing, saying sorry, and caring for someone small.",
   story_zh="皮皮、知更鳥和兔子在同一座山丘。大洞後來變成小池塘，然後是第一場雪。六個平靜的睡前故事：一起合作、分享、說對不起，和關心小小的朋友。"),
 2: dict(
   tone_en="Pom joins the hill, from winter to summer.",
   tone_zh="蓬蓬加入山丘，從冬天到夏天。",
   story_en="Winter, spring, then a hot summer day. Pom the hedgehog joins the hill. The friends say goodbye for now, try again, and dig one more spot in the circle.",
   story_zh="冬天、春天，再到大熱天。刺蝟寶寶蓬蓬加入山丘。大家好好說再見、再試一次，也一起多留一個位子。"),
 3: dict(
   tone_en="A steady light, and a new friend in the valley.",
   tone_zh="一點不閃的光，河谷裡的新朋友。",
   story_en="A light beyond the hill leads Pip, Robin, Rabbit and Pom into a wide valley, and to Old Badger's door. Six stories about saying hello, asking before helping, keeping a promise, and saying what worries you.",
   story_zh="山丘那邊有一點不閃的光。四個好朋友走進新的河谷，敲開獾婆婆的門。六個故事：主動打招呼、先問再幫忙、守承諾、說出擔心。"),
}

def all_seasons():
    return sorted({season_of(b) for b in BOOKS})

def books_in(sn):
    return sorted((b for b in BOOKS if season_of(b) == sn), key=lambda x: x["n"])

def bundle_for(sn):
    return next((x for x in BUNDLES if x["season"] == sn), None)

def featured_season():
    return max(season_of(b) for b in live_books())

def min_bundle_price():
    return min(BUNDLES, key=lambda x: float(x["price"]))["price"]

def bundle_label():
    return f"六本套裝 US${min_bundle_price()}+"

def gum_slug(slug):
    return f"{GR}{slug}{UTM}"

def gum_url(url):
    return f"{url}{UTM}"

def depth_prefix(depth):
    return "../" * depth

def home_href(depth):
    p = depth_prefix(depth)
    return p if p else "./"

def book_by_n(n):
    return next(b for b in BOOKS if b["n"] == n)

BASE_KW = "children's picture book, bilingual Chinese English picture book, Traditional Chinese, 中英雙語繪本, bedtime story, toddler, preschool, ages 3-6, read aloud, PDF ebook, Pip the mole"

# ---------------------------------------------------------------------------
# Visual system — Mood C「故事書架」. Tokens from the art direction.
ROOT_CSS = """
:root{--paper:#FBF6EC;--surface:#FFFDF8;--sage:#E7EDDF;--hairline:#EADFCB;--ink:#3B2F24;--muted:#6B5A48;
--accent:#B8641C;--accent-hover:#8A4B12;--moss:#5E7A4E;
--s1:#6FA84A;--s1b:#E8B83A;--s2:#C4453A;--s2b:#E2862C;--s3:#EE9566;--s3b:#1F2C66;
--font-head:'Fraunces','Noto Sans TC','Noto Sans CJK TC',Georgia,serif;
--font-body:'Noto Sans TC','Noto Sans CJK TC','PingFang TC','Microsoft JhengHei',system-ui,sans-serif;
--maxw:1080px;--textw:640px;--r-card:16px;--r-img:12px;
--shadow:0 6px 20px rgba(59,47,36,.08);
--wave:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='16' viewBox='0 0 120 16'%3E%3Cpath d='M0 8 Q15 2 30 8 T60 8 T90 8 T120 8' fill='none' stroke='%23EADFCB' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E")}
*,*::before,*::after{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;font:400 17px/1.65 var(--font-body);color:var(--ink);background:var(--paper)}
img{max-width:100%;height:auto}
a{color:var(--accent)}a:hover{color:var(--accent-hover)}
h1,h2,h3{font-family:var(--font-head);font-weight:600;font-variation-settings:'SOFT' 100;color:var(--ink);letter-spacing:-.01em;margin:0}
p{margin:0}
.skip{position:absolute;left:-999px;top:8px}
.skip:focus{left:12px;z-index:40;background:var(--surface);color:var(--ink);padding:8px 12px;border-radius:8px}
.wrap{max-width:calc(var(--maxw) + 48px);margin:0 auto;padding:0 24px}
.zh{color:var(--muted);font-weight:400}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media (max-width:720px){body{font-size:16px}.wrap{padding:0 16px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""

SHELL_CSS = """
header.site-head{position:sticky;top:0;z-index:20;background:rgba(251,246,236,.94);backdrop-filter:blur(10px);border-bottom:1px solid var(--hairline)}
.nav-inner{max-width:calc(var(--maxw) + 48px);margin:0 auto;padding:12px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{color:var(--ink);text-decoration:none;display:inline-flex;align-items:center;gap:10px}
.brand:hover{color:var(--ink);text-decoration:none}
.avatar{width:32px;height:32px;border-radius:50%;object-fit:cover;flex:none;box-shadow:0 0 0 2px #fffdf8,0 0 0 3px var(--hairline)}
.brand-name{display:flex;flex-direction:column;line-height:1.15}
.brand-name b{font:600 18px/1.2 var(--font-head);font-variation-settings:'SOFT' 100}
.brand-name span{font-size:13px;color:var(--muted);font-weight:400}
.nav-links{display:flex;align-items:center;gap:22px;list-style:none;margin:0;padding:0;font-size:15px}
.nav-links a,.menu summary{color:var(--ink);text-decoration:none;font-weight:500;cursor:pointer}
.nav-links a:hover,.menu summary:hover{color:var(--accent);text-decoration:none}
.nav-links a[aria-current="page"],.menu summary[aria-current="page"]{color:var(--accent);font-weight:700}
.menu{position:relative}
.menu summary{list-style:none}
.menu summary::-webkit-details-marker{display:none}
.menu summary::after{content:"";display:inline-block;margin-left:5px;border:4px solid transparent;border-top-color:currentColor;transform:translateY(2px)}
.menu .pop{position:absolute;left:0;top:calc(100% + 8px);background:var(--surface);border:1px solid var(--hairline);border-radius:12px;box-shadow:var(--shadow);min-width:230px;padding:6px;z-index:30;display:flex;flex-direction:column}
.menu .pop a{padding:8px 10px;border-radius:8px;font-weight:600}
.menu .pop a:hover{background:var(--paper)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:8px}
.dot.s1{background:var(--s1)}.dot.s2{background:var(--s2)}.dot.s3{background:var(--s3)}
.section{padding:28px 0 8px}
.pill{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;gap:0;background:var(--accent);color:#FFFDF8;font:700 17px/1.25 var(--font-body);padding:12px 22px;border-radius:999px;text-decoration:none;border:1.5px solid var(--accent);text-align:center}
.pill small{display:block;font-weight:500;font-size:12px;line-height:1.3;opacity:.92}
.pill:hover{background:var(--accent-hover);border-color:var(--accent-hover);color:#FFFDF8;text-decoration:none}
.pill.sample{background:var(--surface);color:var(--moss);border-color:var(--moss)}
.pill.sample:hover{background:#F4F7F0;color:var(--moss)}
.textlink{font-weight:700;color:var(--moss);text-decoration:none}
.textlink:hover{color:#3E5634;text-decoration:underline;text-underline-offset:3px}
.checkout-note{margin-top:8px;font-size:14px;line-height:1.45;color:var(--muted)}
.season-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.season-chips a{display:inline-flex;align-items:baseline;gap:6px;border-radius:999px;padding:8px 14px;font-weight:700;text-decoration:none;border:1.5px solid transparent;color:var(--ink)}
.season-chips a small{font-weight:500;font-size:12px}
.season-chips a.s1{background:#E7F3DC;color:#2C5222;border-color:#6FA84A}
.season-chips a.s2{background:#F8E3DC;color:#8A2E28;border-color:#C4453A}
.season-chips a.s3{background:#FDE6D8;color:#8A4524;border-color:#EE9566}
.season-chips a:hover{text-decoration:none;filter:brightness(.98)}
.hero-fan{position:relative;height:320px;width:100%}
.hero-fan a{position:absolute;display:block;width:158px;text-decoration:none}
.hero-fan img{display:block;width:100%;height:auto;border-radius:12px;box-shadow:var(--shadow);aspect-ratio:3/4;object-fit:cover;background:#efe6d4}
.hero-fan a:nth-child(1){left:4%;top:28px;transform:rotate(-7deg)}
.hero-fan a:nth-child(2){left:50%;top:0;margin-left:-79px;z-index:2}
.hero-fan a:nth-child(3){right:4%;top:32px;transform:rotate(7deg)}
.shelf-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px 20px;margin:0 0 18px;padding-top:10px;border-top:4px solid var(--s1);flex-wrap:wrap}
.shelf-head.s2{border-top-color:var(--s2)}.shelf-head.s3{border-top-color:var(--s3)}
.shelf-head h2{font-size:28px;line-height:1.2}
.shelf-head h2 a{color:var(--ink);text-decoration:none}
.shelf-head h2 a:hover{color:var(--accent)}
.shelf-head .range{margin-top:4px;color:var(--muted);font-size:14px}
.shelf-link{font-weight:700;color:var(--accent);text-decoration:none;text-align:right}
.shelf-link small{display:block;font-weight:500;color:var(--muted);font-size:12px}
.shelf-link:hover{text-decoration:underline;text-underline-offset:3px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;align-items:stretch}
.card{background:var(--surface);border-radius:var(--r-card);box-shadow:var(--shadow);padding:12px 12px 14px;display:flex;flex-direction:column;height:100%}
.card .cover img{display:block;width:100%;border-radius:var(--r-img);aspect-ratio:3/4;object-fit:cover;background:#efe6d4}
.card-body{display:flex;flex-direction:column;flex:1;padding:12px 4px 0}
.eyebrow{font-size:13px;line-height:1.4;color:var(--muted);margin:0 0 4px}
.card h3{font-size:20px;line-height:1.3}
.card h3 a{color:var(--ink);text-decoration:none}
.card h3 a:hover{text-decoration:underline;text-underline-offset:3px}
.en-name{margin:2px 0 0;color:var(--muted);font-size:14px;line-height:1.35}
.chip-theme{margin:10px 0 0;font-size:13px;line-height:1.35}
.chip-theme .th{display:inline-block;border-radius:999px;padding:2px 8px;font-weight:700;background:rgba(111,168,74,.16);color:#2C5222}
.card.s2 .chip-theme .th{background:rgba(196,69,58,.12);color:#8A2E28}
.card.s3 .chip-theme .th{background:rgba(238,149,102,.22);color:#8A4524}
.chip-theme .en{display:block;margin-top:4px;color:var(--muted);font-weight:400}
.tag{font-size:11px;font-weight:700;color:var(--accent);background:rgba(184,100,28,.12);border-radius:999px;padding:1px 7px;margin-left:6px}
.card-actions{margin-top:auto;padding-top:12px;display:flex;gap:8px}
.btn-sample,.btn-buy{flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;text-decoration:none;border-radius:999px;padding:8px 4px;font-weight:700;font-size:14px;line-height:1.2;min-height:44px}
.btn-sample small,.btn-buy small{display:block;font-weight:500;font-size:11px;line-height:1.2}
.btn-sample{color:var(--moss);background:var(--surface);border:1.5px solid var(--moss)}
.btn-sample:hover{background:#F4F7F0;color:var(--moss);text-decoration:none}
.btn-buy{color:#FFFDF8;background:var(--accent);border:1.5px solid var(--accent)}
.btn-buy:hover{background:var(--accent-hover);color:#FFFDF8;text-decoration:none}
.btn-buy small{color:rgba(255,253,248,.9)}
.soon-label{color:var(--muted);font-size:14px;font-weight:700}
.entries{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:16px}
.entry{display:flex;flex-direction:column;background:var(--surface);border-radius:16px;box-shadow:var(--shadow);overflow:hidden;text-decoration:none;color:var(--ink);min-height:100%}
.entry:hover{transform:translateY(-2px);color:var(--ink);text-decoration:none}
.entry .band{height:7px;display:block;background:linear-gradient(90deg,var(--s1),var(--s1b))}
.entry.s2 .band{background:linear-gradient(90deg,var(--s2),var(--s2b))}
.entry.s3 .band{background:linear-gradient(90deg,var(--s3),var(--s3b))}
.entry .mini{display:flex;justify-content:center;align-items:flex-end;height:112px;padding-top:14px}
.entry .mini img{width:70px;height:94px;object-fit:cover;border-radius:8px;box-shadow:var(--shadow);margin:0 -8px;background:#efe6d4}
.entry .mini img:nth-child(1){transform:rotate(-6deg)}
.entry .mini img:nth-child(2){position:relative;z-index:1;width:76px;height:102px}
.entry .mini img:nth-child(3){transform:rotate(6deg)}
.entry .body{display:flex;flex-direction:column;gap:4px;flex:1;padding:12px 16px 16px}
.entry strong{font-family:var(--font-head);font-size:26px;font-weight:600;line-height:1.2}
.entry .tone{font-size:14px;line-height:1.45}
.entry .tone .zh{display:block}
.entry .go{margin-top:auto;padding-top:10px;font-weight:700;color:var(--accent)}
.entry .go small{display:block;font-weight:500;color:var(--muted);font-size:12px}
footer.site{margin-top:36px;padding:28px 0 40px;color:var(--muted);font-size:14px;line-height:1.55;background:var(--wave) repeat-x top/120px 16px}
footer.site .wrap{padding-top:18px}
.foot-nav{display:flex;flex-wrap:wrap;gap:8px 16px;margin:14px 0}
.foot-nav a{color:var(--ink);font-weight:700;text-decoration:none}
.foot-nav a:hover{text-decoration:underline;text-underline-offset:3px}
footer.site p{margin-top:8px}
.other-label{margin-top:16px;font-weight:700;color:var(--ink)}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.chip{display:inline-block;padding:8px 14px;border:1px solid var(--hairline);border-radius:999px;color:var(--ink);background:transparent;text-decoration:none;font-size:14px;line-height:1.4}
.chip:hover{border-color:var(--muted);color:var(--ink);text-decoration:none}
footer.site .note{font-size:13px}
.sticky{position:fixed;left:0;right:0;bottom:0;z-index:25;padding:10px 16px calc(10px + env(safe-area-inset-bottom));background:rgba(251,246,236,.96);box-shadow:0 -4px 16px rgba(59,47,36,.08);display:none;transform:translateY(110%);transition:transform .25s}
.sticky .pill{width:100%;padding:12px 16px}
.mt14{margin-top:14px}.mt16{margin-top:16px}.season-block{margin-top:28px}
.sticky.show{transform:none}
@media (max-width:800px){
 .grid{grid-template-columns:repeat(2,1fr);gap:12px}
 .hero-fan{height:200px;max-width:none}
 .hero-fan a{width:31%}
 .hero-fan a:nth-child(1){left:1%;top:18px}
 .hero-fan a:nth-child(2){left:50%;top:0;margin-left:-15.5%}
 .hero-fan a:nth-child(3){right:1%;top:22px}
 .shelf-head h2{font-size:22px}
 .card{padding:8px}
 .card h3{font-size:17px}
 .card-body{padding:10px 2px 0}
 .btn-sample,.btn-buy{font-size:13px;padding:7px 2px}
}
@media (max-width:720px){
 .nav-inner{flex-wrap:wrap;padding:10px 16px;gap:8px}
 .nav-links{width:100%;flex-wrap:wrap;gap:8px 14px;font-size:14px;padding-bottom:2px}
 .brand-name b{font-size:17px}
 .sticky{display:block}
 body.has-sticky{padding-bottom:84px}
}
"""

HOME_CSS = """
.hero{padding:18px 0 8px}
.hero-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(240px,.85fr);grid-template-areas:"copy fan" "why fan";gap:8px 36px;align-items:center}
.hero-copy{grid-area:copy}
.why-pills{grid-area:why;align-self:start}
.hero-fan{grid-area:fan}
.zh-hero{display:block;font-size:46px;line-height:1.15;font-weight:600}
.en-hero{display:block;margin-top:4px;font-family:var(--font-head);font-weight:600;font-size:28px;line-height:1.25;color:var(--muted)}
.hero .meta{margin-top:12px;color:var(--muted);font-size:15px}
.hero-actions{display:flex;flex-wrap:wrap;align-items:center;gap:12px 18px;margin-top:18px}
.why-pills{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:14px 0 0;padding:0}
.why-pills li{background:var(--surface);border:1px solid var(--hairline);border-radius:999px;padding:6px 12px;font-size:14px;line-height:1.4}
.why-pills .en{color:var(--muted);margin-left:4px}
.shelf-note{margin-top:14px;color:var(--muted);font-size:14px}
.shelf-note .en{display:block}
.bundle-jump{margin-top:8px;font-weight:700}
.faq{max-width:760px;margin-top:8px}
details.qa{border-top:1px solid var(--hairline)}
details.qa:last-of-type{border-bottom:1px solid var(--hairline)}
details.qa summary{list-style:none;cursor:pointer;padding:16px 36px 16px 0;position:relative}
details.qa summary::-webkit-details-marker{display:none}
details.qa summary::after{content:"";position:absolute;right:8px;top:22px;width:9px;height:9px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg)}
details.qa[open] summary::after{transform:rotate(-135deg);top:26px}
details.qa .q{display:block;font-weight:700}
details.qa .zh{display:block;font-size:15px}
details.qa .a{padding:0 36px 16px 0;max-width:var(--textw)}
details.qa .a .zh{display:block;margin-top:6px}
.faq-more{margin-top:14px;font-weight:700}
@media (max-width:800px){
 .hero-grid{grid-template-columns:1fr;grid-template-areas:"copy" "fan" "why";gap:12px}
 .zh-hero{font-size:34px}
 .en-hero{font-size:22px}
 .hero-actions{flex-direction:column;align-items:stretch}
 .hero-actions .pill{width:100%}
 .hero-actions .textlink{text-align:center}
}
"""

PAGE_CSS = """
.kicker{margin:14px 0;font-size:14px;font-weight:700}
.kicker a{color:var(--muted);text-decoration:none}
.kicker a:hover{color:var(--accent)}
.season-top{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(220px,.8fr);gap:12px 20px;align-items:center;border-radius:20px;box-shadow:var(--shadow);border-top:8px solid var(--s1);background:linear-gradient(180deg,rgba(111,168,74,.18),var(--surface) 58%);margin-top:8px}
.season-top.s2{border-top-color:var(--s2);background:linear-gradient(180deg,rgba(196,69,58,.14),var(--surface) 58%)}
.season-top.s3{border-top-color:var(--s3);background:linear-gradient(180deg,rgba(238,149,102,.22),var(--surface) 58%)}
.season-copy{padding:26px 8px 22px 26px}
.season-copy h1{font-size:40px;line-height:1.15}
.season-copy h1 .en{display:block;margin-top:4px;font-size:22px;color:var(--muted);font-weight:600}
.season-copy .story{margin-top:12px;max-width:62ch}
.season-copy .story .zh{display:block;margin-top:6px}
.season-copy .meta{margin-top:10px;color:var(--muted);font-size:14px}
.hero-actions{display:flex;flex-wrap:wrap;align-items:center;gap:12px 18px;margin-top:16px}
.season-top .hero-fan{margin-right:12px}
.page-h1{font-size:40px;line-height:1.15;margin-top:18px}
.page-h1 .en{display:block;margin-top:4px;font-size:22px;color:var(--muted);font-weight:600}
.lede{margin-top:12px;max-width:68ch}
.lede .zh{display:block;margin-top:4px}
.bundle-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px;margin-top:16px}
.bcard{background:var(--surface);border-radius:16px;box-shadow:var(--shadow);overflow:hidden;display:flex;flex-direction:column;border-top:8px solid var(--s1)}
.bcard.s2{border-top-color:var(--s2)}.bcard.s3{border-top-color:var(--s3)}
.bcard .pad{padding:16px 16px 18px;display:flex;flex-direction:column;gap:8px;flex:1}
.thumbs{display:flex;gap:8px}
.thumbs img{width:32%;border-radius:8px;aspect-ratio:3/4;object-fit:cover;background:#efe6d4}
.price-big{font:600 42px/1.1 var(--font-head);font-variation-settings:'SOFT' 100}
.was{color:var(--muted);font-size:14px}
.bcard .pill{margin-top:auto}
.bundle-repeat{margin-top:22px;background:var(--surface);border-radius:16px;box-shadow:var(--shadow);padding:20px 22px;border-left:8px solid var(--s1)}
.bundle-repeat.s2{border-left-color:var(--s2)}.bundle-repeat.s3{border-left-color:var(--s3)}
.bundle-repeat .price-big{margin:6px 0}
.quiet{margin-top:42px;padding-top:22px;border-top:1px solid var(--hairline)}
.quiet h2{font-size:22px;color:var(--muted)}
.prose{max-width:68ch;padding-bottom:12px}
.prose h2{font-size:26px;margin:1.3em 0 .35em}
.prose p{margin:0 0 10px}
.prose .zh{display:block}
.about-links{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:8px;font-weight:700}
@media (max-width:800px){
 .season-top{grid-template-columns:1fr}
 .season-copy{padding:20px 16px 4px}
 .season-copy h1,.page-h1{font-size:32px}
 .season-top .hero-fan{margin:0 auto 12px}
 .price-big{font-size:36px}
 .hero-actions{flex-direction:column;align-items:stretch}
 .hero-actions .pill{width:100%}
}
"""

BOOK_CSS = """
.book-wrap{max-width:960px}
.back{margin:12px 0;font-size:14px;font-weight:700}
.back a{color:var(--muted);text-decoration:none}
.back a:hover{color:var(--accent)}
.book{display:grid;grid-template-columns:minmax(0,280px) minmax(0,1fr);grid-template-areas:"cover intro" "cover seq" "cover buy";gap:10px 28px;align-items:start;margin-top:4px}
.cover{grid-area:cover}
.book-intro{grid-area:intro}
.seq{grid-area:seq}
.book-buy{grid-area:buy}
.cover img{width:100%;border-radius:12px;box-shadow:var(--shadow);aspect-ratio:3/4;object-fit:cover;display:block;background:#efe6d4}
.badge{display:inline-flex;gap:6px;align-items:center;margin:0 0 8px;padding:4px 10px;border-radius:999px;font-size:13px;font-weight:700;background:#E7F3DC;color:#2C5222;text-decoration:none}
.badge.s2{background:#F8E3DC;color:#8A2E28}
.badge.s3{background:#FDE6D8;color:#8A4524}
.badge:hover{text-decoration:none;filter:brightness(.98)}
h1.book-title{font-size:2rem;line-height:1.25}
h1.book-title .en-title{display:block;margin-top:4px;font-family:var(--font-body);font-weight:400;font-size:1.05rem;color:var(--muted)}
.theme-line{margin-top:8px}
.seq{display:flex;gap:10px}
.seq a{flex:1;min-width:0;text-decoration:none;color:var(--ink);font-weight:700;font-size:14px;line-height:1.35;background:var(--surface);border-radius:12px;padding:10px 12px;box-shadow:var(--shadow)}
.seq a small{display:block;font-weight:400;color:var(--muted)}
.seq .next{text-align:right}
.seq .spacer{flex:1}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 6px}
.cta .pill{flex:1 1 200px}
.upsell{margin:12px 0;padding:12px 14px;background:var(--surface);border-radius:12px;border-left:4px solid var(--s1);display:flex;flex-direction:column;gap:4px}
.upsell.s2{border-left-color:var(--s2)}.upsell.s3{border-left-color:var(--s3)}
.upsell a{font-weight:700;text-decoration:none}
.upsell a:hover{text-decoration:underline;text-underline-offset:3px}
.upsell .en{color:var(--muted);font-size:14px}
.lead{margin-top:12px}
.lead[lang]{color:var(--muted)}
dl.facts{display:grid;grid-template-columns:auto 1fr;gap:8px 14px;font-size:.95rem;margin:16px 0;background:var(--surface);border-radius:16px;box-shadow:var(--shadow);padding:14px 16px}
dl.facts dt{font-weight:700}dl.facts dd{margin:0}
.book-wrap h2{font-size:1.45rem;margin:2rem 0 .75rem}
.book-wrap h2 span[lang]{font:400 1rem var(--font-body);color:var(--muted);margin-left:6px}
.pages{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.pages img{width:100%;border-radius:12px;box-shadow:var(--shadow);aspect-ratio:3/4;object-fit:cover;background:var(--surface);display:block}
.note{margin-top:10px;font-size:.9rem;color:var(--muted)}
.season-links{display:grid;grid-template-columns:1fr 1fr;gap:16px 24px}
.season-links h3{font-size:1.15rem}
.season-links h3 a{color:var(--ink);text-decoration:none}
.season-links ul{list-style:none;margin:8px 0 0;padding:0}
.season-links li{margin:5px 0}
.season-links li a{color:var(--ink);font-weight:700;text-decoration:none}
.season-links li a:hover,.season-links h3 a:hover{color:var(--accent)}
.season-links .en{font-weight:400}
@media (max-width:720px){
 .book{grid-template-columns:42% 1fr;grid-template-areas:"cover intro" "seq seq" "buy buy";gap:10px 12px}
 h1.book-title{font-size:1.35rem}
 h1.book-title .en-title{font-size:.92rem}
 .pages{grid-template-columns:repeat(2,1fr)}
 .season-links{grid-template-columns:1fr}
 .cta{flex-wrap:nowrap;gap:8px}
 .cta .pill{flex:1 1 0;min-width:0;padding:10px 6px;font-size:15px}
 .cta .pill small{font-size:11px}
}
"""

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

STICKY_JS = """<script>
(function(){
  var st=document.getElementById("sticky"), hero=document.getElementById("hero-cta");
  if(!st||!hero||!("IntersectionObserver" in window)) return;
  function apply(on){
    st.classList.toggle("show", on);
    st.setAttribute("aria-hidden", on ? "false" : "true");
    var a=st.querySelector("a"); if(a) a.tabIndex=on?0:-1;
  }
  new IntersectionObserver(function(es){ apply(!es[0].isIntersecting); }, {threshold:0.2}).observe(hero);
})();
</script>"""

def head(title, desc, kw, url, img, ogtype="website", ogtitle=None, css="", header="", bodycls=None, extra_head=""):
    if ogtitle is None:
        ogtitle = title
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
{ADSENSE}
{extra_head}<style>{css}</style>
</head>
{body}
{header}
"""

def site_header(depth, here):
    p = depth_prefix(depth)
    home = home_href(depth)
    books_href = "#books" if here == "home" else f"{home}#books"
    sample_href = "#samples" if here == "shop" else f"{p}shop/#samples"
    pops = []
    for sn in all_seasons():
        cur = ' aria-current="page"' if here == f"season-{sn}" else ""
        pops.append(
            f'<a href="{p}season-{sn}/"{cur}><i class="dot s{sn}" aria-hidden="true"></i>'
            f'Season {sn} · <span lang="zh-Hant">第{ZH_NUM[sn - 1]}輯</span></a>')
    sum_cur = ' aria-current="page"' if here.startswith("season-") else ""
    def item(key, href, label):
        cur = ' aria-current="page"' if here == key else ""
        return f'<li><a href="{href}"{cur}>{label}</a></li>'
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="nav-inner">
<a class="brand" href="{home}"><img class="avatar" src="{p}img/home/pip-avatar.webp" width="32" height="32" alt=""><span class="brand-name"><b>Pip the Mole</b><span lang="zh-Hant">皮皮繪本</span></span></a>
<nav aria-label="Primary"><ul class="nav-links">
{item("books", books_href, "Books")}
<li><details class="menu"><summary{sum_cur}>Seasons</summary><div class="pop">{"".join(pops)}</div></details></li>
{item("shop", f"{p}shop/", "Shop")}
{item("about", f"{p}about/", "About")}
<li><a href="{sample_href}">Free sample</a></li>
</ul></nav>
</div></header>
'''

def site_footer(depth):
    p = depth_prefix(depth)
    home = home_href(depth)
    faq = "#faq" if depth == 0 else f"{home}#faq"
    seasons = "".join(
        f'<a href="{p}season-{sn}/">Season {sn} · <span lang="zh-Hant">第{ZH_NUM[sn - 1]}輯</span></a>'
        for sn in all_seasons())
    return f'''<footer class="site"><div class="wrap">
<a class="brand" href="{home}"><img class="avatar" src="{p}img/home/pip-avatar.webp" width="32" height="32" alt=""><span class="brand-name"><b>Pip the Mole</b><span lang="zh-Hant">皮皮繪本</span></span></a>
<nav class="foot-nav" aria-label="Footer">
{seasons}
<a href="{p}shop/">Shop · <span lang="zh-Hant">商店</span></a>
<a href="{p}about/">About · <span lang="zh-Hant">關於</span></a>
<a href="{faq}">FAQ · <span lang="zh-Hant">常見問題</span></a>
<a href="mailto:{EMAIL}">Contact · <span lang="zh-Hant">聯絡</span></a>
</nav>
<p>Stories by PP O in Hong Kong. Illustrations are AI-generated. <a href="{p}about/">About · <span lang="zh-Hant">關於</span></a></p>
<p>PDF ebooks. Checkout on Gumroad. <span lang="zh-Hant">電子書（PDF）。結帳在 Gumroad。</span></p>
<p class="other-label">其他店／周邊 · Other shops</p>
<p class="chips">
<a class="chip" href="{ETSY}" target="_blank" rel="noopener">Etsy · <span lang="zh-Hant">同一套 PDF</span></a>
<a class="chip" href="{REDBUBBLE}" target="_blank" rel="noopener">Redbubble · <span lang="zh-Hant">貼紙與杯子等周邊</span></a>
</p>
<p class="note">Etsy sells the same PDF ebooks. Redbubble sells merch. Neither is the Gumroad checkout. <span lang="zh-Hant">Etsy 是同一套 PDF 電子書；Redbubble 是周邊。兩者都不是 Gumroad 結帳。</span></p>
</div></footer>
'''

def sticky_bar(href):
    label = bundle_label()
    return f'''<div class="sticky" id="sticky" aria-hidden="true"><a class="pill" href="{href}" tabindex="-1" aria-label="6-book set from US${min_bundle_price()}"><span lang="zh-Hant">{label}</span></a></div>
{STICKY_JS}'''

def finish(depth, sticky=""):
    return site_footer(depth) + sticky + UTM_JS + "</body>\n</html>\n"

def ld_script(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"

def bundle_products():
    out = []
    for x in BUNDLES:
        out.append({
            "@type": "Product",
            "name": f"Pip the Mole {x['label_en']} bundle · {x['zh']}",
            "description": f"{len(x['books'])} bilingual English + Traditional Chinese picture books (PDF) for ages 3–6.",
            "image": f"{SITE}/img/og-collage.jpg",
            "brand": {"@type": "Brand", "name": "Pip the Mole Books"},
            "offers": {"@type": "Offer", "price": x["price"], "priceCurrency": "USD",
                       "availability": "https://schema.org/InStock", "url": gum_url(x["url"])},
        })
    return out

def cover_img(b, prefix, eager=False):
    slug = b["slug"]
    loading = "eager" if eager else "lazy"
    return (f'<img src="{prefix}img/{slug}/cover-sm.webp" '
            f'srcset="{prefix}img/{slug}/cover-sm.webp 360w, {prefix}img/{slug}/cover.webp 600w" '
            f'sizes="(max-width:800px) 46vw, 320px" width="360" height="480" loading="{loading}" decoding="async" '
            f'alt="Cover of {E(b["en"])} / {E(b["zh"])}">')

def book_card(b, prefix, newest=None):
    sn = season_of(b)
    theme_en = b.get("tag_en") or b["theme_en"]
    theme_en = theme_en[:1].upper() + theme_en[1:]
    zh_n = ZH_NUM[b["n"] - 1]
    img = cover_img(b, prefix)
    eyebrow = f'Book {b["n"]} · <span lang="zh-Hant">第{zh_n}集</span>'
    if status_of(b) != "live":
        return f'''<article class="card soon s{sn}">
<div class="cover">{img}</div>
<div class="card-body">
<p class="eyebrow">{eyebrow}</p>
<h3 lang="zh-Hant">{E(b["zh"])}</h3>
<p class="en-name">{E(b["en"])}</p>
<p class="chip-theme"><span class="th" lang="zh-Hant">{E(b["theme_zh"])}</span><span class="en">{E(theme_en)}</span></p>
<div class="card-actions"><span class="soon-label">Coming soon · <span lang="zh-Hant">即將推出</span></span></div>
</div></article>'''
    tag = ' <span class="tag">New · <span lang="zh-Hant">新</span></span>' if newest is not None and b is newest else ""
    if b.get("sample"):
        sample = (f'<a class="btn-sample" href="{gum_slug(b["sample"])}" '
                  f'aria-label="Free sample of {E(b["en"])}"><span lang="zh-Hant">免費試讀</span><small>Free</small></a>')
    else:
        sample = '<span class="btn-sample" aria-disabled="true">Soon<small>Free sample</small></span>'
    buy = (f'<a class="btn-buy" href="{gum_slug(b["paid"])}" '
           f'aria-label="Buy {E(b["en"])}, US${price_of(b)}"><span>US${price_of(b)}</span><small lang="zh-Hant">購買</small></a>')
    return f'''<article class="card s{sn}">
<a class="cover" href="{prefix}{b["slug"]}/">{img}</a>
<div class="card-body">
<p class="eyebrow">{eyebrow}{tag}</p>
<h3><a href="{prefix}{b["slug"]}/" lang="zh-Hant">{E(b["zh"])}</a></h3>
<p class="en-name">{E(b["en"])}</p>
<p class="chip-theme"><span class="th" lang="zh-Hant">{E(b["theme_zh"])}</span><span class="en">{E(theme_en)}</span></p>
<div class="card-actions">{sample}{buy}</div>
</div></article>'''

def fan_links(nums, prefix):
    bits = []
    for n in nums:
        b = book_by_n(n)
        bits.append(
            f'<a href="{prefix}{b["slug"]}/"><img src="{prefix}img/{b["slug"]}/cover.webp" width="600" height="800" '
            f'alt="Cover of {E(b["en"])} / {E(b["zh"])}"></a>')
    return "".join(bits)

def entry_card(sn, prefix):
    meta = SEASON_META[sn]
    bs = books_in(sn)
    bund = bundle_for(sn)
    price = bund["price"] if bund else min_bundle_price()
    nums = (bund.get("fan") if bund else None) or [b["n"] for b in bs[:3]]
    thumbs = []
    for n in nums:
        b = book_by_n(n)
        thumbs.append(f'<img src="{prefix}img/{b["slug"]}/cover-sm.webp" alt="" width="120" height="160">')
    rng = f'{bs[0]["n"]}–{bs[-1]["n"]}'
    return f'''<a class="entry s{sn}" id="season-{sn}" href="{prefix}season-{sn}/">
<span class="band" aria-hidden="true"></span>
<span class="mini" aria-hidden="true">{"".join(thumbs)}</span>
<span class="body">
<span class="eyebrow">Season {sn} · Books {rng}</span>
<strong lang="zh-Hant">第{ZH_NUM[sn - 1]}輯</strong>
<span class="tone">{E(meta["tone_en"])}<span class="zh" lang="zh-Hant">{meta["tone_zh"]}</span></span>
<span class="go"><span lang="zh-Hant">6 本 · 套裝 US${price}</span><small>6 books · open this season</small></span>
</span></a>'''

def bundle_aside(x, prefix, cls="bcard"):
    each, n = sum(float(price_of(b)) for b in BOOKS if b["n"] in x["books"]), len(x["books"])
    nums = x.get("fan") or x["books"][:3]
    thumbs = []
    for num in nums:
        b = book_by_n(num)
        thumbs.append(f'<img src="{prefix}img/{b["slug"]}/cover-sm.webp" alt="" width="160" height="214">')
    sn = x["season"]
    r = f'{x["books"][0]}–{x["books"][-1]}'
    return f'''<article class="{cls} s{sn}">
<div class="pad">
<p class="eyebrow">{E(x["label_en"])} · <span lang="zh-Hant">{x["label_zh"]}</span></p>
<div class="thumbs" aria-hidden="true">{"".join(thumbs)}</div>
<h2>{E(x["zh"])}</h2>
<p class="en-name">{E(x["en"])}</p>
<p class="was">6 × US${PRICE} = US${each:.2f} · <span lang="zh-Hant">分開買 US${each:.2f}</span></p>
<p class="price-big">US${x["price"]}</p>
<p class="checkout-note">Pay what you want from US${x["price"]}. Checkout on Gumroad. <span lang="zh-Hant">由 US${x["price"]} 起，可自訂更高價錢。結帳在 Gumroad。</span></p>
<a class="pill" href="{gum_url(x["url"])}"><span lang="zh-Hant">購買套裝 US${x["price"]}</span><small>Get Books {r} · {n} PDFs</small></a>
<a class="textlink" href="{prefix}season-{sn}/">這一輯 · Season {sn} →</a>
</div></article>'''

def seq_link(b, prefix, direction):
    if not b:
        return '<span class="spacer"></span>'
    zh = f'← {E(b["zh"])}' if direction == "prev" else f'{E(b["zh"])} →'
    return (f'<a class="{direction}" href="{prefix}{b["slug"]}/" rel="{direction}">'
            f'<span lang="zh-Hant">{zh}</span><small>{E(b["en"])}</small></a>')

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
# Homepage keeps three decisions: download, age/order, Traditional Chinese. No /faq/ page.
FAQ_HOME = (FAQ[0], FAQ[4], FAQ[3])

def book_page(b):
    prefix = "../"
    sn = season_of(b)
    url = f"{SITE}/{b['slug']}/"
    img = f"{SITE}/img/{b['slug']}/og.jpg"
    title = f"{b['en']} {b['zh']} · Bilingual Chinese English Picture Book, Ages 3–6"
    desc = (f"Book {b['n']} of Pip the mole's stories: a bilingual English + Traditional Chinese children's picture book "
            f"(PDF) about {b['theme_en']}, for toddlers and preschoolers aged 3–6. {b['short_en']}"
            + (" Free sample available." if b.get("sample") else ""))
    kw = f"{b['en']}, {b['zh']}, {b['kw']}, " + BASE_KW
    seq = [x for x in books_in(sn) if status_of(x) == "live"]
    i = next(i for i, x in enumerate(seq) if x["n"] == b["n"])
    prev_b = seq[i - 1] if i else None
    next_b = seq[i + 1] if i + 1 < len(seq) else None
    extra = ""
    if prev_b:
        extra += f'<link rel="prev" href="{SITE}/{prev_b["slug"]}/">\n'
    if next_b:
        extra += f'<link rel="next" href="{SITE}/{next_b["slug"]}/">\n'
    pages = "\n".join(
        f'<img src="{prefix}img/{b["slug"]}/page-{n}.webp" width="720" height="960" loading="lazy" decoding="async" '
        f'alt="{E(b["en"])}, story page {n}: illustration with Traditional Chinese and English text">'
        for n in range(1, 5))
    if b.get("sample"):
        sample_top = f'<a class="pill sample" href="{gum_slug(b["sample"])}"><span lang="zh-Hant">免費試讀</span><small>Free sample</small></a>\n'
        sample_note = (f'<p class="note">The free sample has the cover and the first 5 story pages. Book {b["n"]} also reads fine on its own. '
                       f'<span lang="zh-Hant">免費試讀版包括封面和故事的頭 5 頁。</span></p>')
    else:
        sample_top = ""
        sample_note = f'<p class="note">Book {b["n"]} also reads fine on its own. <span lang="zh-Hant">每本都可以單獨閱讀。</span></p>'
    buy = f'<a class="pill" href="{gum_slug(b["paid"])}"><span lang="zh-Hant">購買 US${price_of(b)}</span><small>Buy the full book</small></a>'
    own = bundle_for(sn) if bundle_for(sn) and b["n"] in bundle_for(sn)["books"] else None
    if own:
        r = f'{own["books"][0]}–{own["books"][-1]}'
        upsell = (f'<p class="upsell s{sn}"><a href="{gum_url(own["url"])}">想要套裝？第 {r} 集 6 本 US${own["price"]} →</a>'
                  f'<span class="en">Get Books {r} · checkout on Gumroad</span>'
                  f'<a class="season-jump" href="{prefix}season-{sn}/">這一輯的六本書 · Season {sn}</a></p>')
    else:
        upsell = (f'<p class="upsell s1"><a href="{gum_url(BUNDLE)}">皮皮第 1–6 集套裝 US$9.99 →</a>'
                  f'<span class="en">Books 1–6 bundle · checkout on Gumroad</span></p>')
    rest = [o for o in seq if o is not b]
    rest_html = "\n".join(book_card(o, prefix) for o in rest)
    others = []
    for osn in all_seasons():
        if osn == sn:
            continue
        items = []
        for o in books_in(osn):
            if status_of(o) != "live":
                continue
            items.append(f'<li><a href="{prefix}{o["slug"]}/"><span lang="zh-Hant">{E(o["zh"])}</span> <span class="en">· {E(o["en"])}</span></a></li>')
        others.append(
            f'<div><h3><a href="{prefix}season-{osn}/">Season {osn} · <span lang="zh-Hant">第{ZH_NUM[osn - 1]}輯</span></a></h3>'
            f'<ul>{"".join(items)}</ul></div>')
    theme_en = b["theme_en"][:1].upper() + b["theme_en"][1:]
    zh_n = ZH_NUM[b["n"] - 1]
    css = ROOT_CSS + SHELL_CSS + BOOK_CSS
    header = site_header(1, f"book-{b['slug']}")
    s = head(title, desc, kw, url, img, "book", css=css, header=header, bodycls="book", extra_head=extra)
    s += f'''<main id="main"><div class="wrap book-wrap">
<p class="back"><a href="{prefix}#books">← <span lang="zh-Hant">全部繪本</span> · All books</a></p>
<div class="book">
<div class="cover"><img src="{prefix}img/{b['slug']}/cover.webp" width="600" height="800" alt="Cover of {E(b['en'])} / {E(b['zh'])}: Pip the mole and friends"></div>
<div class="book-intro">
<a class="badge s{sn}" href="{prefix}season-{sn}/">Book {b['n']} · Season {sn} · <span lang="zh-Hant">第{zh_n}集 · 第{ZH_NUM[sn - 1]}輯</span></a>
<h1 class="book-title"><span class="zh-title" lang="zh-Hant">{E(b['zh'])}</span><span class="en-title">{E(b['en'])}</span></h1>
<p class="theme-line"><span lang="zh-Hant">主題：{E(b['theme_zh'])}</span> · {E(theme_en)}</p>
</div>
<nav class="seq" aria-label="In this season">{seq_link(prev_b, prefix, "prev")}{seq_link(next_b, prefix, "next")}</nav>
<div class="book-buy">
<div class="cta">{sample_top}{buy}</div>
<p class="checkout-note">Checkout on Gumroad · <span lang="zh-Hant">結帳在 Gumroad</span></p>
{upsell}
<p class="lead">{E(b['sum_en'])}</p>
<p class="lead" lang="zh-Hant">{E(b['sum_zh'])}</p>
<dl class="facts">
<dt>Ages · <span lang="zh-Hant">年齡</span></dt><dd>3–6 · <span lang="zh-Hant">適合 3–6 歲</span></dd>
<dt>Language · <span lang="zh-Hant">語言</span></dt><dd>English + Traditional Chinese on every page · <span lang="zh-Hant">每頁中英對照（繁體中文）</span></dd>
<dt>Theme · <span lang="zh-Hant">主題</span></dt><dd>{E(theme_en)} · <span lang="zh-Hant">{E(b['theme_zh'])}</span></dd>
<dt>Format · <span lang="zh-Hant">格式</span></dt><dd>PDF ebook, 19 pages (cover, 16 story pages, a read-aloud refrain page, back cover); screen and print-ready 300 dpi versions · <span lang="zh-Hant">PDF 電子書，共 19 頁</span></dd>
<dt>Story · <span lang="zh-Hant">故事</span></dt><dd>PP O (Hong Kong); illustrations AI-generated · <span lang="zh-Hant">插圖由 AI 生成</span> · <a href="{prefix}about/">About · <span lang="zh-Hant">關於</span></a></dd>
</dl>
</div>
</div>
<h2>Look inside · <span lang="zh-Hant">內頁預覽</span></h2>
<div class="pages">{pages}</div>
{sample_note}
<div class="cta">{sample_top}{buy}</div>
<h2><span lang="zh-Hant">本季其餘</span> · Rest of Season {sn}</h2>
<div class="grid">{rest_html}</div>
<h2><span lang="zh-Hant">其他輯</span> · Other seasons</h2>
<div class="season-links">{"".join(others)}</div>
</div></main>
'''
    return s + finish(1)

def season_page(sn):
    meta = SEASON_META[sn]
    bs = books_in(sn)
    live = [b for b in bs if status_of(b) == "live"]
    bund = bundle_for(sn)
    prefix = "../"
    rng = f'{bs[0]["n"]}–{bs[-1]["n"]}'
    zh = f"第{ZH_NUM[sn - 1]}輯"
    title = f"Season {sn} · {zh} · Pip the Mole 皮皮繪本 · Books {rng}"
    desc = (f"Season {sn} of Pip the Mole: books {rng}, bilingual English and Traditional Chinese picture books for ages 3–6. "
            f"{meta['story_en']} {meta['story_zh']}")
    og_b = live[0]
    img = f"{SITE}/img/{og_b['slug']}/og.jpg"
    url = f"{SITE}/season-{sn}/"
    nums = (bund.get("fan") if bund else None) or [b["n"] for b in bs[:3]]
    newest = live_books()[-1]
    cards = "\n".join(book_card(b, prefix, newest) for b in bs)
    cta = ""
    repeat = ""
    if bund:
        cta = (f'<div class="hero-actions"><a class="pill" id="hero-cta" href="{gum_url(bund["url"])}">'
               f'<span lang="zh-Hant">{bundle_label()}</span><small>Season {sn} · Books {rng}</small></a>'
               f'<a class="textlink" href="#books"><span lang="zh-Hant">單本亦售</span> · Singles US${PRICE}</a></div>'
               f'<p class="checkout-note">Checkout on Gumroad · <span lang="zh-Hant">結帳在 Gumroad</span></p>')
        each = sum(float(price_of(b)) for b in BOOKS if b["n"] in bund["books"])
        repeat = (f'<section class="bundle-repeat s{sn}" id="bundle"><p class="eyebrow">{E(bund["label_en"])} · <span lang="zh-Hant">{bund["label_zh"]}</span></p>'
                  f'<p class="price-big">US${bund["price"]}</p>'
                  f'<p class="was">6 × US${PRICE} = US${each:.2f} · <span lang="zh-Hant">分開買 US${each:.2f}</span></p>'
                  f'<p class="checkout-note">Pay what you want from US${bund["price"]}. <span lang="zh-Hant">由 US${bund["price"]} 起，可自訂更高價錢。</span></p>'
                  f'<a class="pill" href="{gum_url(bund["url"])}"><span lang="zh-Hant">購買這輯套裝</span><small>Get Books {rng} on Gumroad</small></a></section>')
    others = "\n".join(entry_card(s, prefix) for s in all_seasons() if s != sn)
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "ItemList", "name": f"Pip the Mole Season {sn}",
             "itemListElement": [{"@type": "ListItem", "position": b["n"], "url": f"{SITE}/{b['slug']}/", "name": b["en"]} for b in live]},
            *([bundle_products()[BUNDLES.index(bund)]] if bund else []),
        ],
    }
    css = ROOT_CSS + SHELL_CSS + PAGE_CSS
    header = site_header(1, f"season-{sn}")
    sticky = sticky_bar(gum_url(bund["url"]) if bund else f"{prefix}shop/")
    s = head(title, desc, BASE_KW, url, img, css=css, header=header, bodycls="season has-sticky",
             extra_head=ld_script(graph))
    s += f'''<main id="main"><div class="wrap">
<p class="kicker"><a href="{prefix}">← Pip the Mole · <span lang="zh-Hant">皮皮繪本</span></a></p>
<section class="season-top s{sn}">
<div class="season-copy">
<p class="eyebrow">Season {sn} · Books {rng} · Ages 3–6</p>
<h1><span lang="zh-Hant">{zh}</span><span class="en">Season {sn}</span></h1>
<p class="story">{E(meta["story_en"])}<span class="zh" lang="zh-Hant">{meta["story_zh"]}</span></p>
<p class="meta">Ages 3–6 · <span lang="zh-Hant">適合 3–6 歲 · 可以不按順序讀</span> · EN + 繁中 · PDF</p>
{cta}
</div>
<div class="hero-fan" aria-label="Covers">{fan_links(nums, prefix)}</div>
</section>
<section class="section" id="books">
<h2 class="shelf-label">六本書 · Six books</h2>
<div class="grid mt16">{cards}</div>
</section>
{repeat}
<section class="section">
<h2><span lang="zh-Hant">其他輯</span> · Other seasons</h2>
<div class="entries mt14">{others}</div>
<p class="bundle-jump mt16"><a href="{prefix}shop/">商店 · 單本和三套一起看 · Shop, singles and all three sets →</a></p>
</section>
</div></main>
'''
    return s + finish(1, sticky)

def shop_page():
    prefix = "../"
    title = "Shop · 商店 · Pip the Mole 皮皮繪本 · Singles and 6-book sets"
    desc = ("Singles are US$4.99. Each 6-book set is pay-what-you-want from US$9.99. "
            "Checkout is on Gumroad. Free sample of every book. "
            "單本 US$4.99，六本套裝由 US$9.99 起。結帳在 Gumroad。每本都有免費試讀。")
    url = f"{SITE}/shop/"
    img = f"{SITE}/img/og-collage.jpg"
    newest = live_books()[-1]
    bundles = "\n".join(bundle_aside(x, prefix) for x in BUNDLES)
    # Mark the first bundle pill as the above-fold CTA the sticky bar watches.
    bundles = bundles.replace('class="pill"', 'class="pill" id="hero-cta"', 1)
    blocks = []
    for sn in all_seasons():
        bs = books_in(sn)
        cards = "\n".join(book_card(b, prefix, newest) for b in bs)
        rng = f'{bs[0]["n"]}–{bs[-1]["n"]}'
        blocks.append(f'''<div class="season-block">
<div class="shelf-head s{sn}"><div><h3>Season {sn} · <span lang="zh-Hant">第{ZH_NUM[sn - 1]}輯</span></h3>
<p class="range">Books {rng}</p></div>
<a class="shelf-link" href="{prefix}season-{sn}/"><span lang="zh-Hant">看這一輯</span><small>Season page</small></a></div>
<div class="grid">{cards}</div></div>''')
    graph = {"@context": "https://schema.org", "@graph": [
        *bundle_products(),
        {"@type": "ItemList", "name": "Pip the Mole picture books",
         "itemListElement": [{"@type": "ListItem", "position": b["n"], "url": f"{SITE}/{b['slug']}/", "name": b["en"]}
                             for b in live_books()]},
    ]}
    css = ROOT_CSS + SHELL_CSS + PAGE_CSS
    header = site_header(1, "shop")
    s = head(title, desc, BASE_KW, url, img, css=css, header=header, bodycls="shop has-sticky",
             extra_head=ld_script(graph))
    s += f'''<main id="main"><div class="wrap">
<h1 class="page-h1"><span lang="zh-Hant">商店</span><span class="en">Shop</span></h1>
<p class="lede">Singles are US${PRICE}. A 6-book set starts at US${min_bundle_price()}. <span lang="zh-Hant">單本 US${PRICE}。六本套裝由 US${min_bundle_price()} 起。</span></p>
<p class="lede">Checkout on Gumroad. <span lang="zh-Hant">結帳在 Gumroad。這頁的橙色按鈕都會去 Gumroad。</span></p>
<section class="section" id="bundles">
<h2>三套六本 · Three 6-book sets</h2>
<div class="bundle-grid">{bundles}</div>
</section>
<section class="section" id="samples">
<h2><span lang="zh-Hant">單本</span> · Singles</h2>
<p class="lede" id="free">Every book has a free sample. <span lang="zh-Hant">每本都有免費試讀。</span> The outline button is the sample; the orange button buys that one book on Gumroad.</p>
{"".join(blocks)}
</section>
<section class="quiet" id="other">
<h2>其他店／周邊 · Other shops</h2>
<p class="lede">These are not the Gumroad checkout. Etsy sells the same PDF ebooks. Redbubble sells stickers, mugs and other merch. <span lang="zh-Hant">這裡不是 Gumroad 結帳。Etsy 是同一套 PDF；Redbubble 是貼紙、杯子等周邊。</span></p>
<p class="chips">
<a class="chip" href="{ETSY}" target="_blank" rel="noopener">Etsy · <span lang="zh-Hant">同一套 PDF</span></a>
<a class="chip" href="{REDBUBBLE}" target="_blank" rel="noopener">Redbubble · <span lang="zh-Hant">周邊</span></a>
</p>
</section>
</div></main>
'''
    return s + finish(1, sticky_bar("#bundles"))

def about_page():
    prefix = "../"
    title = "About Pip the Mole · 關於皮皮繪本 · PP O"
    desc = ("Pip the Mole picture books are written by PP O in Hong Kong. Illustrations are AI-generated. "
            "Bilingual English and Traditional Chinese, ages 3–6. "
            "故事由香港的 PP O 創作，插圖由 AI 生成，適合 3–6 歲。")
    url = f"{SITE}/about/"
    img = f"{SITE}/img/og-collage.jpg"
    css = ROOT_CSS + SHELL_CSS + PAGE_CSS
    header = site_header(1, "about")
    graph = {"@context": "https://schema.org", "@type": "AboutPage",
             "name": "About Pip the Mole 關於皮皮繪本", "url": url,
             "description": desc, "isPartOf": SITE + "/"}
    s = head(title, desc, BASE_KW, url, img, css=css, header=header, bodycls="about", extra_head=ld_script(graph))
    s += f'''<main id="main"><div class="wrap prose">
<p class="kicker"><a href="{prefix}">← Pip the Mole · <span lang="zh-Hant">皮皮繪本</span></a></p>
<h1 class="page-h1"><span lang="zh-Hant">關於皮皮</span><span class="en">About Pip</span></h1>
<h2><span lang="zh-Hant">誰在寫這些故事</span> · Who writes them</h2>
<p>Pip the Mole stories are written by PP O in Hong Kong. Pip is a little mole. Robin and Rabbit are with him from the first book. Pom the hedgehog arrives with the first snow, and Season 3 follows a steady light to Old Badger's door.</p>
<p class="zh" lang="zh-Hant">皮皮繪本的故事，由香港的 PP O 創作。皮皮是一隻小鼴鼠。知更鳥和兔子從第一本就在他身邊。第一場雪帶來刺蝟寶寶蓬蓬。第三輯跟著一點不閃的光，走到河谷裡獾婆婆的門前。</p>
<h2><span lang="zh-Hant">怎樣讀</span> · How to read them</h2>
<p>They are bedtime picture books for ages 3–6. Every page has English and Traditional Chinese. The lines are short and calm, and each book holds one small idea: teamwork, sharing, saying sorry, trying again, and others like them. You can start anywhere. The seasons follow the same friends, and each book still reads on its own.</p>
<p class="zh" lang="zh-Hant">適合 3–6 歲的睡前繪本。每一頁都有英文和繁體中文。句子短、語氣平靜，每本只放一個小道理，例如一起合作、分享、說對不起、再試一次。可以從任何一本開始。故事跟著同一班朋友走過四季，但每本都可以單獨讀。</p>
<h2><span lang="zh-Hant">插圖</span> · The pictures</h2>
<p>The illustrations are AI-generated. PP O writes the stories and the words, and chooses the order of the books. We say this plainly so families know how the pictures were made.</p>
<p class="zh" lang="zh-Hant">插圖由 AI 生成。故事和文字由 PP O 編寫，書的次序也由 PP O 決定。我們直說，是想讓家長知道圖畫是怎樣做成的。</p>
<h2><span lang="zh-Hant">檔案和年齡</span> · Files and age</h2>
<p>Each book is a 19-page PDF: a cover, 16 story pages, a read-aloud page, and a back cover. You get a screen file and a print-ready 300 dpi file. Gumroad handles checkout and sends the download. The books are for ages 3–6, read aloud or alongside an early reader.</p>
<p class="zh" lang="zh-Hant">每本是 19 頁 PDF：封面、16 頁故事、一頁可以跟著唸的句子，和封底。內有螢幕版和 300 dpi 印刷版。結帳和下載由 Gumroad 處理。適合 3–6 歲，可以睡前唸，也可以陪剛開始認字的孩子一起看。</p>
<h2>Contact · <span lang="zh-Hant">聯絡</span></h2>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p class="zh" lang="zh-Hant">問題和印刷方面的查詢，請寫信到上面的電郵。</p>
<p class="about-links"><a href="{prefix}shop/">Shop · <span lang="zh-Hant">商店</span></a><a href="{prefix}#books">Books · <span lang="zh-Hant">繪本</span></a><a href="{prefix}#faq">FAQ · <span lang="zh-Hant">常見問題</span></a></p>
</div></main>
'''
    return s + finish(1)

def index_page():
    sn = featured_season()
    bs = books_in(sn)
    live = live_books()
    newest = live[-1]
    bund = bundle_for(sn)
    meta = SEASON_META[sn]
    n_live = len(live)
    price = min_bundle_price()
    label = bundle_label()
    title = "Pip the Mole 皮皮繪本 · Bilingual Chinese English Picture Books, Ages 3–6"
    desc = (f"{n_live} bilingual picture books for ages 3–6, English and Traditional Chinese on every page. "
            f"Read a free sample, or get a 6-book set from US${price}. "
            f"中英對照繪本 {n_live} 本，每本可免費試讀，六本套裝由 US${price} 起。")
    ogtitle = f"Pip the Mole 皮皮繪本 · {n_live} bilingual picture books for ages 3–6 · 6-book sets from US${price}"
    nums = (bund.get("fan") if bund else None) or [b["n"] for b in bs[:3]]
    mid = book_by_n(nums[min(1, len(nums) - 1)])
    extra = f'<link rel="preload" as="image" href="img/{mid["slug"]}/cover.webp">\n'
    cards = "\n".join(book_card(b, "", newest) for b in bs)
    entries = "\n".join(entry_card(s, "") for s in all_seasons())
    chips = []
    for s in all_seasons():
        chips.append(f'<a class="s{s}" href="season-{s}/"><span lang="zh-Hant">第{ZH_NUM[s - 1]}輯</span><small>Season {s}</small></a>')
    rng = f'{bs[0]["n"]}–{bs[-1]["n"]}'
    gum = gum_url(bund["url"]) if bund else "shop/"
    faq = "\n".join(
        f'<details class="qa"{ " open" if i == 0 else ""}><summary><span class="q">{E(q)}</span>'
        f'<span class="zh" lang="zh-Hant">{qz}</span></summary>'
        f'<div class="a"><p>{E(a)}</p><p class="zh" lang="zh-Hant">{az}</p></div></details>'
        for i, (q, qz, a, az) in enumerate(FAQ_HOME))
    why = (
        '<ul class="why-pills">'
        '<li><span lang="zh-Hant">同頁中英對照</span><span class="en">Two languages, one page</span></li>'
        '<li><span lang="zh-Hant">短而平靜</span><span class="en">Short and calm</span></li>'
        '<li><span lang="zh-Hant">一個小道理</span><span class="en">One small lesson</span></li>'
        '</ul>')
    graph = {"@context": "https://schema.org", "@graph": [
        *bundle_products(),
        {"@type": "ItemList", "name": f"Pip the Mole Season {sn}",
         "itemListElement": [{"@type": "ListItem", "position": b["n"], "url": f"{SITE}/{b['slug']}/", "name": b["en"]} for b in bs if status_of(b) == "live"]},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, qz, a, az in FAQ_HOME]},
    ]}
    css = ROOT_CSS + SHELL_CSS + HOME_CSS
    header = site_header(0, "home")
    s = head(title, desc, BASE_KW, f"{SITE}/", f"{SITE}/img/og-collage.jpg", ogtitle=ogtitle,
             css=css, header=header, bodycls="home has-sticky", extra_head=extra + ld_script(graph))
    s += f'''<main id="main">
<div class="wrap">
<section class="hero">
<div class="hero-grid">
<div class="hero-copy">
<h1><span class="zh-hero" lang="zh-Hant">溫柔睡前故事</span><span class="en-hero">Gentle bedtime stories</span></h1>
<p class="meta">Ages 3–6 · EN + 繁中 · 16 頁 · PDF</p>
<div class="hero-actions">
<a class="pill" id="hero-cta" href="shop/"><span lang="zh-Hant">{label}</span><small>6-book set · compare in the shop</small></a>
<a class="textlink" id="free" href="shop/#samples"><span lang="zh-Hant">免費試讀</span> · Free sample →</a>
</div>
</div>
<div class="hero-fan">{fan_links(nums, "")}</div>
{why}
</div>
<nav class="season-chips" aria-label="Seasons">{"".join(chips)}</nav>
</section>
<section class="section" id="books">
<div class="shelf-head s{sn}">
<div>
<h2><a href="season-{sn}/">Season {sn} · <span lang="zh-Hant">第{ZH_NUM[sn - 1]}輯</span></a></h2>
<p class="range">Books {rng} · <span lang="zh-Hant">{meta["tone_zh"]}</span> {E(meta["tone_en"])}</p>
</div>
<a class="shelf-link" href="{gum}"><span lang="zh-Hant">呢輯套裝 US${bund["price"] if bund else price}</span> →<small>This set on Gumroad</small></a>
</div>
<div class="grid">{cards}</div>
<p class="shelf-note"><span lang="zh-Hant">每本都有免費試讀。橙色按鈕在 Gumroad 結帳。</span><span class="en">Every book has a free sample. Orange buttons check out on Gumroad.</span></p>
<p class="bundle-jump" id="bundles"><a href="shop/"><span lang="zh-Hant">三套六本套裝，在商店比價</span> · Compare all three sets →</a></p>
</section>
<section class="section" id="seasons">
<h2><span lang="zh-Hant">三輯入口</span> · Three seasons</h2>
<p class="lede">Season {sn} is on this page. The other seasons have their own pages. <span lang="zh-Hant">這一頁是第{ZH_NUM[sn - 1]}輯。另外兩輯有自己的系列頁。</span></p>
<div class="entries mt14">{entries}</div>
</section>
<section class="section" id="faq">
<h2>Questions · <span lang="zh-Hant">常見問題</span></h2>
<div class="faq">{faq}</div>
<p class="faq-more"><a href="about/"><span lang="zh-Hant">年齡、語言和創作說明</span> · Ages, language, and how the books are made</a></p>
</section>
</div>
</main>
'''
    return s + finish(0, sticky_bar("shop/"))

def make_og_collage():
    from PIL import ImageDraw, ImageFont
    out = ROOT / "img" / "og-collage.jpg"
    if out.exists() and not os.environ.get("REIMG"):
        return
    bg = Image.new("RGB", (1200, 630), (251, 246, 236))
    w, h = 96, 128   # up to 18 covers, 6 × 3 grid
    for i, b in enumerate(live_books()[:18]):
        c = Image.open(ROOT / "img" / b["slug"] / "cover.webp").convert("RGB").resize((w, h), Image.LANCZOS)
        bg.paste(c, (30 + (i % 6) * (w + 12), 105 + (i // 6) * (h + 12)))
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

def main():
    for b in live_books():
        if not (ROOT / "img" / b["slug"] / "page-4.webp").exists() or os.environ.get("REIMG"):
            make_images(b)
        d = ROOT / b["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(book_page(b), encoding="utf-8")
    make_home_images()
    make_og_collage()
    (ROOT / "index.html").write_text(index_page(), encoding="utf-8")
    for sn in all_seasons():
        d = ROOT / f"season-{sn}"
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(season_page(sn), encoding="utf-8")
    shop = ROOT / "shop"
    shop.mkdir(exist_ok=True)
    (shop / "index.html").write_text(shop_page(), encoding="utf-8")
    about = ROOT / "about"
    about.mkdir(exist_ok=True)
    (about / "index.html").write_text(about_page(), encoding="utf-8")
    day = date.today().isoformat()
    urls = [f"{SITE}/"]
    urls += [f"{SITE}/season-{sn}/" for sn in all_seasons()]
    urls += [f"{SITE}/shop/", f"{SITE}/about/"]
    urls += [f"{SITE}/{b['slug']}/" for b in sorted(live_books(), key=lambda x: -x["n"])]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{day}</lastmod></url>\n" for u in urls)
        + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "ads.txt").write_text(ADS_TXT, encoding="utf-8")
    (ROOT / ".nojekyll").write_text("")
    json.dump([{**{k: b.get(k, "") for k in ("n", "slug", "en", "zh", "paid", "sample")}, "season": season_of(b), "status": status_of(b),
                "theme_en": b["theme_en"], "theme_zh": b["theme_zh"], "price": price_of(b)} for b in live_books()],
              open(ROOT / "books.json", "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
