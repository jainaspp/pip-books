# Pip the Mole Books · 皮皮繪本

Static site for the bilingual (English + Traditional Chinese) Pip picture books, ages 3–6.
Live: https://jainaspp.github.io/pip-books/

- `build.py` regenerates all HTML, `sitemap.xml`, `robots.txt` and the downscaled images (from the book page PNGs on the build box).
- Homepage content is data-driven: the `BOOKS` list (n, season, status live|soon, slug, paid/sample Gumroad slugs, titles, theme) and the `BUNDLES` list at the top of `build.py`. Adding a book or a bundle is a data-only change; a Season 2 heading appears once a season-2 book is listed.
- Pending per-book patches in `/workspace/pip-promo/bookN/` (made before the redesign): apply only their `build.py` and `img/` parts, then rebuild, e.g. `git apply --include=build.py --include='img/*' /workspace/pip-promo/book7/pip-books-book7.patch && python3 build.py`.
- `check_simplified.py` fails if any simplified Chinese character appears in the pages.
- One small inline script forwards incoming utm_* parameters to the Gumroad buttons (default ?utm_source=pipsite). No ads, no trackers.

Stories by PP O (Hong Kong). Illustrations are AI-generated. Contact: jainaspp@gmail.com
