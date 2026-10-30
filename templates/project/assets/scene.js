// __TITLE__. render(t) precisa ser função pura do tempo.
(function () {
  const { popScale, withScale, creamTitle, banner, bubble, drawPerson, drawRobot, frame, profileCard, boxText, winFrame, paper, card, cursorAt, burst, checkBadge, star, lin, stp, bo, eo, rnd, CREAM, RED, K, INKP } = PX;
  const T = window.T, MAIN = '__MAIN__';

  // [texto, tipo ('c' creme | 'b' faixa), y, tamanho, início, fim]
  const TITLES = [
    ['ESCREVA', 'c', 300, 72, T.gancho, T.cena2],
    ['SEU GANCHO', 'b', 410, 54, T.gancho + 0.3, T.cena2],
  ];

  // Uma função por cena. Cada uma decide quando aparece, e nenhuma guarda estado.
  function cenaGancho(t) {
    if (t >= T.cena2) return;
    drawPerson(MAIN, 540, 1320, 18, { mouth: 'o', brow: 'up' });
    bubble('ESTE TEXTO QUEBRA A LINHA E SEMPRE CABE NA CAIXA', 90, 520, 900, 220, { size: 48 });
  }
  function cena2(t) {
    if (t < T.cena2 || t >= T.perfil) return;
    drawRobot(540, 1320, 18, { armL: 'n', armR: 'wave', wave: Math.floor(t * 4) % 2, eyes: 'happy', t });
  }

  function render(t) {
    frame(t);
    cenaGancho(t); cena2(t);
    for (const [s, k, y, sz, t0, t1] of TITLES) {
      withScale(540, y, popScale(t, t0, t1), 0, () => (k === 'c' ? creamTitle(s, 540, y, sz) : banner(s, 540, y, sz)));
    }
    profileCard(t, T.perfil, MAIN);
  }
  window.renderScene = render;
  render(0);
})();
