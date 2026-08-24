/* comment-bridge.js — glue between comment-layer.js and this page's three tabs.
 *
 * The layer assumes a static document. This page is an app: all three views sit in
 * the DOM at once and two of them are hidden, so a comment on a hidden view still
 * resolves but has no layout box, and its pin lands in the top-left corner. Three
 * repairs, all of them read-only with respect to the layer:
 *
 *   1. pins for off-tab comments are hidden,
 *   2. every row in the comments panel says which tab its comment is on,
 *   3. clicking such a row switches to that tab, then opens the thread there.
 *
 * Nothing here patches comment-layer.js, so the asset can be re-copied from the
 * skill without losing any of it.
 */
(function () {
"use strict";

var TAB = { "view-framework": "Framework", "view-table": "Papers", "view-protocol": "Protocol" };
var VSEL = Object.keys(TAB).map(function (id) { return "#" + id; }).join(",");

function q(sel, root) { return (root || document).querySelector(sel); }
function boxed(n) { return !!(n && n.getClientRects().length); }
function nodeFor(id) { return q('.shell [data-cmt-thread="' + CSS.escape(id) + '"]'); }

// Where a thread's target lives: one of the three tabs, or the filter rail, which
// the app hides on the protocol tab.
function locate(id) {
  var n = nodeFor(id);
  if (!n) return null;
  var host = n.closest(VSEL);
  if (host) return { node: n, tab: host.id.slice(5), name: TAB[host.id] };
  if (n.closest("aside:not(#panel)")) return { node: n, tab: "filters", name: "Filters" };
  return { node: n, tab: null, name: null };
}

function whenReady(cb) {
  var layer = window.__commentLayer, list = q(".cmt-drawer-list"), pins = q(".cmt-marker-layer");
  if (layer && list && pins && window.__physai) return cb(layer, list, pins);
  setTimeout(function () { whenReady(cb); }, 80);
}

whenReady(function (layer, list, pins) {

  /* ---- 1. off-tab pins ---------------------------------------------------- */
  // A tab switch can cost the layer several renders, and each one wipes the open
  // thread. reveal() therefore waits out the burst: every rebuild of the pin layer
  // restarts a short timer, and the thread opens once the timer survives it.
  var pending = null, settle = null;
  function reveal(id) {
    var n = nodeFor(id);
    if (n) n.scrollIntoView({ block: "center", behavior: "smooth" });
    var pin = q('.cmt-pin[data-cmt-thread="' + CSS.escape(id) + '"]');
    if (pin) pin.click();
  }
  function arm(id) {
    pending = id;
    // nothing to wait out if the layer never re-renders
    setTimeout(function () { if (pending === id) { pending = null; reveal(id); } }, 600);
  }
  function sweepPins() {
    Array.prototype.forEach.call(pins.querySelectorAll(".cmt-pin"), function (pin) {
      var id = pin.getAttribute("data-cmt-thread");
      pin.style.display = boxed(nodeFor(id)) ? "" : "none";
    });
    if (!pending) return;
    clearTimeout(settle);
    settle = setTimeout(function () {
      var id = pending; pending = null;
      if (id) reveal(id);
    }, 120);
  }
  // childList only — the style writes above are attribute changes and never re-fire it
  new MutationObserver(sweepPins).observe(pins, { childList: true });
  sweepPins();

  /* ---- 2. tab badge on every panel row -------------------------------------
     renderDrawer emits rows in one order: open, then orphaned, then resolved, each
     in store order. threads() hands back the store in that same order, so lining the
     two up gives each row its thread id without touching the layer. */
  function order() {
    var t = layer.threads();
    var live = function (x) { return x.anchored !== "orphan"; };
    return t.filter(function (x) { return live(x) && x.status !== "resolved"; })
      .concat(t.filter(function (x) { return !live(x); }),
              t.filter(function (x) { return live(x) && x.status === "resolved"; }));
  }
  function stamp() {
    var rows = list.querySelectorAll(".cmt-item"), seq = order();
    if (rows.length !== seq.length) return; // the two views disagree — skip this pass
    Array.prototype.forEach.call(rows, function (row, i) {
      var id = seq[i].id;
      row.setAttribute("data-thread", id);
      var at = locate(id), target = row.querySelector(".cmt-item-target");
      if (!at || !at.name || !target || row.querySelector(".cb-view")) return;
      var chip = document.createElement("span");
      chip.className = "cb-view";
      chip.textContent = at.name;
      target.appendChild(chip);
    });
  }
  new MutationObserver(stamp).observe(list, { childList: true });
  stamp();

  /* ---- 3. clicking an off-tab row switches tabs first ---------------------- */
  list.addEventListener("click", function (e) {
    var row = e.target.closest && e.target.closest(".cmt-item");
    if (!row) return;
    var id = row.getAttribute("data-thread");
    if (!id) return;
    var at = locate(id);
    if (!at || !at.tab) return;
    var here = window.__physai.view();
    // the filter rail is up on every tab except protocol
    var want = at.tab === "filters" ? (here === "protocol" ? "framework" : here) : at.tab;
    if (want === here) return; // already looking at it — let the layer do its thing
    e.preventDefault();
    e.stopPropagation();
    arm(id);
    window.__physai.setView(want);
  }, true);
});
})();
