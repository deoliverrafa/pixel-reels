#!/usr/bin/env python3
"""Capa 1080x1920: conteúdo no 4:5 central, que é o recorte da grade do perfil.

Uso: cover.py saida.jpg --num 1 --line "O CLAUDE" --line "[DENTRO DO]" --line "SEU CHROME" --image chave.png
[Colchetes] marcam a palavra na faixa colorida. Use exatamente 3 linhas.
"""
import argparse, html, os, random, re, subprocess, tempfile
from common import SKILL, chrome, load_config

U = 70 / 8
ACC = {'acute': [(4, -3.6), (5, -3.6), (3, -2.6), (4, -2.6)], 'grave': [(2, -3.6), (3, -3.6), (3, -2.6), (4, -2.6)], 'circ': [(3, -3.6), (4, -3.6), (2, -2.6), (5, -2.6)], 'cedil': [(3, 7.4), (4, 7.4), (2, 8.4), (3, 8.4)], 'tilde': [(1, -3.6), (2, -3.6), (3, -3.6), (6, -3.6), (0, -2.6), (3, -2.6), (4, -2.6), (5, -2.6)]}
MAP = {'Ã': ('A', 'tilde'), 'Õ': ('O', 'tilde'), 'É': ('E', 'acute'), 'Ú': ('U', 'acute'), 'Á': ('A', 'acute'), 'Í': ('I', 'acute'), 'Ó': ('O', 'acute'), 'Â': ('A', 'circ'), 'Ê': ('E', 'circ'), 'Ô': ('O', 'circ'), 'À': ('A', 'grave'), 'Ç': ('C', 'cedil')}


def accents(cream, shadow):
    out = ''
    for k, pts in ACC.items():
        sh = lambda dx, c: ','.join(f'{x*U+U/2+dx:.2f}px {y*U+U/2+dx:.2f}px 0 {U/2:.3f}px {c}' for x, y in pts)
        out += f'.a.{k}::after{{content:"";position:absolute;left:0;top:0;width:0;height:0;box-shadow:{sh(0, cream)},{sh(7, shadow)}}}\n'
    return out


def line(s):
    s = ''.join(f'<span class="a {MAP[c][1]}">{MAP[c][0]}</span>' if c in MAP else html.escape(c) for c in s)
    return re.sub(r'\[(.+?)\]', r'<span class="ban">\1</span>', s)


def main():
    a = argparse.ArgumentParser(); a.add_argument('out'); a.add_argument('--num', type=int, required=True); a.add_argument('--line', action='append', required=True); a.add_argument('--image', required=True); a.add_argument('--tag'); o = a.parse_args()
    c = load_config(); s = c['estilo']; f = os.path.join(SKILL, 'templates', 'project', 'assets', 'fonts'); r = random.Random(o.num); stars = ''
    for _ in range(70):
        x, y = r.randrange(0, 1080, 6), r.randrange(0, 1920, 6)
        if 290 < y < 1600: continue
        stars += f'<i style="left:{x}px;top:{y}px;width:6px;height:6px;background:{r.choice([s["cream"], s["accent"]])};opacity:{r.choice([.35, .6, .9])}"></i>'
    page = f'''<!DOCTYPE html><meta charset=utf-8><style>
@font-face{{font-family:PS2P;src:url(file://{f}/PressStart2P-latin.woff2)}}
@font-face{{font-family:Silk;src:url(file://{f}/Silkscreen-700.woff2);font-weight:700}}
*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:1080px;height:1920px;overflow:hidden}}
body{{position:relative;background:radial-gradient(ellipse 760px 900px at 540px 760px,{s["spot"]} 0%,{s["spotMid"]} 35%,{s["bg"]} 66%,{s["bgDeep"]} 100%);font-family:PS2P;color:{s["cream"]}}}
.st i{{position:absolute;display:block}}
.band{{position:absolute;left:0;width:1080px;height:12px;background:repeating-linear-gradient(90deg,{s["accent"]} 0 24px,transparent 24px 48px);opacity:.55}}
.row{{position:absolute;top:336px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center;font-family:Silk;font-weight:700;font-size:30px;text-shadow:3px 3px 0 {s["shadow"]}}}
.tag{{background:{s["accent"]};padding:10px 20px 12px;box-shadow:0 6px 0 0 {s["accentDark"]},6px 12px 0 0 {s["shadow"]}}}
.title{{position:absolute;top:428px;left:0;width:1080px;height:340px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:30px}}
.title div{{font-size:70px;line-height:88px;white-space:nowrap;text-shadow:7px 7px 0 {s["shadow"]}}}
.a{{position:relative;display:inline-block;line-height:70px}}{accents(s["cream"], s["shadow"])}
.ban{{background:{s["accent"]};padding:34px 16px 2px 22px;box-shadow:0 8px 0 0 {s["accentDark"]},9px 16px 0 0 {s["shadow"]};display:inline-block;line-height:76px}}
.frame{{position:absolute;left:80px;top:800px;width:920px;height:700px;border:10px solid {s["cream"]};border-radius:22px;overflow:hidden;box-shadow:16px 16px 0 0 {s["shadow"]};background:{s["shadow"]}}}
.frame img{{width:100%;height:100%;object-fit:cover;display:block}}
.handle{{position:absolute;top:1545px;width:1080px;text-align:center;font-family:Silk;font-weight:700;font-size:28px;letter-spacing:3px;color:{s["accent"]};text-shadow:3px 3px 0 {s["shadow"]}}}
</style><div class=st>{stars}</div><div class=band style="top:250px"></div><div class=band style="top:1658px"></div>
<div class=row><div class=tag>{html.escape(o.tag or c["serie"])}</div><div>#{o.num:02d}</div></div>
<div class=title>{"".join(f"<div>{line(l)}</div>" for l in o.line)}</div>
<div class=frame><img src="file://{os.path.abspath(o.image)}"></div><div class=handle>{html.escape(c["handle"].upper())}</div>'''
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as t: t.write(page)
    png = o.out + '.png'
    try:
        subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--allow-file-access-from-files', '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1080,1920', '--virtual-time-budget=4000', f'--screenshot={os.path.abspath(png)}', 'file://' + t.name], capture_output=True, timeout=120)
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', png, '-q:v', '2', o.out], check=True)
    finally:
        os.remove(t.name)
        if os.path.exists(png): os.remove(png)
    print(o.out)


if __name__ == '__main__':
    main()
