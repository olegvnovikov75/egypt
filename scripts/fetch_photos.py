#!/usr/bin/env python3
"""Загрузка фоток с Wikimedia Commons (через лид-изображения статей en.wikipedia) для КЕМЕТ.
Каждой странице — одно тематическое фото + метаданные атрибуции в photos_manifest.json."""
import json, os, re, sys, urllib.parse, urllib.request, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'img')
os.makedirs(IMG, exist_ok=True)

# страница -> заголовок статьи en.wikipedia (её лид-картинка = свободное фото)
MANIFEST = {
    'index.html':                'Giza pyramid complex',
    'gods/ra.html':              'Ra',
    'gods/osiris.html':          'Osiris',
    'gods/isis.html':            'Isis',
    'gods/horus.html':           'Horus',
    'gods/set.html':             'Set (deity)',
    'gods/thoth.html':           'Thoth',
    'gods/anubis.html':          'Anubis',
    'gods/sekmet.html':          'Sekhmet',
    'gods/hathor.html':          'Hathor',
    'gods/maat.html':            'Maat',
    'gods/ptah.html':            'Ptah',
    'gods/amun.html':            'Amun',
    'gods/sobek.html':           'Sobek',
    'gods/nut.html':             'Nut (sky goddess)',
    'gods/geb.html':             'Geb',
    'gods/apophis.html':         'Apep',
    'symbols/ankh.html':         'Ankh',
    'symbols/udjat.html':        'Eye of Horus',
    'symbols/djed.html':         'Djed',
    'symbols/tyet.html':         'Tyet',
    'symbols/was.html':          'Was sceptre',
    'symbols/scarab.html':       'Scarab (artifact)',
    'death/mummification.html':  'Ancient Egyptian mummification',
    'death/canopic.html':        'Canopic jar',
    'death/book-of-dead.html':   'Book of the Dead',
    'death/duat.html':           'Duat',
    'death/judgment.html':       'Weighing of souls',
    'death/opening-of-mouth.html': 'Opening of the mouth ceremony',
    'death/sarcophagi.html':     'Sarcophagus',
    'death/fields-of-reeds.html': 'Aaru',
    'arch/mastaba.html':         'Mastaba',
    'arch/djoser.html':          'Pyramid of Djoser',
    'arch/giza.html':            'Great Pyramid of Giza',
    'arch/sphinx.html':          'Great Sphinx of Giza',
    'arch/karnak.html':          'Karnak',
    'arch/luxor.html':           'Luxor Temple',
    'arch/abu-simbel.html':      'Abu Simbel',
    'cats/bastet.html':          'Bastet',
    'cats/house.html':           'Cats in ancient Egypt',
}

import time

def api(url, tries=5):
    for i in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': 'KEMET-encyclopedia/1.0 (contact: olegvnovikov75@github.com)'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(4 * (i + 1))
                continue
            raise

def commons_search(query):
    u = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search'
         '&srnamespace=6&srlimit=6&srsearch=' + urllib.parse.quote(query))
    d = api(u)
    for r in d.get('query', {}).get('search', []):
        t = r['title'][5:] if r['title'].startswith('File:') else r['title']
        if t.lower().endswith(('.jpg', '.jpeg', '.png')):
            return t
    return None

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return html.unescape(s).strip()

def lead_image(wtitle):
    u = ('https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages'
         '&piprop=name&titles=' + urllib.parse.quote(wtitle))
    d = api(u)
    pages = d.get('query', {}).get('pages', {})
    for p in pages.values():
        name = p.get('image', {}).get('name')
        if name:
            return name
    return None

def commons_info(fname):
    u = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo'
         '&iiprop=url|extmetadata|mime&iiurlwidth=850&iiextmetadatafilter=Artist|LicenseShortName|ImageDescription&titles='
         + urllib.parse.quote('File:' + fname))
    d = api(u)
    for p in d.get('query', {}).get('pages', {}).values():
        ii = p.get('imageinfo')
        if not ii:
            continue
        i = ii[0]
        em = i.get('extmetadata', {})
        return {
            'thumburl': i.get('thumburl') or i.get('url'),
            'page': i.get('descriptionurl', ''),
            'artist': strip_tags(em.get('Artist', {}).get('value', '')) or 'неизвестный автор',
            'license': strip_tags(em.get('LicenseShortName', {}).get('value', '')) or 'свободная лицензия',
            'desc': strip_tags(em.get('ImageDescription', {}).get('value', '')),
            'mime': i.get('mime', ''),
        }
    return None

def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s[:60]

out = {}
fails = []
for page, wt in MANIFEST.items():
    time.sleep(2.5)
    name = None
    try:
        name = lead_image(wt)
    except Exception as e:
        fails.append((page, wt, 'лид-запрос: %r' % e))
    if not name:
        try:
            name = commons_search(wt + ' egyptian')
        except Exception:
            pass
    if not name:
        fails.append((page, wt, 'нет картинки')); continue
    time.sleep(2.5)
    try:
        info = commons_info(name)
    except Exception as e:
        fails.append((page, wt, 'imageinfo: %r' % e)); continue
    if not info or not info['thumburl']:
        fails.append((page, wt, 'нет imageinfo: ' + name)); continue
    if 'jpeg' not in info['mime'] and 'png' not in info['mime']:
        fails.append((page, wt, 'не jpg/png: %s (%s)' % (name, info['mime']))); continue
    ext = '.jpg' if 'jpeg' in info['mime'] else '.png'
    fn = slug(os.path.splitext(page)[0]) + ext
    dest = os.path.join(IMG, fn)
    time.sleep(1.5)
    try:
        req = urllib.request.Request(info['thumburl'], headers={'User-Agent': 'KEMET-site/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, 'wb') as f:
            f.write(r.read())
    except Exception as e:
        fails.append((page, wt, 'не скачал: %r' % e)); continue
    out[page] = {'file': 'img/' + fn, 'commons_file': name, 'commons_page': info['page'],
                 'artist': info['artist'], 'license': info['license'], 'wiki': wt}
    print('OK  %-28s <- %s (%s)' % (page, name, info['license']))

with open(os.path.join(ROOT, 'photos_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('\nзагружено:', len(out), '| сбоя:', len(fails))
for fl in fails:
    print('FAIL', fl)
