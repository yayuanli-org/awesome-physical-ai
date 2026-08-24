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
 * reopen via the 💬 pill or right-clicking the FAB; drag its left edge to resize.
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
 *   __commentLayer.threads()                      -> array with resolved anchor labels
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
  const fmt = (iso) => { if (!iso) return ""; try { const d = new Date(iso); const o = { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }; if (d.getFullYear() !== new Date().getFullYear()) o.year = "numeric"; return d.toLocaleString([], o); } catch (e) { return ""; } };
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

  function buildAnchor(target, range) {
    if (range && !range.collapsed) {
      const container = range.commonAncestorContainer;
      const elNode = container.nodeType === 1 ? container : container.parentElement;
      const exact = norm(range.toString());
      return { type: "range", elementId: ensureAnchorId(elNode), cssPath: cssPath(elNode), quote: quoteFor(exact), label: labelFor(elNode, exact) };
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

  // Locate a quote's text range inside an element (for range highlighting).
  // One pass: build a normalized string identical to norm() semantics (collapse runs,
  // trim ends) plus a parallel map from each normalized char -> [textNode, offset].
  function locateRange(node, exact) {
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
    const idx = normStr.indexOf(want);
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
  function dice(a, b) {
    a = norm(a).toLowerCase(); b = norm(b).toLowerCase();
    if (!a || !b) return 0;
    if (a === b) return 1;
    if (a.length < 2 || b.length < 2) return a === b ? 1 : 0;
    const grams = (s) => { const m = new Map(); for (let i = 0; i < s.length - 1; i++) { const g = s.substr(i, 2); m.set(g, (m.get(g) || 0) + 1); } return m; };
    const A = grams(a), B = grams(b); let inter = 0, total = 0;
    A.forEach((c, g) => { total += c; if (B.has(g)) inter += Math.min(c, B.get(g)); });
    B.forEach((c) => { total += c; });
    return total ? (2 * inter) / total : 0;
  }
  const SIM_THRESHOLD = 0.62;

  // Render-scoped cache of normalized element text (reset at the top of each renderAll).
  let _normCache = new Map();
  function normText(node) { let v = _normCache.get(node); if (v === undefined) { v = norm(node.textContent); _normCache.set(node, v); } return v; }
  function prevText(node, n) { let s = "", e = node.previousElementSibling, g = 0; while (e && s.length < n && g++ < 8) { s = normText(e) + " " + s; e = e.previousElementSibling; } return s.slice(-n); }
  function nextText(node, n) { let s = "", e = node.nextElementSibling, g = 0; while (e && s.length < n && g++ < 8) { s += " " + normText(e); e = e.nextElementSibling; } return s.slice(0, n); }

  // Does this element's text still contain (or closely resemble) the stored quote?
  function textMatches(node, anchor) {
    if (!anchor.quote || !anchor.quote.exact) return true;
    const want = norm(anchor.quote.exact);
    const have = normText(node);
    return have.indexOf(want) >= 0 || dice(want, have) >= SIM_THRESHOLD;
  }

  const QUOTE_BLOCKS = "p,li,td,th,h1,h2,h3,h4,h5,h6,blockquote,figcaption,span,div,a,code,pre,dt,dd,caption,summary";

  // Find the element that best carries the quote. Returns {node, score} or null.
  function fuzzyFind(quote) {
    const exact = typeof quote === "string" ? quote : (quote && quote.exact);
    const pre = (quote && quote.prefix) || "", suf = (quote && quote.suffix) || "";
    const want = norm(exact);
    if (!want) return null;
    // 1) exact containment.
    const contains = [];
    contentRoot.querySelectorAll("*").forEach((n) => { if (n.closest(".cmt-ui")) return; if (normText(n).indexOf(want) >= 0) contains.push(n); });
    if (contains.length) {
      contains.sort((a, b) => normText(a).length - normText(b).length);
      // most specific candidates: those not containing another candidate
      const leaves = contains.filter((n) => !contains.some((m) => m !== n && n.contains(m)));
      const pool = leaves.length ? leaves : contains;
      // disambiguate repeats (e.g. identical table cells) via stored prefix/suffix context
      if ((pre || suf) && pool.length > 1) {
        const target = norm(pre + " " + want + " " + suf);
        let best = pool[0], bestScore = -1;
        pool.forEach((n) => {
          const s = dice(target, norm(prevText(n, 32) + " " + normText(n) + " " + nextText(n, 32)));
          if (s > bestScore) { bestScore = s; best = n; }
        });
        return { node: best, score: 1 };
      }
      return { node: pool[0], score: 1 };
    }
    // 2) approximate — best block within similarity threshold (handles light text edits).
    let best = null, bestScore = SIM_THRESHOLD;
    contentRoot.querySelectorAll(QUOTE_BLOCKS).forEach((n) => {
      if (n.closest(".cmt-ui")) return;
      const txt = normText(n);
      if (!txt || txt.length > want.length * 3.5) return; // skip oversized blocks
      const s = dice(want, txt);
      if (s > bestScore) { bestScore = s; best = n; }
    });
    return best ? { node: best, score: bestScore } : null;
  }

  // Robustness-ordered resolution: structural hint (validated against quote) -> fuzzy quote.
  function resolveAnchor(anchor) {
    if (!anchor) return { status: "orphan" };
    let node = findElement(anchor);
    let approx = false;
    if (node && !textMatches(node, anchor)) node = null; // resolution success != correctness
    if (!node && anchor.quote && anchor.quote.exact) { const f = fuzzyFind(anchor.quote); if (f) { node = f.node; approx = f.score < 1; } }
    if (!node) return { status: "orphan" };
    let range = null;
    if (anchor.type === "range" && anchor.quote) range = locateRange(node, anchor.quote.exact);
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
      return Object.assign({}, t, { messages: msgs });
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
  async function poll() {
    if (backend !== "server" || ui.pop) return;
    try {
      const r = await fetch(ENDPOINT, { cache: "no-store" });
      const txt = await r.text();
      if (txt && txt !== lastServerSnapshot) { const d = JSON.parse(txt); lastServerSnapshot = txt; state = normalizeState(d); renderAll(); }
    } catch (e) {}
  }

  /* ---------- UI scaffold ---------- */
  const ui = { fab: null, badge: null, markers: null, drawer: null, list: null, pill: null, pop: null };

  function buildUI() {
    const root = el("div", "cmt-ui");

    ui.fab = el("button", "cmt-fab", '<span class="cmt-dot"></span><span class="cmt-fab-label">Comment</span><span class="cmt-badge" data-zero="1">0</span>');
    ui.badge = ui.fab.querySelector(".cmt-badge");
    ui.fab.title = "Toggle comment mode  (C). Right-click for the comments panel.";
    ui.fab.addEventListener("click", toggleMode);
    ui.fab.addEventListener("contextmenu", (e) => { e.preventDefault(); toggleDrawer(); });

    ui.markers = el("div", "cmt-marker-layer");

    ui.drawer = el("div", "cmt-drawer");
    ui.drawer.innerHTML =
      '<div class="cmt-grip" title="Drag to resize"></div>' +
      '<div class="cmt-drawer-head"><h2>Comments</h2><div class="cmt-row" style="margin:0">' +
      '<span class="cmt-backend"></span><button class="cmt-btn cmt-ghost cmt-drawer-close" title="Hide comments panel">»</button></div></div>' +
      '<div class="cmt-drawer-list"></div>';
    ui.list = ui.drawer.querySelector(".cmt-drawer-list");
    ui.drawer.querySelector(".cmt-drawer-close").addEventListener("click", toggleDrawer);
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

    ui.pill = el("button", "cmt-pill", '💬 Comments <span class="cmt-pill-n" data-zero="1">0</span>');
    ui.pill.title = "Show comments panel";
    ui.pill.addEventListener("click", toggleDrawer);

    root.append(ui.fab, ui.markers, ui.drawer, ui.pill);
    document.body.appendChild(root);
  }

  function toggleMode() {
    document.body.classList.toggle("cmt-mode");
    clearHover();
  }

  /* ---------- right comments panel: docked ≥1360px, overlay below ---------- */
  const pmq = window.matchMedia("(min-width: 1360px)");
  function panelSync() {
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
  let hovered = null;
  function clearHover() { if (hovered) { hovered.classList.remove("cmt-hover"); hovered = null; } }
  function onMove(e) {
    if (!document.body.classList.contains("cmt-mode")) return;
    let t = e.target;
    if (!contentRoot.contains(t) || (t.closest && t.closest(".cmt-ui"))) { clearHover(); return; }
    if (t === hovered) return;
    clearHover(); hovered = t; t.classList.add("cmt-hover");
  }

  /* ---------- create / open threads ---------- */
  function onClick(e) {
    const t = e.target;
    // A click outside an open popover dismisses it (any mode); the draft is stashed by
    // closePop and restored when the same target is reopened. The dismissing click is
    // swallowed unless it lands on comment UI that should keep working (pins, drawer, FAB).
    if (ui.pop && !ui.pop.contains(t)) {
      const passThrough = t.closest && t.closest(".cmt-pin, [data-cmt-thread], .cmt-drawer, .cmt-fab, .cmt-pill");
      if (!passThrough) {
        closePop();
        e.preventDefault(); e.stopPropagation();
        return;
      }
    }
    if (!document.body.classList.contains("cmt-mode")) return;
    if (t.closest && t.closest(".cmt-ui")) return; // UI clicks pass through
    // open existing thread when clicking a pin/highlight
    const owner = t.closest && t.closest("[data-cmt-thread]");
    if (owner) { e.preventDefault(); e.stopPropagation(); openThread(owner.getAttribute("data-cmt-thread"), owner); return; }
    if (!contentRoot.contains(t) || t === contentRoot) return;
    e.preventDefault(); e.stopPropagation();
    const sel = window.getSelection();
    if (sel && !sel.isCollapsed && contentRoot.contains(sel.anchorNode)) {
      const range = sel.getRangeAt(0).cloneRange(); sel.removeAllRanges();
      composeNew(buildAnchor(null, range), range);
    } else {
      composeNew(buildAnchor(t, null), null);
    }
  }

  // Unsent popover text, keyed by target — survives dismissals (outside click, Escape,
  // re-renders). Cleared on submit or explicit Cancel.
  const drafts = new Map();
  function closePop() {
    if (!ui.pop) return;
    const key = ui.pop._draftKey, ta = ui.pop.querySelector("textarea");
    if (key && ta) { if (ta.value.trim()) drafts.set(key, ta.value); else drafts.delete(key); }
    ui.pop.remove(); ui.pop = null;
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
    ui.pop = p; document.body.appendChild(p); placePop(rect); wireWho(p);
    const ta = p.querySelector("textarea"); ta.value = drafts.get(draftKey) || "";
    if (!p.querySelector(".cmt-who")) ta.focus();   // else wireWho already focused the name field
    p.querySelector(".cmt-cancel").addEventListener("click", () => { ta.value = ""; closePop(); });
    p.querySelector(".cmt-save").addEventListener("click", async () => {
      const text = ta.value.trim(); if (!text) { ta.focus(); return; }
      const author = me();
      const thread = { id: uid(), createdBy: author, createdAt: now(), status: "open", anchor: anchor, messages: [{ author: author, text: text, at: now() }] };
      state.threads.push(thread); drafts.delete(draftKey); ta.value = "";
      await save(); closePop(); renderAll(); // pin appears; no popover re-open after submit
    });
    ta.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) p.querySelector(".cmt-save").click(); if (e.key === "Escape") closePop(); });
  }

  function openThread(id, nearNode) {
    closePop();
    const thread = state.threads.find((t) => t.id === id); if (!thread) return;
    const res = resolveAnchor(thread.anchor);
    const node = (nearNode && nearNode.closest("[data-cmt-thread]")) ? document.querySelector('[data-cmt-thread="' + id + '"]') : res.node;
    const rect = node ? node.getBoundingClientRect() : (nearNode ? nearNode.getBoundingClientRect() : { top: 80, left: 80, right: 300 });
    const p = el("div", "cmt-pop");
    const msgs = thread.messages.map((m, i) =>
      '<div class="cmt-msg ' + (isAI(m) ? "cmt-ai" : "") + '" data-idx="' + i + '"><div class="cmt-msg-meta"><span class="cmt-msg-author">' +
      esc(m.author) + "</span>" + agentTag(m) + '<span title="' + esc(m.at || "") + '">' + fmt(m.at) + (m.editedAt ? " · edited " + fmt(m.editedAt) : "") + "</span>" +
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
    ui.pop = p; document.body.appendChild(p); placePop(rect); wireWho(p);
    const ta = p.querySelector("textarea"); ta.value = drafts.get(draftKey) || "";
    p.querySelector(".cmt-reply").addEventListener("click", async () => {
      const text = ta.value.trim(); if (!text) { ta.focus(); return; }
      thread.messages.push({ author: me(), text: text, at: now() }); thread.status = "open";
      drafts.delete(draftKey); ta.value = "";
      await save(); openThread(id);
    });
    p.querySelector(".cmt-resolve").addEventListener("click", async () => {
      thread.status = thread.status === "resolved" ? "open" : "resolved"; await save(); renderAll(); closePop();
    });
    p.querySelector(".cmt-del").addEventListener("click", async () => {
      drafts.delete(draftKey); ta.value = "";
      state.threads = state.threads.filter((t) => t.id !== id); await save(); renderAll(); closePop();
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
          if (v !== m.text) { m.text = v; m.editedAt = now(); await save(); }
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
    if (res.node && res.status !== "orphan") {
      res.node.scrollIntoView({ block: "center", behavior: "smooth" });
      res.node.classList.add("cmt-flash");
      setTimeout(() => res.node.classList.remove("cmt-flash"), 1300);
    }
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

  function wrapRange(range, threadId, resolved) {
    try {
      const span = el("span", "cmt-highlight" + (resolved ? " cmt-resolved" : ""));
      span.setAttribute("data-cmt-thread", threadId);
      range.surroundContents(span); injected.push(span); return span;
    } catch (e) { return null; }
  }

  function renderAll() {
    closePop();
    if (mo) mo.disconnect(); // our own wrap/unwrap mutations must not retrigger a render
    try {
    _normCache = new Map();
    unwrapInjected();
    ui.markers.innerHTML = "";
    const rightDock = document.body.classList.contains("cmt-docked") ? panelW + 12 : 0;
    const open = [], resolved = [], orphans = [];
    state.threads.forEach((thread) => {
      if (!thread.messages || !thread.messages.length) return; // degenerate thread — skip
      const res = resolveAnchor(thread.anchor);
      const bucket = res.status === "orphan" ? orphans : thread.status === "resolved" ? resolved : open;
      bucket.push({ thread, res });
      if (res.status === "orphan") return;
      const isResolved = thread.status === "resolved";
      let target = res.node;
      let wrapped = null;
      if (thread.anchor.type === "range" && res.range) wrapped = wrapRange(res.range, thread.id, isResolved);
      if (!wrapped && target) {
        target.classList.add("cmt-anchored"); if (isResolved) target.classList.add("cmt-resolved");
        target.setAttribute("data-cmt-thread", thread.id);
      }
      // marker pin
      const anchorNode = wrapped || target;
      if (anchorNode) {
        const rect = anchorNode.getBoundingClientRect();
        const pin = el("button", "cmt-pin" + (isResolved ? " cmt-resolved" : ""));
        const aiLast = thread.messages[thread.messages.length - 1];
        if (isAI(aiLast) && !isResolved) pin.classList.add("cmt-ai-unread");
        pin.textContent = thread.messages.length;
        pin.title = thread.messages.length + (thread.messages.length > 1 ? " messages" : " message") + (aiLast && aiLast.at ? " · " + aiLast.author + (aiLast.agent && aiLast.agent.host ? " @ " + aiLast.agent.host : "") + " · " + fmt(aiLast.at) : "");
        pin.setAttribute("data-cmt-thread", thread.id);
        pin.style.top = (window.scrollY + rect.top) + "px";
        const gutter = Math.min(window.scrollX + rect.right + 8, window.scrollX + document.documentElement.clientWidth - rightDock - 34);
        pin.style.left = gutter + "px";
        pin.addEventListener("click", (e) => { e.stopPropagation(); openThread(thread.id); });
        ui.markers.appendChild(pin);
      }
    });
    // badge = open threads (incl. orphans)
    const count = open.length + orphans.length;
    ui.badge.textContent = count; ui.badge.setAttribute("data-zero", count ? "0" : "1");
    if (ui.pill) { const n = ui.pill.querySelector(".cmt-pill-n"); n.textContent = count; n.setAttribute("data-zero", count ? "0" : "1"); }
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
        '<span class="cmt-item-when" title="' + esc(m.at || "") + '">' + fmt(m.at) + (m.editedAt ? " · edited " + fmt(m.editedAt) : "") + "</span>" +
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
  window.__commentLayer = {
    docId: docId,
    backend: () => backend,
    identity: () => ({ name: ME, fromGate: MEFIXED }),
    setIdentity: (name) => { setMe(name); return ME; },
    getData: () => JSON.parse(JSON.stringify(state)),
    export: () => JSON.stringify(state, null, 2),
    import: async (json) => { state = normalizeState(typeof json === "string" ? JSON.parse(json) : json); await save(); renderAll(); return true; },
    threads: () => state.threads.map((t) => ({ id: t.id, status: t.status, label: t.anchor && t.anchor.label, quote: t.anchor && t.anchor.quote && t.anchor.quote.exact, anchored: resolveAnchor(t.anchor).status, messages: t.messages })),
    reply: async (id, text, author, agent) => { const t = state.threads.find((x) => x.id === id); if (!t) return false; const m = { author: author || "AI", text: String(text), at: now() }; if (agent && (agent.session || agent.host)) { m.agent = {}; if (agent.session) m.agent.session = String(agent.session); if (agent.host) m.agent.host = String(agent.host); } t.messages.push(m); await save(); renderAll(); return true; },
    editMessage: async (id, idx, text) => { const t = state.threads.find((x) => x.id === id); const m = t && t.messages[idx]; if (!m) return false; m.text = String(text); m.editedAt = now(); await save(); renderAll(); return true; },
    setStatus: async (id, status) => { const t = state.threads.find((x) => x.id === id); if (!t) return false; t.status = status === "resolved" ? "resolved" : "open"; await save(); renderAll(); return true; },
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
    document.addEventListener("keydown", (e) => {
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
    mo = new MutationObserver(() => scheduleRender());
    mo.observe(contentRoot, MO_OPTS);
    setInterval(poll, 4000);
    console.log("[commentable-html] ready — doc:", docId, "| store:", backend,
      "| you:", ME || "(unnamed — asked on first comment)", MEFIXED ? "(from gate)" : "", "| threads:", state.threads.length);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
