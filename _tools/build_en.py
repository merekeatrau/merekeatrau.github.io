#!/usr/bin/env python3
"""Build the English version of the site into en/ from the Russian pages in the root.

Russian pages are the source of truth. Run after any change to them:
    python3 _tools/build_en.py
Translations live in _tools/translations.json as {"ru": ..., "en": ...} pairs;
a new Russian text needs a new pair, otherwise the script reports it as untranslated.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://merekeatrau.github.io/'
CYR = re.compile('[А-Яа-яЁё]')
# Yandex mark in the header: «Я» on Russian pages, «Y» (logo_en.svg) on English ones
LOGO_RU = 'M148.321 208.13H175.481V52.1299H135.975C96.246 52.1299 75.3712 72.5558 75.3712 102.633C75.3712 126.651 86.8186 140.792 107.245 155.382L71.7798 208.13H101.184L140.689 149.097L126.997 139.894C110.387 128.671 102.306 119.917 102.306 101.062C102.306 84.4522 113.978 73.2292 136.2 73.2292H148.321V208.13Z'
LOGO_EN = 'M133.526 143.43C141.123 160.071 143.655 165.858 143.655 185.844V212.342H116.525V167.667L65.3386 56.3418H93.6446L133.526 143.43ZM166.987 56.3418L133.798 131.764H161.38L194.66 56.3418H166.987Z'

os.chdir(ROOT)
pairs = json.load(open('_tools/translations.json', encoding='utf-8'))
pairs.sort(key=lambda p: -len(p['ru']))  # whole blocks before the fragments inside them
os.makedirs('en', exist_ok=True)


def visible_cyrillic(html):
    """Russian text a visitor could still see (scripts, styles and Cargo data excluded)."""
    body = html[html.find('<body'):]
    body = re.sub(r'<script\b[^>]*>.*?</script>', '', body, flags=re.S)
    body = re.sub(r'<style\b[^>]*>.*?</style>', '', body, flags=re.S)
    left = [t.strip() for t in re.findall(r'>([^<>]+)<', body) if CYR.search(t)]
    left += [a for a in re.findall(r'(?:content|title|aria-label|alt)="([^"]*)"', html) if CYR.search(a)]
    for js in re.findall(r'<script>(.*?)</script>', html, flags=re.S):
        left += [q for q in re.findall(r"'([^'\n]*)'", js) if CYR.search(q)]
    return left


problems = 0
for page in sorted(glob.glob('*.html')):
    s = open(page, encoding='utf-8').read()
    for p in pairs:
        ru, en = p['ru'], p['en']
        if len(ru) > 40 or '<' in ru:
            s = s.replace(ru, en)
        else:
            # short strings only as a whole text node or attribute value, never inside a longer word
            for a, z in (('>', '<'), ('"', '"'), ("'", "'")):
                s = s.replace(a + ru + z, a + en + z)

    # assets live one level up
    s = s.replace('"assets/', '"../assets/').replace("'assets/", "'../assets/").replace('url(assets/', 'url(../assets/')

    # language, share links and previews
    s = s.replace('<html lang="ru"', '<html lang="en"', 1)
    s = s.replace('<meta property="og:locale" content="ru_RU">', '<meta property="og:locale" content="en_US">')
    slug = '' if page == 'index.html' else page[:-5]  # pages are linked without .html
    ru_url = SITE + slug
    en_url = SITE + 'en/' + slug
    s = s.replace(f'<meta property="og:url" content="{ru_url}">', f'<meta property="og:url" content="{en_url}">')
    s = s.replace(SITE + 'assets/og/', SITE + 'assets/og/en/')

    # footer switch: EN is current, RU links back to the same page
    s = s.replace(
        f'<small class="ph-lang"><a href="en/{slug}" hreflang="en" lang="en">EN</a><span aria-current="true">RU</span></small>',
        f'<small class="ph-lang"><span aria-current="true">EN</span><a href="../{slug}" hreflang="ru" lang="ru">RU</a></small>')

    # header logo: the Latin «Y» instead of «Я», same one-colour treatment
    s = s.replace(f'<path d="{LOGO_RU}" fill="#fff"/>', f'<path d="{LOGO_EN}" fill="#fff"/>')

    left = visible_cyrillic(s)
    if left:
        problems += len(left)
        print(f'{page}: untranslated', left[:5])
    open(os.path.join('en', page), 'w', encoding='utf-8').write(s)

print(f'built {len(glob.glob("*.html"))} pages into en/' + (f', {problems} untranslated strings' if problems else ''))
sys.exit(1 if problems else 0)
