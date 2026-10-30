#!/usr/bin/env python3
"""Desenha a folha de um personagem (expressões e poses) para aprovação.

Uso: character_sheet.py characters/nome.json saida.png
"""
import json, os, subprocess, sys, tempfile
from common import SKILL, chrome, load_config

POSES = [('NORMAL', {}), ('FELIZ', {'mouth': 'smile'}), ('SURPRESO', {'mouth': 'o', 'brow': 'up'}), ('SEM GRAÇA', {'mouth': 'wavy', 'brow': 'sorry'}), ('ACENANDO', {'armR': 'wave', 'wave': 1, 'mouth': 'grin'}), ('BRAÇOS PARA CIMA', {'armL': 'up', 'armR': 'up', 'mouth': 'grin'})]


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    ch = json.load(open(sys.argv[1], encoding='utf-8')); t = os.path.join(SKILL, 'templates', 'project')
    page = f'''<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:"Press Start 2P";src:url("file://{t}/assets/fonts/PressStart2P-latin.woff2")}}
@font-face{{font-family:"Silkscreen";font-weight:700;src:url("file://{t}/assets/fonts/Silkscreen-700.woff2")}}
@font-face{{font-family:"Silkscreen";font-weight:400;src:url("file://{t}/assets/fonts/Silkscreen-400.woff2")}}
*{{margin:0}}canvas{{display:block}}</style><canvas id=c width=1080 height=1920></canvas>
<script>window.PIXEL_STYLE={json.dumps(load_config()['estilo'])};window.PIXEL_CHARACTERS={{main:{json.dumps(ch)}}}</script>
<script src="file://{t}/assets/engine.js"></script><script>
document.fonts.load('700 40px Silkscreen').then(()=>document.fonts.load('40px "Press Start 2P"')).then(()=>{{
 const {{frame,drawPerson,creamTitle,txt,CREAM}}=PX; frame(1); creamTitle({json.dumps(ch.get('nome','PERSONAGEM').upper())},540,180,64);
 {json.dumps(POSES)}.forEach(([n,st],i)=>{{const x=i%2?780:300,y=660+Math.floor(i/2)*540;drawPerson('main',x,y,11,st);txt(n,x,y+50,40,CREAM,{{f:'sb',sh:3}});}});
 document.title='ok';
}});
</script>'''
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f: f.write(page)
    try:
        subprocess.run([chrome(), '--headless=new', '--disable-gpu', '--allow-file-access-from-files', '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1080,1920', '--virtual-time-budget=4000', f'--screenshot={os.path.abspath(sys.argv[2])}', 'file://' + f.name], capture_output=True, timeout=120)
    finally:
        os.remove(f.name)
    print(sys.argv[2])


if __name__ == '__main__':
    main()
