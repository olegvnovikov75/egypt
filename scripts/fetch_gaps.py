#!/usr/bin/env python3
"""Добор недостающих фото КЕМЕТ прямым поиском Commons (несколько запросов на страницу)."""
import json, os, re, time, urllib.parse, urllib.request, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'img')
MAN = json.load(open(os.path.join(ROOT, 'photos_manifest.json'), encoding='utf-8'))

JOBS = {
 'gods/ra.html':      (['winged sun disk temple egypt', 'sun disk uraeus relief egypt', 'ra god barque egypt'], ['disk','sun','barque'], ['modern','logo','map','drawing']),
 'gods/maat.html':    (['maat goddess statue egypt museum', 'maat feather egypt statue', 'maat bust museum'], ['maat'], ['venus','mons','map','drawing']),
 'death/duat.html':   (['book of gates egypt tomb', 'amduat egypt', 'tomb ceiling stars egypt'], ['gates','amduat','ceiling','nut'], ['map','drawing','plan']),
 'death/sarcophagi.html': (['egyptian sarcophagus painted lid', 'anthropoid sarcophagus egypt museum', 'sarcophagus rameses'], ['sarcophag'], ['map','plan','drawing']),
 'arch/mastaba.html': (['mastaba saqqara egypt', 'mastaba tomb facade relief', 'akhtetih mastaba'], ['mastaba'], ['map','plan','drawing','diagram']),
}

def api(url, tries=5):
    for i in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': 'KEMET-encyclopedia/1.0 (contact: olegvnovikov75@github.com)'})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.load(r)
        except Exception as e:
            if i < tries-1 and ('429' in str(e) or 'timed out' in str(e) or 'Timeout' in str(e) or 'temporarily' in str(e).lower()):
                time.sleep(6*(i+1)); continue
            raise

def strip_tags(s):
    return H.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

def pick(query, need, ban):
    d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srnamespace=6&srlimit=10&srsearch=' + urllib.parse.quote(query))
    for r in d['query']['search']:
        t = r['title']; tl = t.lower()
        if not tl.endswith(('.jpg','.jpeg','.png')): continue
        if any(b in tl for b in ban): continue
        if not any(n in tl for n in need): continue
        return t[5:] if t.startswith('File:') else t
    return None

def cinfo(fname):
    d = api('https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=850&iiextmetadatafilter=Artist|LicenseShortName&titles=' + urllib.parse.quote('File:' + fname))
    for p in d.get('query', {}).get('pages', {}).values():
        ii = p.get('imageinfo')
        if ii:
            i = ii[0]; em = i.get('extmetadata', {})
            return {'thumb': i.get('thumburl') or i.get('url'), 'page': i.get('descriptionurl',''),
                    'artist': strip_tags(em.get('Artist', {}).get('value','')) or 'неизвестный автор',
                    'license': strip_tags(em.get('LicenseShortName', {}).get('value','')) or 'свободная лицензия',
                    'mime': i.get('mime','')}
    return None

for page, (queries, need, ban) in JOBS.items():
    if page in MAN:
        print('уже есть:', page); continue
    fname = None
    for q in queries:
        time.sleep(3)
        try:
            fname = pick(q, need, ban)
        except Exception as e:
            print('FAIL поиск', page, q, repr(e)); continue
        if fname: break
    if not fname:
        print('FAIL: ничего не найдено для', page); continue
    time.sleep(2)
    try:
        info = cinfo(fname)
    except Exception as e:
        print('FAIL инфо', page, fname, repr(e)); continue
    if not info or not info['thumb'] or not any(x in info['mime'] for x in ('jpeg','png')):
        print('FAIL mime', page, fname); continue
    ext = '.jpg' if 'jpeg' in info['mime'] else '.png'
    fn = re.sub(r'[^a-z0-9]+','-', os.path.splitext(page)[0].lower()) + ext
    time.sleep(1.5)
    req = urllib.request.Request(info['thumb'], headers={'User-Agent': 'KEMET-encyclopedia/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r, open(os.path.join(IMG, fn), 'wb') as f:
        f.write(r.read())
    MAN[page] = {'file': 'img/' + fn, 'commons_file': fname, 'commons_page': info['page'],
                 'artist': info['artist'], 'license': info['license'], 'wiki': queries[0]}
    print('OK', page, '<-', fname, '(%s)' % info['license'])

json.dump(MAN, open(os.path.join(ROOT, 'photos_manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('всего в манифесте:', len(MAN))
