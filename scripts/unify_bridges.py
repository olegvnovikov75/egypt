#!/usr/bin/env python3
"""Единый стиль навигации двух сайтов + полосы «близнецы мифа» на всех страницах."""
import os, re, subprocess

EG = '/home/user/Projects/egypt'
SC = '/home/user/Projects/scandic'
EG_URL = 'https://olegvnovikov75.github.io/egypt/'
SC_URL = 'https://olegvnovikov75.github.io/scandic/'

# ─── 1. Навигация: единые подписи-разъяснения ───
SWITCH_NEW = '<a class="nav__switch" href="' + SC_URL + '" title="Скандик — «старый обычай» (forn siðr): вера викингов в асов и ванов, в Одина, Тора и Фрейю">ᛋ Скандик — вера севера</a>'
SISTER_NEW = '<a class="nav__sister" href="' + EG_URL + '" title="КЕМЕТ — «Чёрная земля»: древняя вера египтян (нетжер, nṯr — «божественное») в Ра, Осириса, Исиду и Маат">☥ КЕМЕТ — вера Чёрной земли</a>'
n1 = n2 = n3 = 0
for root, dirs, files in [(EG, None, None), (SC, None, None)]:
    pass

def html_files(base):
    for dp, dns, fns in os.walk(base):
        if 'templates' in dp or '/.git' in dp: continue
        for f in fns:
            if f.endswith('.html'): yield os.path.join(dp, f)

for p in html_files(EG):
    h = open(p, encoding='utf-8').read(); h0 = h
    h = re.sub(r'<a class="nav__switch"[^>]*>.*?</a>', SWITCH_NEW, h, flags=re.S)
    h = h.replace('𓋹 КЕМЕТ', '☥ КЕМЕТ')
    if h != h0: open(p, 'w', encoding='utf-8').write(h); n1 += 1
for p in html_files(SC):
    h = open(p, encoding='utf-8').read(); h0 = h
    h = re.sub(r'<a class="nav__sister"[^>]*>.*?</a>', SISTER_NEW, h, flags=re.S)
    if h != h0: open(p, 'w', encoding='utf-8').write(h); n2 += 1
print('навигация: egypt', n1, '· scandic', n2)

# ─── 2. Геройские алиасы: с уважением к вере ───
p = os.path.join(EG, 'index.html'); h = open(p, encoding='utf-8').read()
if 'вера в Ра, Осириса' not in h:
    h = re.sub(r'<p class="hero__alias">.*?</p>', '<p class="hero__alias">(нетжер nṯr — «божественное» · вера в Ра, Осириса, Исиду и Маат)</p>', h, flags=re.S)
    open(p, 'w', encoding='utf-8').write(h)
p = os.path.join(SC, 'index.html'); h = open(p, encoding='utf-8').read()
if 'асов и ванов' not in h:
    h = re.sub(r'<p class="hero__alias">.*?</p>', '<p class="hero__alias">(forn siðr — «старый обычай» · вера в асов и ванов, в Одина, Тора и Фрейю)</p>', h, flags=re.S)
    open(p, 'w', encoding='utf-8').write(h)
print('алиасы обновлены')

# ─── 3. Карта близнецов ───
# egypt_rel -> [(scandic_rel, сканд.название, подпись)]
TWIN_EG = {
 'gods/thoth.html':  [('runes.html', 'Руны', 'Один добился рун — Тот дал письмо')],
 'gods/ra.html':     [('cosmos.html', 'Космос', 'солнце везут по небу')],
 'gods/nut.html':    [('realms.html', 'Девять миров', 'небо — тело богини')],
 'gods/apophis.html':[('creatures.html', 'Существа', 'Апоп ↔ Ёрмунганд')],
 'arch/sphinx.html': [('creatures.html', 'Существа', 'каменный страж порога')],
 'gods/osiris.html': [('ragnarok.html', 'Рагнарёк', 'смерть, открывающая утро')],
 'gods/set.html':    [('gods.html', 'Боги', 'Сет ↔ Локи')],
 'gods/isis.html':   [('gods.html', 'Боги', 'Исида ↔ Фрейя')],
 'symbols/udjat.html':[('runes.html', 'Руны', 'знаки, что исцеляют и берегут')],
 'symbols/djed.html':[('cosmos.html', 'Космос', 'столб Джед ↔ Иггдрасиль')],
 'death/fields-of-reeds.html': [('realms.html', 'Девять миров', 'Иару ↔ луга Вальхаллы')],
 'death/judgment.html': [('ragnarok.html', 'Рагнарёк', 'последний суд')],
 'death/duat.html':  [('realms.html', 'Девять миров', 'Дуат ↔ дорога в Хель')],
 'death/mummification.html': [('vikings.html', 'Викинги', 'тело отправляют в вечность')],
 'death/book-of-dead.html':  [('eddas.html', 'Эдды', 'книги, что говорят за мёртвых и богов')],
 'sources.html':     [('eddas.html', 'Эдды', 'что знаем и откуда'), ('literature.html', 'Литература', 'надписи ↔ саги')],
 'gods.html':        [('gods.html', 'Боги', 'два пантеона')],
 'symbols.html':     [('runes.html', 'Руны', 'два алфавита силы')],
 'death.html':       [('vikings.html', 'Викинги', 'похороны и загробный путь')],
}
# скандик_rel -> [(egypt_rel, егип.название, подпись)]  (обратная)
TWIN_SC = {}
for eg, lst in TWIN_EG.items():
    for sc, _lab, note in lst:
        TWIN_SC.setdefault(sc, []).append((eg, note))
