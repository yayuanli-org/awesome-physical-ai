/* cite-layer.js — a citation opens its reference in a card beside it.
 *
 * A click on an in-text citation shows the reference it points to in a small card under the
 * citation, the way Google Scholar's PDF reader previews a cited paper, so the reader keeps
 * their place instead of jumping to the reference list and back. The card holds the entry as
 * the page wrote it, with its own links live, then a Google Scholar search for it, arXiv and
 * DOI links when the entry names one, and "In references", which is the old jump.
 *
 * A citation is any <a href="#id"> whose target sits in a reference list (an element with
 * class "refs", or marked data-refs) or whose id starts with "ref-". The house markup:
 *   <span class="cite">[<a href="#ref-zacks2001">1</a>, <a href="#ref-kurby2008">2</a>]</span>
 *   <ol class="refs"><li id="ref-zacks2001">J. M. Zacks and B. Tversky. …</li> …</ol>
 * Scholar searches the title when the entry marks it (<cite>, class="title", or a link of three
 * or more words), else the whole entry.
 *
 * Esc, a click elsewhere or a second click on the citation closes the card. ⌘, Ctrl and ⇧ clicks
 * keep the browser's own behaviour. Comment mode (C) and present mode (P) own every click while
 * they run, so the card closes when either starts. data-cite="off" on <html> turns the layer off,
 * and citations jump again.
 *
 * Bridge: window.__citeLayer.{open, close, current}
 */
