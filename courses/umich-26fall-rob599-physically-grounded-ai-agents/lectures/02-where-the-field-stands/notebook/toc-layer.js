/* toc-layer.js — foldable left table of contents for commentable-html deliverables.
 *
 * Auto-builds from headings inside the content root at load; no hand-authored nav.
 * Levels: h2.part → parts (top), other h2 → sections, h3 → groups (folded by default).
 * Docs without h2.part: h2 → top, h3 → folded groups. Fewer than 3 headings → no TOC.
 * Docked left of the content on wide viewports (≥1360px, content shifted right);
 * hidden behind a ☰ Contents pill below that (opens as a sidebar the content moves
 * over for; Escape or « closes it). Clicking an entry keeps the nav open, so the
 * reader can click around — it is a map to navigate by, not a menu to dismiss.
 * The « button hides it; drag the right edge to resize. Both choices persist per doc
 * (localStorage, keyed by data-comment-doc). Content margins are coordinated with the
 * comment layer's right panel through window.__dockLayout (defined by whichever layer
 * loads first), so left TOC + right comments panel + content never overlap.
 * Disable entirely with data-toc="off" on <html>, or point at a different content
 * root with data-content="<selector>" on this script tag.
 *
 * Headings without ids get slugified ones so links work; ids already present are
 * never touched (comment-layer anchors and the TOC share them — prefer stable ids).
 */
