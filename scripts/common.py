"""Configuração compartilhada dos scripts do pixel-reels."""
import json, os, shutil, subprocess, sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.expanduser(os.environ.get('PIXEL_REELS_CONFIG', '~/.config/pixel-reels/config.json'))
HYPERFRAMES = 'hyperframes@0.8.34'
CHROMES = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', 'google-chrome', 'chromium', 'chromium-browser', 'chrome']


def load_config():
    base = json.load(open(os.path.join(SKILL, 'config.example.json'), encoding='utf-8'))
    if os.path.exists(CONFIG):
        user = json.load(open(CONFIG, encoding='utf-8'))
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict): base[k].update(v)
            else: base[k] = v
    return base


def chrome():
    c = next((c for c in CHROMES if shutil.which(c) or os.path.exists(c)), None)
    if not c: sys.exit('Chrome não encontrado. Instale o Google Chrome.')
    return c


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).strip())
