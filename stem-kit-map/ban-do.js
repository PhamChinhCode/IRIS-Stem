/* Bản đồ kit STEM: giao diện ba tab Dự án / Module / Bảng tổng hợp, sơ đồ nối và khung 3D.
   Cần trước: three.js (window.THREE, gói vendor/three.bundle.min.js) và du-lieu.js.
   Trang chỉ cần một phần tử <div id="kit-map" class="kit-map">; tệp này tự dựng phần còn lại.
   window.KIT_GOC: thư mục chứa mo-hinh/, hinh/, tai-lieu/ khi trang không nằm cùng thư mục (web IRIS Lab đặt 'assets/stem/'). */
const GOC = window.KIT_GOC || '';
document.getElementById('kit-map').innerHTML = `
  <div class="km-facts" id="facts"></div>
  <div class="km-tabs" role="tablist" aria-label="Chế độ xem">
    <button role="tab" id="tab-proj" data-tab="proj" aria-selected="true">Dự án</button>
    <button role="tab" id="tab-mod" data-tab="mod" aria-selected="false">Module</button>
    <button role="tab" id="tab-mat" data-tab="mat" aria-selected="false">Bảng tổng hợp</button>
  </div>
  <section class="view" id="v-proj">
    <div class="levels" id="levels"></div>
    <div class="picks" id="picks"></div>
    <article class="panel" id="pdetail"></article>
  </section>
  <section class="view" id="v-mod" hidden>
    <article class="panel" id="mdetail"></article>
    <div id="mlist" class="view"></div>
  </section>
  <section class="view" id="v-mat" hidden>
    <p class="km-lede">Mỗi chấm là một module được dùng trong dự án ở cột đó. Bấm số dự án hoặc tên module để xem chi tiết.</p>
    <div class="scroll" id="matrix"></div>
    <div class="legend" id="tlegend"></div>
  </section>`;

const modsOf = p => {
  const s = new Set(['C1']);
  if (p.pw === 'bat') s.add('C2');
  Object.values(p.c).forEach(v => [].concat(v).forEach(m => s.add(m)));
  (p.extra || []).forEach(m => s.add(m));
  (p.k || []).forEach(m => s.add(m));
  return s;
};
const USES = {};
Object.keys(M).forEach(m => USES[m] = []);
P.forEach(p => modsOf(p).forEach(m => USES[m].push(p.id)));

const state = {tab:'proj', lv:1, proj:10, mod:'S1'};
const $ = id => document.getElementById(id);

const chip = (m, att, pressed) =>
  `<button class="chip t-${M[m].t}" data-mod="${m}"${pressed ? ' aria-pressed="true"' : ''}><span class="code">${m}</span><span>${M[m].n}</span>${att ? `<span class="att">${att}</span>` : ''}</button>`;
const pick = (p, pressed) =>
  `<button class="pick" data-proj="${p.id}" aria-pressed="${pressed}"><span class="num">${p.id}</span>${p.n}</button>`;

function row(label, pcls, wcls, items) {
  if (!items.length) return `<div class="row off"><span class="port ${pcls}">${label}</span><span class="empty">trống</span></div>`;
  return `<div class="row"><span class="port ${pcls}">${label}</span><div class="run ${wcls}">${items.map(h => `<span class="w"></span>${h}`).join('')}</div></div>`;
}

function renderProject() {
  const p = P.find(x => x.id === state.proj), lv = LV[p.lv], c = p.c;
  const att = m => (p.att && p.att[m]) || ATT[m];
  const one = m => m ? [chip(m, att(m))] : [];
  let rows = `<div class="row"><span class="bhead">C1<br>BO CHỦ</span><span></span></div>`;
  rows += row('NGUỒN', 'p-pwr', 'wc-pwr', [p.pw === 'bat' ? chip('C2', c.I2C && c.I2C.includes('S1') ? '7,4 V sang S1' : (c.I2C && c.I2C.includes('O7') ? '7,4 V sang O7' : '')) : `<span class="note">${PW[p.pw]}</span>`]);
  DA.forEach(k => rows += row(k, 'p-da', 'wc-da', one(c[k])));
  rows += row('I2C', 'p-i2c', 'wc-i2c', (c.I2C || []).map(m => chip(m, att(m))));
  rows += row('SPI', 'p-spi', 'wc-spi', one(c.SPI));
  rows += row('SERVO', 'p-sv', 'wc-sv', (c.SV || []).map(m => chip(m)));
  rows += row('TRÊN BO', 'p-on', 'wc-da', (p.on || []).map(t => `<span class="note">${t}</span>`));
  rows += row('WIFI', 'p-on', 'wc-da', p.wifi ? [`<span class="note">${p.wifi}</span>`] : []);
  const count = [...modsOf(p)].filter(m => M[m].t !== 'mech').length;
  $('pdetail').innerHTML = `
    <div class="group">
      <h2>${p.id} · ${p.n}</h2>
      <p class="meta">Cấp ${p.lv + 1}: ${lv.n} · ${lv.age}${p.open ? '' : ` · ${count} module điện tử`}</p>
    </div>
    <p class="what">${p.d}</p>
    <p class="stem"><b>Kiến thức STEM:</b> ${p.stem}</p>
    ${p.open ? '<p class="note">Không có sơ đồ cố định. Học sinh chọn module ở tab Module và tự thiết kế cách nối.</p>' : `
    ${window.THREE ? `<div class="group" id="g3d"><h3>Mô hình 3D</h3>
      <div class="km-stage" id="stage"><div class="mode"><button data-view3d="cad" aria-pressed="${view3d === 'cad'}">Mô hình CAD</button><button data-view3d="so" aria-pressed="${view3d === 'so'}">Sơ đồ khối</button></div><div class="zoom"><button data-zoom="0.85" aria-label="Phóng to">+</button><button data-zoom="1.18" aria-label="Thu nhỏ">−</button></div></div>
      <p class="km-hint">Kéo để xoay, bấm + hoặc − để phóng to, thu nhỏ. «Mô hình CAD» là bản thiết kế cơ khí đúng tỉ lệ, ở cấu hình đầy đủ của nhóm dự án. «Sơ đồ khối» chỉ gồm các module của riêng dự án này, kèm nhãn mã module như trong sơ đồ nối bên dưới.</p></div>` : ''}
    <div class="group"><h3>Sơ đồ nối</h3><div class="dg">${rows}</div></div>
    ${p.k ? `<div class="extra"><span>Cơ khí:</span>${p.k.map(m => chip(m)).join('')}</div>` : ''}
    <div class="legend">
      <span class="wc-da"><i></i>Cổng D/A</span><span class="wc-i2c"><i></i>I2C, nối chuỗi</span>
      <span class="wc-spi"><i></i>SPI</span><span class="wc-sv"><i></i>Servo</span><span class="wc-pwr"><i></i>Nguồn</span>
    </div>`}`;
  if (!p.open) mount3d(p);
}

