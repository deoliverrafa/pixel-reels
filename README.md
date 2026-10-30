# Pixel Reels

Skill para o [Claude Code](https://claude.com/claude-code) que cria Reels verticais animados em pixel art, do roteiro à pasta de entrega.

Você pede o vídeo, e uma equipe de agentes faz o resto:

| Agente | O que faz |
|---|---|
| **Roteirista** | Pesquisa os fatos e escreve gancho, desenvolvimento e finalização |
| **Personagem** | Cria o seu personagem em pixel art a partir de uma descrição ou foto |
| **Produtor** | Anima as cenas sincronizadas com cada palavra, cria os efeitos sonoros e a capa |
| **Revisor** | Procura erros de forma independente e reprova o vídeo até ficar bom |

![Exemplo de personagem](docs/personagem.png)

## Instalação

Você precisa de Claude Code, Node 22+, Python 3, ffmpeg e Google Chrome.

```bash
git clone https://github.com/deoliverrafa/pixel-reels ~/.claude/skills/pixel-reels
~/.claude/skills/pixel-reels/scripts/setup.sh
```

Edite `~/.config/pixel-reels/config.json` com o seu perfil, a sua série e as suas cores.

## Como usar

No Claude Code:

```
/pixel-reels faça um vídeo explicando como criar uma skill no Claude
```

Ou peça com as suas palavras: "cria um Reel em pixel art sobre X". Se quiser usar a sua voz, grave o áudio e passe o arquivo:

```
/pixel-reels anima este áudio: ~/Downloads/minha-gravacao.m4a
```

Para criar um personagem:

```
/pixel-reels cria meu personagem: cabelo cacheado, óculos redondos, camiseta verde
```

## O que você recebe

- Vídeo 1080x1920 e cópia menor para celular
- Capa e descrição do post
- Efeitos sonoros separados para editar no CapCut
- Narração

## Narração com a sua voz (opcional)

Precisa de uma conta paga no [ElevenLabs](https://elevenlabs.io) para clonar a voz. Salve a chave com permissão restrita e coloque o ID da voz no config:

```bash
pbpaste > ~/.elevenlabs_key && chmod 600 ~/.elevenlabs_key
```

Clone só a sua própria voz ou a de alguém que autorizou. Ao postar, ative o rótulo de conteúdo de IA da plataforma. Sem ElevenLabs, basta gravar o áudio no celular.

## O verificador de texto

`scripts/audit_text.py` percorre o vídeo inteiro e mede cada texto desenhado. Ele aponta o que sai da caixa, sai do quadro, fica fora da zona segura ou está pequeno demais. Isso pega erros que uma revisão visual rápida deixa passar.

## Personalização

- **Cores:** `estilo` no config
- **Personagens:** arquivos em `characters/`
- **Agentes:** instruções em `references/agents/`
- **Regras de estilo, áudio e capa:** `references/`

## Problemas comuns

**`Falta instalar: node` (ou `ffmpeg`, `ffprobe`, `python3`)**
O `setup.sh` não achou o programa no PATH. O `ffprobe` vem junto com o `ffmpeg`. Instale e rode o setup de novo:

```bash
brew install node ffmpeg python            # macOS
sudo apt install nodejs ffmpeg python3     # Ubuntu/Debian
```

**`Precisa do Node 22 ou mais novo`**
O Node instalado é antigo (o do `apt` costuma ser). Instale uma versão nova pelo [nvm](https://github.com/nvm-sh/nvm) e abra um terminal novo:

```bash
nvm install 22 && nvm alias default 22
```

**`Permission denied` ao rodar o `setup.sh`**
O arquivo perdeu a permissão de execução. Rode com `bash ~/.claude/skills/pixel-reels/scripts/setup.sh`.

**`ensurepip is not available` ou erro ao criar o `.venv`**
No Ubuntu/Debian o módulo de ambientes virtuais vem separado. Instale com `sudo apt install python3-venv`, apague a pasta `.venv` da skill e rode o setup de novo.

**Erro no `pip install` do `faster-whisper`**
Normalmente é falta de internet ou uma versão do Python nova demais para as bibliotecas dele. Confira a conexão; se persistir, use o Python 3.12, apague o `.venv` e rode o setup de novo.

**`ModuleNotFoundError: No module named 'numpy'`**
O script rodou com o `python3` do sistema em vez do `.venv`. Os scripts `words.py`, `mix_audio.py` e `sfx_bed.py` precisam de `.venv/bin/python`. Se o `.venv` não existir, rode o setup.

**`Chrome não encontrado. Instale o Google Chrome.`**
Os scripts procuram o Chrome em `/Applications/Google Chrome.app` (macOS) ou pelos comandos `google-chrome`, `chromium`, `chromium-browser` e `chrome`. No Linux, confira se um deles responde no terminal (por exemplo, `google-chrome --version`).

**A skill não aparece no Claude Code**
A pasta precisa estar em `~/.claude/skills/pixel-reels`, com o `SKILL.md` direto dentro dela. Se você clonou em outro lugar, mova a pasta e reinicie o Claude Code.

**O `npx hyperframes` trava ou falha na primeira renderização**
O HyperFrames é baixado na hora do primeiro uso, então precisa de internet. Se der erro de cache do npm, rode `npm cache verify` e tente de novo.

**`JSONDecodeError` ao rodar qualquer script**
O `~/.config/pixel-reels/config.json` tem um erro de digitação, como vírgula sobrando ou aspas faltando. Valide com `python3 -m json.tool ~/.config/pixel-reels/config.json`.

**`Configure voz.voice_id` ou erro `401` do ElevenLabs**
Só acontece se você usa narração com a sua voz. Coloque o ID da voz em `voz.voice_id` e confira se a chave em `~/.elevenlabs_key` está certa e sem espaços extras. O erro `429` significa limite de requisições do plano; o script já espera e tenta de novo sozinho.

**`pbpaste: command not found`**
O `pbpaste` só existe no macOS. No Linux, use `xclip -o -selection clipboard > ~/.elevenlabs_key` ou cole a chave num editor, e depois rode `chmod 600 ~/.elevenlabs_key`.

## Limites

- Os vídeos são animados por código, então cada vídeo consome uso do Claude Code. Vídeos com vários agentes consomem bem mais do que uma conversa comum.
- Confira sempre os fatos e os passos antes de publicar. Menus de produtos mudam.

## Créditos e licença

Código sob [licença MIT](LICENSE). Fontes Press Start 2P e Silkscreen sob [SIL Open Font License](templates/project/assets/fonts). Renderização com [HyperFrames](https://www.npmjs.com/package/hyperframes), baixado na hora de usar e sujeito à licença dele.

Projeto independente de [@aprendaclaude](https://instagram.com/aprendaclaude). Não é oficial e não tem vínculo com a Anthropic.
