#!/usr/bin/env python3
"""Привязка страницы Мут: навигация, фото, карточка в каталоге, ссылка от Амона, побратим Фригг."""
import json, os, re

EG = '/home/user/Projects/egypt'
P = os.path.join(EG, 'gods', 'mut.html')
h = open(P, encoding='utf-8').read()

# 1. навигация — копия живого блока с ra.html
ra = open(os.path.join(EG, 'gods', 'ra.html'), encoding='utf-8').read()
nav = re.search(r'<header class="nav".*?</header>', ra, re.S).group(0)
nav = re.sub(r'\sclass="on active"', '', nav)
h = h.replace('<!--NAV-->', nav, 1)

# 2. фото с подписью
fig = open(os.path.join(EG, 'img', 'fig-mut.txt'), encoding='utf-8').read()
h = h.replace('  <!--PHOTO-->', '\n  ' + fig, 1)

# 3. ссылочный текст в see-also поправлен
h = h.replace('>Мут и Фригг: матери пантеонов</a>', '>Сравнение: Египет × Скандинавия</a>')
open(P, 'w', encoding='utf-8').write(h)
print('mut.html: nav+фото вставлены,', len(h), 'байт')

# 4. карточка в каталог богов
p = os.path.join(EG, 'gods.html')
h = open(p, encoding='utf-8').read()
if 'gods/mut.html' not in h:
    card = ('      <a class="card" href="gods/mut.html">\n'
            '        <div class="card__glyph">🦅</div>\n'
            '        <div class="card__title">Мут</div>\n'
            '        <div class="card__text">«Мать» фиванской триады: супруга Амона, мать Хонсу. Единственная богиня в двойной короне Обеих Земель; у её озера Ашеру справляли праздник опьянения.</div>\n'
            '        <div class="card__tag">Фивы · Карнак</div>\n'
            '      </a>\n')
    m = re.search(r'[ \t]*<a class="card" href="gods/amun\.html">.*?</a>\n', h, re.S)
    assert m, 'карточка Амона не найдена'
    h = h[:m.end()] + card + h[m.end():]
    open(p, 'w', encoding='utf-8').write(h)
    print('gods.html: карточка Мут добавлена')

# 5. ссылка от Амона
p = os.path.join(EG, 'gods', 'amun.html')
h = open(p, encoding='utf-8').read()
if 'href="mut.html"' not in h:
    h = h.replace('с супругой Мут', 'с супругой <a href="mut.html">Мут</a>', 1)
    open(p, 'w', encoding='utf-8').write(h)
    print('amun.html: ссылка на Мут')

# 6. побратим Фригг
p = '/home/user/Projects/sites-shared/twins.json'
t = json.load(open(p, encoding='utf-8'))
if 'gods/mut.html' not in t:
    t['gods/mut.html'] = [["family/frigg_1.html", "Фригг", "мать богов — и на Ниле, и у фьордов"]]
    json.dump(t, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('twins.json: Мут ↔ Фригг')

# 7. карта PLAN.md
p = os.path.join(EG, 'PLAN.md')
h = open(p, encoding='utf-8').read()
if 'gods/mut.html' not in h:
    h = h.replace('gods/ra.html          Гаечка',
                  'gods/mut.html         Гаечка   — Мут, мать фиванской триады (по слову Шефа 28.10)\ngods/ra.html          Гаечка', 1)
    open(p, 'w', encoding='utf-8').write(h)
    print('PLAN.md: Мут в карте')
print('ГОТОВО')
