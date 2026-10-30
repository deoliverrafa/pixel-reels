#!/usr/bin/env python3
"""Renderiza, junta o áudio e monta a pasta de entrega sem apagar nada.

Uso: finish.py <projeto> --name nome-do-video --folder "Pasta de entrega" [--skip-render]
Precisa de work/capa.jpg e da descrição em roteiro.json (ou work/descricao.txt).
"""
import argparse, glob, json, os, shutil, subprocess, sys, time
from common import HYPERFRAMES, load_config


def run(*c, **k): subprocess.run(c, check=True, **k)


def main():
    a = argparse.ArgumentParser(); a.add_argument('project'); a.add_argument('--name', required=True); a.add_argument('--folder', required=True); a.add_argument('--skip-render', action='store_true'); o = a.parse_args()
    p = os.path.abspath(o.project)
    desc = None
    if os.path.exists(f'{p}/work/descricao.txt'): desc = open(f'{p}/work/descricao.txt', encoding='utf-8').read()
    elif os.path.exists(f'{p}/roteiro.json'): desc = json.load(open(f'{p}/roteiro.json', encoding='utf-8')).get('descricao')
    missing = [n for n, ok in [('work/capa.jpg', os.path.exists(f'{p}/work/capa.jpg')), ('work/mix.wav', os.path.exists(f'{p}/work/mix.wav')), ('descrição (roteiro.json ou work/descricao.txt)', desc)] if not ok]
    if missing: sys.exit('Falta antes de entregar: ' + ', '.join(missing))
    base = f'{p}/renders/base.mp4'; final = f'{p}/renders/{o.name}.mp4'; phone = f'{p}/renders/{o.name}-celular.mp4'
    if not o.skip_render: run('npx', '--yes', HYPERFRAMES, 'render', '-o', 'renders/base.mp4', '--quality', 'high', cwd=p)
    run('ffmpeg', '-loglevel', 'error', '-y', '-i', base, '-i', f'{p}/work/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', final)
    run('ffmpeg', '-loglevel', 'error', '-y', '-i', final, '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264', '-crf', '20', '-c:a', 'copy', phone)
    out = os.path.join(os.path.expanduser(load_config()['pasta_entrega']), o.folder)
    for d in ('', 'versoes anteriores', 'para o CapCut', 'narracao'): os.makedirs(os.path.join(out, d), exist_ok=True)
    stamp = time.strftime('%Y%m%d-%H%M%S')
    for src, dst in [(final, f'{o.name}.mp4'), (phone, f'{o.name}-celular.mp4'), (f'{p}/work/efeitos.wav', 'para o CapCut/efeitos-sonoros-separados.wav'), (f'{p}/work/capa.jpg', 'capa.jpg')]:
        d = os.path.join(out, dst)
        if os.path.exists(d): shutil.move(d, os.path.join(out, 'versoes anteriores', f'{stamp}-{os.path.basename(dst)}'))
        shutil.copy(src, d)
    for f in glob.glob(f'{p}/src/*'): shutil.copy(f, os.path.join(out, 'narracao'))
    open(os.path.join(out, 'descricao-instagram.txt'), 'w', encoding='utf-8').write(desc.strip() + '\n')
    print('entregue em', out)


if __name__ == '__main__':
    main()