(function () {
  'use strict';
  var doc = document, html = doc.documentElement, body = doc.body;

  // Shared left/right dock layout — defined by whichever layer (toc/comment) loads first.
  // Each docked sidebar reports its width; the content root is re-margined to the free band.
  window.__dockLayout = window.__dockLayout || (function () {
    var slots = { left: 0, right: 0 }, root = null;
    function apply() {
      if (!root) return;
      var L = slots.left ? slots.left + 24 : 0, R = slots.right ? slots.right + 24 : 0;
      if (!L && !R) { root.style.marginLeft = ''; root.style.marginRight = ''; return; }
      var cs = getComputedStyle(root);
      var mw = parseFloat(cs.maxWidth);
      var outer = mw ? mw + (parseFloat(cs.paddingLeft) || 0) + (parseFloat(cs.paddingRight) || 0) : 0;
      var avail = window.innerWidth - L - R;
      if (outer && avail > outer) { // content keeps its width, centered in the free band
        root.style.marginLeft = (L + (avail - outer) / 2) + 'px';
        root.style.marginRight = '';
      } else { // not enough room: pin to both docks and let the content shrink
        root.style.marginLeft = L ? L + 'px' : '';
        root.style.marginRight = R ? R + 'px' : '';
      }
    }
    window.addEventListener('resize', apply);
    return {
      set: function (side, px, contentRoot) {
        if (contentRoot && (contentRoot !== document.body || !root)) {
          if (root && root !== contentRoot) { root.style.marginLeft = ''; root.style.marginRight = ''; }
          root = contentRoot;
        }
        slots[side] = px || 0; apply();
      },
    };
  })();

  if ((html.getAttribute('data-toc') || '').toLowerCase() === 'off') return;

  var sel = (doc.currentScript && doc.currentScript.getAttribute('data-content')) || '#content';
  var root = doc.querySelector(sel) || doc.querySelector('main') || body;

  var hs = Array.prototype.slice.call(root.querySelectorAll('h2, h3')).filter(function (h) {
    return !h.closest('nav') && !h.closest('.toc-layer');
  });
  if (hs.length < 3) return;

  var hasParts = hs.some(function (h) { return h.tagName === 'H2' && h.classList.contains('part'); });
  var maxLevel = hasParts ? 2 : 1;
  function levelOf(h) {
    if (h.tagName === 'H2') return hasParts ? (h.classList.contains('part') ? 0 : 1) : 0;
    return maxLevel;
  }
  function labelOf(h) {
    var c = h.cloneNode(true);
    Array.prototype.forEach.call(c.querySelectorAll('.era, .chip, .meta'), function (n) { n.remove(); });
    var t = c.textContent.replace(/\s+/g, ' ').trim();
    return t.length > 72 ? t.slice(0, 69) + '…' : t;
  }

  // ---- ensure ids (never touch existing ones) ----
  var used = {};
  Array.prototype.forEach.call(doc.querySelectorAll('[id]'), function (n) { used[n.id] = 1; });
  hs.forEach(function (h) {
    if (h.id) return;
    var s = labelOf(h).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || 'sec';
    var id = s, i = 1;
    while (used[id]) id = s + '-' + (++i);
    used[id] = 1; h.id = id;
  });

  // ---- build the nav ----
  var nav = doc.createElement('nav');
  nav.className = 'toc-layer';
  nav.setAttribute('aria-label', 'Contents');
  nav.innerHTML = '<div class="tl-head"><span>Contents</span>' +
    '<button type="button" class="tl-close" title="Hide contents" aria-label="Hide contents">«</button></div>';

  var containers = [nav], gid = 0;
  hs.forEach(function (h, i) {
    var L = levelOf(h);
    var next = hs[i + 1];
    var hasKids = !!next && levelOf(next) > L;
    var parent = containers[L] || containers[L - 1] || nav;

    var row = doc.createElement('div');
    row.className = 'tl-row tl-l' + L;
    if (hasKids) {
      var grp = doc.createElement('div');
      grp.className = 'tl-grp tl-g' + L;
      grp.id = 'tl-g' + (++gid);
      var fold = levelOf(next) === maxLevel;         // deepest-level groups start folded
      if (fold) grp.classList.add('tl-fold');
      var car = doc.createElement('button');
      car.type = 'button'; car.className = 'tl-car';
      car.setAttribute('data-for', grp.id);
      car.setAttribute('aria-expanded', fold ? 'false' : 'true');
      car.setAttribute('aria-label', 'Toggle section');
      row.appendChild(car);
      parent.appendChild(row);
      parent.appendChild(grp);
      containers[L + 1] = grp;
      containers.length = L + 2;
    } else {
      var sp = doc.createElement('span');
      sp.className = 'tl-noc';
      row.appendChild(sp);
      parent.appendChild(row);
    }
    var a = doc.createElement('a');
    a.href = '#' + h.id; a.textContent = labelOf(h);
    row.appendChild(a);
  });

  var btn = doc.createElement('button');
  btn.type = 'button'; btn.className = 'tl-btn';
  btn.setAttribute('aria-label', 'Show contents');
  btn.innerHTML = '☰ Contents';
  body.appendChild(btn);
  body.appendChild(nav);

  // ---- behavior ----
  var DOCKEY = html.getAttribute('data-comment-doc') || location.pathname;
  var KEY = 'toc-hidden:' + DOCKEY;
  var WKEY = 'toc-w:' + DOCKEY;
  var mq = window.matchMedia('(min-width: 1360px)');
  var curW = Math.min(420, Math.max(180, parseInt(localStorage.getItem(WKEY), 10) || 248));
  nav.style.width = curW + 'px';

  function sync() {
    // Docked or opened as an overlay: either way the nav stays put while the reader
    // clicks through it, so the content moves over in both states.
    var on = body.classList.contains('tl-docked') || body.classList.contains('tl-open');
    window.__dockLayout.set('left', on ? curW : 0, root);
  }
  function apply() {
    if (mq.matches && localStorage.getItem(KEY) !== '1') body.classList.add('tl-docked');
    else body.classList.remove('tl-docked');
    sync();
  }
  apply();
  (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(apply);

  // drag the right edge to resize; width persists per doc
  var grip = doc.createElement('div');
  grip.className = 'tl-grip';
  grip.title = 'Drag to resize';
  nav.appendChild(grip);
  grip.addEventListener('pointerdown', function (e) {
    e.preventDefault();
    try { grip.setPointerCapture(e.pointerId); } catch (err) {}
    var sx = e.clientX, sw = curW;
    nav.classList.add('tl-resizing');
    var mv = function (ev) { curW = Math.min(420, Math.max(180, sw + (ev.clientX - sx))); nav.style.width = curW + 'px'; sync(); };
    var up = function () {
      nav.classList.remove('tl-resizing');
      localStorage.setItem(WKEY, curW);
      grip.removeEventListener('pointermove', mv);
      grip.removeEventListener('pointerup', up);
    };
    grip.addEventListener('pointermove', mv);
    grip.addEventListener('pointerup', up);
  });

  btn.addEventListener('click', function () {
    if (mq.matches) { localStorage.removeItem(KEY); body.classList.add('tl-docked'); sync(); }
    else { body.classList.add('tl-open'); sync(); }
  });
  nav.querySelector('.tl-close').addEventListener('click', function () {
    if (body.classList.contains('tl-docked')) { localStorage.setItem(KEY, '1'); body.classList.remove('tl-docked'); }
    body.classList.remove('tl-open');
    sync();
  });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') { body.classList.remove('tl-open'); sync(); } });

  nav.addEventListener('click', function (e) {
    var car = e.target.closest('.tl-car');
    if (car) {
      var g = doc.getElementById(car.getAttribute('data-for'));
      car.setAttribute('aria-expanded', g.classList.toggle('tl-fold') ? 'false' : 'true');
      return;
    }
    // A link click scrolls the document and leaves the nav where it is. Closing it
    // here made every hop cost a reopen (reader's complaint, 2026-09-14).
  });
})();
