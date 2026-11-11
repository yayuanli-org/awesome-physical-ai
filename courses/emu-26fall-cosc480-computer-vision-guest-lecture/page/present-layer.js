/* present-layer.js — present a commentable-html page on the page itself.
 *
 * P toggles present mode. The page keeps its layout and only opacity changes, so the page
 * the presenter learned is the page the audience sees. A script of steps decides what is
 * lit: the current step's 1–3 targets at full strength, earlier steps of the same section
 * half-lit, everything else faded. Blocks marked hidden stay invisible, with their space
 * kept, until a step lights them.
 *
 * Two states inside present mode:
 *   play  → Space PageDown Enter = next · ← PageUp = back · Home / End
 *         click = a spotlight off the script, ⇧click adds to it, Esc returns to the step
 *         S presenter window (notes, next step, timer) · B or . blank · T contents · E edit
 *   edit  the step list docks on the right; everything stays readable.
 *         click = new step after this one · ⇧click = add to this step (3 at most)
 *         ⌥click = hide / show in the talk · select text = a step that marks those words
 *         ⌥↑ / ⌥↓ = wider / narrower block for the last pick · ⌫ delete step · ⌘Z undo
 *   Esc or P leaves present mode. The TOC turns into the progress map: done sections ink,
 *   the current one lit, the rest faint; clicking a section in play jumps to its first step.
 *
 * Store: <docId>.present.json beside the page, through serve.py's /__present__/<docId>.
 * Elsewhere a published <docId>.present.json loads read-only, and file:// keeps it in
 * localStorage. Targets are anchored with the comment layer's resolver (element id, CSS path
 * checked against a text quote, fuzzy quote), so a step re-finds its block after content
 * edits the way a comment does. Images keep their src as the check, since they have no text.
 *
 * Bridge: window.__presentLayer.{enter, exit, go, next, prev, edit, state, steps, export, import}
 */
