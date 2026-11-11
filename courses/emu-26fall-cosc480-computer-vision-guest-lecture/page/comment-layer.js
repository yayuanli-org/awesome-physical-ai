/* commentable-html — in-context comment layer for AI-delivered HTML.
 *
 * A toggleable overlay that lets a human attach threaded comments to selected
 * elements / text ranges, and lets an AI read them and reply — across rounds.
 * Content is never owned by this layer; comments live in a separate store.
 *
 * Dependency-free. Drop in with:
 *   <link rel="stylesheet" href="comment-layer.css">
 *   <script src="comment-layer.js"></script>
 * Optional on <html>: data-comment-doc="<id>"  data-comment-root="<selector>"
 *
 * A comments panel docks on the right (≥1360px; overlay below): every thread with
 * its full message history, click to jump to the commented content. Fold with »,
 * reopen via the « Comments chip bottom-right; drag its left edge to resize.
 * Panel state and width persist per doc. Content margins are coordinated with the
 * TOC layer through window.__dockLayout so sidebars and content never overlap.
 *
 * Persistence:
 *   - Served over http(s) with serve.py  -> reads/writes <docId>.comments.json
 *   - Opened as file://                  -> localStorage + window.__commentLayer
 *
 * Authorship: each message is signed with the commenter's name, resolved at load from
 * the access gate (GET ./__whoami__, served by publish-commentable-html's app.py), else
 * a name remembered in this browser, else asked once in the compose box. On a shared doc
 * the panel therefore shows who said what. "AI" stays the reserved author for AI replies.
 *
 * AI bridge (works in any mode, via Chrome devtools / file mode):
 *   __commentLayer.export()                       -> JSON string of all threads
 *   __commentLayer.import(jsonString)             -> replace store, re-render
 *   __commentLayer.reply(threadId, text[, author, agent]) -> append an AI reply;
 *       agent = { session, host } identity note (which AI session, on which machine)
 *   __commentLayer.editMessage(threadId, idx, text) -> rewrite a message in place
 *   __commentLayer.setStatus(threadId, "resolved"|"open")
 *   __commentLayer.threads()                      -> array with resolved anchor labels, and `drawn`:
 *       "words" (just the picked words are painted), "block" (the whole element), or "none"
 *
 * For present-layer.js (present mode), which anchors its steps the same way comments anchor:
 *   __commentLayer.ready                          -> Promise, resolved once init has finished
 *   __commentLayer.root()                         -> the content root
 *   __commentLayer.anchor.{build, resolveMany, label}
 *   __commentLayer.setMode(bool) · __commentLayer.relayout()
 * While body.pr-on is set, this layer ignores its keys and leaves the right dock alone.
 */
