#!/usr/bin/env python3
"""Фото шести новых богов партии I: en.wikipedia pageimage или поиск Commons.
Скрипт сам подставляет <figure> и подпись с лицензией в каждую страницу."""
import json, os, re, urllib.parse, urllib.request, html as H, time

EG = '/home/user/Projects/egypt'
UA = {'User-Agent': 'Kemet-site/1.0 (contact: olegvnovikov75@github.com)'}

def api(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if i < tries - 1 and any(s in str(e) for s in ('429', 'timed out', 'Timeout', 'reset', 'urlopen', 'SSL')):
                time.sleep(6 * (i + 1)); continue
            raise

def strip_tags(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

BAN = ('map', 'plan', 'diagram', 'drawing', 'illustration', 'engraving', 'woodcut',
       'etching', 'coat', 'logo', 'model', 'sketch')

GODS = [
    ('khonsu',  'Khonsu',       'Khonsu relief Karnak temple'),
    ('bes',     'Bes (deity)',  'Bes Egyptian Museum figurine'),
    ('taweret', 'Taweret',      'Taweret hippopotamus faience'),
    ('hapi',    'Hapi (deity)', 'Hapi Nile god statue'),
    ('wadjet',  'Wadjet',       'Wadjet cobra uraeus gold'),
    ('nekhbet', 'Nekhbet',      'Nekhbet vulture relief'),
]

for key, wtitle, csrch in GODS:
    fname = None
    d = api('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&piprop=name&titles=' + urllib.parse.quote(wtitle))
    for p in d.get('query', {}).get('pages', {}).values():
        t = p.get('thumbnail', {}).get('title') or p.get('original', {}).get('title') or ''
        if t and not any(b in t.lower() for b in BAN):
            fname = t[5:] if t.startswith('File:') else t
            break
    if not fname:
        d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srlimit=12&srsearch=' + urllib.parse.quote(csrch))
        for r in d.get('query', {}).get('search', []):
            t = r.get('title', '')
            tl = t.lower()
            if not tl.endswith(('.jpg', '.jpeg')) or any(b in tl for b in BAN):
                continue
            fname = t[5:] if t.startswith('File:') else t
            break
    if not fname:
        print('НЕТ фото:', key); continue
    d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=850&iiextmetadatafilter=Artist|LicenseShortName|UsageTerms&titles=' + urllib.parse.quote('File:' + fname))
    url = lic = artist = page = ''
    for p in d.get('query', {}).get('pages', {}).values():
        ii = (p.get('imageinfo') or [{}])[0]
        url = ii.get('thumburl') or ii.get('url') or ''
        em = ii.get('extmetadata', {})
        lic = strip_tags(em.get('LicenseShortName', {}).get('value', '')) or 'Public domain'
        artist = strip_tags(em.get('Artist', {}).get('value', ''))[:80] or 'неизвестный автор'
        page = 'https://commons.wikimedia.org/wiki/File:' + fname.replace(' ', '_')
    if not url:
        print('НЕТ ССЫЛКИ:', key); continue
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
    if len(data) < 15000:
        print('МЕЛКО, пропускаю:', key, len(data)); continue
    dst = os.path.join(EG, 'img', 'gods-%s.jpg' % key)
    open(dst, 'wb').write(data)
    p = os.path.join(EG, 'gods', '%s.html' % key)
    h = open(p, encoding='utf-8').read()
    fig = ('<figure class="hero-photo">\n'
           '    <img src="../img/gods-%s.jpg" alt="%s" loading="lazy" decoding="async">\n'
           '    <figcaption>%s Фото: <a href="%s">%s</a> · Wikimedia Commons · %s</figcaption>\n'
           '  </figure>' % (key, wtitle, fname.replace('_', ' '), page, artist, lic))
    if re.search(r'\n  <figure class="hero-photo">.*?</figure>\n', h, re.S):
        h = re.sub(r'\n  <figure class="hero-photo">.*?</figure>\n', '\n  ' + fig + '\n', h, count=1, flags=re.S)
    else:
        h = h.replace('</header>\n\n', '</header>\n\n  ' + fig + '\n\n', 1)
    open(p, 'w', encoding='utf-8').write(h)
    print('OK %s: %s | %s | %s | %d Б' % (key, fname[:40], lic, artist[:30], len(data)))
print('ГОТОВО фото партии I')
