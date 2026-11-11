"""Estilo e interação offline do relatório exportado."""

ESTILO = """
:root { color-scheme: light; --ink:#122d30; --muted:#52696b; --border:#dce6e5; }
* { box-sizing: border-box; }
body { margin:0; background:#edf3f3; color:var(--ink); font:16px/1.5 "Segoe UI",system-ui,sans-serif; }
.container { max-width:1240px; margin:auto; padding-inline:clamp(16px,4vw,48px); }
.capa { background:#102e32; color:#f4fbfa; padding:28px 0 60px; }
.marca { display:flex; align-items:center; gap:10px; font-weight:700; margin:0 0 22px; }
.marca span { background:#94e0cb; color:#123a33; font-size:.78rem; border-radius:8px; padding:5px 7px; }
h1 { margin:0; font-size:clamp(2rem,4vw,3.3rem); letter-spacing:-.04em; line-height:1.1; }
h2 { margin:0; font-size:1.35rem; letter-spacing:-.02em; }
.arquivo { font-size:1.15rem; margin:12px 0 0; overflow-wrap:anywhere; }
.data { color:#a9c5c4; margin:4px 0 0; }
.resumo { margin:-32px 0 20px; position:relative; display:grid; grid-template-columns:repeat(5,1fr);
  background:#fff; border:1px solid var(--border); border-radius:14px; box-shadow:0 6px 20px #132e3210; }
.resumo div { padding:15px 18px; border-inline-end:1px solid var(--border); }
.resumo div:last-child { border:0; }
dt,.muted { color:var(--muted); font-size:.9rem; }
dd { margin:2px 0 0; overflow-wrap:anywhere; }
.resumo dd { font-size:1.85rem; font-weight:750; font-variant-numeric:tabular-nums; }
.painel { background:#fff; border:1px solid var(--border); border-radius:14px; padding:clamp(14px,2vw,26px); margin-bottom:20px; }
.titulo-lista { display:flex; justify-content:space-between; align-items:start; gap:12px; }
.titulo-lista p { margin:4px 0 0; }
.filtros { display:grid; grid-template-columns:2fr 1fr 1fr; gap:12px; margin-top:18px; }
label { font-size:.84rem; font-weight:650; }
input,select,button { font:inherit; color:inherit; border:1px solid #a8bcba; border-radius:8px; background:#fff; padding:8px 10px; }
label input,label select { display:block; width:100%; margin-top:4px; font-weight:400; }
button { cursor:pointer; font-size:.89rem; font-weight:650; white-space:nowrap; }
:focus-visible { outline:2px solid #08765e; outline-offset:2px; }
.tabela { overflow:auto; }
table { border-collapse:collapse; width:100%; text-align:left; font-size:.89rem; }
thead { background:#edf5f4; }
th,td { padding:11px 10px; border-bottom:1px solid var(--border); vertical-align:top; }
tbody th { font-weight:650; }
tbody tr:nth-child(even) { background:#f8fbfb; }
small { display:block; color:var(--muted); font-weight:400; }
.num { white-space:nowrap; text-align:right; font-variant-numeric:tabular-nums; }
.desvio { color:#80512b; font-weight:700; }
.estado { display:inline-block; border-radius:6px; padding:2px 7px; font-weight:650; font-size:.8rem; }
.pendente { color:#75470d; background:#fff1d7; }
.anomalia_confirmada { color:#8a303a; background:#fde8ec; }
.situacao_justificada { color:#125e4d; background:#e4f4ec; }
summary { color:#07634f; cursor:pointer; font-weight:650; white-space:nowrap; }
.evidencia { min-width:170px; max-width:320px; overflow-wrap:anywhere; }
.evidencia ul { padding-inline-start:1.2em; margin:.35em 0; }
.evidencia p { margin:.35em 0; }
.nota { border-inline-start:2px solid #81c8b4; padding-inline-start:.5em; white-space:pre-wrap; }
.vazio { text-align:center; padding:16px; }
.parametros dl { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
@media (max-width:760px) {
  .resumo { grid-template-columns:repeat(2,1fr); }
  .filtros,.parametros dl { grid-template-columns:1fr; }
  .titulo-lista { flex-wrap:wrap; }
}
@media print {
  body { background:#fff; font-size:10pt; }
  .capa { background:#fff; color:#122d30; padding:0 0 12px; }
  .data { color:var(--muted); }
  .container { padding:0; }
  .resumo { margin:0 0 12px; box-shadow:none; grid-template-columns:repeat(5,1fr); }
  .resumo div { padding:6px; }
  .resumo dd { font-size:16pt; }
  .painel { padding:8px 0; border:0; }
  .filtros,button,#contagem,#vazio { display:none; }
  .tabela { overflow:visible; }
  table { font-size:8pt; }
  th,td { padding:4px; }
  tr { break-inside:avoid; }
  .evidencia { min-width:0; max-width:none; }
  summary { display:none; }
  .parametros { break-inside:avoid; }
}
"""

INTERACAO = r"""
const corpo = document.getElementById('linhas');
const linhas = Array.from(corpo.rows);
const busca = document.getElementById('busca');
const estado = document.getElementById('classificacao');
const ordem = document.getElementById('ordem');
const total = document.getElementById('contagem');
const vazio = document.getElementById('vazio');
const pt = new Intl.NumberFormat('pt-BR');
const normalizar = texto => texto.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
const termos = linhas.map(linha =>
  normalizar(linha.cells[0].textContent + ' ' + linha.cells[1].textContent)
);

function filtrar() {
  const chaves = normalizar(busca.value.trim()).split(/\s+/);
  let visiveis = 0;
  linhas.forEach((linha, i) => {
    linha.hidden = (estado.value && linha.dataset.estado !== estado.value)
      || !chaves.every(chave => termos[i].includes(chave));
    if (!linha.hidden) visiveis += 1;
  });
  total.textContent = `${pt.format(visiveis)} de ${pt.format(linhas.length)} alertas`;
  vazio.hidden = visiveis !== 0;
}
busca.addEventListener('input', filtrar);
estado.addEventListener('change', filtrar);
ordem.addEventListener('change', () => {
  const sinal = ordem.value === 'menor' ? 1 : -1;
  [...linhas].sort((a, b) => sinal * (Number(a.dataset.desvio) - Number(b.dataset.desvio)))
    .forEach(linha => corpo.appendChild(linha));
});
document.getElementById('imprimir').addEventListener('click', () => window.print());
let detalhes;
window.addEventListener('beforeprint', () => {
  detalhes = Array.from(corpo.querySelectorAll('details'))
    .filter(item => !item.closest('tr').hidden)
    .map(item => [item, item.open]);
  detalhes.forEach(([item]) => { item.open = true; });
});
window.addEventListener('afterprint', () => {
  if (detalhes) detalhes.forEach(([item, aberto]) => { item.open = aberto; });
});
"""