function renderProjTab() {
  $('levels').innerHTML = LV.map((l, i) =>
    `<button data-lv="${i}" aria-pressed="${i === state.lv}"><span class="lvn">Cấp ${i + 1} · ${l.n}</span><small>${l.age} · ${l.s}</small></button>`).join('');
  $('picks').innerHTML = P.filter(p => p.lv === state.lv).map(p => pick(p, p.id === state.proj)).join('');
  renderProject();
}

function renderModTab() {
  const m = state.mod, o = M[m], u = USES[m];
  const byLv = LV.map((l, i) => ({l, i, ps: P.filter(p => p.lv === i && u.includes(p.id))})).filter(g => g.ps.length);
  $('mdetail').innerHTML = `
    <div class="group">
      <span class="badge t-${o.t}">${TYPES[o.t]}</span>
      <h2>${m} · ${o.n}</h2>
    </div>
    <p class="what">${o.d}</p>
    <dl class="kv"><dt>Cách nối</dt><dd>${o.port}</dd><dt>Số dự án dùng</dt><dd>${u.length} / ${P.length}</dd><dt class="ktd" hidden>Kích thước bao</dt><dd class="ktd" id="kt" hidden></dd>${
      (window.TAI_LIEU || {})[m] ? `<dt>Tài liệu</dt><dd><a href="${GOC}tai-lieu/${m}.pdf?v=${TAI_LIEU[m]}" target="_blank" rel="noopener">${m}.pdf</a></dd>` : ''}</dl>
    ${window.THREE && coMoHinh(m) ? `<div class="group" id="g3d"><h3>Mô hình 3D</h3>
      <div class="km-stage" id="stage"><div class="zoom"><button data-zoom="0.85" aria-label="Phóng to">+</button><button data-zoom="1.18" aria-label="Thu nhỏ">−</button></div></div>
      <p class="km-hint">Kéo để xoay, bấm + hoặc − để phóng to, thu nhỏ. Mô hình đúng tỉ lệ; bo mang hiện kèm đế và nắp in 3D.</p></div>` : ''}
    ${o.t === 'mech' ? '' : `<div class="group" id="gshots"><h3>Sơ đồ nguyên lý và mạch in</h3><div class="shots">
      <figure><a href="${hinh(m + '-so-do')}" target="_blank" rel="noopener"><img src="${hinh(m + '-so-do')}" alt="Sơ đồ nguyên lý ${m}" loading="lazy"></a><figcaption>Sơ đồ nguyên lý. Bấm để mở cỡ lớn.</figcaption></figure>
      <figure><a href="${hinh(m + '-pcb')}" target="_blank" rel="noopener"><img src="${hinh(m + '-pcb')}" alt="Mạch in ${m}, mặt trên" loading="lazy"></a><figcaption>Mạch in, mặt trên.</figcaption></figure>
    </div></div>`}
    ${byLv.map(g => `<div class="group"><h3>Cấp ${g.i + 1} · ${g.l.n}</h3><div class="picks">${g.ps.map(p => pick(p, false)).join('')}</div></div>`).join('')}`;
  $('mlist').innerHTML = Object.keys(TYPES).map(t =>
    `<div class="group"><h3>${TYPES[t]}</h3><div class="picks">${Object.keys(M).filter(k => M[k].t === t).map(k =>
      `<button class="chip t-${t}" data-mod="${k}" aria-pressed="${k === m}"><span class="code">${k}</span><span>${M[k].n}</span><span class="cnt">${USES[k].length}</span></button>`).join('')}</div></div>`).join('');
  // hình nào chưa có thì ẩn ô đó; không còn hình nào thì ẩn cả nhóm
  document.querySelectorAll('#gshots img').forEach(im => im.addEventListener('error', () => {
    im.closest('figure').remove();
    const g = $('gshots'); if (g && !g.querySelector('figure')) g.remove();
  }));
  if (coMoHinh(m)) mount3d({mod:m});
}