EG_NAME = {k: None for k in TWIN_EG}
MANUAL = {'gods/thoth.html':'Тот','gods/ra.html':'Ра','gods/nut.html':'Нут','gods/apophis.html':'Апоп',
 'arch/sphinx.html':'Сфинкс','gods/osiris.html':'Осирис','gods/set.html':'Сет','gods/isis.html':'Исида',
 'symbols/udjat.html':'Уджат','symbols/djed.html':'Джед','death/fields-of-reeds.html':'Полосы Иару',
 'death/judgment.html':'Весы суда','death/duat.html':'Дуат','death/mummification.html':'Мумификация',
 'death/book-of-dead.html':'Книга мёртвых','sources.html':'Источники','gods.html':'Боги КЕМЕТ',
 'symbols.html':'Символы','death.html':'Смерть и Дуат'}

def h1_of(h):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def band(south: bool, own_label: str, twins, base_url: str):
    """south=True — страница КЕМЕТ (свой мир справа внизу, близнец северный)."""
    if south:
        own = ('<span class="world world--south" aria-hidden="true">☥</span>'
               '<span class="twinband__own">' + own_label + ' · КЕМЕТ</span>')
        other = ''.join('<a class="twinband__twin" href="' + SC_URL + u + '">'
                        '<span>ᛋ ' + lab + ' · Скандик</span><small>' + note + '</small></a>'
                        for u, lab, note in twins)
    else:
        own = ('<span class="world world--north" aria-hidden="true">ᛋ</span>'
               '<span class="twinband__own">' + own_label + ' · Скандик</span>')
        other = ''.join('<a class="twinband__twin" href="' + EG_URL + u + '">'
                        '<span>☥ ' + (MANUAL.get(u) or h1_of(open(os.path.join(EG, u), encoding="utf-8").read())) + ' · КЕМЕТ</span><small>' + note + '</small></a>'
                        for u, note in twins)
    if not twins:
        other = '<span class="twinband__solo">у этого сюжета нет близнеца на другом берегу — он сам по себе</span>'
    return ('<section class="twinband" aria-label="Два берега мифа">' + own +
            ('<span class="twinband__vs" aria-hidden="true">⟷</span>' if twins else '') + other + '</section>\n')

def insert_before_footer(h, block):
    for mark in ('<footer class="footer"', '<div class="footer'):
        i = h.find(mark)
        if i != -1: return h[:i] + block + h[i:]
    i = h.rfind('</main>')
    return h[:i] + block + h[i:] if i != -1 else h

# Египет: все подстраницы +指定 страницы
SKIP_EG = {'index.html', '404.html', 'about.html', 'contact.html', 'compare.html', 'templates/page-skeleton.html'}
cnt_eg = 0
for p in html_files(EG):
    rel = os.path.relpath(p, EG).replace(os.sep, '/')
    if rel in SKIP_EG or 'twinband' in open(p, encoding='utf-8').read(): continue
    h = open(p, encoding='utf-8').read()
    twins = TWIN_EG.get(rel, [])
    label = MANUAL.get(rel) or h1_of(h)
    h = insert_before_footer(h, band(True, label, twins, EG_URL))
    open(p, 'w', encoding='utf-8').write(h); cnt_eg += 1
