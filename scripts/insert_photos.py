#!/usr/bin/env python3
"""Вставка фотографий (photos_manifest.json) в страницы КЕМЕТ: фигура с описанием и атрибуцией."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = json.load(open(os.path.join(ROOT, 'photos_manifest.json'), encoding='utf-8'))

CAPS = {
 'index.html': 'Пирамиды Гизы — единственное сохранившееся чудо античного мира.',
 'gods/ra.html': 'Ра — солнце, ставшее богом: его диск правит небом от рассвета до заката.',
 'gods/osiris.html': 'Осирис — владыка Вечного Покоя, бог умирающей и восстающей жизни.',
 'gods/isis.html': 'Исида — великая чародейка, собравшая и оживившая Осириса.',
 'gods/horus.html': 'Хор — сокол небес: царская власть, явленная в живом фараоне.',
 'gods/set.html': 'Сет — владыка пустыни и шторма: чужая сила, без которой мир не держится.',
 'gods/thoth.html': 'Тот — ибис мудрости: писец богов, владыка меры и времени.',
 'gods/anubis.html': 'Анубис — шакал некрополя: бальзамировщик и проводник душ.',
 'gods/sekmet.html': 'Сехмет — львица: гнев Ра, который истребляет и исцеляет.',
 'gods/hathor.html': 'Хатхор — небо в образе коровы: любовь, музыка и радость.',
 'gods/maat.html': 'Маат — перо и истина: порядок мира, единственный перевес на весах суда.',
 'gods/ptah.html': 'Птах — бог-ремесленник: мир назван его словом, Мемфис — под его рукой.',
 'gods/amun.html': 'Амон — Скрытый: ветер в парусах, царь богов Карнака.',
 'gods/sobek.html': 'Собек — крокодил Нила: сила, что живёт в воде и охраняет берега.',
 'gods/nut.html': 'Нут — небо, изогнувшееся над землёй: в её чреве солнце умирает и рождается вновь.',
 'gods/geb.html': 'Геб — земля: лоно, из которого прорастает всякая жизнь.',
 'gods/apophis.html': 'Апоп — змей тьмы, что каждую ночь поджидает солнце в Дуате.',
 'symbols/ankh.html': 'Анх — «ключ жизни», который боги подносят к губам фараона.',
 'symbols/udjat.html': 'Уджат — целый глаз Гора: исцеление, защита, целостность.',
 'symbols/djed.html': 'Джед — позвоночник Осириса: опора неба и устойчивость царства.',
 'symbols/tyet.html': 'Тьет — «узел Исиды»: амулет из красной яшмы, кровь богини на шее.',
 'symbols/was.html': 'Уас — скипетр власти: посох с головой зверя Сета и раздвоенным низом.',
 'symbols/scarab.html': 'Скарабей — Хепри, катящий солнце по небу: жизнь, рождающаяся из себя самой.',
 'death/mummification.html': 'Мумификация: 70 дней между смертью и вечностью — путь через палатку бальзамировщика.',
 'death/canopic.html': 'Каноппы: четыре сына Гора хранят органы умершего до суда.',
 'death/book-of-dead.html': '«Книга выхода днём» — свиток заклинаний, который кладут в гроб.',
 'death/duat.html': 'Дуат — двенадцать часов ночи солнца: путь через тьму к рассвету.',
 'death/judgment.html': 'Зал Двух Истин: сердце на весах против пера Маат, Тот записывает приговор.',
 'death/opening-of-mouth.html': 'Отверзание уст: ритуал возвращает статуе или мумии зрение, слух и речь.',
 'death/sarcophagi.html': 'Саркофаг — «поедающий плоть»: каменный дом тела на века.',
 'death/fields-of-reeds.html': 'Поля Иалу — пашни загробного рая: ячмень в четыре локтя для праведных.',
 'arch/mastaba.html': 'Мастаба — «скамья»: первая вечная гробница Египта.',
 'arch/djoser.html': 'Ступенчатая пирамида Джосера в Саккаре — замысел Имхотепа, первая каменная гора.',
 'arch/giza.html': 'Пирамида Хеопса: 146 метров камня — единственное чудо из античного списка.',
 'arch/sphinx.html': 'Большой Сфинкс: монолит вышиной с шестиэтажный дом, лицо Хафры.',
 'arch/karnak.html': 'Карнак — каменная летопись Фив: два тысячелетия, колоннады, священные озёра.',
 'arch/luxor.html': 'Луксор — «южный гарем» Амона: аллея сфинксов ведёт к Карнаку.',
 'arch/abu-simbel.html': 'Абу-Симбел: четыре колосса Рамсеса II в скале — дважды в год солнце касается святилища.',
 'cats/bastet.html': 'Бастет — кошка дома: солнце, ласка и защита очага.',
 'cats/house.html': 'Кошка в египетском доме: от ловца мышей до богини.',
}

# правки подписей, где в машинном описании смешалось другое
CAPS = {k: v for k, v in CAPS.items()}

def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

changed = 0
for page, info in man.items():
    p = os.path.join(ROOT, page)
    if not os.path.exists(p):
        print('НЕТ СТРАНИЦЫ', page); continue
    html = open(p, encoding='utf-8').read()
    if 'hero-photo' in html:
        print('уже вставлено:', page); continue
    depth = page.count('/')
    src = '../' * depth + info['file']
    cap = CAPS.get(page, '')
    artist = esc(info['artist'])[:120]
    lic = esc(info['license'])
    cpage = info['commons_page']
    figure = (
        '\n  <figure class="hero-photo">\n'
        f'    <img src="{src}" alt="{esc(cap[:100])}" loading="lazy" decoding="async">\n'
        f'    <figcaption>{cap} Фото: <a href="{cpage}">{artist}</a> · Wikimedia Commons · {lic}</figcaption>\n'
        '  </figure>\n'
    )
    if page == 'index.html':
        m = re.search(r'<section[^>]*class="[^"]*hero[^"]*"[^>]*>.*?</section>', html, re.S)
        if not m:
            print('не найден якорь в', page); continue
        html = html[:m.end()] + figure + html[m.end():]
    else:
        m = re.search(r'(</header>)', html)
        if not m:
            print('нет header в', page); continue
        html = html[:m.end(1)] + figure + html[m.end(1):]
    open(p, 'w', encoding='utf-8').write(html)
    changed += 1
    print('вставлено:', page, '->', info['file'])

print('всего вставлено:', changed)