(function () {
  "use strict";
  if (window.__citeLayerLoaded) return;
  window.__citeLayerLoaded = true;

  const doc = document, html = doc.documentElement;
  if ((html.getAttribute("data-cite") || "").toLowerCase() === "off") return;

  const LIST = ".refs, [data-refs]";
  const UI = ".toc-layer, .tl-btn, .cmt-ui, .pr-ui";   // the other layers' chrome: its links are never citations
  const GAP = 8, EDGE = 16;                             // card to citation · card to the viewport's edge

  const norm = (s) => (s || "").replace(/\s+/g, " ").trim();
  const el = (tag, cls, inner) => { const n = doc.createElement(tag); if (cls) n.className = cls; if (inner != null) n.innerHTML = inner; return n; };

  const ui = {};
  let cur = null;     // the open card: {a, entry, id, line, up}
  let raf = 0;

  /* ---------- what a citation points at ---------- */
  // The reference entry behind a link, as {entry, id}, or null when the link is not a citation.
  function targetOf(a) {
    const href = a.getAttribute("href") || "";
    if (href.length < 2 || href[0] !== "#") return null;
    let id = href.slice(1);
    try { id = decodeURIComponent(id); } catch (e) {}
    const t = doc.getElementById(id);
    if (!t || t.contains(a)) return null;
    const list = t.closest(LIST);
    if (list && list !== t) {
      const li = t.closest("li");
      return { entry: li && list.contains(li) ? li : t, id: id };
    }
    return /^ref-/i.test(id) ? { entry: t, id: id } : null;
  }

  // "[12]": the citation's own text when it is a short label, else the entry's own number.
  function labelOf(a, entry) {
    const own = norm(a.textContent).replace(/^\[|\]$/g, "");
    if (own && own.length <= 8) return "[" + own + "]";
    const n = entry.querySelector(":scope > .n");
    if (n) return norm(n.textContent);
    const ol = entry.tagName === "LI" && entry.parentElement && entry.parentElement.tagName === "OL" ? entry.parentElement : null;
    if (ol) return "[" + ((parseInt(ol.getAttribute("start"), 10) || 1) + Array.prototype.indexOf.call(ol.children, entry)) + "]";
    return "";
  }

  // The entry as written, minus what the layers put on it: ids (the card must not hold a second
  // copy of an anchor), comment highlights, the layers' classes and data, and a leading "[1]".
  function cloneOf(entry) {
    const c = entry.cloneNode(true);
    c.querySelectorAll(".cmt-highlight").forEach((s) => s.replaceWith(...s.childNodes));
    const lead = c.querySelector(":scope > .n");
    if (lead) lead.remove();
    [c].concat(Array.from(c.querySelectorAll("*"))).forEach((n) => {
      n.removeAttribute("id");
      Array.from(n.attributes).forEach((at) => { if (/^data-(cmt|pr)-/.test(at.name)) n.removeAttribute(at.name); });
      Array.from(n.classList).forEach((k) => { if (/^(cmt|pr|ct)-/.test(k)) n.classList.remove(k); });
    });
    // A link out of the card opens a tab, so the page stays where the reader was.
    c.querySelectorAll("a[href]").forEach((x) => { if (/^https?:/i.test(x.getAttribute("href"))) { x.target = "_blank"; x.rel = "noopener"; } });
    return c;
  }

  // What to ask Scholar for: the title when the entry marks one, else the whole entry.
  function queryOf(c) {
    const t = c.querySelector("cite, .title");
    if (t) return norm(t.textContent);
    const link = Array.from(c.querySelectorAll("a[href^='http']")).find((x) => norm(x.textContent).split(" ").length >= 3);
    if (link) return norm(link.textContent);
    const x = c.cloneNode(true);
    x.querySelectorAll(".note").forEach((n) => n.remove());
    return norm(x.textContent).replace(/["“”]/g, "").slice(0, 300);
  }

  // arXiv and DOI links for an entry that names an id in its text but does not link it.
  function linksOf(c) {
    const text = c.textContent;
    const hrefs = Array.from(c.querySelectorAll("a[href]")).map((x) => x.getAttribute("href")).join(" ");
    const out = [];
    const ax = /arxiv[:\s]\s*(\d{4}\.\d{4,5})/i.exec(text);
    if (ax && !/arxiv\.org/i.test(hrefs)) out.push(["arXiv", "https://arxiv.org/abs/" + ax[1]]);
    const doi = /\b10\.\d{4,9}\/[-._;()\/:a-z0-9]+/i.exec(text);
    if (doi && !/doi\.org/i.test(hrefs)) out.push(["DOI", "https://doi.org/" + doi[0].replace(/[.,;)]+$/, "")]);
    return out;
  }

  /* ---------- the card ---------- */
  function build() {
    ui.card = el("div", "ct-pop",
      '<button type="button" class="ct-x" aria-label="Close">×</button>' +
      '<div class="ct-in"><div class="ct-ref"></div><div class="ct-acts"></div></div>');
    ui.card.setAttribute("role", "dialog");
    ui.card.tabIndex = -1;
    ui.card.hidden = true;
    ui.ref = ui.card.querySelector(".ct-ref");
    ui.acts = ui.card.querySelector(".ct-acts");
    ui.card.querySelector(".ct-x").addEventListener("click", () => close(true));
    doc.body.appendChild(ui.card);
  }

  function open(a, hit, line, keyboard) {
    if (!ui.card) build();
    if (cur && cur.a !== a) cur.a.classList.remove("ct-on");
    const c = cloneOf(hit.entry);
    const label = labelOf(a, hit.entry);
    const query = queryOf(c), links = linksOf(c);

    ui.ref.replaceChildren();
    if (label) ui.ref.appendChild(el("span", "ct-n")).textContent = label;
    ui.ref.append(...c.childNodes);
    ui.acts.replaceChildren();
    const add = (text, href, cls) => {
      const x = ui.acts.appendChild(el("a", cls));
      x.textContent = text;
      x.setAttribute("href", href);
      if (!cls) { x.target = "_blank"; x.rel = "noopener"; }
    };
    add("Google Scholar ↗", "https://scholar.google.com/scholar?q=" + encodeURIComponent(query));
    links.forEach((l) => add(l[0] + " ↗", l[1]));
    add("In references ↓", "#" + encodeURIComponent(hit.id), "ct-go");

    ui.card.setAttribute("aria-label", "Reference " + (label || hit.id));
    a.classList.add("ct-on");
    cur = { a: a, entry: hit.entry, id: hit.id, line: line, up: false };
    ui.card.hidden = false;
    ui.card.querySelector(".ct-in").scrollTop = 0;
    place(true);
    if (keyboard) ui.card.focus({ preventScroll: true });
  }

  function close(refocus) {
    if (!cur) return;
    const a = cur.a;
    a.classList.remove("ct-on");
    const inside = ui.card.contains(doc.activeElement);
    cur = null;
    ui.card.hidden = true;
    if (refocus && inside) a.focus({ preventScroll: true });
  }

  // "In references": the browser follows the link, as a citation used to. A link into a closed
  // <details> scrolls nowhere, so the folds around the entry open first. The entry flashes on arrival.
  function jump() {
    const entry = cur.entry;
    for (let d = entry.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) d.open = true;
    close(false);
    entry.classList.remove("ct-flash");
    void entry.offsetWidth;   // restarts the animation when the same entry flashes twice
    entry.classList.add("ct-flash");
    setTimeout(() => entry.classList.remove("ct-flash"), 2600);
  }

  /* ---------- placement ----------
     Under the citation, or above it when the space below is short and the space above is larger.
     The side is chosen when the card opens and kept while the page scrolls, so the card never flips
     under the reader's eye. Centred on the citation and held inside the content column when it
     fits there, else inside what the screen shows. Document coordinates, like the comment
     popover, so a scrolling window carries the card with the page. "What the screen shows" is
     the visual viewport: a phone zooms a page wider than itself out, and a pinch zooms it in. */
  function place(full) {
    if (!cur) return;
    const rs = cur.a.isConnected ? cur.a.getClientRects() : [];
    if (!rs.length) { close(false); return; }
    const r = rs[Math.min(cur.line, rs.length - 1)];
    const card = ui.card, inner = card.querySelector(".ct-in");
    const vv = window.visualViewport;
    const vx = vv ? vv.offsetLeft : 0, vy = vv ? vv.offsetTop : 0;
    const vw = vv ? vv.width : html.clientWidth, vh = vv ? vv.height : html.clientHeight;
    if (full) {
      // Measure at the page's corner: left where it last sat, the card could widen the page.
      card.style.left = "0px"; card.style.top = "0px";
      inner.style.maxHeight = "none";
      const below = vy + vh - r.bottom - GAP - EDGE, above = r.top - vy - GAP - EDGE;
      cur.up = card.offsetHeight > below && above > below;
      inner.style.maxHeight = Math.max(120, (cur.up ? above : below) - 2) + "px";
    }
    const w = card.offsetWidth, h = card.offsetHeight;
    let lo = vx + EDGE, hi = vx + vw - EDGE;
    const sel = html.getAttribute("data-comment-root");
    const col = (sel && doc.querySelector(sel)) || doc.querySelector("#content, main");
    if (col && col !== doc.body) {
      const cr = col.getBoundingClientRect();
      if (Math.min(hi, cr.right) - Math.max(lo, cr.left) >= w) { lo = Math.max(lo, cr.left); hi = Math.min(hi, cr.right); }
    }
    const cx = (r.left + r.right) / 2;
    const left = Math.max(lo, Math.min(cx - w / 2, hi - w));
    const top = cur.up ? r.top - GAP - h : r.bottom + GAP;
    card.style.left = (left + window.scrollX) + "px";
    card.style.top = (top + window.scrollY) + "px";
    card.classList.toggle("ct-up", cur.up);
    card.style.setProperty("--ct-tip", Math.max(14, Math.min(w - 14, cx - left)) + "px");
  }
  // Rect maths only. Capture phase, because a scroll inside a nested pane does not reach window.
  function schedule() { if (!cur || raf) return; raf = requestAnimationFrame(() => { raf = 0; place(false); }); }

  /* ---------- input ---------- */
  // Which line box of a wrapped citation was clicked, so the card points at that line.
  function lineOf(a, x, y) {
    const rs = a.getClientRects();
    for (let i = 0; i < rs.length; i++) if (y >= rs[i].top && y <= rs[i].bottom && x >= rs[i].left - 1 && x <= rs[i].right + 1) return i;
    return 0;
  }

  function onClick(e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest ? e.target.closest("a[href^='#']") : null;
    if (!a || a.closest(UI)) return;
    const inCard = !!ui.card && ui.card.contains(a);
    if (inCard && a.classList.contains("ct-go")) { jump(); return; }
    const hit = targetOf(a);
    if (!hit) return;
    e.preventDefault();
    if (cur && cur.a === a) { close(true); return; }
    // A citation inside the card (an entry that cites another) swaps the card's content in place.
    if (inCard) open(cur.a, hit, cur.line, e.detail === 0);
    else open(a, hit, lineOf(a, e.clientX, e.clientY), e.detail === 0);
  }

  // Dismissal listens to pointerdown: iOS fires no click on plain text, so a tap on the page
  // would never reach a click listener. A press on a citation is left to the click above.
  function onDown(e) {
    if (!cur) return;
    const t = e.target;
    if (ui.card.contains(t)) return;
    const a = t.closest ? t.closest("a[href^='#']") : null;
    if (a && !a.closest(UI) && targetOf(a)) return;
    close(false);
  }

  function onKey(e) {
    if (!cur || e.key !== "Escape") return;
    e.preventDefault(); e.stopPropagation();   // one Esc closes one thing: this card, not the comment panel too
    close(true);
  }

  /* ---------- bridge ---------- */
  window.__citeLayer = {
    open: (a) => {
      a = typeof a === "string" ? doc.querySelector(a) : a;
      const hit = a && targetOf(a);
      if (hit) open(a, hit, 0, false);
      return !!hit;
    },
    close: () => close(false),
    current: () => (cur ? {
      id: cur.id, up: cur.up, label: ui.card.getAttribute("aria-label"), text: norm(ui.ref.textContent),
      links: Array.from(ui.acts.querySelectorAll("a")).map((x) => [x.textContent, x.getAttribute("href")]),
    } : null),
  };

  /* ---------- init ---------- */
  function init() {
    doc.addEventListener("click", onClick);
    doc.addEventListener("pointerdown", onDown, true);
    doc.addEventListener("keydown", onKey, true);
    window.addEventListener("scroll", schedule, true);
    window.addEventListener("resize", () => { if (cur) place(true); });
    if (window.visualViewport) window.visualViewport.addEventListener("resize", () => { if (cur) place(true); });
    // Comment mode and present mode take every click while they run, so the card gives way to
    // them. Any other class on <body> (a sidebar docking) moves the column, so the card follows.
    new MutationObserver(() => {
      if (!cur) return;
      if (/\b(cmt-mode|pr-on)\b/.test(doc.body.className)) close(false);
      else schedule();
    }).observe(doc.body, { attributes: true, attributeFilter: ["class"] });
  }

  if (doc.readyState === "loading") doc.addEventListener("DOMContentLoaded", init);
  else init();
})();
