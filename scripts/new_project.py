#!/usr/bin/env python3
"""Cria o projeto de um vídeo a partir do molde.

Uso: new_project.py <pasta> --title "Título" --audio narracao.m4a [--character rafa] [--roteiro roteiro.json] [--extra 1.5]
"""
import argparse, glob, json, os, shutil, sys
from common import SKILL, duration, load_config


def character(name):
    path = name if os.path.exists(name) else os.path.join(SKILL, 'characters', name + '.json')
    if not os.path.exists(path): sys.exit(f'Personagem não encontrado: {name}')
    data = json.load(open(path, encoding='utf-8'))
    return os.path.splitext(os.path.basename(path))[0], data


def main():
    a = argparse.ArgumentParser(); a.add_argument('folder'); a.add_argument('--title', required=True); a.add_argument('--audio', required=True)
    a.add_argument('--character', action='append', default=[]); a.add_argument('--extra', type=float, default=1.5); a.add_argument('--roteiro')
    o = a.parse_args()
    if os.path.exists(o.folder) and os.listdir(o.folder): sys.exit(f'A pasta já existe e não está vazia: {o.folder}')
    shutil.copytree(os.path.join(SKILL, 'templates', 'project'), o.folder, dirs_exist_ok=True)
    for d in ('src', 'work', 'renders', 'review'): os.makedirs(os.path.join(o.folder, d), exist_ok=True)
    ext = os.path.splitext(o.audio)[1]; shutil.copy(o.audio, os.path.join(o.folder, 'src', 'narracao' + ext))
    dur = round(duration(o.audio) + o.extra, 1)  # respiro no final: o card do perfil não pode ser cortado
    if o.roteiro: shutil.copy(o.roteiro, os.path.join(o.folder, 'roteiro.json'))
    cfg = load_config(); chars = dict(character(c) for c in (o.character or ['rafa']))
    rep = {'__DURATION__': str(dur), '__TITLE__': o.title, '__MAIN__': next(iter(chars)), '__PERFIL__': str(round(max(dur - 3.5, 0), 1)), '__HANDLE__': json.dumps(cfg['handle']), '__STYLE__': json.dumps(cfg['estilo']), '__CHARACTERS__': json.dumps(chars, ensure_ascii=False)}
    for f in glob.glob(os.path.join(o.folder, '**', '*'), recursive=True):
        if f.endswith(('.html', '.js', '.py')) and not f.endswith('engine.js'):
            s = open(f, encoding='utf-8').read()
            for k, v in rep.items(): s = s.replace(k, v)
            open(f, 'w', encoding='utf-8').write(s)
    print(f'Projeto criado em {o.folder} ({dur} s, personagens: {", ".join(chars)})')


if __name__ == '__main__':
    main()
