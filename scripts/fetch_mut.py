#!/usr/bin/env python3
"""Фото Мут: лид-картинка en.wikipedia 'Mut (goddess)' или поиск Commons. Нужное в имени — 'mut'."""
import json, re, time, urllib.parse, urllib.request, html as H

UA = {'User-Agent': 'Kemet-site/1.0 (contact: olegvnovikov75@github.com)'}

def api(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if i < tries - 1 and ('429' in str(e) or 'timed out' in str(e) or 'Timeout' in str(e) or 'reset' in str(e).lower() or 'urlopen' in str(e) or 'SSL' in str(e)):
                time.sleep(6 * (i + 1)); continue
            raise

def strip_tags(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

BAN = ('map', 'plan', 'diagram', 'drawing', 'illustration', 'engraving', 'woodcut',
       'etching', 'coat', 'logo', 'model', 'sketch', 'god_')
cand = None
d = api('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&piprop=name&titles=' + urllib.parse.quote('Mut (goddess)'))
for p in d['query']['pages'].values():
    t = p.get('thumbnail', {}).get('title') or p.get('original', {}).get('title') or ''
    if t and 'mut' in t.lower() and not any(b in t.lower() for b in BAN):
        cand = t; break
if not cand:
    d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srlimit=10&srsearch=' + urllib.parse.quote('Mut goddess statue Karnak British Museum'))
    for r in d['query']['search']:
        t = r['title']; tl = t.lower()
        if not tl.endswith(('.jpg', '.jpeg')): continue
        if 'mut' not in tl or any(b in tl for b in BAN): continue
        cand = t; break
assert cand, 'фото Мут не найдено'
fname = cand[5:] if cand.startswith('File:') else cand
d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=850&iiextmetadatafilter=Artist|LicenseShortName&titles=' + urllib.parse.quote('File:' + fname))
for p in d['query']['pages'].values():
    ii = p.get('imageinfo')
    if not ii: continue
    i = ii[0]; em = i.get('extmetadata', {})
    artist = strip_tags(em.get('Artist', {}).get('value', '')) or 'неизвестный автор'
    lic = strip_tags(em.get('LicenseShortName', {}).get('value', '')) or 'свободная лицензия'
    esc = lambda s: (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    url = i.get('thumburl') or i.get('url')
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r, open('/home/user/Projects/egypt/img/gods-mut.jpg', 'wb') as f:
                f.write(r.read())
            break
        except Exception:
            if a == 3: raise
            time.sleep(8)
    cap = 'Мут в двойной короне Верхнего и Нижнего Египта — так её высекали в Карнаке: владычица обеих земель и мать царя.'
    page = i.get('descriptionurl', '')
    fig = ('<figure class="hero-photo">\n<img src="../img/gods-mut.jpg" alt="Мут — богиня-мать фиванской триады" loading="lazy" decoding="async">\n'
           '<figcaption>' + cap + ' Фото: <a href="' + page + '">' + esc(artist)[:120] + '</a> · Wikimedia Commons · ' + esc(lic) + '</figcaption>\n</figure>\n')
    open('/home/user/Projects/egypt/img/fig-mut.txt', 'w', encoding='utf-8').write(fig)
    print('OK', fname, '|', lic)
    break
