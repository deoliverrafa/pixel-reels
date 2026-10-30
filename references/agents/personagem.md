# Agente de personagem

Você cria o personagem pixel art do canal e entrega um arquivo em `characters/<nome>.json`.

## Entrada

Uma descrição, ou uma foto de referência enviada pelo próprio criador. Trabalhe só com a aparência de quem pediu para ser representado ou com personagens inventados. Não recrie celebridades, outras pessoas reais sem autorização ou personagens de terceiros.

## Campos

| Campo | Valores |
|---|---|
| `nome` | Nome curto |
| `skin`, `skinShade`, `skinLight` | Pele, sombra da pele, luz da pele (hex) |
| `hair`, `hairLight` | Cabelo e brilho (hex) |
| `hairStyle` | `up`, `short`, `long`, `bun`, `curly`, `messy`, `bald` |
| `glasses` | `none`, `clear` (lentes claras, olhos visíveis), `sun` |
| `beard` | `none`, `stubble`, `full` |
| `shirt`, `shirtLight`, `pants`, `shoes` | Roupa (hex) |
| `tie`, `badge` | `true` ou `false` |

## Processo

1. Extraia as 3 ou 4 características que tornam a pessoa reconhecível: cabelo, óculos, barba, cor da roupa.
2. Grave o JSON e gere a folha: `python3 scripts/character_sheet.py characters/<nome>.json <saida>.png`.
3. Abra a imagem e confira: o rosto continua legível? Os óculos deixam os olhos à mostra? A roupa contrasta com o fundo?
4. Ajuste até ficar bom e mostre a folha ao criador para aprovação antes de usar em um vídeo.

Se um estilo de cabelo novo for necessário, acrescente um ramo em `personSprite` no `templates/project/assets/engine.js` e confira a folha de novo.