function renderMatrix() {
  const start = id => { const p = P.find(x => x.id === id), i = P.indexOf(p); return i === 0 || P[i - 1].lv !== p.lv ? ' lvstart' : ''; };
  $('matrix').innerHTML = `<table><thead><tr><th class="corner">Module \\ Dự án</th>${P.map(p =>
      `<th class="${start(p.id).trim()}"><button data-proj="${p.id}" title="${p.n}" aria-label="Dự án ${p.id}: ${p.n}">${p.id}</button></th>`).join('')}</tr></thead><tbody>${
    Object.keys(M).map(m => `<tr class="t-${M[m].t}"><th class="mh"><button data-mod="${m}"><span class="code">${m}</span>${M[m].n}</button></th>${P.map(p =>
      `<td class="${start(p.id).trim()}">${USES[m].includes(p.id) ? '<i></i>' : ''}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  $('tlegend').innerHTML = Object.keys(TYPES).map(t => `<span class="t-${t}"><span class="dot"></span>${TYPES[t]}</span>`).join('');
}

function render() {
  ['proj', 'mod', 'mat'].forEach(t => {
    $('v-' + t).hidden = state.tab !== t;
    $('tab-' + t).setAttribute('aria-selected', state.tab === t);
  });
  if (state.tab !== 'proj') $('pdetail').innerHTML = '';      // hai tab dùng chung một khung 3D (#stage)
  if (state.tab !== 'mod') $('mdetail').innerHTML = '';
  if (state.tab === 'proj') renderProjTab();
  else if (state.tab === 'mod') renderModTab();
  else renderMatrix();
}

document.getElementById('kit-map').addEventListener('click', e => {
  const b = e.target.closest('button');
  if (!b) return;
  const d = b.dataset;
  if (d.zoom) { zoom3d(+d.zoom); return; }
  if (d.view3d) {
    view3d = d.view3d;
    document.querySelectorAll('[data-view3d]').forEach(x => x.setAttribute('aria-pressed', x.dataset.view3d === view3d));
    if (R3 && cur3d) build3d(cur3d);
    return;
  }
  if (d.tab) state.tab = d.tab;
  else if (d.lv !== undefined) { state.lv = +d.lv; state.proj = P.find(p => p.lv === state.lv).id; }
  else if (d.proj) { state.proj = +d.proj; state.lv = P.find(p => p.id === state.proj).lv; state.tab = 'proj'; }
  else if (d.mod) { state.mod = d.mod; state.tab = 'mod'; }
  else return;
  render(); ghiHash();
  if (d.proj || d.mod) document.querySelector('.km-tabs').scrollIntoView({block:'start', behavior:'auto'});
});

/* Link sâu: #du-an-11, #module-I1, #bang-tong-hop — trang khác trỏ thẳng tới một dự án hoặc module. */
function docHash() {
  const h = decodeURIComponent(location.hash.slice(1)); let k;
  if ((k = h.match(/^du-an-(\d+)$/)) && P.some(p => p.id === +k[1])) { state.proj = +k[1]; state.lv = P.find(p => p.id === state.proj).lv; state.tab = 'proj'; }
  else if ((k = h.match(/^module-(\w+)$/)) && M[k[1]]) { state.mod = k[1]; state.tab = 'mod'; }
  else if (h === 'bang-tong-hop') state.tab = 'mat';
  else return false;
  return true;
}
function ghiHash() {
  history.replaceState(null, '', '#' + (state.tab === 'proj' ? 'du-an-' + state.proj : state.tab === 'mod' ? 'module-' + state.mod : 'bang-tong-hop'));
}
window.addEventListener('hashchange', () => { if (docHash()) render(); });

/* ---------- Mô hình 3D ---------- */
const T3 = {core:0x2f5be0, smart:0x7c3aed, in:0x0891b2, out:0xea6a1f, mech:0x8a8f99};
const SIZE = {C1:[8,6], C2:[7,4], S1:[5,4], S2:[9,1.6], O7:[6,3], I13:[4,6], I4:[4,4], O2:[6,1.2], O3:[3,3]};
const PI = Math.PI;
let R3 = null, G = null, sway = null, az = .75, el = .5, dist = 62, auto = true, ty = 4, view3d = 'cad', cur3d = null;
const v = (x, y, z) => new THREE.Vector3(x, y, z);
const mat = c => new THREE.MeshLambertMaterial({color:c});
const glow = c => new THREE.MeshLambertMaterial({color:c, emissive:c, emissiveIntensity:.75});
function add(geo, c, x, y, z, p) { const m = new THREE.Mesh(geo, c.isMaterial ? c : mat(c)); m.position.set(x, y, z); (p || G).add(m); return m; }
const box = (w, h, d, c, x, y, z, p) => add(new THREE.BoxGeometry(w, h, d), c, x, y, z, p);
const cyl = (r, h, c, x, y, z, p, rt) => add(new THREE.CylinderGeometry(rt === undefined ? r : rt, r, h, 24), c, x, y, z, p);
const ball = (r, c, x, y, z, p) => add(new THREE.SphereGeometry(r, 18, 12), c, x, y, z, p);
const lay = m => { m.rotation.x = PI / 2; return m; };
function rod(a, b, r, c, p) {
  const d = v(0, 0, 0).subVectors(b, a), m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, d.length(), 8), mat(c));
  m.position.copy(a).addScaledVector(d, .5);
  m.quaternion.setFromUnitVectors(v(0, 1, 0), d.clone().normalize());
  (p || G).add(m); return m;
}
const ground = (w, d, c) => box(w, .5, d, c || 0xdfe4e2, 0, -.25, 0);

function label(code, x, y, z, p) {
  const c = document.createElement('canvas'); c.width = 128; c.height = 64;
  const k = c.getContext('2d'), r = 14;
  k.fillStyle = '#' + T3[M[code].t].toString(16).padStart(6, '0');
  k.beginPath(); k.moveTo(r, 4); k.arcTo(124, 4, 124, 60, r); k.arcTo(124, 60, 4, 60, r); k.arcTo(4, 60, 4, 4, r); k.arcTo(4, 4, 124, 4, r); k.fill();
  k.fillStyle = '#ffffff'; k.font = '600 34px "JetBrains Mono", monospace'; k.textAlign = 'center'; k.textBaseline = 'middle';
  k.fillText(code, 64, 34);
  const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace;
  const s = new THREE.Sprite(new THREE.SpriteMaterial({map:tx, depthTest:false}));
  s.scale.set(2.8, 1.4, 1); s.position.set(x, y, z); s.renderOrder = 5; (p || G).add(s); return s;
}

const DECO = {
  _: g => box(1, .3, 1, 0x1b2221, 0, .55, 0, g),
  C1: g => { box(2.2, .5, 2.6, 0xb9c2bf, 0, .65, -1, g); for (let i = 0; i < 6; i++) box(.8, .5, .5, 0xf1f1ec, -3 + i * 1.2, .65, 2.5, g); box(.9, .5, .6, 0x2f6fe4, -3.4, .65, -2.5, g); box(.9, .5, .6, 0xe2b714, 3.4, .65, -2.5, g); },
  C2: g => { for (const z of [-.95, .95]) { cyl(.9, 6.2, 0x3a7bd5, 0, 1.3, z, g).rotation.z = PI / 2; } },
  S1: g => { box(1.4, .3, 1.4, 0x1b2221, -.8, .55, 0, g); box(1.2, .5, .8, 0xc9451a, 1.6, .65, -1.2, g); box(1.2, .5, .8, 0xc9451a, 1.6, .65, 1.2, g); },
  S2: (g, w) => { for (let i = 0; i < 8; i++) box(.5, .3, .5, 0x1b2221, -w / 2 + .9 + i * 1.03, -.15, 0, g); },
  S3: g => box(.9, .25, .9, 0x1b2221, 0, .52, 0, g),
  I1: g => { cyl(.5, .5, 0xd94a3a, -.8, .65, 0, g); cyl(.5, .5, 0x3a7bd5, .8, .65, 0, g); },
  I2: g => cyl(.8, 1.2, 0x2a3230, 0, 1, 0, g),
  I3: g => { cyl(.25, 1.6, 0x2a3230, 0, 1.2, 0, g); ball(.6, 0x2a3230, 0, 2.1, 0, g); },
  I4: g => { for (let i = 0; i < 16; i++) box(.6, .25, .6, 0xf1f1ec, -1.2 + (i % 4) * .8, .52, -1.2 + (i >> 2) * .8, g); },
  I7: g => ball(.9, 0xf1f1ec, 0, .4, 0, g),
  I8: g => cyl(.9, 1.2, 0xb9bfbd, 0, 1, 0, g),
  I11: g => { lay(cyl(.7, .8, 0xb9bfbd, -.8, 1.1, .4, g)); lay(cyl(.7, .8, 0xb9bfbd, .8, 1.1, .4, g)); },
  I13: g => box(3, .1, 3, 0xd8b84a, 0, .46, -1, g),
  O1: g => { ball(.4, glow(0xe5483a), -.8, .75, 0, g); ball(.4, glow(0x37c26b), .8, .75, 0, g); },
  O2: g => { [0xe5483a, 0xf0a030, 0xf2d83b, 0x37c26b, 0x31c4c4, 0x3a7bd5, 0x8a55e0, 0xe055b0].forEach((c, i) => ball(.28, glow(c), -2.45 + i * .7, .6, 0, g)); },
  O3: g => { box(2.5, .15, 1.7, 0x0b0f10, 0, .48, 0, g); box(1.6, .16, .22, glow(0x56e0d0), -.2, .5, -.3, g); box(1.1, .16, .22, glow(0x56e0d0), -.45, .5, .2, g); },
  O4: g => box(1.5, 1.3, 1.7, 0x2b6cc4, 0, 1.05, 0, g),
  O5: g => { cyl(1.3, .5, 0x2a3230, 0, .65, 0, g); box(2.2, .2, .4, 0xb9bfbd, 0, 1, 0, g); box(.4, .2, 2.2, 0xb9bfbd, 0, 1, 0, g); },
  O6: g => { box(2.3, 1.9, 1.2, 0x2b6cc4, 0, 1.35, 0, g); cyl(.35, .4, 0xf1f1ec, .6, 2.5, 0, g); box(1.8, .15, .4, 0xf1f1ec, .6, 2.72, 0, g); },
  O7: g => { box(1.2, .3, 1.2, 0x1b2221, -1.6, .55, 0, g); for (let i = 0; i < 6; i++) box(.3, .7, .9, 0xe2b714, -.2 + i * .5, .75, .6, g); }
};

/* Một module = tấm mạch màu theo loại + chi tiết nhận dạng + nhãn mã module. */
function mod(code, x, y, z, o) {
  o = o || {};
  const par = o.p || G, g = new THREE.Group(), sz = SIZE[code] || [3.2, 2.4], w = sz[0], d = sz[1];
  g.position.set(x, y, z);
  if (o.ry) g.rotation.y = o.ry;
  if (o.wall === 'b') g.rotation.x = PI / 2;
  if (o.wall === 'r') g.rotation.z = -PI / 2;
  par.add(g);
  box(w, .4, d, T3[M[code].t], 0, .2, 0, g);
  (DECO[code] || DECO._)(g, w, d);
  if (o.lp) label(code, o.lp[0], o.lp[1], o.lp[2], par);
  else if (o.wall === 'b') label(code, x, y + d / 2 + 1.1, z + .8, par);
  else if (o.wall === 'r') label(code, x + 1.2, y + w / 2 + 1.1, z, par);
  else label(code, x, y + 2.9, z, par);
  return g;
}

function bench(p) {
  ground(36, 28);
  const c = p.c, W = {da:0x8f9b98, i2c:0x2f6fe4, spi:0xd9a900, sv:0x3a4442, pwr:0xc9451a};
  const wire = (a, b, col) => rod(v(a[0], .55, a[1]), v(b[0], .55, b[1]), .14, col);
  mod('C1', 0, 0, 0);
  const da = DA.filter(k => c[k]);
  da.forEach((k, i) => { const z = (i - (da.length - 1) / 2) * 5; mod(c[k], -12, 0, z); wire([-4, z * .3], [-10.4, z], W.da); });
  let prev = [4, 0];
  (c.I2C || []).forEach((m, i, a) => { const z = (i - (a.length - 1) / 2) * 6.5; mod(m, 12, 0, z); wire(prev, [12, z], W.i2c); prev = [12, z]; });
  if (c.SPI) { mod(c.SPI, -5, 0, -10); wire([-2, -3], [-5, -7], W.spi); }
  (c.SV || []).forEach((m, i) => { mod(m, 4 + i * 5, 0, -10); wire([2, -3], [4 + i * 5, -9], W.sv); });
  if (p.pw === 'bat') { mod('C2', 0, 0, 10); wire([0, 3], [0, 8], W.pwr); }
}

function house(p) {
  const h = modsOf(p), has = m => h.has(m), sv = (p.c.SV || []).length, wall = 0xe9ecea;
  const door = has('I13') || has('I4');
  ground(40, 32, 0xa9bfa2);
  box(24, .4, 16, 0xdccfb9, -2, .2, -2);
  box(24, 10, .5, 0xf1f3f2, -2, 5.4, -10.2);
  box(.5, 10, 16, wall, -14.2, 5.4, -2);
  box(.5, 10, 10, wall, 10.2, 5.4, -5);
  box(.5, 2.5, 4.4, wall, 10.2, 9.15, 2.2); box(.5, 10, .5, wall, 10.2, 5.4, 4.4);
  box(5, 3.5, .7, 0x9fd3ea, -8, 6.6, -10.2);
  const dg = new THREE.Group(); dg.position.set(10.2, .4, 0); dg.rotation.y = door ? -.7 : 0; G.add(dg);
  box(.3, 7.5, 4, 0x9a6b3f, 0, 3.75, 2, dg);
  mod('C1', -1, .4, -5);
  if (has('O3')) mod('O3', 2, 6.5, -9.9, {wall:'b'});
  if (has('I6')) mod('I6', 6, 6.5, -9.9, {wall:'b'});
  if (has('I5')) mod('I5', -8, 3.2, -9.7, {wall:'b', lp:[-8, 2, -8.9]});
  if (has('I7')) mod('I7', -3, 8.4, -9.9, {wall:'b', lp:[-3, 6.6, -9.1]});
  if (has('O2')) mod('O2', 3, 9.4, -9.9, {wall:'b', lp:[7.6, 9.4, -9.1]});
  if (has('I8')) { box(3.4, 2.4, 2.6, 0x7b8582, 7.5, 1.6, -8.4); mod('I8', 7.5, 2.8, -8.4, {lp:[7.5, 1.6, -6.4]}); }
  if (has('I2')) mod('I2', 5, .4, -3);
  if (has('O4') || has('O1')) { rod(v(-7, 10.4, -4), v(-7, 8.2, -4), .1, 0x2a3230); ball(.9, glow(0xffd76a), -7, 7.4, -4); }
  if (has('O4')) mod('O4', -11, .4, -7);
  if (has('O1')) mod('O1', -11.4, 8.6, -9.9, {wall:'b', lp:[-11.4, 6.9, -9.1]});
  if (has('O5')) mod('O5', -9, .4, 1.5);
  if (has('I13')) mod('I13', 10.5, 5, -3.3, {wall:'r'});
  if (has('I4')) mod('I4', 10.5, 5, -8.2, {wall:'r'});
  if (door && sv) mod('O6', 10.5, 9.1, 2.2, {wall:'r', lp:[12, 11.4, 2.2]});
  if (has('I10')) {
    mod('I10', -10, 0, 11);
    if (sv && (!door || sv > 1)) {
      rod(v(-2, 0, 11), v(-2, 6, 11), .25, 0x8a8178); rod(v(8, 0, 11), v(8, 6, 11), .25, 0x8a8178); rod(v(-2, 6, 11), v(8, 6, 11), .15, 0x8a8178);
      [[0, 0xe5483a], [3, 0x3a7bd5], [6, 0xf2d83b]].forEach(a => box(1.8, 2.6, .15, a[1], a[0], 4.6, 11));
      mod('O6', -5, 0, 12.5);
    }
  }
}

function car(p) {
  const h = modsOf(p), has = m => h.has(m), id = p.id;
  ground(46, 34, 0xe9ecea);
  let cz = 0;
  if (has('S2')) { const t = add(new THREE.TorusGeometry(10, .45, 6, 56), 0x1b1f20, 0, .06, 0); t.scale.set(1.5, 1, .1); t.rotation.x = PI / 2; cz = 10; }
  if (id === 16) { box(4, 3, 3, 0x2b7fd0, 0, 1.5, -14); box(4, 3, 3, 0xd9731e, 19.5, 1.5, 0); box(1.8, .1, 1.8, 0xd8b84a, 0, .12, -10); box(1.8, .1, 1.8, 0xd8b84a, 15, .12, 0); }
  if (id === 12) { box(3, 5, 3, 0xb5673c, 15, 2.5, 3); box(4, 4, 3, 0x7b8582, 13, 2, -8); cyl(1.6, 5, 0x9a6b3f, -14, 2.5, -9); }
  if (id === 15) { const q = [[-8, -8], [8, -8], [8, 8], [-8, 8]]; q.forEach((a, i) => { const b = q[(i + 1) % 4]; rod(v(a[0], .1, a[1]), v(b[0], .1, b[1]), .2, 0xe5483a); }); cz = 8; }
  if (id === 11) { box(2, .6, 4.4, 0x2a3230, 14, .3, 10); cyl(.35, .2, 0xe5483a, 14, .7, 9); }
  const g = new THREE.Group(); g.position.set(0, 0, cz); G.add(g);
  box(18, .4, 9, 0xf5f6f5, 0, 3.4, 0, g);
  for (const s of [-1, 1]) {
    lay(cyl(3.2, 1.4, 0x23292a, -5, 3.2, s * 5.4, g)); lay(cyl(1.1, 1.5, 0xc9d1ce, -5, 3.2, s * 5.4, g));
    lay(cyl(1.1, 3.2, 0xb9bfbd, -5, 2.1, s * 2.6, g));
  }
  label('K1', -5, 3.2, 7.6, g);
  ball(1, 0x8a8178, 8.2, 1, 0, g); box(1.2, 1.3, 1.2, 0x8a8178, 8.2, 2.6, 0, g);
  mod('S1', -6.5, 3.6, 0, {p:g, ry:PI / 2});
  mod('C1', 0, 3.6, 0, {p:g, ry:PI / 2});
  mod('C2', -.5, 1, 0, {p:g, lp:[-.5, 1.6, -6]});
  if (has('S2')) { box(.4, 2.2, 2, 0x8a8178, 9.2, 2.3, 0, g); mod('S2', 10, 1, 0, {p:g, ry:PI / 2, lp:[11.6, 2.6, 0]}); }
  if (has('I11')) { mod('O6', 6.5, 3.6, 0, {p:g, lp:[6.5, 4.6, 3.4]}); mod('I11', 6.9, 6.4, 0, {p:g, ry:PI / 2}); }
  if (has('I12')) mod('I12', 6.5, 3.6, 0, {p:g});
  if (has('O3')) mod('O3', 6.5, 3.6, 2.4, {p:g});
  if (has('S3')) mod('S3', 6.5, 3.6, -2.6, {p:g});
  if (has('I13')) mod('I13', 5.2, 2.3, 0, {p:g, lp:[5.2, 5.6, 0]});
}

function balance(p) {
  ground(34, 24, 0xe9ecea);
  const b = new THREE.Group(); b.position.set(0, 3.2, 0); G.add(b); sway = b;
  for (const s of [-1, 1]) {
    lay(cyl(3.2, 1.4, 0x23292a, 0, 0, s * 5.6, b)); lay(cyl(1.1, 1.5, 0xc9d1ce, 0, 0, s * 5.6, b));
    lay(cyl(1.1, 3, 0xb9bfbd, 0, 0, s * 2.4, b));
  }
  label('K1', 0, 0, 7.8, b);
  [1.3, 6.3, 11.3].forEach(y => box(6, .3, 8, 0xf5f6f5, 0, y, 0, b));
  for (const x of [-2.6, 2.6]) for (const z of [-3.6, 3.6]) rod(v(x, 1.3, z), v(x, 11.3, z), .15, 0xb9bfbd, b);
  mod('S1', 0, 1.45, -1.6, {p:b, lp:[-5, 2.6, -1.6]});
  mod('S3', 0, 1.45, 2.5, {p:b, ry:PI / 2, lp:[5, 2.6, 2.5]});
  mod('C1', 0, 6.45, 0, {p:b, ry:PI / 2, lp:[-5, 7.8, 0]});
  mod('C2', 0, 11.45, 0, {p:b, ry:PI / 2});
  if (p.wifi) { box(3.4, .4, 6.4, 0x15201e, 11, .2, 7); box(2.8, .1, 5.4, glow(0x56c8d8), 11, .42, 7); }
}

function arm(p) {
  ground(38, 28, 0xe9ecea);
  cyl(3.2, 1.2, 0x2a3230, 0, .6, 0);
  const j = (par, y, rz, ry) => { const g = new THREE.Group(); g.position.y = y; g.rotation.z = rz || 0; g.rotation.y = ry || 0; par.add(g); box(2.2, 1.6, 1.4, 0x2b6cc4, 0, 0, 0, g); return g; };
  const g1 = j(G, 2, 0, .5); box(1.1, 7, 1.1, 0xf5f6f5, 0, 4.2, 0, g1);
  const g2 = j(g1, 8.4, -1); box(1.1, 6, 1.1, 0xf5f6f5, 0, 3.7, 0, g2);
  const g3 = j(g2, 7.4, -1.2); box(1, 2.6, 1, 0xf5f6f5, 0, 2, 0, g3);
  const g4 = j(g3, 3.9, 0); box(.4, 2.4, .6, 0x2a3230, -.8, 1.8, 0, g4); box(.4, 2.4, .6, 0x2a3230, .8, 1.8, 0, g4);
  label('O6', -2.6, 0, 0, g1); label('O6', 0, 2.2, 0, g2); label('O6', 0, 2.2, 0, g3);
  box(1.6, 1.6, 1.6, 0xd94a3a, 9, .8, -5);
  mod('O7', -11, 0, 5.5); mod('C1', -11, 0, -5); mod('C2', 9, 0, 8); mod('I3', 1, 0, 9.5);
}

function conveyor(p) {
  ground(46, 28, 0xe9ecea);
  box(26, .6, 5, 0x23292a, 0, 3.3, 0);
  for (const x of [-13, 13]) lay(cyl(.9, 5, 0xb9bfbd, x, 3.3, 0));
  for (const x of [-11, 11]) for (const z of [-2, 2]) box(.5, 3, .5, 0x8a8178, x, 1.5, z);
  [[-9, 0xe5483a], [-4.5, 0x37c26b], [3, 0x3a7bd5]].forEach(a => box(1.5, 1.5, 1.5, a[1], a[0], 4.35, 0));
  for (const z of [-3.2, 3.2]) rod(v(-1, 0, z), v(-1, 8.5, z), .25, 0x8a8178);
  box(.6, .5, 7, 0x8a8178, -1, 8.5, 0);
  mod('I14', -1, 7.4, 0);
  box(2.6, 3.6, 2, 0x8a8178, 6, 1.8, -4.4); mod('O6', 6, 3.6, -4.4); box(.3, 1, 5, 0xf1f1ec, 6.6, 4.6, -1.4);
  [[2, 0xe5483a], [6, 0x37c26b], [10, 0x3a7bd5]].forEach(a => box(3.4, 1.6, 3.4, a[1], a[0], .8, 5.6));
  lay(cyl(1.1, 3, 0xb9bfbd, 14.4, 3.3, 3.6));
  mod('S1', 18, 0, 8); mod('C1', -15, 0, 9); mod('C2', -16, 0, -8);
  if (modsOf(p).has('O3')) mod('O3', -5, 0, 10.5);
}

function garden(p) {
  ground(38, 28);
  cyl(3, 5, 0xb5673c, -6, 2.5, 0, G, 4.2); cyl(3.9, .3, 0x4a3a2c, -6, 5, 0);
  rod(v(-6, 5, 0), v(-6, 9, 0), .2, 0x3f8f4a);
  [[-6, 10, 0, 1.6], [-7.4, 8.4, .6, 1.1], [-4.8, 8.8, -.5, 1.2]].forEach(a => ball(a[3], 0x4fae5b, a[0], a[1], a[2]));
  box(.9, 3.2, .25, T3.in, -4.2, 5.6, 1.4); label('I9', -3.2, 8.3, 2.4);
  box(5, 5, 5, new THREE.MeshLambertMaterial({color:0x5aa9e6, transparent:true, opacity:.55}), 7, 2.5, -5);
  mod('O5', 7, 0, 2.5);
  rod(v(7, 5, -5), v(7, 7, -5), .18, 0x7b8582); rod(v(7, 7, -5), v(-4, 7, -1), .18, 0x7b8582); rod(v(-4, 7, -1), v(-4.6, 5.4, -.6), .18, 0x7b8582);
  rod(v(-13, 0, -4), v(-13, 13.5, -4), .3, 0x8a8178); rod(v(-13, 13.5, -4), v(-6, 13.5, 0), .3, 0x8a8178);
  box(6, .4, 1.4, glow(0xfff0a8), -6, 13.1, 0);
  mod('O4', -13.5, 0, 3); mod('C1', 1, 0, 9); mod('O3', 10, 0, 10); mod('I6', -10, 0, 9.5);
}

/* Mô hình CAD: lưới tam giác xuất từ mechanical/ (mỗi mô hình một tệp trong mo-hinh/, do update_3d.py ghi), toạ độ mm, trục Z hướng lên. */
const nhomCad = id => id >= 5 && id <= 10 ? 'nha_thong_minh' : id >= 11 && id <= 16 ? 'xe_do_line' : id === 18 ? 'vuon_thong_minh'
  : (id === 21 || id === 22) ? 'xe_can_bang' : id === 23 ? 'canh_tay_robot' : id === 24 ? 'bang_tai' : 'ban_thuc_hanh';
/* Danh sách mô hình có trong mo-hinh/ do update_3d.py ghi (mo-hinh/danh-sach.js). */
const coMoHinh = ten => (window.MO_HINH_DS || []).includes(ten);
/* Đường dẫn hình kèm số phiên bản để trình duyệt không dùng lại hình cũ đã lưu đệm. */
const hinh = ten => GOC + 'hinh/' + ten + '.svg?v=' + ((window.HINH_V || {})[ten] || 0);
/* Mô hình riêng của một dự án (du_an_<số>) được ưu tiên hơn mô hình của nhóm dự án. */
const cadName = id => coMoHinh('du_an_' + id) ? 'du_an_' + id : nhomCad(id);
const dangNap = {};
function nap(ten, xong) {
  window.MO_HINH = window.MO_HINH || {};
  if (MO_HINH[ten]) return xong(true);
  if (!coMoHinh(ten)) return xong(false);
  if (dangNap[ten]) { dangNap[ten].push(xong); return; }
  dangNap[ten] = [xong];
  const sc = document.createElement('script'); sc.src = GOC + 'mo-hinh/' + encodeURIComponent(ten) + '.js?v=' + ((window.MO_HINH_V || {})[ten] || 0); sc.async = true;
  const het = ok => { const ds = dangNap[ten]; delete dangNap[ten]; ds.forEach(f => f(ok)); };
  sc.onload = () => het(!!MO_HINH[ten]); sc.onerror = () => het(false);
  document.head.appendChild(sc);
}
function b64(str, T) {
  const b = atob(str), u = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
  return new T(u.buffer);
}
function cad(name) {
  const d = window.MO_HINH[name], g = new THREE.Group();
  for (const m of d.m) {
    const q = b64(m.p, Int16Array), pos = new Float32Array(q.length);
    for (let i = 0; i < q.length; i++) pos[i] = q[i] * d.s + d.o[i % 3];
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setIndex(new THREE.BufferAttribute(b64(m.i, m.w === 2 ? Uint16Array : Uint32Array), 1));
    g.add(new THREE.Mesh(geo, new THREE.MeshPhongMaterial({color:m.c, flatShading:true, shininess:10, side:THREE.DoubleSide})));
  }
  g.rotation.x = -PI / 2;
  const bb = new THREE.Box3().setFromObject(g), sz = bb.getSize(new THREE.Vector3()), c = bb.getCenter(new THREE.Vector3());
  const k = 46 / Math.max(sz.x, sz.z, sz.y * 1.5), w = new THREE.Group();      // mô hình cao cũng phải nằm gọn trong khung
  g.position.set(-c.x, -bb.min.y, -c.z); w.add(g); w.scale.setScalar(k); G.add(w);
  ty = Math.min(16, sz.y * k / 2); dist = 72;
}
function don3d() {
  if (G) {
    G.traverse(o => { if (o.geometry) o.geometry.dispose(); if (o.material) { if (o.material.map) o.material.map.dispose(); o.material.dispose(); } });
    R3.scene.remove(G);
  }
  G = new THREE.Group(); sway = null; R3.scene.add(G);
}
function buildMod(q) {
  cur3d = q; don3d();
  nap(q.mod, ok => { if (cur3d === q && ok) { don3d(); cad(q.mod); dist = 96; hienKt(q.mod); } });
}
/* Kích thước bao lấy từ chính tệp mô hình, nên luôn khớp với tệp 3D đang hiển thị. */
function hienKt(m) {
  const d = window.MO_HINH && MO_HINH[m], o = $('kt');
  if (!o || !d || !d.kt) return;
  o.textContent = d.kt.map(x => String(x).replace('.', ',')).join(' × ') + ' mm';
  document.querySelectorAll('.ktd').forEach(e => e.hidden = false);
}

function build3d(p) {
  if (p.mod) return buildMod(p);
  cur3d = p; ty = 4;
  don3d();
  const id = p.id; let f = bench, dd = 64;
  if (id >= 5 && id <= 10) { f = house; dd = 78; }
  else if (id >= 11 && id <= 16) { f = car; dd = 76; }
  else if (id === 18) { f = garden; dd = 68; }
  else if (id === 21 || id === 22) { f = balance; dd = 60; }
  else if (id === 23) { f = arm; dd = 68; }
  else if (id === 24) { f = conveyor; dd = 76; }
  const cn = cadName(id);
  if (view3d === 'cad' && window.MO_HINH && MO_HINH[cn]) { cad(cn); return; }
  dist = dd; f(p);                      // sơ đồ khối hiện ngay; mô hình CAD thay vào khi nạp xong
  if (view3d === 'cad') nap(cn, ok => { if (ok && cur3d === p && view3d === 'cad') build3d(p); });
}

function init3d() {
  const cv = document.createElement('canvas'); cv.setAttribute('aria-label', 'Mô hình 3D của dự án');
  const renderer = new THREE.WebGLRenderer({canvas:cv, antialias:true, alpha:true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(32, 1.6, 1, 500);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa0a8, 2.6));
  const dl = new THREE.DirectionalLight(0xffffff, 1.9); dl.position.set(20, 40, 25); scene.add(dl);
  let drag = null;
  cv.addEventListener('pointerdown', e => { drag = [e.clientX, e.clientY]; auto = false; try { cv.setPointerCapture(e.pointerId); } catch (_) {} });
  cv.addEventListener('pointermove', e => {
    if (!drag) return;
    az -= (e.clientX - drag[0]) * .008;
    el = Math.min(1.35, Math.max(.1, el + (e.clientY - drag[1]) * .006));
    drag = [e.clientX, e.clientY];
  });
  const end = () => { drag = null; };
  cv.addEventListener('pointerup', end); cv.addEventListener('pointercancel', end);
  function size() {
    const s = cv.parentElement; if (!s) return;
    const w = s.clientWidth, h = s.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
  }
  const ro = new ResizeObserver(size);
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  (function tick(t) {
    requestAnimationFrame(tick);
    if (!cv.isConnected || state.tab === 'mat' || document.hidden) return;
    if (auto && !still) az += .0025;
    if (sway && !still) sway.rotation.z = Math.sin((t || 0) / 700) * .05;
    const c = Math.cos(el);
    cam.position.set(Math.sin(az) * c * dist, Math.sin(el) * dist + ty, Math.cos(az) * c * dist);
    cam.lookAt(0, ty, 0);
    renderer.render(scene, cam);
  })(0);
  R3 = {cv, scene, ro, size};
}

function mount3d(p) {
  const st = $('stage'); if (!st || !window.THREE) return;
  try { if (!R3) init3d(); } catch (e) { $('g3d').hidden = true; return; }
  R3.ro.disconnect(); st.prepend(R3.cv); R3.ro.observe(st);
  build3d(p); R3.size();
}
function zoom3d(k) { dist = Math.min(150, Math.max(28, dist * k)); }

const elec = Object.keys(M).filter(m => M[m].t !== 'mech').length;
$('facts').innerHTML = `<span><b>${P.length}</b> dự án</span><span><b>${LV.length}</b> cấp độ</span><span><b>${elec}</b> module điện tử</span><span><b>3</b> module thông minh tự thiết kế</span><span>Học sinh <b>12–18</b> tuổi</span><span>Lập trình kéo thả <b>MicroBlocks</b></span>`;
docHash();
render();
/* Nạp danh sách mô hình sau khi trang đã hiện rồi vẽ lại; từng mô hình chỉ được nạp khi cần xem. */
(() => {
  const sc = document.createElement('script'); sc.src = GOC + 'mo-hinh/danh-sach.js?t=' + Date.now(); sc.async = true;
  sc.onload = () => render();
  document.head.appendChild(sc);
})();
