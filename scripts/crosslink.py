#!/usr/bin/env python3
"""Мост КЕМЕТ <-> Скандик: встречные ссылки в навигации + переклички по сущности."""
import os, re, subprocess, time

EG = '/home/user/Projects/egypt'
SC = '/home/user/Projects/scandic'
EG_URL = 'https://olegvnovikov75.github.io/egypt/'
SC_URL = 'https://olegvnovikov75.github.io/scandic/'

# ── 1. Скандик: сестринская ссылка в шапке всех 16 страниц ──
NAV = '  <a class="nav__sister" href="' + EG_URL + '" title="Юг — сайт о мифологии Древнего Египта">☥ КЕМЕТ</a>\n</header>'
n = 0
for f in sorted(os.listdir(SC)):
    if not f.endswith('.html'): continue
    p = os.path.join(SC, f)
    h = open(p, encoding='utf-8').read()
    if 'github.io/egypt' in h: continue
    h2 = re.sub(r'</header>', NAV, h, count=1)
    if h2 != h:
        open(p, 'w', encoding='utf-8').write(h2); n += 1
print('скандик шапки:', n)

# ── 2. Скандик: строка под геройским заголовком главной ──
p = os.path.join(SC, 'index.html')
h = open(p, encoding='utf-8').read()
if 'hero__sister' not in h:
    h = re.sub(r'(<p class="hero__sub">[^<]*</p>)',
               r'\1\n    <p class="hero__sister"><a href="' + EG_URL + '">☥ КЕМЕТ — мифология Древнего Египта →</a></p>', h, count=1)
    open(p, 'w', encoding='utf-8').write(h)
print('скандик герой:', 'hero__sister' in open(p, encoding='utf-8').read())

# ── 3. Скандик: блоки перекличек по сущности ──
REL = {
 'runes.html':     ('Юг зовёт: письмо богов', [('gods/thoth.html','Тот — изобретатель письма'),('symbols/udjat.html','Уджат — магический знак'),('compare.html','Один и Тот')]),
 'creatures.html': ('Юг зовёт: чудовища пустыни', [('gods/apophis.html','Апоп — змей хаоса'),('arch/sphinx.html','Великий Сфинкс')]),
 'ragnarok.html':  ('Юг зовёт: смерть и возрождение солнца', [('gods/apophis.html','Апоп — битва, что повторяется каждую ночь'),('death/duat.html','Дуат — путь сквозь смерть')]),
 'vikings.html':   ('Юг зовёт: мир мёртвых', [('death/mummification.html','Мумификация — корабль в вечность'),('arch/giza.html','Гиза — горизонты фараонов')]),
 'cosmos.html':    ('Юг зовёт: небо — это богиня', [('gods/nut.html','Нут — звёздное небо'),('gods/ra.html','Ра — путь солнца')]),
 'realms.html':    ('Юг зовёт: тот свет', [('death/fields-of-reeds.html','Полосы Иару — рай праведных'),('death/judgment.html','Весы суда Осириса')]),
 'gods.html':      ('Юг зовёт: пантеон пустыни', [('gods.html','Боги КЕМЕТ'),('compare.html','Один и Тот, Тор и Сет')]),
 'eddas.html':     ('Юг зовёт: голоса юга', [('death/book-of-dead.html','Книга мёртвых'),('sources.html','Источники по египетской мифологии')]),
 'literature.html':('Юг зовёт: источники', [('sources.html','Источники КЕМЕТ')]),
 'myths.html':     ('Юг зовёт: мифы юга', [('compare.html','Один и Тот: боги знания')]),
}
for f, (title, links) in REL.items():
    p = os.path.join(SC, f)
    h = open(p, encoding='utf-8').read()
    if 'class="crosslink"' in h: continue
    box = ('\n<section class="crosslink"><div class="prose">\n<h3>' + title + ':</h3>\n'
           + '\n'.join('<a href="' + EG_URL + u + '">' + t + ' →</a>' for u, t in links)
           + '\n</div></section>\n')
    h = h.replace('</main>', box + '</main>', 1)
    open(p, 'w', encoding='utf-8').write(h)
print('скандик переклички:', sum(1 for f in REL if 'crosslink' in open(os.path.join(SC,f), encoding='utf-8').read()))