(function () {
  "use strict";
  if (window.__commentLayerLoaded) return;
  window.__commentLayerLoaded = true;

  // Shared left/right dock layout — defined by whichever layer (toc/comment) loads first.
  // Each docked sidebar reports its width; the content root is re-margined to the free band.
  window.__dockLayout = window.__dockLayout || (function () {
    var slots = { left: 0, right: 0 }, root = null;
    function apply() {
      if (!root) return;
      var L = slots.left ? slots.left + 24 : 0, R = slots.right ? slots.right + 24 : 0;
      if (!L && !R) { root.style.marginLeft = ""; root.style.marginRight = ""; return; }
      var cs = getComputedStyle(root);
      var mw = parseFloat(cs.maxWidth);
      var outer = mw ? mw + (parseFloat(cs.paddingLeft) || 0) + (parseFloat(cs.paddingRight) || 0) : 0;
      var avail = window.innerWidth - L - R;
      if (outer && avail > outer) { // content keeps its width, centered in the free band
        root.style.marginLeft = (L + (avail - outer) / 2) + "px";
        root.style.marginRight = "";
      } else { // not enough room: pin to both docks and let the content shrink
        root.style.marginLeft = L ? L + "px" : "";
        root.style.marginRight = R ? R + "px" : "";
      }
    }
    window.addEventListener("resize", apply);
    return {
      set: function (side, px, contentRoot) {
        if (contentRoot && (contentRoot !== document.body || !root)) {
          if (root && root !== contentRoot) { root.style.marginLeft = ""; root.style.marginRight = ""; }
          root = contentRoot;
        }
        slots[side] = px || 0; apply();
      },
    };
  })();

  /* ---------- small utils ---------- */
  const $ = (sel, root) => (root || document).querySelector(sel);
  const el = (tag, cls, html) => {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  };
  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const hash = (s) => { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) >>> 0; return h.toString(36); };
  const uid = () => "t" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
  const now = () => new Date().toISOString();
  // Timestamps are stored as UTC ISO ("...Z") and always DISPLAYED in the reader's own
  // timezone — toLocale* resolves the system zone, so nothing here is hard-coded.
  // parseISO exists because bare strings are the trap: JS reads a date-only "2026-08-30"
  // as UTC midnight (renders a day early west of Greenwich) and a zone-less
  // "2026-08-30T09:00" as local. Both are treated as local wall time here, so an entry
  // hand-written into the JSON without a "Z" still lands on the day it says.
  const parseISO = (iso) => {
    if (!iso) return null;
    const m = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,3})\d*)?)?)?$/.exec(String(iso).trim());
    if (m) return new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0), +(m[6] || 0), +((m[7] || "0") + "00").slice(0, 3));
    const d = new Date(iso);
    return isNaN(d.getTime()) ? null : d;
  };
  // toLocaleString builds a new formatter on every call, and a render formats every message twice,
  // so the formatters are built once and reused. Same output, a tenth of a second less per render.
  const DTF = {};
  const dtf = (key, o) => DTF[key] || (DTF[key] = new Intl.DateTimeFormat([], o));
  const fmt = (iso) => { const d = parseISO(iso); if (!d) return ""; const o = { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }; const other = d.getFullYear() !== new Date().getFullYear(); if (other) o.year = "numeric"; return dtf(other ? "short-y" : "short", o).format(d); };
  // Hover text: the same instant spelled out in full, with the zone name, so a reader can
  // tell at a glance which timezone the short label above is in.
  const fmtFull = (iso) => { const d = parseISO(iso); if (!d) return String(iso || ""); try { return dtf("full", { dateStyle: "full", timeStyle: "long" }).format(d); } catch (e) { return d.toString(); } };
  // Identity chip for a message's optional agent note ({ session, host } — which AI wrote it,
  // from which machine). Shows "host · short-session"; the full ids live in the hover title.
  // Human authors are free text (the reader's own name), so "not AI" can't be inferred
  // from the name — key off the reserved author "AI" or the presence of an agent note.
  const isAI = (m) => !!m && (m.author === "AI" || !!(m.agent && (m.agent.session || m.agent.host)));
  const agentTag = (m) => {
    const a = m && m.agent; if (!a || (!a.session && !a.host)) return "";
    const sess = String(a.session || "");
    const short = sess.replace(/^session[_-]?/, "").slice(0, 8);
    const label = [a.host, short].filter(Boolean).join(" · ");
    const full = [sess && "session " + sess, a.host && "host " + a.host].filter(Boolean).join(" · ");
    return '<span class="cmt-msg-agent" title="' + esc(full) + '">' + esc(label) + "</span>";
  };

  /* ---------- config ---------- */
  const docId = (document.documentElement.getAttribute("data-comment-doc")
    || (location.pathname.split("/").pop() || "document").replace(/\.[^.]*$/, "")
    || "document");
  const ENDPOINT = "./__comments__/" + encodeURIComponent(docId);
  const LSKEY = "commentable-html::" + docId;
  const PKEY = "cmt-panel-hidden:" + docId, PWKEY = "cmt-panel-w:" + docId;

  /* ---------- identity: who is commenting ---------- */
  // Resolved once at init, in priority order:
  //   1. the access gate — GET ./__whoami__ returns the name the reader typed at the
  //      sign-in prompt (served by the gated app.py from `publish-commentable-html`;
  //      absent on plain serve.py, which has no gate);
  //   2. a name remembered in this browser from a previous visit;
  //   3. nothing yet — the compose box grows a "Your name" field, asked once.
  // Whatever it resolves to is written into every message's `author`, so a doc several
  // people read shows who said what instead of a wall of identical "Human".
  const WHOAMI = "./__whoami__";
  const NAMEKEY = "commentable-html::name";
  let ME = "";           // "" until known
  let MEFIXED = false;   // true when the gate supplied it — then it isn't editable here

  async function resolveIdentity() {
    if (location.protocol.startsWith("http")) {
      try {
        const r = await fetch(WHOAMI, { cache: "no-store" });
        if (r.ok) {
          const d = await r.json();
          if (d && d.name) { MEFIXED = true; return String(d.name).trim().slice(0, 40); }
        }
      } catch (e) {}
    }
    return (localStorage.getItem(NAMEKEY) || "").trim().slice(0, 40);
  }
  function setMe(name) {
    name = String(name || "").trim().slice(0, 40);
    if (!name || name === ME) return;
    ME = name;
    if (!MEFIXED) { try { localStorage.setItem(NAMEKEY, ME); } catch (e) {} }
    renderWho();
  }
  // Author for anything written right now. Adopts whatever was typed into the open
  // popover's "Your name" field, so there is no separate save-your-name step.
  function me() {
    const inp = ui.pop && ui.pop.querySelector(".cmt-who");
    if (inp && inp.value.trim()) setMe(inp.value);
    return ME || "Human";
  }
  // The "Your name" field — rendered only while we still don't know who this is.
  function whoField() {
    return ME ? "" : '<input class="cmt-who" placeholder="Your name" autocomplete="name" maxlength="40">';
  }
  function wireWho(p) {
    const w = p.querySelector(".cmt-who");
    if (!w) return;
    const ta = p.querySelector("textarea");
    w.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); if (ta) ta.focus(); } });
    w.focus();
  }
  // Panel header: which store, and who you are signing as. Click the name to change it
  // (unless the gate set it — then the name is whatever you signed in with).
  function renderWho() {
    const box = ui.drawer && ui.drawer.querySelector(".cmt-backend");
    if (!box) return;
    box.innerHTML = "store: <b>" + backend + "</b>" +
      (ME ? ' · you: <b class="cmt-me' + (MEFIXED ? " cmt-me-fixed" : "") + '">' + esc(ME) + "</b>" : "");
    const chip = box.querySelector(".cmt-me");
    if (!chip) return;
    if (MEFIXED) { chip.title = "From the access gate — the name you signed in with"; return; }
    chip.title = "Click to change the name your comments are signed with";
    chip.addEventListener("click", () => {
      const inp = el("input", "cmt-who cmt-who-inline");
      inp.value = ME; inp.maxLength = 40;
      chip.replaceWith(inp); inp.focus(); inp.select();
      let done = false;
      const commit = () => { if (done) return; done = true; setMe(inp.value || ME); renderWho(); };
      inp.addEventListener("keydown", (e) => { if (e.key === "Enter") commit(); if (e.key === "Escape") { done = true; renderWho(); } });
      inp.addEventListener("blur", commit);
    });
  }

  let panelW = Math.min(560, Math.max(260, parseInt(localStorage.getItem(PWKEY), 10) || 340));
  let panelPref = "1"; // resolved at init: stored choice, else open iff the doc has comments
  let contentRoot; // set on init

  /* ---------- state ---------- */
  let state = { docId: docId, version: 1, threads: [] };
  let backend = "local"; // "server" | "local"
  let lastServerSnapshot = "";
  const injected = []; // highlight spans we created, to unwrap before re-render
  let mo = null; // MutationObserver — disconnected while we mutate the DOM ourselves
  const MO_OPTS = { childList: true, subtree: true, characterData: true };

  /* ---------- anchoring ---------- */
  function cssPath(node) {
    if (!node || node === contentRoot) return "";
    const parts = [];
    let n = node;
    while (n && n.nodeType === 1 && n !== contentRoot && n !== document.body) {
      if (n.id) { parts.unshift("#" + CSS.escape(n.id)); break; }
      let sel = n.tagName.toLowerCase();
      const p = n.parentElement;
      if (p) {
        const same = Array.prototype.filter.call(p.children, (c) => c.tagName === n.tagName);
        if (same.length > 1) sel += ":nth-of-type(" + (same.indexOf(n) + 1) + ")";
      }
      parts.unshift(sel);
      n = n.parentElement;
    }
    return parts.join(" > ");
  }

  function ensureAnchorId(node) {
    if (node.id) return node.id;
    let a = node.getAttribute("data-cmt-anchor");
    if (a) return a;
    // deterministic: same path + text -> same id, so a regenerated page re-matches.
    a = "cmt-" + hash(cssPath(node) + "|" + norm(node.textContent).slice(0, 80));
    node.setAttribute("data-cmt-anchor", a);
    return a;
  }

  // Human-readable description of the target — this is what gives the AI context.
  function labelFor(node, exact) {
    const cell = node.closest && node.closest("td, th");
    if (cell) {
      const tr = cell.closest("tr");
      const table = cell.closest("table");
      const colIdx = tr ? Array.prototype.indexOf.call(tr.children, cell) : -1;
      let col = "";
      if (table && colIdx >= 0) {
        const headRow = table.querySelector("thead tr") || table.querySelector("tr");
        if (headRow && headRow.children[colIdx]) col = norm(headRow.children[colIdx].textContent);
      }
      const rowName = tr && tr.children[0] ? norm(tr.children[0].textContent).slice(0, 40) : "";
      const bits = [rowName, col].filter(Boolean);
      if (bits.length) return bits.join(" · ");
    }
    const heading = (() => {
      let h = node.closest && node.closest("h1,h2,h3,h4,h5,h6,section,article,li,tr");
      if (h && /^H[1-6]$/.test(h.tagName)) return norm(h.textContent).slice(0, 40);
      let prev = node;
      for (let i = 0; i < 6 && prev; i++) { prev = prev.previousElementSibling; if (prev && /^H[1-6]$/.test(prev.tagName)) return norm(prev.textContent).slice(0, 40); }
      return "";
    })();
    const snippet = norm(exact || node.textContent).slice(0, 48);
    return [heading, node.tagName.toLowerCase() + (snippet ? " “" + snippet + "”" : "")].filter(Boolean).join(" · ");
  }

  function docText() { return contentRoot.innerText || contentRoot.textContent || ""; }

  function quoteFor(exact) {
    const text = docText();
    const i = text.indexOf(exact);
    if (i < 0) return { exact: exact, prefix: "", suffix: "" };
    return { exact: exact, prefix: text.slice(Math.max(0, i - 32), i), suffix: text.slice(i + exact.length, i + exact.length + 32) };
  }

  // The words on either side of a pick, read around the pick itself. quoteFor() takes them from
  // the first copy of the words anywhere in the page, which is the wrong copy when a short phrase
  // repeats, and the prefix and suffix exist to tell those copies apart (locateRange).
  function contextOf(range) {
    try {
      const pre = document.createRange(); pre.selectNodeContents(contentRoot); pre.setEnd(range.startContainer, range.startOffset);
      const suf = document.createRange(); suf.selectNodeContents(contentRoot); suf.setStart(range.endContainer, range.endOffset);
      return { prefix: norm(pre.toString()).slice(-32), suffix: norm(suf.toString()).slice(0, 32) };
    } catch (e) { return null; }
  }

  function buildAnchor(target, range) {
    if (range && !range.collapsed) {
      const container = range.commonAncestorContainer;
      const elNode = container.nodeType === 1 ? container : container.parentElement;
      const exact = norm(range.toString());
      const quote = Object.assign({ exact: exact }, contextOf(range) || quoteFor(exact));
      return { type: "range", elementId: ensureAnchorId(elNode), cssPath: cssPath(elNode), quote: quote, label: labelFor(elNode, exact) };
    }
    const node = target.nodeType === 1 ? target : target.parentElement;
    const exact = norm(node.textContent).slice(0, 120);
    return { type: "element", elementId: ensureAnchorId(node), cssPath: cssPath(node), quote: quoteFor(exact), label: labelFor(node, exact) };
  }

  function findElement(anchor) {
    let node = null;
    if (anchor.elementId) {
      node = document.getElementById(anchor.elementId) || $('[data-cmt-anchor="' + CSS.escape(anchor.elementId) + '"]', contentRoot);
    }
    if (!node && anchor.cssPath) { try { node = contentRoot.querySelector(anchor.cssPath); } catch (e) {} }
    return node && contentRoot.contains(node) ? node : null;
  }

  // Where in `hay` the quoted words sit when they occur more than once: the copy whose neighbours
  // match the stored prefix and suffix over the most characters, counted outward from the words.
  // With one copy, or no context stored, that is the first copy.
  function pickOccurrence(hay, want, quote) {
    const first = hay.indexOf(want);
    if (first < 0) return -1;
    const pre = norm(quote && quote.prefix), suf = norm(quote && quote.suffix);
    if ((!pre && !suf) || hay.indexOf(want, first + 1) < 0) return first;
    let best = first, bestScore = -1;
    for (let i = first; i >= 0; i = hay.indexOf(want, i + 1)) {
      const before = hay.slice(Math.max(0, i - pre.length - 2), i).trimEnd();
      const after = hay.slice(i + want.length, i + want.length + suf.length + 2).trimStart();
      let s = 0, k = 0;
      while (s < pre.length && s < before.length && pre[pre.length - 1 - s] === before[before.length - 1 - s]) s++;
      while (k < suf.length && k < after.length && suf[k] === after[k]) k++;
      if (s + k > bestScore) { bestScore = s + k; best = i; }
    }
    return best;
  }

  // Locate a quote's text range inside an element (for range highlighting).
  // One pass: build a normalized string identical to norm() semantics (collapse runs,
  // trim ends) plus a parallel map from each normalized char -> [textNode, offset].
  function locateRange(node, exact, quote) {
    if (!node || !exact) return null;
    const want = norm(exact);
    if (!want) return null;
    const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null);
    let t, normStr = "", map = [], prevWs = true; // prevWs=true drops leading whitespace
    while ((t = walker.nextNode())) {
      const v = t.nodeValue;
      for (let i = 0; i < v.length; i++) {
        if (/\s/.test(v[i])) { if (prevWs) continue; normStr += " "; map.push([t, i]); prevWs = true; }
        else { normStr += v[i]; map.push([t, i]); prevWs = false; }
      }
    }
    while (normStr.endsWith(" ")) { normStr = normStr.slice(0, -1); map.pop(); } // trim trailing
    const idx = pickOccurrence(normStr, want, quote);
    if (idx < 0 || !map[idx] || !map[idx + want.length - 1]) return null;
    try {
      const r = document.createRange();
      r.setStart(map[idx][0], map[idx][1]);
      const end = map[idx + want.length - 1];
      r.setEnd(end[0], end[1] + 1);
      return r;
    } catch (e) { return null; }
  }

  // Sørensen–Dice similarity on character bigrams (0..1). Lightweight, no deps.
  // A "side" is one string prepared once: lowercased normalized text, its bigram count, and its
  // bigram Map, built on first need. Matching one quote against thousands of blocks used to
  // rebuild the quote's Map for every block, which was a third of a render on a long page.
  function sideOf(s) { const low = norm(s).toLowerCase(); return { low: low, n: Math.max(0, low.length - 1), grams: null }; }
  function gramsOf(s) { const m = new Map(); for (let i = 0; i < s.length - 1; i++) { const g = s.substr(i, 2); m.set(g, (m.get(g) || 0) + 1); } return m; }
  // The highest dice() the two sides could reach: every bigram of the shorter one matched.
  // Comparing it first skips the count wherever even that could not clear the bar.
  function diceBound(a, b) {
    if (!a.low || !b.low) return 0;
    if (a.low === b.low) return 1;
    if (a.low.length < 2 || b.low.length < 2) return 0;
    return (2 * Math.min(a.n, b.n)) / (a.n + b.n);
  }
  function diceSides(a, b) {
    if (!a.low || !b.low) return 0;
    if (a.low === b.low) return 1;
    if (a.low.length < 2 || b.low.length < 2) return 0;
    if (!a.grams) a.grams = gramsOf(a.low);
    if (!b.grams) b.grams = gramsOf(b.low);
    const small = a.grams.size <= b.grams.size ? a.grams : b.grams, big = small === a.grams ? b.grams : a.grams;
    let inter = 0;
    small.forEach((c, g) => { const d = big.get(g); if (d) inter += Math.min(c, d); });
    return (2 * inter) / (a.n + b.n);
  }
  function dice(a, b) { return diceSides(sideOf(a), sideOf(b)); }
  const SIM_THRESHOLD = 0.62;

  /* Caches that live as long as the content's DOM does. `gen` goes up on every change the
     MutationObserver reports (and on any it has queued but not yet delivered, see syncGen), so a
     text, a candidate list or a resolved anchor is reused across renders until the page changes.
     A render used to recompute all of them, about 4 s on a 16,800-element page with 112 threads. */
  let gen = 0, cacheGen = -1, _normCache = new Map(), _sides = new Map(), _found = new Map(), _blocks = null;
  function caches() {
    if (cacheGen !== gen) { cacheGen = gen; _normCache = new Map(); _sides = new Map(); _found = new Map(); _blocks = null; }
  }
  function normText(node) { caches(); let v = _normCache.get(node); if (v === undefined) { v = norm(node.textContent); _normCache.set(node, v); } return v; }
  function nodeSide(node) { caches(); let s = _sides.get(node); if (!s) { s = sideOf(normText(node)); _sides.set(node, s); } return s; }
  function prevText(node, n) { let s = "", e = node.previousElementSibling, g = 0; while (e && s.length < n && g++ < 8) { s = normText(e) + " " + s; e = e.previousElementSibling; } return s.slice(-n); }
  function nextText(node, n) { let s = "", e = node.nextElementSibling, g = 0; while (e && s.length < n && g++ < 8) { s += " " + normText(e); e = e.nextElementSibling; } return s.slice(0, n); }

  // Does this element's text still contain (or closely resemble) the stored quote?
  function textMatches(node, anchor) {
    if (!anchor.quote || !anchor.quote.exact) return true;
    const want = norm(anchor.quote.exact);
    const have = normText(node);
    if (have.indexOf(want) >= 0) return true;
    const w = sideOf(want), h = nodeSide(node);
    return diceBound(w, h) >= SIM_THRESHOLD && diceSides(w, h) >= SIM_THRESHOLD;
  }

  const QUOTE_BLOCKS = "p,li,td,th,h1,h2,h3,h4,h5,h6,blockquote,figcaption,span,div,a,code,pre,dt,dd,caption,summary";
  const BLOCK_TAGS = new Set(QUOTE_BLOCKS.split(","));

  // Every content element in document order, and the subset a fuzzy match may land on, skipping
  // the layers' own UI and this layer's highlight spans. Built once per DOM generation; each
  // thread's search used to run two querySelectorAll calls and a closest() per element.
  // end[i] is the index just past element i's descendants, so a search can skip a whole subtree.
  function candidates() {
    caches();
    if (_blocks) return _blocks;
    const all = [], blocks = [];
    const w = document.createTreeWalker(contentRoot, NodeFilter.SHOW_ELEMENT, { acceptNode: (n) =>
      n.matches(".cmt-ui, .pr-ui") ? NodeFilter.FILTER_REJECT : n.classList.contains("cmt-highlight") ? NodeFilter.FILTER_SKIP : NodeFilter.FILTER_ACCEPT });
    for (let n = w.nextNode(); n; n = w.nextNode()) { all.push(n); if (BLOCK_TAGS.has(n.localName)) blocks.push(n); }
    const end = new Array(all.length), open = [];
    for (let i = 0; i < all.length; i++) {
      while (open.length && !all[open[open.length - 1]].contains(all[i])) end[open.pop()] = i;
      open.push(i);
    }
    while (open.length) end[open.pop()] = all.length;
    return (_blocks = { all: all, end: end, blocks: blocks });
  }

  // Find the element that best carries the quote. Returns {node, score} or null.
  function fuzzyFind(quote) {
    const exact = typeof quote === "string" ? quote : (quote && quote.exact);
    const pre = (quote && quote.prefix) || "", suf = (quote && quote.suffix) || "";
    const want = norm(exact);
    if (!want) return null;
    const C = candidates();
    // 1) exact containment. An element's text holds all of its descendants' text, so an element
    //    without the words rules out its whole subtree, and the page's own text rules out the
    //    whole page for words that were deleted. The search walks only down toward the words.
    const contains = [];
    if (normText(contentRoot).indexOf(want) >= 0) {
      for (let i = 0; i < C.all.length; ) {
        const t = normText(C.all[i]);
        if (t.length >= want.length && t.indexOf(want) >= 0) { contains.push(C.all[i]); i++; } else i = C.end[i];
      }
    }
    if (contains.length) {
      // most specific candidates: those not containing another candidate. In document order a
      // candidate's descendants come right after it, so only its successor needs checking.
      const leaves = contains.filter((n, i) => !(i + 1 < contains.length && n.contains(contains[i + 1])));
      leaves.sort((a, b) => normText(a).length - normText(b).length); // stable: ties stay in page order
      const pool = leaves;
      // disambiguate repeats (e.g. identical table cells) via stored prefix/suffix context
      if ((pre || suf) && pool.length > 1) {
        const target = sideOf(pre + " " + want + " " + suf);
        let best = pool[0], bestScore = -1;
        pool.forEach((n) => {
          const s = diceSides(target, sideOf(prevText(n, 32) + " " + normText(n) + " " + nextText(n, 32)));
          if (s > bestScore) { bestScore = s; best = n; }
        });
        return { node: best, score: 1 };
      }
      return { node: pool[0], score: 1 };
    }
    // 2) approximate — best block within similarity threshold (handles light text edits).
    //    A block whose length alone caps its score at the best so far cannot win, so its
    //    bigrams are never counted: that drops nearly every span of typeset math.
    const w = sideOf(want);
    let best = null, bestScore = SIM_THRESHOLD;
    C.blocks.forEach((n) => {
      const txt = normText(n);
      if (!txt || txt.length > want.length * 3.5) return; // skip oversized blocks
      const b = nodeSide(n);
      if (diceBound(w, b) <= bestScore) return;
      const s = diceSides(w, b);
      if (s > bestScore) { bestScore = s; best = n; }
    });
    return best ? { node: best, score: bestScore } : null;
  }

  // Pending mutations the observer has not delivered yet: a caller that reads the page in the
  // same task as a change (a script, a test, present mode) must not get the old answer.
  function syncGen(redraw) {
    if (!mo) return;
    if (mo.takeRecords().length) { gen++; if (redraw) scheduleRender(); }
  }

  // Resolved anchors, reused while the DOM stays the same. Only with the highlight API: the
  // span fallback rewrites text nodes on every render, which would leave cached ranges stale.
  function resolveAnchor(anchor) {
    if (!anchor) return { status: "orphan" };
    if (!HL) return resolveFresh(anchor);
    caches();
    const key = JSON.stringify(anchor);
    const hit = _found.get(key);
    if (hit && (!hit.node || hit.node.isConnected)) return hit;
    const res = resolveFresh(anchor);
    _found.set(key, res);
    return res;
  }

  // Robustness-ordered resolution: structural hint (validated against quote) -> fuzzy quote.
  function resolveFresh(anchor) {
    let node = findElement(anchor);
    let approx = false;
    if (node && !textMatches(node, anchor)) node = null; // resolution success != correctness
    if (!node && anchor.quote && anchor.quote.exact) { const f = fuzzyFind(anchor.quote); if (f) { node = f.node; approx = f.score < 1; } }
    if (!node) return { status: "orphan" };
    let range = null;
    if (anchor.type === "range" && anchor.quote) range = locateRange(node, anchor.quote.exact, anchor.quote);
    return { status: approx ? "approx" : "anchored", node: node, range: range };
  }

  /* ---------- persistence ---------- */
  async function detectBackend() {
    if (location.protocol.startsWith("http")) {
      try { const r = await fetch(ENDPOINT, { cache: "no-store" }); if (r.ok) return "server"; } catch (e) {}
    }
    return "local";
  }
  async function load() {
    if (backend === "server") {
      try {
        const r = await fetch(ENDPOINT, { cache: "no-store" });
        const txt = await r.text(); lastServerSnapshot = txt;
        const d = JSON.parse(txt || "{}");
        state = normalizeState(d); return;
      } catch (e) { /* fall through */ }
    }
    try { state = normalizeState(JSON.parse(localStorage.getItem(LSKEY) || "{}")); } catch (e) { state = normalizeState({}); }
  }
  function normalizeState(d) {
    const threads = (d && Array.isArray(d.threads) ? d.threads : []).filter((t) => t && t.anchor && Array.isArray(t.messages));
    return { docId: docId, version: 1, threads: threads };
  }
  // Merge: keep the LOCAL thread set (so deletes stick) but union each thread's messages
  // with the disk copy, so an AI reply written while a thread was open isn't clobbered.
  // Key excludes text so an in-place edit supersedes the disk copy instead of duplicating it.
  const msgKey = (m) => m.author + "|" + m.at;
  function mergeForSave(local, remote) {
    const remoteById = new Map((remote || []).map((t) => [t.id, t]));
    return (local || []).map((t) => {
      const rt = remoteById.get(t.id);
      if (!rt || !Array.isArray(rt.messages)) return t;
      const seen = new Set(t.messages.map(msgKey));
      const msgs = t.messages.slice();
      rt.messages.forEach((m) => { if (!seen.has(msgKey(m))) { seen.add(msgKey(m)); msgs.push(m); } });
      msgs.sort((x, y) => String(x.at).localeCompare(String(y.at)));
      // In place: saves now run behind the page, and a thread card opened meanwhile holds this
      // object, so a reply typed into it must land in state, not in a copy the merge replaced.
      t.messages = msgs;
      return t;
    });
  }
  async function save() {
    if (backend === "server") {
      try {
        let remote = { threads: [] };
        try { const r = await fetch(ENDPOINT, { cache: "no-store" }); remote = normalizeState(await r.json()); } catch (e) {}
        state = { docId: docId, version: 1, threads: mergeForSave(state.threads, remote.threads) };
        const txt = JSON.stringify(state, null, 2);
        await fetch(ENDPOINT, { method: "PUT", headers: { "Content-Type": "application/json" }, body: txt });
        lastServerSnapshot = txt;
        return;
      } catch (e) {}
    }
    try { localStorage.setItem(LSKEY, JSON.stringify(state, null, 2)); } catch (e) {}
  }
  // server poll so AI replies written to disk appear live
  // A save goes out over the network, so the page redraws first and saves behind the redraw;
  // posting used to hold the comment box open for the whole round trip. Saves run one at a time
  // and in order, so an older body never lands after a newer one. The poll stands down while one
  // is out, because adopting the disk copy then would drop the change still on its way. When the
  // merge brings in a reply written meanwhile, the page redraws again once no popover is open.
  let saving = Promise.resolve(), savesOut = 0, redrawLater = false;
  function saveSoon() {
    savesOut++;
    saving = saving.then(async () => {
      const before = JSON.stringify(state.threads);
      try { await save(); } finally { savesOut--; }
      if (JSON.stringify(state.threads) === before) return;
      if (ui.pop) redrawLater = true; else renderAll();
    }).catch(() => {});
    return saving;
  }

  async function poll() {
    if (backend !== "server" || ui.pop || savesOut) return;
    try {
      const r = await fetch(ENDPOINT, { cache: "no-store" });
      const txt = await r.text();
      if (ui.pop || savesOut) return; // a box opened or a save began while the copy was on its way
      if (txt && txt !== lastServerSnapshot) { const d = JSON.parse(txt); lastServerSnapshot = txt; state = normalizeState(d); renderAll(); }
    } catch (e) {}
  }

  /* ---------- UI scaffold ---------- */
  const ui = { chip: null, badge: null, markers: null, drawer: null, list: null, pop: null };

  function buildUI() {
    const root = el("div", "cmt-ui");

    // One floating control. It opens the panel; comment mode is the C key and the switch inside
    // the panel, and the chip just goes accent to say the mode is on.
    ui.chip = el("button", "cmt-chip", '<span class="cmt-chip-caret">\u00ab</span>Comments <span class="cmt-chip-n" data-zero="1">0</span>');
    ui.badge = ui.chip.querySelector(".cmt-chip-n");
    ui.chip.title = "Show the comments panel.  Press C for comment mode.";
    ui.chip.addEventListener("click", toggleDrawer);

    ui.markers = el("div", "cmt-marker-layer");

    ui.drawer = el("div", "cmt-drawer");
    ui.drawer.innerHTML =
      '<div class="cmt-grip" title="Drag to resize"></div>' +
      '<div class="cmt-drawer-head"><h2>Comments</h2><div class="cmt-row" style="margin:0">' +
      '<span class="cmt-backend"></span><button class="cmt-btn cmt-ghost cmt-drawer-close" title="Hide comments panel">»</button></div></div>' +
      '<div class="cmt-modebar"><button class="cmt-switch" role="switch" aria-checked="false" ' +
      'title="Click elements to comment on them"><span class="cmt-switch-track">' +
      '<span class="cmt-switch-knob"></span></span><span class="cmt-switch-label">Comment mode</span>' +
      '<kbd class="cmt-kbd">C</kbd></button></div>' +
      '<div class="cmt-drawer-list"></div>';
    ui.list = ui.drawer.querySelector(".cmt-drawer-list");
    ui.drawer.querySelector(".cmt-drawer-close").addEventListener("click", toggleDrawer);
    ui.drawer.querySelector(".cmt-switch").addEventListener("click", toggleMode);
    renderWho();

    // drag the panel's left edge to resize; width persists per doc
    const grip = ui.drawer.querySelector(".cmt-grip");
    grip.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      try { grip.setPointerCapture(e.pointerId); } catch (err) {}
      const sx = e.clientX, sw = panelW;
      ui.drawer.classList.add("cmt-resizing");
      const mv = (ev) => { panelW = Math.min(560, Math.max(260, sw + (sx - ev.clientX))); panelSync(); };
      const up = () => {
        ui.drawer.classList.remove("cmt-resizing");
        localStorage.setItem(PWKEY, panelW);
        grip.removeEventListener("pointermove", mv); grip.removeEventListener("pointerup", up);
        scheduleRender(); // pins track the reflowed content
      };
      grip.addEventListener("pointermove", mv);
      grip.addEventListener("pointerup", up);
    });

    root.append(ui.chip, ui.markers, ui.drawer);
    document.body.appendChild(root);
  }

  function toggleMode() {
    document.body.classList.toggle("cmt-mode");
    syncMode();
    clearHover();
  }
  // The chip's colour comes from body.cmt-mode in CSS; the switch needs its state set by hand.
  function syncMode() {
    const on = document.body.classList.contains("cmt-mode");
    const sw = ui.drawer && ui.drawer.querySelector(".cmt-switch");
    if (sw) sw.setAttribute("aria-checked", on ? "true" : "false");
  }

  /* ---------- right comments panel: docked ≥1360px, overlay below ---------- */
  const pmq = window.matchMedia("(min-width: 1360px)");
  function panelSync() {
    // Present mode (present-layer.js) owns the right dock while it runs, and calls relayout() on exit.
    if (document.body.classList.contains("pr-on")) return;
    document.body.style.setProperty("--cmt-panel-w", panelW + "px");
    window.__dockLayout.set("right", document.body.classList.contains("cmt-docked") ? panelW : 0, contentRoot);
  }
  function panelApply() {
    if (pmq.matches && panelPref !== "1") document.body.classList.add("cmt-docked");
    else document.body.classList.remove("cmt-docked");
    panelSync();
    if (ui.markers) scheduleRender(); // pins track the reflowed content
  }
  function toggleDrawer() {
    if (pmq.matches) {
      panelPref = document.body.classList.contains("cmt-docked") ? "1" : "0";
      localStorage.setItem(PKEY, panelPref);
      panelApply();
    } else {
      ui.drawer.classList.toggle("cmt-open");
    }
  }

  /* ---------- hover highlight in comment mode ---------- */
  // Painted words have no element of their own to outline, so pointing at them deepens their
  // paint instead, and the block around them stays unoutlined: a click there opens their thread.
  let hovered = null, hoverMark = null;
  function clearMarkHover() {
    if (!hoverMark) return;
    hoverMark = null; paint("cmt-range-hover", null); document.body.classList.remove("cmt-over-mark");
  }
  function clearHover() { if (hovered) { hovered.classList.remove("cmt-hover"); hovered = null; } clearMarkHover(); }
  function onMove(e) {
    if (!document.body.classList.contains("cmt-mode")) return;
    let t = e.target;
    if (!contentRoot.contains(t) || (t.closest && t.closest(".cmt-ui"))) { clearHover(); return; }
    const m = marks.length ? markAt(e.clientX, e.clientY) : null;
    if (m) {
      if (hovered) { hovered.classList.remove("cmt-hover"); hovered = null; }
      if (hoverMark !== m) { hoverMark = m; paint("cmt-range-hover", [m.range]); document.body.classList.add("cmt-over-mark"); }
      return;
    }
    clearMarkHover();
    if (t === hovered) return;
    clearHover(); hovered = t; t.classList.add("cmt-hover");
  }

  // Words dragged over inside the content, or null. A pick that reaches outside the content root
  // (into a sidebar or the panel) is not a pick of the document's words.
  function pickedRange() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    const r = sel.getRangeAt(0);
    const c = r.commonAncestorContainer, n = c.nodeType === 1 ? c : c.parentElement;
    if (!n || !contentRoot.contains(n) || n.closest(".cmt-ui, .pr-ui") || !norm(r.toString())) return null;
    return r.cloneRange();
  }

  /* ---------- create / open threads ---------- */
  function onClick(e) {
    const t = e.target;
    // A click outside an open popover dismisses it (any mode); the draft is stashed by
    // closePop and restored when the same target is reopened. The dismissing click is
    // swallowed unless it lands on comment UI that should keep working (pins, drawer, FAB).
    if (ui.pop && !ui.pop.contains(t)) {
      const passThrough = t.closest && t.closest(".cmt-pin, [data-cmt-thread], .cmt-drawer, .cmt-chip");
      if (!passThrough) {
        closePop();
        e.preventDefault(); e.stopPropagation();
        return;
      }
    }
    if (!document.body.classList.contains("cmt-mode")) return;
    if (t.closest && t.closest(".cmt-ui")) return; // UI clicks pass through
    // Words dragged over come first. The click that ends the drag lands on the block holding them,
    // and when that block already carried a thread, the click used to open that thread and drop
    // the pick. A drag across two blocks lands on the content root, which used to drop it too.
    const range = pickedRange();
    if (range) {
      e.preventDefault(); e.stopPropagation();
      window.getSelection().removeAllRanges();
      composeNew(buildAnchor(null, range), range);
      return;
    }
    // open an existing thread: painted words under the pointer, then an element (or, without the
    // highlight API, a highlight span) that carries one
    const m = markAt(e.clientX, e.clientY);
    if (m) { e.preventDefault(); e.stopPropagation(); openThread(m.id); return; }
    const owner = t.closest && t.closest("[data-cmt-thread]");
    if (owner) { e.preventDefault(); e.stopPropagation(); openThread(owner.getAttribute("data-cmt-thread"), owner); return; }
    if (!contentRoot.contains(t) || t === contentRoot) return;
    e.preventDefault(); e.stopPropagation();
    composeNew(buildAnchor(t, null), null);
  }

  // Unsent popover text, keyed by target — survives dismissals (outside click, Escape,
  // re-renders). Cleared on submit or explicit Cancel. Only the reply / compose box in the footer
  // is a draft: the ✎ editor's textarea sits above it, and a bare "textarea" picked the editor,
  // so every saved edit came back as a copy of itself in the reply box.
  const drafts = new Map();
  function closePop() {
    if (!ui.pop) return;
    const key = ui.pop._draftKey, ta = ui.pop.querySelector(".cmt-pop-foot > textarea");
    if (key && ta) { if (ta.value.trim()) drafts.set(key, ta.value); else drafts.delete(key); }
    ui.pop.remove(); ui.pop = null;
    paint("cmt-range-draft", null);
    if (redrawLater) { redrawLater = false; scheduleRender(); } // a save merged in a reply while the box was open
  }

  function placePop(rect) {
    const p = ui.pop; if (!p) return;
    const pw = 320, gap = 10;
    let left = window.scrollX + rect.right + gap;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 8) left = window.scrollX + Math.max(8, rect.left - pw - gap);
    if (left < window.scrollX + 8) left = window.scrollX + 8;
    let top = window.scrollY + rect.top;
    const maxTop = window.scrollY + document.documentElement.clientHeight - p.offsetHeight - 8;
    if (top > maxTop) top = Math.max(window.scrollY + 8, maxTop);
    p.style.left = left + "px"; p.style.top = top + "px";
  }

  function composeNew(anchor, range) {
    closePop();
    const probe = range || (findElement(anchor) && (() => { const r = document.createRange(); r.selectNode(findElement(anchor)); return r; })());
    const rect = probe ? probe.getBoundingClientRect() : { top: 80, left: 80, right: 300 };
    const p = el("div", "cmt-pop");
    p.innerHTML =
      '<div class="cmt-pop-head"><span>New comment on</span><span class="cmt-pop-target">' + esc(anchor.label || "selection") + "</span></div>" +
      '<div class="cmt-pop-foot">' + whoField() + '<textarea placeholder="Your comment… (context is attached)"></textarea>' +
      '<div class="cmt-row"><button class="cmt-btn cmt-ghost cmt-cancel">Cancel</button><button class="cmt-btn cmt-primary cmt-save">Comment</button></div></div>';
    const draftKey = "new|" + (anchor.elementId || "") + "|" + ((anchor.quote && anchor.quote.exact) || "").slice(0, 40);
    p._draftKey = draftKey;
    p._anchorNode = range || findElement(anchor);
    // Removing the selection to focus the box would leave no sign of which words the comment is
    // on, so they stay painted while it is written.
    if (range) paint("cmt-range-draft", [range]);
    ui.pop = p; document.body.appendChild(p); placePop(rect); wireWho(p);
    const ta = p.querySelector("textarea"); ta.value = drafts.get(draftKey) || "";
    if (!p.querySelector(".cmt-who")) ta.focus();   // else wireWho already focused the name field
    p.querySelector(".cmt-cancel").addEventListener("click", () => { ta.value = ""; closePop(); });
    p.querySelector(".cmt-save").addEventListener("click", async () => {
      const text = ta.value.trim(); if (!text) { ta.focus(); return; }
      const author = me();
      const thread = { id: uid(), createdBy: author, createdAt: now(), status: "open", anchor: anchor, messages: [{ author: author, text: text, at: now() }] };
      state.threads.push(thread); drafts.delete(draftKey); ta.value = "";
      closePop(); renderAll(); saveSoon(); // pin and paint appear at once; no popover re-open after submit
    });
    ta.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) p.querySelector(".cmt-save").click(); if (e.key === "Escape") closePop(); });
  }

  // An anchor inside a closed <details> has no box, so the jump would scroll nowhere and the
  // popover would land in the page corner. Open every fold around it first.
  function openFolds(node) {
    for (let d = node && node.closest ? node.closest("details") : null; d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
  }

  function openThread(id, nearNode) {
    closePop();
    const thread = state.threads.find((t) => t.id === id); if (!thread) return;
    syncGen(true);
    const res = resolveAnchor(thread.anchor);
    if (res.node && res.status !== "orphan") openFolds(res.node);
    // painted words: the card sits beside them, and the jump and the flash land on them, not on their block
    const words = HL && res.range && res.status !== "orphan" ? res.range : null;
    const node = words || ((nearNode && nearNode.closest("[data-cmt-thread]")) ? document.querySelector('[data-cmt-thread="' + id + '"]') : res.node);
    const rect = node ? node.getBoundingClientRect() : (nearNode ? nearNode.getBoundingClientRect() : { top: 80, left: 80, right: 300 });
    const p = el("div", "cmt-pop");
    const msgs = thread.messages.map((m, i) =>
      '<div class="cmt-msg ' + (isAI(m) ? "cmt-ai" : "") + '" data-idx="' + i + '"><div class="cmt-msg-meta"><span class="cmt-msg-author">' +
      esc(m.author) + "</span>" + agentTag(m) + '<span title="' + esc(fmtFull(m.at)) + '">' + fmt(m.at) + (m.editedAt ? " · edited " + fmt(m.editedAt) : "") + "</span>" +
      (isAI(m) ? "" : '<button class="cmt-msg-edit" title="Edit this comment">✎</button>') +
      "</div><div class=\"cmt-msg-text\">" + esc(m.text) + "</div></div>").join("");
    const statusLabel = thread.status === "resolved" ? "Reopen" : "Resolve";
    p.innerHTML =
      '<div class="cmt-pop-head"><span class="cmt-pop-target" title="' + esc(thread.anchor.label) + '">' + esc(thread.anchor.label || "comment") + "</span>" +
      "<span>" + (res.status === "orphan" ? "⚠ orphaned" : res.status === "approx" ? "≈ moved" : "") + "</span></div>" +
      '<div class="cmt-pop-body">' + msgs + "</div>" +
      '<div class="cmt-pop-foot">' + whoField() + '<textarea placeholder="Reply…"></textarea>' +
      '<div class="cmt-row"><button class="cmt-btn cmt-ghost cmt-del">Delete</button><span class="cmt-spacer"></span>' +
      '<button class="cmt-btn cmt-resolve">' + statusLabel + '</button><button class="cmt-btn cmt-primary cmt-reply">Reply</button></div></div>';
    const draftKey = "reply|" + id;
    p._draftKey = draftKey;
    p._anchorNode = node || null;
    ui.pop = p; document.body.appendChild(p); placePop(rect); wireWho(p);
    const ta = p.querySelector("textarea"); ta.value = drafts.get(draftKey) || "";
    p.querySelector(".cmt-reply").addEventListener("click", async () => {
      const text = ta.value.trim(); if (!text) { ta.focus(); return; }
      thread.messages.push({ author: me(), text: text, at: now() }); thread.status = "open";
      drafts.delete(draftKey); ta.value = "";
      renderAll(); openThread(id); saveSoon(); // the pin's count and the panel show the reply at once
    });
    p.querySelector(".cmt-resolve").addEventListener("click", async () => {
      thread.status = thread.status === "resolved" ? "open" : "resolved"; renderAll(); closePop(); saveSoon();
    });
    p.querySelector(".cmt-del").addEventListener("click", async () => {
      drafts.delete(draftKey); ta.value = "";
      state.threads = state.threads.filter((t) => t.id !== id); renderAll(); closePop(); saveSoon();
    });
    // In-place edit of an existing message (human messages only — the ✎ in the meta row).
    p.querySelectorAll(".cmt-msg-edit").forEach((btn) => btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const msgEl = btn.closest(".cmt-msg");
      const m = thread.messages[+msgEl.getAttribute("data-idx")];
      if (!m || msgEl.querySelector(".cmt-msg-editor")) return;
      const editor = el("div", "cmt-msg-editor",
        '<textarea></textarea><div class="cmt-row"><button class="cmt-btn cmt-ghost cmt-edit-cancel">Cancel</button><button class="cmt-btn cmt-primary cmt-edit-save">Save</button></div>');
      msgEl.querySelector(".cmt-msg-text").replaceWith(editor);
      const eta = editor.querySelector("textarea");
      eta.value = m.text; eta.focus(); eta.setSelectionRange(eta.value.length, eta.value.length);
      const done = async (commit) => {
        if (commit) {
          const v = eta.value.trim(); if (!v) { eta.focus(); return; }
          if (v !== m.text) { m.text = v; m.editedAt = now(); saveSoon(); }
        }
        openThread(id); // re-render the thread card
      };
      editor.querySelector(".cmt-edit-cancel").addEventListener("click", (ev) => { ev.stopPropagation(); done(false); });
      editor.querySelector(".cmt-edit-save").addEventListener("click", (ev) => { ev.stopPropagation(); done(true); });
      eta.addEventListener("keydown", (ev) => {
        if (ev.key === "Enter" && (ev.metaKey || ev.ctrlKey)) { ev.stopPropagation(); done(true); }
        if (ev.key === "Escape") { ev.stopPropagation(); done(false); }
      });
    }));
    ta.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) p.querySelector(".cmt-reply").click(); if (e.key === "Escape") closePop(); });
    if (words) {
      scrollToRange(words);
      paint("cmt-range-flash", [words]);
      clearTimeout(flashTimer);
      flashTimer = setTimeout(() => paint("cmt-range-flash", null), 1300);
    } else if (res.node && res.status !== "orphan") {
      res.node.scrollIntoView({ block: "center", behavior: "smooth" });
      res.node.classList.add("cmt-flash");
      setTimeout(() => res.node.classList.remove("cmt-flash"), 1300);
    }
  }
  let flashTimer = 0;

  // Centre a range in its scroller. A Range has no scrollIntoView, and centring the block instead
  // can leave words at the top of a tall paragraph off screen.
  function scrollToRange(range) {
    const r = range.getBoundingClientRect();
    const sp = scrollParent(range.startContainer);
    if (sp) { const c = sp.getBoundingClientRect(); sp.scrollBy({ top: r.top + r.height / 2 - (c.top + c.height / 2), behavior: "smooth" }); }
    else window.scrollBy({ top: r.top + r.height / 2 - window.innerHeight / 2, behavior: "smooth" });
  }

  /* ---------- render ---------- */
  function unwrapInjected() {
    while (injected.length) {
      const s = injected.pop();
      if (s.parentNode) { const parent = s.parentNode; while (s.firstChild) parent.insertBefore(s.firstChild, s); parent.removeChild(s); parent.normalize(); }
    }
    contentRoot.querySelectorAll(".cmt-anchored").forEach((n) => n.classList.remove("cmt-anchored", "cmt-resolved"));
    contentRoot.querySelectorAll("[data-cmt-thread]").forEach((n) => n.removeAttribute("data-cmt-thread"));
  }

  // Only for browsers without the CSS Custom Highlight API (below). surroundContents throws when
  // the range crosses an element boundary, so such a pick falls back to marking its whole block.
  function wrapRange(range, threadId, resolved) {
    try {
      const span = el("span", "cmt-highlight" + (resolved ? " cmt-resolved" : ""));
      span.setAttribute("data-cmt-thread", threadId);
      range.surroundContents(span); injected.push(span); return span;
    } catch (e) { return null; }
  }

  /* ---------- picked words ----------
     A thread on picked words paints exactly those words through the CSS Custom Highlight API,
     the way present mode marks words, and wraps nothing. The span wrap above threw on any pick
     that crossed an element boundary (a citation like [49], a link, emphasis, math), and every
     such thread was drawn on its whole block although its anchor held the right words. Painting
     also leaves the layout, the math and other layers' ranges untouched. */
  const HL = typeof CSS !== "undefined" && !!CSS.highlights && typeof Highlight === "function";
  let marks = []; // this render's painted threads: { id, range, resolved }; resolved ones are not painted
  function paint(name, ranges) {
    if (!HL) return;
    if (ranges && ranges.length) CSS.highlights.set(name, new Highlight(...ranges));
    else CSS.highlights.delete(name);
  }
  // The open thread whose painted words lie under the point. Of several, the smallest wins, so a
  // short pick inside a longer one can still be opened.
  function markAt(x, y) {
    let best = null, bestArea = Infinity;
    marks.forEach((m) => {
      if (m.resolved || !m.range.startContainer.isConnected) return;
      const rs = m.range.getClientRects();
      let hit = false, area = 0;
      for (let i = 0; i < rs.length; i++) {
        const r = rs[i]; area += r.width * r.height;
        if (x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) hit = true;
      }
      if (hit && area < bestArea) { bestArea = area; best = m; }
    });
    return best;
  }
  const isRange = (x) => typeof Range !== "undefined" && x instanceof Range;
  const nodeOf = (x) => (isRange(x) ? x.startContainer : x);
  // The block the words sit in: their pin goes on its left edge, beside the words' first line.
  function blockOf(n) {
    for (let e = n && (n.nodeType === 1 ? n : n.parentElement); e && e !== contentRoot; e = e.parentElement) {
      if (!/^(inline|contents)/.test(getComputedStyle(e).display)) return e;
    }
    return contentRoot;
  }
  // An element's box, or the first line of a range's words (a range's own box spans every line).
  function boxOf(x) {
    if (!isRange(x)) return x.getBoundingClientRect();
    const first = Array.prototype.find.call(x.getClientRects(), (r) => r.width || r.height);
    return first || { top: 0, left: 0, right: 0, bottom: 0, width: 0, height: 0 };
  }

  /* ---------- marker placement ----------
     Pins are absolutely positioned from live rects, so every scroller has to move them. The
     window is not always the scroller: drop this layer on an app shell whose single `<main>`
     scrolls and the markers stay put, ending up hundreds of pixels from the row they belong
     to. `placed` is the last render's pin↔anchor pairing; a capture-phase scroll listener
     (the only kind that hears a nested scroller) replays it, rect by rect. */
  const PIN = 18;
  let placed = [];

  // Nearest ancestor that actually scrolls — used to hide a pin whose anchor has slid under a
  // sticky header or out of its pane. Null on an ordinary document, where the window scrolls
  // and document-coordinate placement is already scroll-invariant.
  function scrollParent(n) {
    for (let e = n && n.parentElement; e && e !== document.body; e = e.parentElement) {
      const c = getComputedStyle(e);
      if (/(auto|scroll|overlay)/.test(c.overflowY + c.overflow) && e.scrollHeight > e.clientHeight) return e;
    }
    return null;
  }

  // A closed <details> hides its content, but Chrome now hides it with content-visibility, which
  // keeps the layout: an anchor inside a closed fold still reports a real rect, so its pin landed
  // in blank space below the page and one doc grew 80,000px of empty scroll. Returns the
  // outermost closed fold between the anchor and the root (its summary is the one on screen),
  // or null. An anchor inside a fold's own summary stays visible.
  function closedFold(node) {
    let top = null;
    for (let d = node.parentElement && node.parentElement.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) {
      if (d.open) continue;
      const s = d.querySelector(":scope > summary");
      if (s && s.contains(node)) continue;
      top = d;
    }
    return top;
  }

  // A closed fold that holds open threads says so on its summary line, so comments in folded
  // detail stay findable without opening every fold.
  function markFolds() {
    contentRoot.querySelectorAll("summary[data-cmt-inside]").forEach((s) => s.removeAttribute("data-cmt-inside"));
    const counts = new Map();
    placed.forEach((x) => {
      const n = x.node && nodeOf(x.node);
      if (x.resolved || !n || !n.isConnected) return;
      const d = closedFold(n);
      if (d) counts.set(d, (counts.get(d) || 0) + 1);
    });
    counts.forEach((n, d) => {
      const s = d.querySelector(":scope > summary");
      if (s) s.setAttribute("data-cmt-inside", n + (n > 1 ? " comments" : " comment"));
    });
  }

  // `target` is an element or the Range of painted words; `edge` is the block whose left edge a
  // range's pin uses, so the pin never covers the words in front of the pick.
  function placePin(pin, target, clip, edge) {
    const node = target && nodeOf(target);
    if (!node || !node.isConnected || closedFold(node)) { pin.style.display = "none"; return; }
    let r = boxOf(target);
    if (!r.width && !r.height) { pin.style.display = "none"; return; }
    if (edge && edge.isConnected) r = { top: r.top, height: r.height, left: Math.min(r.left, edge.getBoundingClientRect().left) };
    const cy = r.top + Math.min(r.height, 22) / 2;
    if (clip) { const c = clip.getBoundingClientRect(); if (cy < c.top + 2 || cy > c.bottom - 2) { pin.style.display = "none"; return; } }
    pin.style.display = "";
    pin.style.top = (window.scrollY + cy - PIN / 2) + "px";
    // The marker rides the anchor's OWN left edge, inside its padding — never the strip to its
    // right. That strip is a margin in a prose document and the NEXT COLUMN in a full-bleed
    // sheet, where `rect.right + 8` parked pins over a table's own cells. Left edge, clamped
    // to the page edge, occludes nothing at any width, on either kind of page.
    pin.style.left = Math.max(window.scrollX + 2, window.scrollX + r.left - PIN + 4) + "px";
  }

  let rafPins = false;
  function schedulePins() {
    if (rafPins) return;
    rafPins = true;
    requestAnimationFrame(() => {
      rafPins = false;
      placed.forEach((x) => placePin(x.pin, x.node, x.clip, x.edge));
      markFolds();
      const an = ui.pop && ui.pop._anchorNode;
      if (an && nodeOf(an).isConnected) placePop(an.getBoundingClientRect());
    });
  }

  function renderAll() {
    redrawLater = false; // this render is the one a finished save asked for
    closePop();
    syncGen(false); // before disconnect(), which drops the observer's undelivered records
    if (mo) mo.disconnect(); // our own wrap/unwrap mutations must not retrigger a render
    try {
    unwrapInjected();
    ui.markers.innerHTML = ""; placed = []; marks = [];
    clearMarkHover(); // its range belongs to the last render
    const open = [], resolved = [], orphans = [], pins = [];
    // Write every mark first and measure after: a class set between two measurements makes the
    // browser recompute style and layout once per thread instead of once per render.
    state.threads.forEach((thread) => {
      if (!thread.messages || !thread.messages.length) return; // degenerate thread — skip
      const res = resolveAnchor(thread.anchor);
      const bucket = res.status === "orphan" ? orphans : thread.status === "resolved" ? resolved : open;
      bucket.push({ thread, res });
      if (res.status === "orphan") return;
      const isResolved = thread.status === "resolved";
      let target = res.node;
      let wrapped = null, words = null;
      if (thread.anchor.type === "range" && res.range) {
        if (HL) { words = res.range; marks.push({ id: thread.id, range: words, resolved: isResolved }); }
        else wrapped = wrapRange(res.range, thread.id, isResolved);
      }
      if (!wrapped && !words && target) {
        target.classList.add("cmt-anchored"); if (isResolved) target.classList.add("cmt-resolved");
        target.setAttribute("data-cmt-thread", thread.id);
      }
      const anchorNode = words || wrapped || target;
      if (anchorNode) pins.push({ thread: thread, anchorNode: anchorNode, words: words, isResolved: isResolved });
    });
    // marker pins, built off the page and added in one go, so placing one never re-lays out the rest
    const frag = document.createDocumentFragment();
    pins.forEach(({ thread, anchorNode, words, isResolved }) => {
      const pin = el("button", "cmt-pin" + (isResolved ? " cmt-resolved" : ""));
      const aiLast = thread.messages[thread.messages.length - 1];
      if (isAI(aiLast) && !isResolved) pin.classList.add("cmt-ai-unread");
      pin.innerHTML = '<span class="cmt-pin-n">' + thread.messages.length + "</span>";
      pin.title = thread.messages.length + (thread.messages.length > 1 ? " messages" : " message") + (aiLast && aiLast.at ? " · " + aiLast.author + (aiLast.agent && aiLast.agent.host ? " @ " + aiLast.agent.host : "") + " · " + fmt(aiLast.at) : "");
      pin.setAttribute("data-cmt-thread", thread.id);
      const clip = scrollParent(nodeOf(anchorNode));
      const edge = words ? blockOf(words.startContainer) : null;
      placePin(pin, anchorNode, clip, edge);
      placed.push({ pin: pin, node: anchorNode, clip: clip, edge: edge, resolved: isResolved });
      pin.addEventListener("click", (e) => { e.stopPropagation(); openThread(thread.id); });
      frag.appendChild(pin);
    });
    ui.markers.appendChild(frag);
    paint("cmt-range", marks.filter((m) => !m.resolved).map((m) => m.range));
    markFolds();
    // badge = open threads (incl. orphans)
    const count = open.length + orphans.length;
    ui.badge.textContent = count; ui.badge.setAttribute("data-zero", count ? "0" : "1");
    renderDrawer(open, resolved, orphans);
    } finally {
      if (mo) mo.observe(contentRoot, MO_OPTS); // always resume, even if a render throws
    }
  }

  // Full thread — anchor label + every message. Clicking jumps to the anchor and opens it.
  function drawerItem({ thread, res }, extraClass) {
    const item = el("div", "cmt-item " + (extraClass || ""));
    const flag = res.status === "orphan" ? '<span class="cmt-item-flag">⚠ orphaned</span>' : res.status === "approx" ? '<span class="cmt-item-flag">≈ moved</span>' : "";
    item.innerHTML =
      '<div class="cmt-item-target">' + esc(thread.anchor.label || "—") + flag + "</div>" +
      thread.messages.map((m) =>
        '<div class="cmt-item-msg' + (isAI(m) ? " cmt-ai" : "") + '"><span class="cmt-item-author">' + esc(m.author) + "</span>" + agentTag(m) +
        '<span class="cmt-item-when" title="' + esc(fmtFull(m.at)) + '">' + fmt(m.at) + (m.editedAt ? " · edited " + fmt(m.editedAt) : "") + "</span>" +
        '<div class="cmt-item-text">' + esc(m.text) + "</div></div>").join("");
    item.addEventListener("click", () => openThread(thread.id));
    return item;
  }

  function renderDrawer(open, resolved, orphans) {
    ui.list.innerHTML = "";
    if (!open.length && !resolved.length && !orphans.length) {
      ui.list.appendChild(el("div", "cmt-empty", "No comments yet. Turn on comment mode and click anything in the page."));
      return;
    }
    const section = (label, arr, cls) => {
      if (!arr.length) return;
      ui.list.appendChild(el("div", "cmt-section-label", label + " (" + arr.length + ")"));
      arr.forEach((x) => ui.list.appendChild(drawerItem(x, cls)));
    };
    section("Open", open, "");
    section("Orphaned", orphans, "cmt-orphan");
    section("Resolved", resolved, "cmt-resolved");
  }

  /* ---------- reposition on resize / mutation ---------- */
  let rafPending = false;
  function scheduleRender() { if (rafPending) return; rafPending = true; requestAnimationFrame(() => { rafPending = false; renderAll(); }); }

  /* ---------- AI bridge ---------- */
  // How the last render drew a thread: "words" (only the picked words), "block" (the whole
  // element), or "none" (orphaned, or never rendered).
  function drawnAs(id) {
    if (marks.some((m) => m.id === id) || contentRoot.querySelector('.cmt-highlight[data-cmt-thread="' + CSS.escape(id) + '"]')) return "words";
    return contentRoot.querySelector('[data-cmt-thread="' + CSS.escape(id) + '"]:not(.cmt-pin)') ? "block" : "none";
  }
  let markReady;
  const ready = new Promise((r) => { markReady = r; });
  window.__commentLayer = {
    docId: docId,
    ready: ready, // resolves once the store is loaded and the content root is known
    root: () => contentRoot,
    // The anchoring, shared with present-layer.js so a presentation step re-finds its block the
    // way a comment does. resolveMany resets the text cache once for the whole batch.
    anchor: {
      build: (node, range) => buildAnchor(node, range),
      resolveMany: (list) => { syncGen(true); return list.map((a) => resolveAnchor(a)); },
      label: (node, exact) => labelFor(node, exact),
    },
    setMode: (v) => { if (!!v !== document.body.classList.contains("cmt-mode")) toggleMode(); },
    relayout: () => panelApply(),
    backend: () => backend,
    identity: () => ({ name: ME, fromGate: MEFIXED }),
    setIdentity: (name) => { setMe(name); return ME; },
    getData: () => JSON.parse(JSON.stringify(state)),
    export: () => JSON.stringify(state, null, 2),
    import: async (json) => { state = normalizeState(typeof json === "string" ? JSON.parse(json) : json); await saveSoon(); renderAll(); return true; },
    threads: () => { syncGen(true); return state.threads.map((t) => ({ id: t.id, status: t.status, label: t.anchor && t.anchor.label, quote: t.anchor && t.anchor.quote && t.anchor.quote.exact, anchored: resolveAnchor(t.anchor).status, drawn: drawnAs(t.id), messages: t.messages })); },
    reply: async (id, text, author, agent) => { const t = state.threads.find((x) => x.id === id); if (!t) return false; const m = { author: author || "AI", text: String(text), at: now() }; if (agent && (agent.session || agent.host)) { m.agent = {}; if (agent.session) m.agent.session = String(agent.session); if (agent.host) m.agent.host = String(agent.host); } t.messages.push(m); await saveSoon(); renderAll(); return true; },
    editMessage: async (id, idx, text) => { const t = state.threads.find((x) => x.id === id); const m = t && t.messages[idx]; if (!m) return false; m.text = String(text); m.editedAt = now(); await saveSoon(); renderAll(); return true; },
    setStatus: async (id, status) => { const t = state.threads.find((x) => x.id === id); if (!t) return false; t.status = status === "resolved" ? "resolved" : "open"; await saveSoon(); renderAll(); return true; },
    reanchor: () => renderAll(),
  };

  /* ---------- init ---------- */
  async function init() {
    const rootSel = document.documentElement.getAttribute("data-comment-root");
    contentRoot = (rootSel ? ($(rootSel) || document.body) : document.body);
    backend = await detectBackend();
    ME = await resolveIdentity();
    await load();
    // panel default: open when the doc already has comments, folded when not (stored choice wins)
    panelPref = localStorage.getItem(PKEY) || (state.threads.length ? "0" : "1");
    buildUI();
    panelApply();
    renderAll();
    document.addEventListener("mousemove", onMove, true);
    document.addEventListener("click", onClick, true);
    window.addEventListener("resize", scheduleRender);
    // Capture phase: a scroll event on a nested pane does not bubble to window, and on an app
    // shell that pane is the only scroller. Repositioning is rect maths only — the full
    // renderAll (which rewraps ranges and rebuilds the drawer) stays on mutation and resize.
    window.addEventListener("scroll", schedulePins, true);
    // Opening or closing a fold moves everything below it and shows or hides the pins inside
    // it. `toggle` does not bubble, hence capture, and the observer above ignores attributes.
    document.addEventListener("toggle", schedulePins, true);
    document.addEventListener("keydown", (e) => {
      if (document.body.classList.contains("pr-on")) return; // present mode has its own keys
      // Plain C toggles comment mode (also ⌥C — e.code is layout-independent, so mac's "ç" still matches).
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName || "") || e.target.isContentEditable;
      if (!typing && !e.metaKey && !e.ctrlKey && e.code === "KeyC") { e.preventDefault(); toggleMode(); }
      if (e.key === "Escape") {
        if (ui.pop) closePop();
        else if (ui.drawer.classList.contains("cmt-open")) ui.drawer.classList.remove("cmt-open");
        else if (document.body.classList.contains("cmt-mode")) toggleMode();
      }
    });
    (pmq.addEventListener ? pmq.addEventListener.bind(pmq, "change") : pmq.addListener.bind(pmq))(panelApply);
    mo = new MutationObserver(() => { gen++; scheduleRender(); });
    mo.observe(contentRoot, MO_OPTS);
    setInterval(poll, 4000);
    markReady();
    console.log("[commentable-html] ready — doc:", docId, "| store:", backend,
      "| you:", ME || "(unnamed — asked on first comment)", MEFIXED ? "(from gate)" : "", "| threads:", state.threads.length);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
