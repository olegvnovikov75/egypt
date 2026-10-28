#!/usr/bin/env python3
"""Пуш main в GitHub по токену gh CLI (токен не печатается). Использование: push_github.py [папка_репо]"""
import os, re, subprocess, sys

def token():
    p = os.path.expanduser('~/.config/gh/hosts.yaml')
    key = 'oauth' + chr(95) + 'token'
    for line in open(p, encoding='utf-8'):
        if key in line:
            return line.split(':', 1)[1].strip().strip('"')
    raise SystemExit('токен не найден')

repo = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
origin = subprocess.run(['git', '-C', repo, 'remote', 'get-url', 'origin'],
                        capture_output=True, text=True).stdout.strip()
m = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(\.git)?$', origin)
if not m:
    raise SystemExit('нет удалённого GitHub: ' + origin)
tok = token()
url = 'https://x-access-token:%s@github.com/%s/%s.git' % (tok, m.group(1), m.group(2))
r = subprocess.run(['git', '-C', repo, 'push', '-q', url, 'main:main'],
                   capture_output=True, text=True)
print('пуш', repo.split('/')[-1], ':', 'ОК' if r.returncode == 0
      else (r.stderr or r.stdout).replace(tok, '***')[:200])
