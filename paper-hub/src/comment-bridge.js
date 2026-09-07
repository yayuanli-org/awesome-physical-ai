/* comment-bridge.js — glue between comment-layer.js and this page's three tabs.
 *
 * The layer assumes one document. This page is an app: all three views sit in the DOM
 * at once and two of them are hidden, so a comment can point at content that is not on
 * screen. The layer hides the marker for an anchor with no box, which handles the
 * pins. What it cannot know is which tab the content is on, so:
 *
 *   1. every row in the comments panel says which tab its comment is on,
 *   2. clicking such a row switches to that tab, then opens the thread there.
 *
 * Nothing here patches comment-layer.js, so the asset can be re-copied from the
 * commentable-html skill without losing any of it.
 */
(function () {
"use strict";

var TAB = { "view-framework": "Framework", "view-table": "Papers", "view-protocol": "Protocol" };
var VSEL = Object.keys(TAB).map(function (id) { return "#" + id; }).join(",");

function q(sel, root) { return (root || document).querySelector(sel); }
function boxed(n) { return !!(n && n.getClientRects().length); }
function nodeFor(id) { return q('.shell [data-cmt-thread="' + CSS.escape(id) + '"]'); }
function pinFor(id) { return q('.cmt-pin[data-cmt-thread="' + CSS.escape(id) + '"]'); }

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
  var layer = window.__commentLayer, list = q(".cmt-drawer-list");
  if (layer && list && window.__physai) return cb(layer, list);
  setTimeout(function () { whenReady(cb); }, 80);
}

whenReady(function (layer, list) {

  /* ---- 1. tab badge on every panel row -------------------------------------
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
      if (!target) return;
      var chip = target.querySelector(".cb-view");
      // Rewrite rather than skip: a thread read before its view was rendered resolves
      // somewhere else for a moment, and a badge stamped once would keep saying so.
      if (!at || !at.name) { if (chip) chip.remove(); return; }
      if (!chip) { chip = document.createElement("span"); chip.className = "cb-view"; target.appendChild(chip); }
      if (chip.textContent !== at.name) chip.textContent = at.name;
    });
  }
  // childList only, no subtree: the chips above land inside a row, so they never re-fire this
  new MutationObserver(stamp).observe(list, { childList: true });
  stamp();

  /* ---- 2. clicking an off-tab row switches tabs first ----------------------
     Switching redraws the whole page and the layer re-places its markers some frames
     later, so poll for the marker rather than guess a delay. A render landing just
     after the click closes the thread again, which one retry covers. */
  function reveal(id, tries) {
    tries = tries || 0;
    var node = nodeFor(id), pin = pinFor(id);
    // The layer re-places its markers on an animation frame, which a busy or
    // background tab defers, so wait for the marker rather than time the render.
    if ((!pin || !boxed(node)) && tries < 40) {
      setTimeout(function () { reveal(id, tries + 1); }, 100);
      return;
    }
    // Instant, not smooth: a smooth scroll is an animation, and the redraw that
    // follows a tab switch cancels it halfway, leaving the comment off screen.
    if (node) node.scrollIntoView({ block: "center" });
    if (!pin) return;
    open(pin, 0);
  }

  // A render landing just after the click closes the thread again. Re-open a few times
  // over half a second, then stop — past that the user has moved on.
  function open(pin, tries) {
    pin.click();
    if (tries > 2) return;
    setTimeout(function () { if (!q(".cmt-pop")) open(pin, tries + 1); }, 180);
  }

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
    window.__physai.setView(want);
    reveal(id);
  }, true);
});
})();
