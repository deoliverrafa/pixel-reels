#!/usr/bin/env bash
# Prepara o ambiente do pixel-reels: confere programas e cria o .venv com as bibliotecas Python.
set -e
cd "$(dirname "$0")/.."
for c in node ffmpeg ffprobe python3; do command -v "$c" >/dev/null || { echo "Falta instalar: $c"; exit 1; }; done
node -e 'process.exit(parseInt(process.versions.node) >= 22 ? 0 : 1)' || { echo "Precisa do Node 22 ou mais novo"; exit 1; }
python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q numpy faster-whisper
mkdir -p ~/.config/pixel-reels
[ -f ~/.config/pixel-reels/config.json ] || cp config.example.json ~/.config/pixel-reels/config.json
echo "Pronto. Edite ~/.config/pixel-reels/config.json com o seu perfil e a sua voz."