# ── 4. CSS скандика ──
css = open(os.path.join(SC,'css/style.css'), encoding='utf-8').read()
if 'nav__sister' not in css:
    css += ('\n.nav__sister{color:var(--gold);border:1px solid var(--line);border-radius:20px;padding:3px 12px;white-space:nowrap;align-self:center}\n'
            '.nav__sister:hover{background:rgba(201,162,39,.12)}\n'
            '.hero__sister{margin-top:14px}\n.hero__sister a{color:var(--gold);border:1px solid var(--line);border-radius:20px;padding:6px 16px;display:inline-block;font-size:15px}\n'
            '.crosslink{margin:40px 0 6px;border:1px dashed var(--line);border-radius:14px;padding:18px 22px;background:rgba(201,162,39,.06)}\n'
            '.crosslink h3{color:var(--gold);font-size:16px;margin-bottom:10px}\n'
            '.crosslink a{display:inline-block;margin:0 16px 6px 0}\n')
    open(os.path.join(SC,'css/style.css'), 'w', encoding='utf-8').write(css)

# ── 5. Египет: сестринские переклички внутри see-also ──
EGREL = {
 'gods/thoth.html':        ('runes.html','Один, открывший руны'),
 'symbols/udjat.html':     ('runes.html','Руны — знаки силы севера'),
 'gods/apophis.html':      ('creatures.html','Ёрмунганд и Нидхёгг — змеи севера'),
 'gods/ra.html':           ('cosmos.html','Колесница солнца: Соль и Ра'),
 'gods/nut.html':          ('cosmos.html','Иггдрасиль — мировое дерево'),
 'death/fields-of-reeds.html': ('realms.html','Хельхейм и Вальхалла'),
 'death/judgment.html':    ('ragnarok.html','Рагнарёк — весы для целого мира'),
 'death/mummification.html': ('vikings.html','Корабельные погребения викингов'),
 'death/book-of-dead.html':('eddas.html','Эдды — книги севера'),
 'arch/sphinx.html':       ('creatures.html','Чудовища скандинавских мифов'),
 'gods/osiris.html':       ('gods.html','Бальдр — умирающий бог севера'),
}
n = 0
for rel, (su, label) in EGREL.items():
    p = os.path.join(EG, rel)
    h = open(p, encoding='utf-8').read()
    if 'github.io/scandic/' + su in h: continue
    add = '    <a class="sister" href="' + SC_URL + su + '">⛰ ' + label + '</a>\n  </div>'
    h2 = re.sub(r'(\n  </div>)(?=\s*(?:<footer|</main>|<div class="footer))', add, h, count=1)
    if h2 == h:  # запасной вариант: закрывающий see-also
        h2 = h.replace('  </div>\n', '  </div>\n', 1)
        m = re.search(r'(<div class="see-also">.*?)  </div>', h, re.S)
        if m:
            h2 = h[:m.end(1)] + '    <a class="sister" href="' + SC_URL + su + '">⛰ ' + label + '</a>\n' + h[m.end(1):]
    if h2 != h:
        open(p, 'w', encoding='utf-8').write(h2); n += 1
print('египет переклички:', n)

css = open(os.path.join(EG,'css/style.css'), encoding='utf-8').read()
if 'a.sister' not in css:
    css += '\n.see-also a.sister{color:var(--sky);border:1px solid var(--line);border-radius:14px;padding:2px 10px}\n'
    open(os.path.join(EG,'css/style.css'), 'w', encoding='utf-8').write(css)

# ── 6. Контроль ссылок, коммиты, пуш ──
r = subprocess.run(['python3', os.path.join(EG,'scripts/check_links.py'), EG], capture_output=True, text=True)
print('check egypt:', r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.returncode)
for d, m in ((EG, 'Мост: переклички КЕМЕТ ↔ Скандик (see-also сестринские ссылки)'),
             (SC, 'Мост: ссылка на КЕМЕТ в шапке + блоки перекличек по сущности')):
    subprocess.run(['git','-C',d,'add','-A'])
    subprocess.run(['git','-C',d,'commit','-qm',m])
    pr = subprocess.run(['python3', os.path.join(EG,'scripts/push_github.py'), d], capture_output=True, text=True)
    print('пуш', os.path.basename(d), ':', pr.stdout.strip() or pr.stderr.strip()[:100])
print('ГОТОВО')
