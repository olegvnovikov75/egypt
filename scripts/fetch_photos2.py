#!/usr/bin/env python3
"""Вторая волна: добор и замена фото КЕМЕТ через прямой поиск Commons с проверкой заголовков."""
import json, os, re, time, urllib.parse, urllib.request, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'img')
os.makedirs(IMG, exist_ok=True)
MAN = json.load(open(os.path.join(ROOT, 'photos_manifest.json'), encoding='utf-8'))

# page -> (запрос, обязательные слова в заголовке, запрещённые слова)
JOBS = {
 'index.html':                  ('All Gizah Pyramids', ['pyramid'], ['sphinx','map','plan']),
 'gods/ra.html':                ('winged sun disk temple relief Egypt', ['sun'], ['venus']),
 'gods/anubis.html':            ('Anubis jackal statue Egyptian Museum', ['anubis'], ['baboon','macaque']),
 'gods/maat.html':              ('Maat goddess feather Egyptian statue', ['maat'], ['venus','mons']),
 'cats/house.html':             ('ancient Egyptian cat bronze statue', ['cat'], ['mask','mummy']),
 'symbols/scarab.html':         ('Egyptian scarab amulet faience', ['scarab'], []),
 'arch/giza.html':              ('Pyramids of Giza view', ['pyramid'], ['sphinx']),
 'death/mummification.html':    ('Egyptian mummy cartonnage', ['mummy'], ['animal']),
 'death/canopic.html':          ('canopic jars Egypt museum', ['canop'], []),
 'death/book-of-dead.html':     ('Book of the Dead papyrus hieroglyphs', ['dead'], []),
 'death/duat.html':             ('Book of Gates tomb ceiling', ['gates'], []),
 'death/judgment.html':         ('weighing of the heart Ani papyrus', ['weigh'], []),
 'death/opening-of-mouth.html': ('opening of the mouth ceremony relief', ['mouth'], []),
 'death/sarcophagi.html':       ('painted anthropoid sarcophagus Egypt', ['sarcophag'], []),
 'death/fields-of-reeds.html':  ('book of the dead papyrus field grain', ['papyrus'], []),
 'arch/mastaba.html':           ('mastaba relief hunting Saqqara', ['relief','mastaba','hunt'], ['plan','map','drawing']),
 'arch/djoser.html':            ('Djoser step pyramid Saqqara', ['djoser','step'], ['plan','map','drawing']),
}

def api(url, tries=5):
    for i in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': 'KEMET-encyclopedia/1.0 (contact: olegvnovikov75@github.com)'})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if i < tries - 1 and ('429' in str(e) or 'Timeout' in str(e) or 'timed out' in str(e)):
                time.sleep(5 * (i + 1)); continue
            raise

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    return H.unescape(s).strip()

def pick(query, need, ban):
    u = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search'
         '&srnamespace=6&srlimit=10&srsearch=' + urllib.parse.quote(query))
    for r in api(u)['query']['search']:
        t = r['title']
        tl = t.lower()
        if not tl.endswith(('.jpg', '.jpeg', '.png')):
            continue
        if any(b in tl for b in ban):
            continue
        if not any(n in tl for n in need):
            continue
        return t[5:] if t.startswith('File:') else t
    return None

def commons_info(fname):
    u = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo'
         '&iiprop=url|extmetadata|mime&iiurlwidth=850&iiextmetadatafilter=Artist|LicenseShortName&titles='
         + urllib.parse.quote('File:' + fname))
    d = api(u)
    for p in d.get('query', {}).get('pages', {}).values():
        ii = p.get('imageinfo')
        if ii:
            i = ii[0]; em = i.get('extmetadata', {})
            return {'thumburl': i.get('thumburl') or i.get('url'), 'page': i.get('descriptionurl',''),
                    'artist': strip_tags(em.get('Artist', {}).get('value','')) or 'неизвестный автор',
                    'license': strip_tags(em.get('LicenseShortName', {}).get('value','')) or 'свободная лицензия',
                    'mime': i.get('mime','')}
    return None

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60]

for page, (q, need, ban) in JOBS.items():
    time.sleep(3.0)
    try:
        fname = pick(q, need, ban)
    except Exception as e:
        print('FAIL поиск', page, repr(e)); continue
    if not fname:
        print('FAIL ничего не нашёл', page, '|', q); continue
    time.sleep(2.0)
    try:
        info = commons_info(fname)
    except Exception as e:
        print('FAIL инфо', page, fname, repr(e)); continue
    if not info or not info['thumburl'] or ('jpeg' not in info['mime'] and 'png' not in info['mime']):
        print('FAIL mime', page, fname); continue
    ext = '.jpg' if 'jpeg' in info['mime'] else '.png'
    fn = slug(os.path.splitext(page)[0]) + ext
    # удалить прежний файл страницы с другим расширением
    old = MAN.get(page, {}).get('file')
    if old and os.path.exists(os.path.join(ROOT, old)) and old != 'img/' + fn:
        os.remove(os.path.join(ROOT, old))
    time.sleep(1.5)
    try:
        req = urllib.request.Request(info['thumburl'], headers={'User-Agent': 'KEMET-encyclopedia/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r, open(os.path.join(IMG, fn), 'wb') as f:
            f.write(r.read())
    except Exception as e:
        print('FAIL скачка', page, fname, repr(e)); continue
    MAN[page] = {'file': 'img/' + fn, 'commons_file': fname, 'commons_page': info['page'],
                 'artist': info['artist'], 'license': info['license'], 'wiki': q}
    print('OK  %-30s <- %s (%s)' % (page, fname, info['license']))

json.dump(MAN, open(os.path.join(ROOT, 'photos_manifest.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('всего в манифесте:', len(MAN))
