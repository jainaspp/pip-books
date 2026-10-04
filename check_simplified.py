#!/usr/bin/env python3
"""Flag any CJK character that OpenCC's simplified->traditional converter would change (i.e. a simplified form)."""
import sys, re, glob
import opencc
s2t = opencc.OpenCC('s2t')
# Characters that are already correct Traditional but that the one-char s2t lookup rewrites (ambiguous mappings):
# 栗 (栗子 chestnut, Book 18) -> 慄 (shiver).
ALLOW = {'栗'}
bad = 0; total = 0
files = sys.argv[1:] or glob.glob('**/*.html', recursive=True) + ['sitemap.xml']
for f in files:
    txt = open(f, encoding='utf-8').read()
    for ln, line in enumerate(txt.splitlines(), 1):
        for ch in re.findall(r'[\u3400-\u9fff\uf900-\ufaff]', line):
            total += 1
            if ch in ALLOW:
                continue
            t = s2t.convert(ch)
            if t != ch:
                bad += 1; print(f"{f}:{ln}: '{ch}' -> '{t}'")
print(f"checked {total} CJK chars in {len(files)} files; simplified-looking: {bad}")
sys.exit(1 if bad else 0)
