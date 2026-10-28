#!/bin/bash
# Фотоприёмка КЕМЕТ: докачать, вычистить неверные, вставить, оформить, проверить, запушить.
# Пишет коротко; токен в вывод не попадает.
set -u
cd /home/user/Projects/egypt || exit 1
log(){ echo "[$(date +%H:%M:%S)] $*"; }

if pgrep -f '[f]etch_photos2.py' >/dev/null; then
  log 'вторая волна ещё идёт — жду'; while pgrep -f '[f]etch_photos2.py' >/dev/null; do sleep 10; done
else
  log 'запуск второй волны докачки'; timeout 1200 python3 scripts/fetch_photos2.py >>/tmp/fetch2.log 2>&1 || true
fi
log 'докачка завершена'

python3 - <<'PYEOF'
import json
m = json.load(open('photos_manifest.json', encoding='utf-8'))
def bad(k, v):
    cf = (v.get('commons_file','') + ' ' + v.get('file','')).lower()
    if k.startswith('gods/anubis') and 'baboon' in cf: return True
    if k.startswith('gods/maat') and ('venus' in cf or 'mons' in cf): return True
    if k.startswith('cats/') and 'mask' in cf: return True
    if k.startswith('arch/giza') and 'sphinx' in cf: return True
    if k.startswith('symbols/scarab') and 'amulet (am' in cf: return True
    return False
rm = [k for k, v in list(m.items()) if bad(k, v)]
for k in rm: m.pop(k)
json.dump(m, open('photos_manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('манифест:', len(m), 'записей; убрано неверных:', rm)
PYEOF

log 'вставка фигур в страницы'
python3 scripts/insert_photos.py | tail -2

# стили для фото — один раз
grep -q '.hero-photo {' css/style.css || cat >> css/style.css <<'EOF'

/* --- фотографии Wikimedia Commons --- */
.hero-photo { margin: 1.6rem 0 0; }
.hero-photo img { width: 100%; max-height: 460px; object-fit: cover;
  border-radius: 14px; border: 1px solid var(--line); }
.hero-photo figcaption { font-size: .85rem; color: var(--muted);
  text-align: center; margin-top: .45rem; line-height: 1.5; }
.hero-photo figcaption a { color: var(--sky); }
EOF
log 'стили есть'

python3 scripts/check_links.py | head -4
git add -A
git commit -q -m 'КЕМЕТ: реальные фото Wikimedia Commons на страницах — подписи, атрибуция и лицензии' && log 'коммит готов'
TOKEN=*** -oP 'oauth_token:\s*\K\S+' ~/.config/gh/hosts.yaml | head -1)
git push -q "https://x-access-token:***}@github.com/olegvnovikov75/egypt.git" main:main 2>&1 | sed "s/${TOKEN}/***/g" || { log 'ПУШ НЕ ПРОШЁЛ'; exit 1; }
log 'пуш прошёл'

for i in $(seq 1 12); do
  sleep 15
  n=$(curl -s https://olegvnovikov75.github.io/egypt/symbols/ankh.html | grep -c 'hero-photo' || true)
  [ "$n" -ge 2 ] && break
done
total=$(curl -s https://olegvnovikov75.github.io/egypt/ | grep -c 'hero-photo' || true)
log 'ИТОГ: на главной блок с фото: '"$total"'; на странице анха: '"$n"'; ссылка https://olegvnovikov75.github.io/egypt/'
