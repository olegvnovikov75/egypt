#!/usr/bin/env python3
"""Фото богов партии J (Сешат, Нефертем, Ментху, Хех, Мин, Апис):
en.wikipedia pageimage или поиск Commons; вставляет <figure> в каждую страницу."""
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
       'etching', 'coat', 'logo', 'model', 'sketch', 'hieroglyph')

GODS = [
    ('seshat',    'Seshat',    'Seshat goddess relief temple'),
    ('nefertem',  'Nefertem',  'Nefertem lotus god statue'),
    ('menthu',    'Montu',     'Montu Theban war god'),
    ('heh',       'Heh (deity)','Heh god kneeling eternity Egyptian'),
    ('min',       'Min (god)', 'Min god ithyphallic statue temple'),
    ('apis',      'Apis (deity)', 'Apis bull stele sacred Egyptian'),
]

for key, wtitle, csrch in GODS:
    page = os.path.join(EG, 'gods', key + '.html')
    h = open(page, encoding='utf-8').read()
    if '<figure class="hero-photo">' in h:
        print('уже есть фото:', key); continue
    fname = None
    try:
        d = api('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages&piprop=name&titles=' + urllib.parse.quote(wtitle))
        for p in d.get('query', {}).get('pages', {}).values():
            t = p.get('thumbnail', {}).get('title') or p.get('original', {}).get('title') or ''
            if t and not any(b in t.lower() for b in BAN):
                fname = t[5:] if t.startswith('File:') else t
                break
    except Exception as e:
        print('вики мимо:', key, str(e)[:60])
    if not fname:
        try:
            d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srlimit=12&srsearch=' + urllib.parse.quote(csrch))
            for r in d.get('query', {}).get('search', []):
                t = r.get('title', ''); tl = t.lower()
                if not tl.endswith(('.jpg', '.jpeg')) or any(b in tl for b in BAN):
                    continue
                fname = t[5:] if t.startswith('File:') else t
                break
        except Exception as e:
            print('коммонс мимо:', key, str(e)[:60])
    if not fname:
        print('НЕТ фото:', key); continue
    d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=850&iiextmetadatafilter=Artist|LicenseShortName|UsageTerms&titles=' + urllib.parse.quote('File:' + fname))
    url = lic = artist = ''
    for p in d.get('query', {}).get('pages', {}).values():
        ii = (p.get('imageinfo') or [{}])[0]
        url = ii.get('thumburl') or ii.get('url') or ''
        em = ii.get('extmetadata', {})
        lic = strip_tags(em.get('LicenseShortName', {}).get('value', '')) or 'Public domain'
        artist = strip_tags(em.get('Artist', {}).get('value', ''))[:80] or 'неизвестный автор'
    if not url:
        print('НЕТ урла:', key, fname); continue
    raw = os.path.join(EG, 'img', 'gods-%s.jpg' % key)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(raw, 'wb') as f:
        f.write(r.read())
    fig = ('<figure class="hero-photo">\n    <img src="../img/gods-%s.jpg" alt="%s" loading="lazy" decoding="async">\n'
           '    <figcaption>%s Фото: <a href="https://commons.wikimedia.org/wiki/File:%s">%s</a> · Wikimedia Commons · %s</figcaption>\n  </figure>\n'
           % (key, H.escape(art := ('%s' % key)), key, urllib.parse.quote(fname.replace(' ', '_')), artist, lic))
    alt = {'seshat': 'Сешат — госпожа домашней библиотеки и покровительница письма',
           'nefertem': 'Нефертем — лотосный бог благовоний, сын Птаха и Сехмет',
           'menthu': 'Ментху — фиванский бог войны, бык Мневис',
           'heh': 'Хех — обожествлённая вечность, четвероногие духи бесконечности',
           'min': 'Мин — бог урожая и плодородия Востока',
           'apis': 'Апис — священный бык Птаха, живое оракульское чучело Мемфиса'}[key]
    fig = fig.replace('alt="%s"' % H.escape('seshat'), 'alt="%s"' % H.escape(alt)).replace('<figcaption>%s Фото' % key, '<figcaption>%s · фото с Викисклада. Фото' % alt)
    m = re.search(r'(<main class="main[^"]*">)', h)
    h = h.replace(m.group(1), m.group(1) + '\n  ' + fig, 1) if m else (fig + h)
    open(page, 'w', encoding='utf-8').write(h)
    print('фото:', key, '·', fname, '·', lic, '·', os.path.getsize(raw), 'Б')
    time.sleep(1)
