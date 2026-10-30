# Voz e áudio

## Voz

Duas opções:

1. **Gravação do criador.** Passe o arquivo direto para `new_project.py --audio`.
2. **ElevenLabs, com `scripts/tts.py`.** Configure `voz.voice_id` e a chave. Clone apenas a própria voz ou uma voz com autorização expressa da pessoa.

Configuração que funcionou bem em português:

- Modelo `eleven_v3`, stability `1.0`, similarity `0.8`.
- Uma única marcação `[excited]` no começo. Várias marcações deixam a voz estranha.
- Pontuação expressiva (! e ...) para variar a entonação.
- EQ contra som abafado, já aplicado pelo script.
- `voz.pronuncia` corrige palavras que a voz erra. Exemplo: `"Claude": "Clóde"`, senão sai "cloud".

Depois de gerar ou receber o áudio, transcreva com `words.py` e compare com o roteiro: pronúncia e texto. Mostre a narração ao criador antes de animar. Ao postar voz sintética, ative o rótulo de conteúdo de IA da plataforma.

**Chave:** nunca imprima, nunca coloque em arquivo do repositório, nunca passe na linha de comando.

## Efeitos

- Sintetizados em `sfx_bed.py`, um `put()` por batida da cena.
- `mix_audio.py` faz o ducking pela voz e calibra o volume por medição.
- **Meta na média: efeitos sozinhos 18 a 22 dB abaixo da voz.** Menos de 15 dB incomoda e passa por cima da fala. Com poucos efeitos, é aceitável até 30 dB; acima disso ninguém ouve.
- **Meta nas batidas, em janelas de 200 ms: durante a fala, efeito ao menos 6 dB abaixo da voz; na pausa, ao menos 3 dB abaixo da média da voz.** A média sozinha engana: com poucos efeitos, ela fica baixa mesmo quando uma batida cobre uma palavra. O script mede as duas coisas e dá prioridade à batida.
- O ganho de cada `put()` é relativo, porque o arquivo é normalizado pela batida mais forte. Se uma batida segura o volume de tudo, reduza o ganho dela.
- Volume fixo não funciona, porque cada voz tem um nível. Sempre meça.
