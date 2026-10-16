# Pip the Mole Books · 皮皮繪本

Static site for the bilingual (English + Traditional Chinese) Pip picture books, ages 3–6.
Live: https://jainaspp.github.io/pip-books/

- `build.py` regenerates all HTML, `sitemap.xml`, `robots.txt`, `ads.txt` and the downscaled images (from the book page PNGs on the build box).
- Pages: `/` (Mood C homepage: latest season’s six books, three season entry cards, three FAQs at `#faq`), `/season-1/` `/season-2/` `/season-3/`, `/shop/`, `/about/`, and one folder per book. There is no `/faq/` or `/books/` page. Nav Books points at `/#books`.
- Content is data-driven: the `BOOKS` list (n, season, status live|soon, slug, paid/sample Gumroad slugs, titles, theme) and the `BUNDLES` list at the top of `build.py`. Adding a book or a bundle is a data-only change. The homepage shelf follows the latest live season.
- Pending per-book patches in `/workspace/pip-promo/bookN/` (made before the redesign): apply only their `build.py` and `img/` parts, then rebuild, e.g. `git apply --include=build.py --include='img/*' /workspace/pip-promo/book7/pip-books-book7.patch && python3 build.py`.
- `check_simplified.py` fails if any simplified Chinese character appears in the pages.
- One small inline script forwards incoming utm_* parameters to the Gumroad buttons (default ?utm_source=pipsite). Google AdSense Auto ads load once from `adsbygoogle.js` in each page `<head>` (publisher `ca-pub-8392975944327076`); there are no manual ad units.

Stories by PP O (Hong Kong). Illustrations are AI-generated. Contact: jainaspp@gmail.com
