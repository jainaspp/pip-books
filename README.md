# Pip the Mole Books · 皮皮繪本

Static site for the bilingual (English + Traditional Chinese) Pip picture books, ages 3–6.
Live: https://jainaspp.github.io/pip-books/

- `build.py` regenerates all HTML, `sitemap.xml`, `robots.txt` and the downscaled images (from the book page PNGs on the build box).
- `check_simplified.py` fails if any simplified Chinese character appears in the pages.
- One small inline script forwards incoming utm_* parameters to the Gumroad buttons (default ?utm_source=pipsite). No ads, no trackers.

Stories by PP O (Hong Kong). Illustrations are AI-generated. Contact: jainaspp@gmail.com