print('египет полос:', cnt_eg)

# Скандик: старые crosslink-блоки заменяем на twinband
SKIP_SC = {'index.html', '404.html', 'about.html', 'contact.html'}
cnt_sc = 0
for f in sorted(os.listdir(SC)):
    if not f.endswith('.html') or f in SKIP_SC: continue
    p = os.path.join(SC, f); h = open(p, encoding='utf-8').read()
    h = re.sub(r'<section class="crosslink">.*?</section>\n', '', h, flags=re.S)
    if 'twinband' in h:
        open(p, 'w', encoding='utf-8').write(h); continue
    h = insert_before_footer(h, band(False, h1_of(h), TWIN_SC.get(f, []), SC_URL))
    open(p, 'w', encoding='utf-8').write(h); cnt_sc += 1
print('скандик полос:', cnt_sc)

# ─── 4. Единый CSS ───
CSS = '''
/* ─── единый мост: навигация двух сайтов + полосы близнецов ─── */
.nav{position:relative}
.nav::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:linear-gradient(90deg,#5f8dd6 0%,#c9a227 45%,#e0b84c 55%,#ff8a3c 100%)}
.nav__logo{font-family:Georgia,'Times New Roman',serif;font-size:22px;color:#e0b84c;border:none;white-space:nowrap}
.twinband{display:flex;align-items:center;flex-wrap:wrap;gap:10px 16px;margin:46px 0 8px;padding:16px 18px;border:1px dashed rgba(224,184,76,.45);border-radius:16px;background:linear-gradient(90deg,rgba(95,141,214,.10),rgba(224,184,76,.05) 46%,rgba(255,138,60,.10))}
.world{flex:0 0 48px;width:48px;height:48px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:20px;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.55)}
.world--north{background:linear-gradient(180deg,#0e1c30 0%,#2a4a70 40%,#e8f4ff 41%,#b7d4ee 52%,#33587e 53%,#16273d 100%);border:1px solid rgba(191,224,255,.55)}
.world--south{background:linear-gradient(90deg,transparent 46%,#3f7fbf 47.5% 52.5%,transparent 53.5%),linear-gradient(180deg,#ffe2b0 0%,#ffab52 38%,#c96f2b 39%,#7a3c14 100%);border:1px solid rgba(255,217,160,.55)}
.twinband__own{font-family:Georgia,serif;color:#f4d98c;font-size:16px}
.twinband__vs{color:#a7b4d4;font-size:18px}
.twinband__twin{display:flex;flex-direction:column;color:#9fc3ff;font-family:Georgia,serif;font-size:16px;border:none}
.twinband__twin:hover{color:#f4d98c}
.twinband__twin small{font-family:'Segoe UI',sans-serif;color:#a7b4d4;font-size:12px}
.twinband__solo{color:#a7b4d4;font-size:13px;font-style:italic}
'''
for d in (EG, SC):
    c = os.path.join(d, 'css/style.css')
    css = open(c, encoding='utf-8').read()
    if 'twinband' not in css:
        open(c, 'w', encoding='utf-8').write(css + CSS)
# скандик: логотип в тот жеGeorgia 22px
sc_css = os.path.join(SC, 'css/style.css')
css = open(sc_css, encoding='utf-8').read()
if '.nav__logo' not in css:
    open(sc_css, 'w', encoding='utf-8').write(css + '.nav__logo{font-family:Georgia,serif;font-size:22px;color:#e0b84c}\n')

# ─── 5. Линковка + пуш ───
r = subprocess.run(['python3', os.path.join(EG, 'scripts/check_links.py'), EG], capture_output=True, text=True)
print('check egypt:', r.stdout.strip().splitlines()[-1] if r.stdout.strip() else 'rc=' + str(r.returncode))
for d, m in ((EG, 'Единый стиль навигации + полосы «близнецы мифа» (южный берег)'),
             (SC, 'Единый стиль навигации + полосы «близнецы мифа» (северный берег); crosslink заменён')):
    subprocess.run(['git', '-C', d, 'add', '-A'])
    subprocess.run(['git', '-C', d, 'commit', '-qm', m])
    pr = subprocess.run(['python3', os.path.join(EG, 'scripts/push_github.py'), d], capture_output=True, text=True)
    print('пуш', os.path.basename(d), ':', pr.stdout.strip() or pr.stderr.strip()[:80])
print('ГОТОВО')
