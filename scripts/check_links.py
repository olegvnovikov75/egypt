#!/usr/bin/env python3
"""Проверка внутренних ссылок сайта КЕМЕТ. Запуск: python3 scripts/check_links.py [папка]"""
import os, re, sys
from html.parser import HTMLParser

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LinkGrab(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag in ('a', 'link'):
            d = dict(attrs)
            href = d.get('href', '')
            if href and not href.startswith(('http', 'mailto:', '#', 'tel:')):
                self.links.append(href)

pages, broken, total = [], [], 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ('.git', 'scripts', 'templates')]
    for fn in filenames:
        if fn.endswith('.html'):
            pages.append(os.path.join(dirpath, fn))

for p in pages:
    with open(p, encoding='utf-8', errors='replace') as f:
        html = f.read()
    grab = LinkGrab()
    try:
        grab.feed(html)
    except Exception:
        pass
    for href in grab.links:
        total += 1
        target = href.split('#')[0].split('?')[0]
        if not target:
            continue
        tp = os.path.normpath(os.path.join(os.path.dirname(p), target))
        if not os.path.exists(tp):
            broken.append((os.path.relpath(p, ROOT), href))

size = sum(os.path.getsize(p) for p in pages)
thin = [(os.path.relpath(p, ROOT), os.path.getsize(p)) for p in pages if os.path.getsize(p) < 2500 and os.path.basename(p) not in ('404.html')]
print(f'страниц: {len(pages)} · размер: {size//1024} КБ · внутр. ссылок: {total}')
if broken:
    print('БИТЫЕ ССЫЛКИ:')
    for src, href in broken:
        print(f'  {src} -> {href}')
else:
    print('битых ссылок: нет')
if thin:
    print('ТОЩИЕ СТРАНИЦЫ (<2.5КБ):')
    for src, s in thin:
        print(f'  {src} ({s} Б)')
sys.exit(1 if broken else 0)