(function () {
  "use strict";
  if (window.__presentLayerLoaded) return;
  window.__presentLayerLoaded = true;

  const doc = document, html = doc.documentElement;
  const SVGNS = "http://www.w3.org/2000/svg";
  const docId = (html.getAttribute("data-comment-doc")
    || (location.pathname.split("/").pop() || "document").replace(/\.[^.]*$/, "")
    || "document");
  const ENDPOINT = "./__present__/" + encodeURIComponent(docId);
  const STATIC = "./" + encodeURIComponent(docId) + ".present.json";
  const LSKEY = "present-layer::" + docId;
  const SKEY = "present-session::" + docId;     // on / edit / step, so a reload resumes
  const MAX = 3;                                // targets per step: one topic at a time
  const PANEL_W = 330;
  const LOOK = { earlier: "section", title: "past", past: 0.4, rest: 0.1 };
  const LV_REST = 0, LV_PAST = 1, LV_NOW = 2;
  const SKIP = ".pr-ui, .cmt-ui, .toc-layer, .tl-btn, script, style, template";

  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const clip = (s, n) => { s = norm(s); return s.length > n ? s.slice(0, n - 1) + "…" : s; };
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const sid = () => "s" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
  const el = (tag, cls, inner) => { const n = doc.createElement(tag); if (cls) n.className = cls; if (inner != null) n.innerHTML = inner; return n; };

  let root = null;
  let script = normalize({});
  let backend = "local", writable = true;
  let on = false, editing = false, blank = false;
  let cur = 0;
  let spot = null;                       // [{node, range}]: a spotlight off the script (play)
  let res = { steps: [], hidden: [] };   // resolved targets: steps[i][k] = {node, range} | null
  let stepSec = [];                      // the heading each step sits under
  let headings = [];                     // [{a, row, h}] in document order
  let painted = [];
  const touched = new Set();             // carry .pr-t so opacity animates both ways
  let hoverNode = null;
  let last = null;                       // {step, idx, chain, pos}: the last pick, for ⌥↑ / ⌥↓
  const undo = [];
  const ui = {};

  function normalize(d) {
    d = d && typeof d === "object" ? d : {};
    const steps = (Array.isArray(d.steps) ? d.steps : [])
      .filter((s) => s && Array.isArray(s.targets))
      .map((s) => ({ id: s.id || sid(), targets: s.targets.filter(Boolean), note: typeof s.note === "string" ? s.note : "" }));
    const hidden = (Array.isArray(d.hidden) ? d.hidden : []).filter(Boolean);
    return { docId: docId, version: 1, steps: steps, hidden: hidden, look: Object.assign({}, LOOK, d.look || {}) };
  }

  /* ---------- picking blocks ----------
     Opacity multiplies down the tree, so a lit block can only sit inside parents that stay at
     full strength. Targets are therefore whole blocks — a paragraph, a list item, a figure, a
     table row, a drawing — never an inline run whose sibling text could not be dimmed. */
  const BLOCKY = /^(block|list-item|table|table-row-group|table-header-group|table-footer-group|table-row|table-cell|table-caption|flex|grid|flow-root)$/;
  const MEDIA = /^(img|video|canvas|iframe)$/i;
  const SVG_PART = /^(g|rect|circle|ellipse|line|polyline|polygon|path|text|image|use|foreignObject)$/;

  function outerSvg(e) { let s = null; for (let x = e; x && x.namespaceURI === SVGNS; x = x.parentElement) if (x.tagName.toLowerCase() === "svg") s = x; return s; }
  function isBlock(e) {
    if (!e || e.nodeType !== 1) return false;
    if (e.namespaceURI === SVGNS) return outerSvg(e) === e;   // the drawing as a whole
    if (MEDIA.test(e.tagName)) return true;
    return BLOCKY.test(getComputedStyle(e).display);
  }
  function isUnit(e) { return isBlock(e) || (e.namespaceURI === SVGNS && SVG_PART.test(e.tagName)); }
  function blockOf(n) {
    if (n && n.nodeType !== 1) n = n.parentElement;
    for (let e = n; e && e !== root && root.contains(e); e = e.parentElement) if (isBlock(e)) return e;
    return null;
  }
  // The default unit under a click: the nearest block, except that an image or drawing inside a
  // <figure> picks the figure (picture with its caption) and a table cell picks its row.
  function pickFrom(t) {
    if (t && t.nodeType !== 1) t = t.parentElement;
    const chain = [];
    for (let e = t; e && e !== root && root.contains(e); e = e.parentElement) chain.push(e);
    let pos = chain.findIndex(isBlock);
    if (pos < 0) return null;
    const n = chain[pos], tag = n.tagName.toLowerCase();
    if (MEDIA.test(tag) || tag === "svg") { const f = n.closest("figure"); if (f && chain.indexOf(f) > pos) pos = chain.indexOf(f); }
    else if (tag === "td" || tag === "th") { const tr = n.closest("tr"); if (tr && chain.indexOf(tr) > pos) pos = chain.indexOf(tr); }
    if (chain[pos].closest(SKIP)) return null;
    return { node: chain[pos], chain: chain, pos: pos };
  }

  /* ---------- anchoring (shared with the comment layer) ---------- */
  const api = () => (window.__commentLayer && window.__commentLayer.anchor) || null;

  function cssPathLite(node) {
    const parts = [];
    for (let n = node; n && n.nodeType === 1 && n !== root; n = n.parentElement) {
      if (n.id) { parts.unshift("#" + CSS.escape(n.id)); break; }
      let s = n.tagName.toLowerCase();
      const p = n.parentElement;
      if (p) { const same = Array.prototype.filter.call(p.children, (c) => c.tagName === n.tagName); if (same.length > 1) s += ":nth-of-type(" + (same.indexOf(n) + 1) + ")"; }
      parts.unshift(s);
    }
    return parts.join(" > ");
  }
  function anchorOf(node, range) {
    const a = api();
    const block = range ? blockOf(range.commonAncestorContainer) : node;
    const anchor = a ? a.build(range ? null : node, range || null)
      : { type: range ? "range" : "element", elementId: node && node.id || "", cssPath: cssPathLite(block),
          quote: { exact: norm(range ? range.toString() : node.textContent).slice(0, 120), prefix: "", suffix: "" } };
    if (!range) {
      anchor.tag = node.tagName.toLowerCase();
      // Media has no text, so the quote cannot tell a moved picture from its neighbour. Its src can.
      const media = MEDIA.test(node.tagName) ? node : (!norm(node.textContent) && node.querySelector ? node.querySelector("img,video") : null);
      if (media && media.getAttribute("src")) anchor.src = media.getAttribute("src");
    }
    anchor.label = describe(block, range);
    return anchor;
  }
  function resolveLite(anchor) {
    let node = null;
    if (anchor.elementId) node = doc.getElementById(anchor.elementId) || root.querySelector('[data-cmt-anchor="' + CSS.escape(anchor.elementId) + '"]');
    if (!node && anchor.cssPath) { try { node = root.querySelector(anchor.cssPath); } catch (e) {} }
    const want = anchor.quote && norm(anchor.quote.exact);
    if (node && want && norm(node.textContent).indexOf(want) < 0) node = null;
    if (!node && want) {
      let best = null;
      root.querySelectorAll("*").forEach((n) => { if (norm(n.textContent).indexOf(want) >= 0 && (!best || best.contains(n))) best = n; });
      node = best;
    }
    return node ? { status: "anchored", node: node, range: null } : { status: "orphan" };
  }
  function hasSrc(node, src) {
    return !!node && ((node.getAttribute && node.getAttribute("src") === src) || !!(node.querySelector && node.querySelector('[src="' + CSS.escape(src) + '"]')));
  }
  function settle(anchor, r) {
    let node = r && r.status !== "orphan" ? r.node : null;
    if (anchor.src && !hasSrc(node, anchor.src)) {
      const m = root.querySelector('[src="' + CSS.escape(anchor.src) + '"]');
      node = m ? (anchor.tag && anchor.tag !== m.tagName.toLowerCase() ? (m.closest(anchor.tag) || m) : m) : null;
    }
    if (!node || !root.contains(node)) return null;
    return { node: node, range: anchor.type === "range" ? ((r && r.range) || null) : null };
  }
  function resolveAll() {
    const all = [];
    script.steps.forEach((s) => s.targets.forEach((t) => all.push(t)));
    script.hidden.forEach((t) => all.push(t));
    const a = api();
    const out = a && a.resolveMany ? a.resolveMany(all) : all.map(resolveLite);
    let k = 0;
    res.steps = script.steps.map((s) => s.targets.map(() => { const r = settle(all[k], out[k]); k++; return r; }));
    res.hidden = script.hidden.map(() => { const r = settle(all[k], out[k]); k++; return r ? r.node : null; });
    stepSec = res.steps.map((ts) => { const t = ts.find(Boolean); return t ? headingOf(litOf(t)) : null; });
  }
  const litOf = (t) => (t.range ? (blockOf(t.node) || t.node) : t.node);
  const targetsOf = (i) => (res.steps[i] || []).filter(Boolean);

  /* ---------- headings: the TOC rows, or the headings themselves without a TOC ---------- */
  function readHeadings() {
    headings = Array.prototype.map.call(doc.querySelectorAll(".toc-layer .tl-row > a[href^='#']"), (a) => {
      let id = a.getAttribute("href").slice(1);
      try { id = decodeURIComponent(id); } catch (e) {}
      return { a: a, row: a.parentElement, h: doc.getElementById(id) };
    }).filter((x) => x.h && root.contains(x.h));
    if (!headings.length) headings = Array.prototype.map.call(root.querySelectorAll("h2, h3"), (h) => ({ a: null, row: null, h: h }));
  }
  function headingOf(node) {
    let best = null;
    if (!node) return null;
    for (const x of headings) {
      if (x.h === node || x.h.contains(node) || (x.h.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING)) best = x;
      else break;
    }
    return best;
  }

  /* ---------- painting ----------
     Three tiers plus hidden. Walk down from the root: an element whose subtree holds something
     brighter than itself stays at full strength and passes the decision to its children; any
     other element takes its tier and stops the walk. Only classes change, never layout. */
  function unpaint() {
    painted.forEach((n) => n.classList.remove("pr-rest", "pr-past", "pr-hide", "pr-now"));
    painted = [];
  }
  function paint(now, past) {
    unpaint();
    const lit = new Map();
    past.forEach((t) => { const n = litOf(t); if (n && !lit.has(n)) lit.set(n, LV_PAST); });
    now.forEach((t) => { const n = litOf(t); if (n) lit.set(n, LV_NOW); });
    const hidden = new Set(res.hidden.filter(Boolean));
    const below = new Map();
    lit.forEach((lv, n) => {
      for (let e = n; e; e = e.parentElement) {
        const b = below.get(e);
        if (b !== undefined && b >= lv) break;
        below.set(e, lv);
        if (e === root) break;
      }
    });
    const hidBelow = new Set();
    hidden.forEach((n) => { for (let e = n.parentElement; e; e = e.parentElement) { if (hidBelow.has(e)) break; hidBelow.add(e); if (e === root) break; } });
    const put = (e, c) => { e.classList.add(c, "pr-t"); painted.push(e); touched.add(e); };
    (function walk(E, inLv, inHid) {
      if (E !== root && E.matches(SKIP)) return;
      const litLv = lit.get(E);
      const own = litLv !== undefined ? Math.max(inLv, litLv) : inLv;
      const hid = litLv !== undefined ? false : (inHid || hidden.has(E));
      const b = below.get(E);
      if ((b !== undefined && (b > own || hid)) || (!hid && hidBelow.has(E))) {
        for (const c of E.children) walk(c, own, hid);
        return;
      }
      if (hid) put(E, "pr-hide");
      else if (own === LV_PAST) put(E, "pr-past");
      else if (own === LV_REST) put(E, "pr-rest");
    })(root, lit.size ? LV_REST : LV_NOW, false);
    now.forEach((t) => { if (!t.ctx) { const n = litOf(t); if (n) put(n, "pr-now"); } });
    setMarks(now, past);
  }

  // Words picked inside a block get a highlighter, through the CSS Custom Highlight API: no DOM
  // is wrapped, so neither the layout nor the comment layer's own wrapping is disturbed.
  const HL = typeof CSS !== "undefined" && CSS.highlights && typeof Highlight === "function";
  function setMarks(now, past) {
    if (!HL) return;
    const a = now.filter((t) => t.range).map((t) => t.range), b = past.filter((t) => t.range).map((t) => t.range);
    if (a.length) CSS.highlights.set("pr-mark", new Highlight(...a)); else CSS.highlights.delete("pr-mark");
    if (b.length) CSS.highlights.set("pr-mark-past", new Highlight(...b)); else CSS.highlights.delete("pr-mark-past");
  }

  /* ---------- the step on screen ---------- */
  function lookNow() {
    const n = script.steps.length;
    let now = [], past = [];
    if (n) {
      cur = Math.max(0, Math.min(n - 1, cur));
      const sec = stepSec[cur] || null;
      if (spot) { now = spot.slice(); past = targetsOf(cur); }
      else {
        now = targetsOf(cur);
        const scope = script.look.earlier;
        if (scope !== "none") for (let j = 0; j < cur; j++) if (scope === "all" || stepSec[j] === sec) past = past.concat(targetsOf(j));
        if (sec && sec.h && script.look.title !== "rest") (script.look.title === "now" ? now : past).push({ node: sec.h, range: null, ctx: true });
      }
    } else if (spot) now = spot.slice();
    return { now: now, past: past };
  }
  function render(opts) {
    if (!on) return;
    resolveAll();
    const v = lookNow();
    paint(v.now, v.past);
    tocProgress(script.steps.length ? (spot ? headingOf(litOf(spot[0])) : stepSec[cur]) : null);
    renderChrome();
    if (editing) renderPanel();
    syncSpeaker(true);
    if (opts && opts.scroll) scrollToItems(v.now.filter((t) => !t.ctx));
    remember();
  }
  function scrollToItems(items) {
    items.forEach((t) => openFolds(litOf(t)));
    const rects = items.map((t) => (t.range ? t.range.getBoundingClientRect() : litOf(t).getBoundingClientRect())).filter((r) => r && (r.width || r.height));
    if (!rects.length) return;
    const top = Math.min.apply(null, rects.map((r) => r.top)), bottom = Math.max.apply(null, rects.map((r) => r.bottom));
    const vh = window.innerHeight, h = bottom - top;
    if (top >= vh * 0.1 && bottom <= vh * 0.9) return;   // already in view: the page does not move
    const y = h < vh * 0.8 ? window.scrollY + top - (vh - h) / 2 : window.scrollY + top - vh * 0.08;
    window.scrollTo({ top: Math.max(0, y), behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }
  function openFolds(n) {
    for (let d = n && n.closest ? n.closest("details") : null; d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
  }

  function go(i, opts) {
    const n = script.steps.length;
    spot = null;
    cur = n ? Math.max(0, Math.min(n - 1, i)) : 0;
    render({ scroll: !(opts && opts.noScroll) });
  }
  function next() { if (spot) { spot = null; } if (cur >= script.steps.length - 1) { flashCount(); render({ scroll: true }); return; } go(cur + 1); }
  function prev() { if (spot) { spot = null; } if (cur <= 0) { flashCount(); render({ scroll: true }); return; } go(cur - 1); }

  /* ---------- the TOC as the progress map ---------- */
  const unfolded = new Set();   // TOC groups present mode opened, folded again on the way out
  function setFold(g, folded) {
    g.classList.toggle("tl-fold", folded);
    const car = doc.querySelector('.tl-car[data-for="' + g.id + '"]');
    if (car) car.setAttribute("aria-expanded", folded ? "false" : "true");
  }
  function tocProgress(curSec) {
    headings.forEach((x) => { if (x.row) x.row.classList.remove("pr-done", "pr-cur", "pr-todo", "pr-up"); });
    if (!on) { unfolded.forEach((g) => setFold(g, true)); unfolded.clear(); return; }
    if (!(script.steps.length || spot)) return;
    // A step above the first heading (the title, the overview) has every section still to come.
    const ci = curSec ? headings.indexOf(curSec) : -1;
    if (ci < 0) { headings.forEach((x) => { if (x.row) x.row.classList.add("pr-todo"); }); return; }
    headings.forEach((x, i) => { if (x.row) x.row.classList.add(i < ci ? "pr-done" : i === ci ? "pr-cur" : "pr-todo"); });
    if (!curSec.row) return;
    // Only the part being presented is unfolded, so the sidebar reads as an agenda.
    const keep = new Set();
    for (let g = curSec.row.parentElement; g && !g.classList.contains("toc-layer"); g = g.parentElement) {
      if (!g.classList.contains("tl-grp")) continue;
      keep.add(g);
      if (g.classList.contains("tl-fold")) { setFold(g, false); unfolded.add(g); }
      const head = g.previousElementSibling;
      if (head && head.classList.contains("tl-row")) head.classList.add("pr-up");
    }
    unfolded.forEach((g) => { if (!keep.has(g)) { setFold(g, true); unfolded.delete(g); } });
    const nav = curSec.row.closest(".toc-layer");
    if (nav) {
      const r = curSec.row.getBoundingClientRect(), nr = nav.getBoundingClientRect();
      if (r.top < nr.top + 48 || r.bottom > nr.bottom - 48) nav.scrollTop += r.top - nr.top - nr.height / 3;
    }
  }

  /* ---------- store ---------- */
  async function load() {
    if (location.protocol.startsWith("http")) {
      try {
        const r = await fetch(ENDPOINT, { cache: "no-store" });
        if (r.ok && /json/.test(r.headers.get("Content-Type") || "")) { backend = "server"; writable = true; return normalize(await r.json()); }
      } catch (e) {}
      try {
        const r = await fetch(STATIC, { cache: "no-store" });
        if (r.ok) { backend = "static"; writable = false; return normalize(await r.json()); }
      } catch (e) {}
    }
    backend = "local"; writable = true;
    try { return normalize(JSON.parse(localStorage.getItem(LSKEY) || "{}")); } catch (e) { return normalize({}); }
  }
  let saveTimer = null;
  function save() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, 250);
  }
  async function flush() {
    clearTimeout(saveTimer); saveTimer = null;
    const txt = JSON.stringify(script, null, 2);
    if (backend === "server") {
      try { const r = await fetch(ENDPOINT, { method: "PUT", headers: { "Content-Type": "application/json" }, body: txt }); if (r.ok) return; } catch (e) {}
      toast("Could not reach the server. The script is kept in this browser for now.");
    }
    try { localStorage.setItem(LSKEY, txt); } catch (e) {}
  }
  function remember() {
    try { sessionStorage.setItem(SKEY, JSON.stringify({ on: on, editing: editing, cur: cur })); } catch (e) {}
  }

  /* ---------- editing the script ---------- */
  function snapshot() { undo.push(JSON.stringify(script)); if (undo.length > 80) undo.shift(); }
  function changed(opts) { save(); render({ scroll: !!(opts && opts.scroll) }); }
  function guard() {
    if (writable) return true;
    toast("This copy is read-only. Edit the script where serve.py runs, then publish it.");
    return false;
  }
  function newStep(anchor, pickInfo) {
    snapshot();
    const at = script.steps.length ? cur + 1 : 0;
    script.steps.splice(at, 0, { id: sid(), targets: [anchor], note: "" });
    cur = at;
    last = pickInfo ? { step: at, idx: 0, chain: pickInfo.chain, pos: pickInfo.pos } : null;
    changed();
  }
  function addToStep(anchor, node, pickInfo) {
    const s = script.steps[cur];
    if (!s) return newStep(anchor, pickInfo);
    const have = (res.steps[cur] || []).findIndex((r) => r && litOf(r) === node && !r.range);
    if (have >= 0 && anchor.type !== "range") {         // ⇧click on a lit block takes it back out
      snapshot(); s.targets.splice(have, 1);
      if (!s.targets.length) { script.steps.splice(cur, 1); cur = Math.max(0, cur - 1); }
      last = null; return changed();
    }
    if (s.targets.length >= MAX) { toast("A step lights " + MAX + " things at most. Start a new step, or widen to their common block with ⌥↑."); return; }
    snapshot();
    s.targets.push(anchor);
    last = pickInfo ? { step: cur, idx: s.targets.length - 1, chain: pickInfo.chain, pos: pickInfo.pos } : null;
    changed();
  }
  function toggleHidden(node) {
    const i = res.hidden.indexOf(node);
    snapshot();
    if (i >= 0) script.hidden.splice(i, 1);
    else script.hidden.push(anchorOf(node, null));
    changed();
    toast(i >= 0 ? "Shown again in the talk." : "Hidden in the talk until a step lights it.");
  }
  function deleteStep(i) {
    if (!script.steps[i]) return;
    snapshot();
    script.steps.splice(i, 1);
    cur = Math.max(0, Math.min(cur, script.steps.length - 1));
    last = null;
    changed();
    toast("Step deleted. ⌘Z brings it back.");
  }
  function moveStep(from, to) {
    if (from === to || !script.steps[from]) return;
    snapshot();
    const curId = script.steps[cur] && script.steps[cur].id;
    const s = script.steps.splice(from, 1)[0];
    script.steps.splice(to > from ? to - 1 : to, 0, s);
    cur = Math.max(0, script.steps.findIndex((x) => x.id === curId));
    last = null;
    changed();
  }
  function removeTarget(i, k) {
    const s = script.steps[i]; if (!s) return;
    snapshot();
    s.targets.splice(k, 1);
    if (!s.targets.length) { script.steps.splice(i, 1); if (cur >= i) cur = Math.max(0, cur - 1); }
    last = null;
    changed();
  }
  function retarget(p) {
    const s = script.steps[last.step];
    if (!s || !s.targets[last.idx]) return;
    snapshot();
    s.targets[last.idx] = anchorOf(last.chain[p], null);
    last.pos = p;
    changed();
  }
  function widen() {
    if (!last) { toast("⌥↑ widens the block you picked last. Pick one first."); return; }
    for (let p = last.pos + 1; p < last.chain.length; p++) if (isBlock(last.chain[p])) return retarget(p);
    toast("That is already the widest block inside the page.");
  }
  function narrow() {
    if (!last) { toast("⌥↓ narrows the block you picked last. Pick one first."); return; }
    for (let p = last.pos - 1; p >= 0; p--) if (isUnit(last.chain[p])) return retarget(p);
    toast("Nothing smaller under that click.");
  }
  function undoOnce() {
    const s = undo.pop();
    if (!s) { toast("Nothing to undo."); return; }
    script = normalize(JSON.parse(s));
    last = null;
    changed();
    toast("Undone.");
  }

  /* ---------- input ---------- */
  function onKey(e) {
    const t = e.target;
    const typing = !!t && t.nodeType === 1 && (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable);
    const plain = !e.metaKey && !e.ctrlKey && !e.altKey;
    if (!on) {
      if (!typing && plain && (e.code === "KeyP" || e.key === "F5")) { e.preventDefault(); e.stopImmediatePropagation(); enter(); }
      return;
    }
    if (typing) { if (e.key === "Escape") t.blur(); return; }
    const k = e.key;
    let done = true;
    if ((e.metaKey || e.ctrlKey) && e.code === "KeyZ" && editing) undoOnce();
    else if (e.altKey && k === "ArrowUp" && editing) widen();
    else if (e.altKey && k === "ArrowDown" && editing) narrow();
    else if (!plain) done = false;                           // leave the browser's own shortcuts alone
    else if (k === "ArrowRight" || k === "PageDown" || k === "Enter" || (k === " " && !e.shiftKey)) { if (blank) toggleBlank(false); else next(); }
    else if (k === "ArrowLeft" || k === "PageUp" || (k === " " && e.shiftKey)) { if (blank) toggleBlank(false); else prev(); }
    else if (k === "Home") go(0);
    else if (k === "End") go(script.steps.length - 1);
    else if (k === "Escape") { if (blank) toggleBlank(false); else if (spot) { spot = null; render({ scroll: true }); } else exit(); }
    else if (e.code === "KeyP") exit();
    else if (e.code === "KeyE") setEditing(!editing);
    else if (e.code === "KeyS") openSpeaker();
    else if (e.code === "KeyB" || k === ".") toggleBlank();
    else if (e.code === "KeyT") toggleToc();
    else if ((k === "Backspace" || k === "Delete") && editing) { if (guard()) deleteStep(cur); }
    else if (e.code === "KeyC" || k === "F5") {}            // comment mode stays off while presenting
    else done = false;
    if (done) { e.preventDefault(); e.stopImmediatePropagation(); }
  }

  // A drag selects words; a click picks a block. The browser turns ⇧click into "extend the
  // selection to here", so a modified press must not start or extend a selection at all.
  let down = null;
  function onDown(e) {
    if (!on || e.button !== 0) return;
    const t = e.target;
    if (!t || !t.closest || t.closest(SKIP) || !root.contains(t)) { down = null; return; }
    down = { x: e.clientX, y: e.clientY };
    if (e.shiftKey || e.altKey) e.preventDefault();
  }
  function onClick(e) {
    if (!on) return;
    const t = e.target;
    if (!t || !t.closest || t.closest(SKIP) || !root.contains(t)) return;
    if (!editing && (e.metaKey || e.ctrlKey)) return;          // ⌘click still opens a link
    e.preventDefault(); e.stopImmediatePropagation();
    if (e.detail > 1) return;                                  // the second click of a double-click
    const sel = window.getSelection();
    const dragged = !!down && Math.hypot(e.clientX - down.x, e.clientY - down.y) > 4;
    let range = null;
    if (dragged && sel && !sel.isCollapsed && root.contains(sel.anchorNode) && root.contains(sel.focusNode) && norm(sel.toString())) {
      range = sel.getRangeAt(0).cloneRange();
    } else if (sel && !sel.isCollapsed && editing) sel.removeAllRanges();
    if (editing) {
      if (!guard()) return;
      if (range) {
        sel.removeAllRanges();
        const block = blockOf(range.commonAncestorContainer);
        if (!block) return;
        const anchor = anchorOf(null, range);
        if (e.shiftKey) addToStep(anchor, block, null); else newStep(anchor, null);
        return;
      }
      const p = pickFrom(t);
      if (!p) return;
      if (e.altKey) { toggleHidden(p.node); return; }
      const anchor = anchorOf(p.node, null);
      if (e.shiftKey) addToStep(anchor, p.node, p); else newStep(anchor, p);
      return;
    }
    // play: a spotlight off the script. A drag leaves the browser's own selection as the highlight.
    if (dragged) return;
    const p = pickFrom(t);
    if (!p || res.hidden.some((h) => h && (h === p.node || h.contains(p.node)))) return;
    const item = { node: p.node, range: null };
    if (e.shiftKey && spot) { if (!spot.some((x) => x.node === p.node) && spot.length < MAX) spot.push(item); }
    else spot = [item];
    render({ scroll: false });
  }

  let hoverRaf = 0, hoverTarget = null;
  function onMove(e) {
    if (!on || !editing) return;
    hoverTarget = e.target;
    if (hoverRaf) return;
    hoverRaf = requestAnimationFrame(() => {
      hoverRaf = 0;
      const t = hoverTarget;
      const p = t && t.closest && !t.closest(SKIP) && root.contains(t) ? pickFrom(t) : null;
      setHover(p ? p.node : null);
    });
  }
  function setHover(n) {
    if (hoverNode === n) return;
    if (hoverNode) hoverNode.classList.remove("pr-pick");
    hoverNode = n;
    if (n) n.classList.add("pr-pick");
  }

  /* ---------- entering and leaving ---------- */
  function enter(opts) {
    if (on) return;
    on = true;
    const cl = window.__commentLayer;
    if (cl && cl.setMode) cl.setMode(false);
    doc.body.classList.add("pr-on");
    root.setAttribute("data-pr-root", "");
    applyLook();
    resolveAll();
    editing = opts && typeof opts.editing === "boolean" ? opts.editing : !script.steps.length;
    doc.body.classList.toggle("pr-edit", editing);
    cur = opts && Number.isFinite(opts.cur) ? opts.cur : 0;
    dock();
    render({ scroll: true });
    if (!script.steps.length) toast("Present mode. Click what you will talk about first, then the next thing. E plays it, P leaves.");
  }
  function exit() {
    if (!on) return;
    on = false; editing = false; spot = null; blank = false; last = null;
    unpaint();
    setMarks([], []);
    setHover(null);
    touched.forEach((n) => n.classList.remove("pr-t"));
    touched.clear();
    tocProgress(null);
    doc.body.classList.remove("pr-on", "pr-edit", "pr-blanked", "pr-docked", "pr-preview");
    root.removeAttribute("data-pr-root");
    dock();
    const cl = window.__commentLayer;
    if (cl && cl.relayout) cl.relayout();
    if (spk && !spk.closed) spk.close();
    if (saveTimer) flush();
    remember();
  }
  function setEditing(v) {
    editing = !!v; spot = null;
    doc.body.classList.toggle("pr-edit", editing);
    if (!editing) { setHover(null); doc.body.classList.remove("pr-preview"); }
    dock();
    render({ scroll: false });
  }
  function dock() {
    const wide = matchMedia("(min-width: 1360px)").matches;
    const show = on && editing;
    if (ui.panel) ui.panel.classList.toggle("pr-open", show);
    doc.body.classList.toggle("pr-docked", show && wide);
    if (window.__dockLayout) window.__dockLayout.set("right", show && wide ? PANEL_W : 0, root);
  }
  function applyLook() {
    doc.body.style.setProperty("--pr-past", String(script.look.past));
    doc.body.style.setProperty("--pr-rest", String(script.look.rest));
  }
  function toggleBlank(v) { blank = v === undefined ? !blank : !!v; doc.body.classList.toggle("pr-blanked", blank); }
  function toggleToc() {
    const nav = doc.querySelector(".toc-layer");
    if (!nav) return;
    if (doc.body.classList.contains("tl-docked") || doc.body.classList.contains("tl-open")) { const c = nav.querySelector(".tl-close"); if (c) c.click(); }
    else { const b = doc.querySelector(".tl-btn"); if (b) b.click(); }
  }

  /* ---------- chrome: progress bar, counter, toast, blank ---------- */
  function buildUI() {
    const u = el("div", "pr-ui");
    ui.bar = el("div", "pr-bar", "<i></i>");
    ui.count = el("button", "pr-count");
    ui.count.addEventListener("click", () => setEditing(!editing));
    ui.toast = el("div", "pr-toast");
    ui.blank = el("div", "pr-blank");
    ui.panel = el("aside", "pr-panel");
    ui.panel.style.width = PANEL_W + "px";
    ui.panel.innerHTML =
      '<div class="pr-head"><b>Present</b><span class="pr-store"></span><span class="pr-sp"></span>' +
      '<button class="pr-btn pr-play" title="Play the script (E)">▶ Play</button>' +
      '<button class="pr-btn pr-ghost pr-x" title="Leave present mode (P or Esc)">×</button></div>' +
      '<div class="pr-look">' +
      '<label class="pr-lrow"><span>Earlier steps</span><select class="pr-earlier">' +
      '<option value="section">stay half-lit in their section</option><option value="all">stay half-lit all talk</option>' +
      '<option value="none">fade with the rest</option></select></label>' +
      '<label class="pr-lrow"><span>Section title</span><select class="pr-title">' +
      '<option value="now">stays lit</option><option value="past">half-lit</option><option value="rest">fades</option></select></label>' +
      '<label class="pr-lrow"><span>Half-lit</span><input type="range" class="pr-past-r" min="0" max="100" step="5"><b class="pr-past-v"></b></label>' +
      '<label class="pr-lrow"><span>Faded</span><input type="range" class="pr-rest-r" min="0" max="60" step="2"><b class="pr-rest-v"></b></label>' +
      '<div class="pr-look-note">While the pointer is here, the page shows the talk\'s true look.</div>' +
      "</div>" +
      '<div class="pr-list"></div>' +
      '<details class="pr-hid"><summary>Hidden in the talk <span class="pr-hid-n"></span></summary><div class="pr-hid-list"></div></details>' +
      '<div class="pr-keys">' +
      "<div><kbd>click</kbd> new step after this one</div><div><kbd>⇧ click</kbd> add to this step, 3 at most</div>" +
      "<div><kbd>⌥ click</kbd> hide or show in the talk</div><div><kbd>select text</kbd> a step that marks those words</div>" +
      "<div><kbd>⌥↑</kbd> <kbd>⌥↓</kbd> wider or narrower block</div><div><kbd>⌫</kbd> delete step · <kbd>⌘Z</kbd> undo</div>" +
      "<div><kbd>→</kbd> <kbd>←</kbd> walk the steps · <kbd>E</kbd> play · <kbd>S</kbd> presenter window</div></div>";
    u.append(ui.bar, ui.count, ui.toast, ui.blank, ui.panel);
    doc.body.appendChild(u);
    wirePanel();
  }
  function renderChrome() {
    const n = script.steps.length;
    ui.bar.firstChild.style.width = n ? ((cur + 1) / n * 100) + "%" : "0";
    ui.count.innerHTML = (editing ? "<em>edit</em>" : "") + (spot ? "<em>spotlight</em>" : "") + (n ? (cur + 1) + " / " + n : "no steps");
    ui.count.title = editing ? "Editing the script. Click or press E to play it." : "Presenting. Click or press E to edit the script. P leaves.";
  }
  let countTimer = null;
  function flashCount() { ui.count.classList.add("pr-bump"); clearTimeout(countTimer); countTimer = setTimeout(() => ui.count.classList.remove("pr-bump"), 500); }
  let toastTimer = null;
  function toast(msg) {
    if (!ui.toast) return;
    ui.toast.textContent = msg;
    ui.toast.classList.add("pr-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => ui.toast.classList.remove("pr-show"), 3200);
  }

  /* ---------- the edit panel ---------- */
  function describe(node, range) {
    if (range) return "“" + clip(range.toString(), 44) + "”";
    if (!node || node.nodeType !== 1) return "?";
    const tag = node.tagName.toLowerCase(), t = (s) => clip(s, 44);
    if (/^h[1-6]$/.test(tag)) return "§ " + t(node.textContent);
    if (tag === "figure") { const c = node.querySelector("figcaption b") || node.querySelector("figcaption"); const i = node.querySelector("img"); return "▣ " + t(c ? c.textContent : (i && i.alt) || "figure"); }
    if (tag === "img") return "▣ " + t(node.alt || (node.getAttribute("src") || "").split("/").pop());
    if (tag === "svg") return "▣ " + t(node.textContent || "drawing");
    if (node.namespaceURI === SVGNS) return "▣ part: " + t(node.textContent || tag);
    if (tag === "pre") return node.classList.contains("map") ? "▤ map box" : "▤ " + t(node.textContent);
    if (tag === "li") return "• " + t(node.textContent);
    if (tag === "tr") return "row: " + t(Array.prototype.map.call(node.children, (c) => c.textContent).join(" · "));
    if (tag === "table") { const c = node.querySelector("caption"); return "▦ " + t(c ? c.textContent : node.textContent); }
    if (tag === "ul" || tag === "ol") return "list: " + t(node.textContent);
    if (node.classList.contains("gal")) { const c = node.querySelector("figcaption b"); return "▣ gallery: " + t(c ? c.textContent : "images"); }
    return t(node.textContent) || tag;
  }
  function renderPanel() {
    const P = ui.panel;
    P.querySelector(".pr-store").textContent = backend === "server" ? "saved beside the page" : backend === "static" ? "read-only copy" : "saved in this browser";
    P.querySelector(".pr-earlier").value = script.look.earlier;
    P.querySelector(".pr-title").value = script.look.title;
    P.querySelector(".pr-past-r").value = Math.round(script.look.past * 100);
    P.querySelector(".pr-rest-r").value = Math.round(script.look.rest * 100);
    P.querySelector(".pr-past-v").textContent = Math.round(script.look.past * 100) + "%";
    P.querySelector(".pr-rest-v").textContent = Math.round(script.look.rest * 100) + "%";
    const list = P.querySelector(".pr-list");
    const keepScroll = list.scrollTop;
    list.innerHTML = "";
    if (!script.steps.length) list.appendChild(el("div", "pr-empty", "No steps yet. Click what you will talk about first, then the next thing, in the order you will say them."));
    let lastSec;
    script.steps.forEach((s, i) => {
      const sec = stepSec[i] || null;
      if (i === 0 || sec !== lastSec) list.appendChild(el("div", "pr-sec", esc(sec ? clip(sec.h.textContent, 52) : "Before the first section")));
      lastSec = sec;
      const chips = s.targets.map((a, k) => {
        const r = (res.steps[i] || [])[k];
        const label = r ? describe(litOf(r), r.range) : "⚠ not found: " + (a.label || "?");
        return '<span class="pr-chip' + (r ? "" : " pr-lost") + '" data-k="' + k + '" title="' + esc(a.label || "") + '">' +
          esc(label) + '<button class="pr-chip-x" title="Take it out of this step">×</button></span>';
      }).join("");
      const row = el("div", "pr-step" + (i === cur ? " pr-on-step" : ""));
      row.dataset.i = String(i);
      row.innerHTML = '<span class="pr-num" draggable="true" title="Drag to reorder">' + (i + 1) + "</span>" +
        '<div class="pr-body"><div class="pr-chips">' + chips + "</div>" +
        (i === cur
          ? '<textarea class="pr-note" rows="2" placeholder="Notes for this step. Only the presenter window (S) shows them.">' + esc(s.note) + "</textarea>"
          : (s.note ? '<div class="pr-peek">' + esc(clip(s.note, 90)) + "</div>" : "")) +
        '</div><button class="pr-del" title="Delete this step (⌫)">×</button>';
      list.appendChild(row);
    });
    list.scrollTop = keepScroll;
    const curRow = list.querySelector(".pr-on-step");
    if (curRow) {
      const r = curRow.getBoundingClientRect(), lr = list.getBoundingClientRect();
      if (r.top < lr.top || r.bottom > lr.bottom) list.scrollTop += r.top - lr.top - lr.height / 3;
    }
    const hl = P.querySelector(".pr-hid-list");
    P.querySelector(".pr-hid-n").textContent = script.hidden.length ? "(" + script.hidden.length + ")" : "";
    hl.innerHTML = script.hidden.length ? script.hidden.map((a, k) => {
      const n = res.hidden[k];
      return '<span class="pr-chip' + (n ? "" : " pr-lost") + '" data-h="' + k + '" title="' + esc(a.label || "") + '">' +
        esc(n ? describe(n, null) : "⚠ not found: " + (a.label || "?")) + '<button class="pr-chip-x" title="Show it again">×</button></span>';
    }).join("") : '<div class="pr-empty">⌥click a block to keep it out of the talk until a step lights it.</div>';
  }
  function wirePanel() {
    const P = ui.panel;
    P.querySelector(".pr-play").addEventListener("click", () => setEditing(false));
    P.querySelector(".pr-x").addEventListener("click", exit);
    const setLook = (k, v) => { script.look[k] = v; applyLook(); save(); render({ scroll: false }); };
    P.querySelector(".pr-earlier").addEventListener("change", (e) => setLook("earlier", e.target.value));
    P.querySelector(".pr-title").addEventListener("change", (e) => setLook("title", e.target.value));
    P.querySelector(".pr-past-r").addEventListener("input", (e) => setLook("past", +e.target.value / 100));
    P.querySelector(".pr-rest-r").addEventListener("input", (e) => setLook("rest", +e.target.value / 100));
    // Edit keeps the page readable, so tuning the look would show nothing. Preview it while the
    // pointer or the keyboard focus is on the look controls.
    const lookBox = P.querySelector(".pr-look");
    const preview = (v) => doc.body.classList.toggle("pr-preview", v);
    lookBox.addEventListener("mouseenter", () => preview(true));
    lookBox.addEventListener("mouseleave", () => preview(lookBox.contains(doc.activeElement)));
    lookBox.addEventListener("focusin", () => preview(true));
    lookBox.addEventListener("focusout", () => preview(lookBox.matches(":hover")));
    const list = P.querySelector(".pr-list");
    list.addEventListener("click", (e) => {
      const row = e.target.closest(".pr-step");
      if (!row) return;
      const i = +row.dataset.i;
      if (e.target.closest(".pr-del")) { if (guard()) deleteStep(i); return; }
      const x = e.target.closest(".pr-chip-x");
      if (x) { if (guard()) removeTarget(i, +x.parentElement.dataset.k); return; }
      if (e.target.closest(".pr-note")) return;
      go(i);
    });
    list.addEventListener("input", (e) => {
      if (!e.target.classList.contains("pr-note")) return;
      const s = script.steps[+e.target.closest(".pr-step").dataset.i];
      if (s && writable) { s.note = e.target.value; save(); syncSpeaker(true); }
    });
    // Drag a step by its number to reorder.
    let from = null;
    const clear = () => list.querySelectorAll(".pr-drop-before, .pr-drop-after, .pr-dragging").forEach((r) => r.classList.remove("pr-drop-before", "pr-drop-after", "pr-dragging"));
    list.addEventListener("dragstart", (e) => {
      const row = e.target.closest && e.target.closest(".pr-step");
      if (!row) return;
      from = +row.dataset.i;
      row.classList.add("pr-dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", String(from));
    });
    list.addEventListener("dragover", (e) => {
      const row = e.target.closest && e.target.closest(".pr-step");
      if (!row || from == null) return;
      e.preventDefault();
      const r = row.getBoundingClientRect(), after = e.clientY > r.top + r.height / 2;
      list.querySelectorAll(".pr-drop-before, .pr-drop-after").forEach((x) => { if (x !== row) x.classList.remove("pr-drop-before", "pr-drop-after"); });
      row.classList.toggle("pr-drop-after", after); row.classList.toggle("pr-drop-before", !after);
    });
    list.addEventListener("drop", (e) => {
      const row = e.target.closest && e.target.closest(".pr-step");
      if (!row || from == null) return;
      e.preventDefault();
      const to = +row.dataset.i + (row.classList.contains("pr-drop-after") ? 1 : 0);
      const f = from; from = null; clear();
      if (guard()) moveStep(f, to);
    });
    list.addEventListener("dragend", () => { from = null; clear(); });
    P.querySelector(".pr-hid-list").addEventListener("click", (e) => {
      const chip = e.target.closest(".pr-chip");
      if (!chip) return;
      const k = +chip.dataset.h;
      if (e.target.closest(".pr-chip-x")) { if (guard()) { snapshot(); script.hidden.splice(k, 1); changed(); } return; }
      const n = res.hidden[k];
      if (n) { openFolds(n); n.scrollIntoView({ block: "center", behavior: "smooth" }); }
    });
  }

  /* ---------- presenter window ----------
     A popup the opener writes and drives directly (same origin, so no messaging layer).
     Share the main tab and keep this one to yourself: the audience never sees the notes. */
  let spk = null, t0 = 0, tick = null;
  const SPK_CSS =
    "body{margin:0;font:16px/1.5 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1f2330;background:#fbfbfd}" +
    "header{position:sticky;top:0;display:flex;gap:14px;align-items:baseline;padding:14px 20px;border-bottom:1px solid #e6e8ee;background:#fff}" +
    "#n{font-weight:700;font-size:20px}#t{font-variant-numeric:tabular-nums;color:#6b7280}" +
    "#sec{flex:1;text-align:right;color:#d24d7c;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}" +
    "main{padding:6px 20px 90px}.k{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#9aa0b1;margin:16px 0 6px}" +
    ".chips span{display:inline-block;margin:0 6px 6px 0;padding:2px 9px;border-radius:999px;background:#fbeef4;color:#8a2f55;font-size:13px}" +
    "#note{font-size:24px;line-height:1.45;white-space:pre-wrap}#note:empty::before{content:'No notes for this step.';color:#b4b8c4}" +
    "#next{opacity:.7}#nnote{font-size:15px;line-height:1.45;white-space:pre-wrap;color:#5a6072}" +
    "nav{position:fixed;left:0;right:0;bottom:0;display:flex;gap:10px;padding:10px 20px;background:#fff;border-top:1px solid #e6e8ee}" +
    "button{font:600 14px/1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:10px 16px;border-radius:8px;border:1px solid #e6e8ee;background:#fff;cursor:pointer}" +
    "button:hover{background:#f5f6f8}";
  function openSpeaker() {
    if (spk && !spk.closed) { spk.focus(); return; }
    spk = window.open("", "pr-speaker-" + docId, "popup=yes,width=560,height=760");
    if (!spk) { toast("The browser blocked the presenter window. Allow pop-ups for this page, then press S again."); return; }
    const d = spk.document;
    d.open();
    d.write('<!doctype html><html><head><meta charset="utf-8"><title>Presenter · ' + esc(doc.title) + "</title><style>" + SPK_CSS + "</style></head><body>" +
      '<header><span id="n"></span><span id="t">0:00</span><span id="sec"></span></header>' +
      '<main><div class="k">now</div><div class="chips" id="now"></div><div id="note"></div>' +
      '<div id="next"><div class="k">next</div><div class="chips" id="nx"></div><div id="nnote"></div></div></main>' +
      '<nav><button id="back">← back</button><button id="fwd">next →</button><span style="flex:1"></span><button id="reset">reset timer</button></nav></body></html>');
    d.close();
    d.getElementById("back").addEventListener("click", () => prev());
    d.getElementById("fwd").addEventListener("click", () => next());
    d.getElementById("reset").addEventListener("click", () => { t0 = Date.now(); syncSpeaker(false); });
    d.addEventListener("keydown", onKey, true);
    t0 = Date.now();
    clearInterval(tick);
    tick = setInterval(() => syncSpeaker(false), 1000);
    syncSpeaker(true);
  }
  function syncSpeaker(full) {
    if (!spk) return;
    if (spk.closed) { spk = null; clearInterval(tick); return; }
    const d = spk.document, $ = (id) => d.getElementById(id);
    if (!$("n")) return;
    const s = Math.floor((Date.now() - t0) / 1000);
    $("t").textContent = Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
    if (!full) return;
    const n = script.steps.length;
    $("n").textContent = n ? (cur + 1) + " / " + n : "no steps";
    $("sec").textContent = stepSec[cur] ? norm(stepSec[cur].h.textContent) : "";
    const chips = (i) => (script.steps[i] ? script.steps[i].targets.map((a, k) => {
      const r = (res.steps[i] || [])[k];
      return "<span>" + esc(r ? describe(litOf(r), r.range) : a.label || "?") + "</span>";
    }).join("") : "");
    $("now").innerHTML = spot ? "<span>spotlight, off the script</span>" : chips(cur);
    $("note").textContent = (script.steps[cur] && script.steps[cur].note) || "";
    $("nx").innerHTML = chips(cur + 1) || "<span>the end</span>";
    $("nnote").textContent = (script.steps[cur + 1] && script.steps[cur + 1].note) || "";
  }

  /* ---------- the TOC header gets a Present button ---------- */
  function addTocButton() {
    const head = doc.querySelector(".toc-layer .tl-head");
    if (!head || head.querySelector(".pr-tocbtn")) return;
    const b = el("button", "pr-tocbtn", "▶ Present");
    b.type = "button";
    b.title = "Present this page (P)";
    b.addEventListener("click", () => (on ? exit() : enter()));
    head.insertBefore(b, head.querySelector(".tl-close"));
  }
  // A click on a section in the TOC, while playing, jumps to that section's first step.
  function onTocClick(e) {
    if (!on || editing) return;
    const a = e.target.closest && e.target.closest(".toc-layer .tl-row > a");
    if (!a) return;
    const x = headings.find((h) => h.a === a);
    if (!x) return;
    const hi = headings.indexOf(x);
    const j = stepSec.findIndex((s) => s && headings.indexOf(s) >= hi);
    if (j < 0) return;
    e.preventDefault(); e.stopPropagation();
    a.blur();   // keep the focus ring off the sidebar while presenting
    go(j);
  }

  /* ---------- bridge ---------- */
  window.__presentLayer = {
    docId: docId,
    enter: (o) => enter(o), exit: exit, next: next, prev: prev,
    go: (i) => go(i), edit: (v) => setEditing(v === undefined ? true : v),
    state: () => ({ on: on, editing: editing, cur: cur, steps: script.steps.length, hidden: script.hidden.length, backend: backend, writable: writable, look: Object.assign({}, script.look), speaker: !!(spk && !spk.closed) }),
    speakerText: () => (spk && !spk.closed ? spk.document.body.innerText : null),
    steps: () => { if (!on) resolveAll(); return script.steps.map((s, i) => ({ i: i, section: stepSec[i] ? norm(stepSec[i].h.textContent) : "", targets: s.targets.map((a, k) => { const r = (res.steps[i] || [])[k]; return r ? describe(litOf(r), r.range) : "⚠ " + (a.label || "?"); }), note: s.note })); },
    export: () => JSON.stringify(script, null, 2),
    import: (json) => { snapshot(); script = normalize(typeof json === "string" ? JSON.parse(json) : json); applyLook(); save(); if (on) render({ scroll: true }); return true; },
  };

  /* ---------- init ---------- */
  async function init() {
    const cl = window.__commentLayer;
    // Wait for the comment layer's store and root, but never hang on it.
    if (cl && cl.ready) { try { await Promise.race([cl.ready, new Promise((r) => setTimeout(r, 4000))]); } catch (e) {} }
    const sel = html.getAttribute("data-comment-root");
    root = (cl && cl.root && cl.root()) || (sel && doc.querySelector(sel)) || doc.querySelector("#content") || doc.querySelector("main") || doc.body;
    script = await load();
    buildUI();
    readHeadings();
    addTocButton();
    window.addEventListener("keydown", onKey, true);
    window.addEventListener("mousedown", onDown, true);
    window.addEventListener("click", onClick, true);
    doc.addEventListener("click", onTocClick, true);
    window.addEventListener("mousemove", onMove, true);
    window.addEventListener("resize", () => { if (on) dock(); });
    // A save still waiting on its debounce when the tab closes goes out as a beacon (serve.py takes POST as PUT).
    window.addEventListener("pagehide", () => {
      if (!saveTimer) return;
      clearTimeout(saveTimer); saveTimer = null;
      const txt = JSON.stringify(script, null, 2);
      if (backend === "server" && navigator.sendBeacon) navigator.sendBeacon(ENDPOINT, new Blob([txt], { type: "application/json" }));
      else { try { localStorage.setItem(LSKEY, txt); } catch (e) {} }
    });
    let s = null;
    try { s = JSON.parse(sessionStorage.getItem(SKEY) || "null"); } catch (e) {}
    if (s && s.on) enter({ editing: !!s.editing, cur: s.cur | 0 });
    console.log("[present-layer] ready — doc:", docId, "| store:", backend, "| steps:", script.steps.length, "| press P to present");
  }

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init);
  else init();
})();
