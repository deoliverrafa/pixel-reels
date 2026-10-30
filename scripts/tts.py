#!/usr/bin/env python3
"""Gera a narração no ElevenLabs e corrige o som abafado de vozes clonadas.

Uso: tts.py roteiro.txt saida.m4a
A chave vem de ELEVENLABS_API_KEY ou do arquivo indicado no config. Ela nunca é impressa.
"""
import json, os, re, subprocess, sys, tempfile, time, urllib.error, urllib.request
from common import load_config

EQ = 'highpass=f=80,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1.2:g=3,highshelf=f=7000:g=4,loudnorm=I=-16:TP=-1.5:LRA=7'


def main():
    if len(sys.argv) != 3: sys.exit(__doc__)
    cfg = load_config()['voz']; text = open(sys.argv[1], encoding='utf-8').read().strip()
    if cfg['voice_id'].startswith('COLE'): sys.exit('Configure voz.voice_id em ~/.config/pixel-reels/config.json')
    key = os.environ.get('ELEVENLABS_API_KEY') or open(os.path.expanduser(cfg['arquivo_chave'])).read().strip()
    for a, b in cfg.get('pronuncia', {}).items(): text = re.sub(rf'\b{re.escape(a)}\b', b, text)
    if not text.startswith('['): text = '[excited] ' + text  # uma marcação só: várias deixam a voz estranha
    body = json.dumps({'text': text, 'model_id': cfg['modelo'], 'voice_settings': {'stability': cfg['stability'], 'similarity_boost': cfg['similarity']}}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice_id']}?output_format=mp3_44100_128", body, {'xi-api-key': key, 'Content-Type': 'application/json'})
    for attempt in range(5):  # o plano limita requisições simultâneas (429)
        try:
            audio = urllib.request.urlopen(req, timeout=240).read(); break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4: time.sleep(15 * (attempt + 1)); continue
            sys.exit(f'ElevenLabs respondeu {e.code}: {e.read()[:200].decode(errors="ignore")}')
    with tempfile.NamedTemporaryFile(suffix='.mp3') as t:
        t.write(audio); t.flush()
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', t.name, '-af', EQ, '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', sys.argv[2]], check=True)
    print('narração:', sys.argv[2])


if __name__ == '__main__':
    main()
