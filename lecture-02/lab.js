/* lab.js — turn JupyterLab into a reading room for a Jupyter doc.
 *
 * Injected by nbdoc.lab() as part of the hidden first cell's output. JupyterLab
 * runs <script> tags found in a TRUSTED cell's output (rendermime calls
 * evalInnerHTMLScriptTags on them); an untrusted notebook shows a "Run" button
 * instead. So this file travels inside the .ipynb and needs no extension.
 *
 * A bar in the bottom-right corner carries five controls:
 *
 *   Zen       hide the menu bar, tab bar, notebook toolbar, sidebars and status
 *             bar, leaving the document and the table of contents
 *   Focus     dim every cell except the one you are on
 *   Reveal    cells below the reading line are faint and sharpen as you reach
 *             them — reading one paragraph at a time without leaving the notebook
 *   Present   open build.py's deck.html in a new tab (not RISE — see the button)
 *   ?         the key list, on Alt+?, the way reveal answers `?` inside the deck
 *
 * Plus the floating table of contents from toc-layer.js, overlaying the notebook
 * rather than taking one of Lab's dock slots. Alt+Z / Alt+F / Alt+R / Alt+T /
 * Alt+P / Alt+? do the same as the buttons, unless you are typing in a cell.
 *
 * Two things it needs from the way Lab was started, both set by lab.sh:
 *
 *   windowingMode "defer"      every cell in the DOM. Lab's default, "full",
 *                              keeps only the ~17 around the viewport attached,
 *                              which would give a two-entry table of contents.
 *   --expose-app-in-browser    window.jupyterapp, so zen can call Lab's own
 *                              commands. Lumino positions the panels absolutely,
 *                              so CSS that collapses one leaves its gap behind;
 *                              only a real command relayouts. Without the flag
 *                              zen falls back to that imperfect CSS.
 *
 * Zen deliberately does not persist across a reload. Lab remembers its own
 * chrome state in the workspace, so a notebook that came back untrusted — with
 * this script never running — would leave you in a Lab with no menu bar and no
 * way to bring it back. A localStorage receipt covers the case where the script
 * does run but the page died mid-zen; an untrusted notebook is still unreachable.
 * Focus and reveal are pure styling and do persist.
 */
(function () {
  'use strict';
  if (window.__nbdocLab) { window.__nbdocLab.refresh(); return; }

  // Only in a live notebook host. build.py's static exports ship this same cell
  // output but wire their own copy of toc-layer.js at the page level, so running
  // here too would build the nav twice.
  if (!document.querySelector('.jp-LabShell, .jp-WindowedPanel-outer, #rendered_cells')) return;
  // RISE builds its deck inside Lab's own notebook widget, so the check above
  // matches a slideshow too. A deck is not a document to navigate, and the table
  // of contents would pad its scroller and shift every slide 272px right.
  if (/\/rise\//.test(location.pathname) || document.body.classList.contains('rise-enabled')) return;

  var body = document.body;
  body.classList.add('nbdoc-live');
  var LS = 'nbdoc-lab:' + (location.pathname || 'doc');
  var app = window.jupyterapp || null;

  // Which element scrolls the document depends on the host. JupyterLab puts the
  // notebook in its own scroller; Voila renders the same cells into #rendered_cells;
  // a plain nbconvert page just scrolls the window. All three render the same
  // .jp-Notebook, so everything else here is host-agnostic.
  function scroller() {
    return document.querySelector('.jp-WindowedPanel-outer')
        || document.getElementById('rendered_cells')
        || document.scrollingElement;
  }
  function isDocScroller(sc) { return sc === document.scrollingElement; }
  function cells() { return document.querySelectorAll('.jp-Notebook .jp-Cell'); }
  // Lab chrome to hide. Absent in Voila and in an exported page, where zen has
  // nothing to do and the button is not offered.
  function hasChrome() { return !!document.querySelector('#jp-top-panel, .jp-NotebookPanel-toolbar'); }
  function visible(sel) {
    var e = document.querySelector(sel);
    return !!(e && e.offsetHeight > 0 && e.offsetParent !== null);
  }
  function run(cmd, args) { try { return app.commands.execute(cmd, args || {}); } catch (e) {} }

  // ------------------------------------------------------------ panel edges
  // The table of contents anchors to the notebook panel, not to the window, so
  // it never covers Lab's menu bar. Zen collapses that chrome, the panel grows,
  // and the nav follows it to full height without knowing anything about zen.
  // Left and right too: the nav sits at the panel's left edge and the mode bar
  // at its right, so opening Lab's file browser moves the nav over instead of
  // leaving it underneath, and a right sidebar does the same for the bar.
  function measure() {
    var p = document.querySelector('.jp-NotebookPanel');
    var r = p ? p.getBoundingClientRect() : null;
    var s = document.documentElement.style;
    // Behind Lab's splash, and in a tab Lab has not laid out yet, the panel is
    // 0x0 at (0,0). Taking that literally puts the nav's bottom edge at the top
    // of the window and the mode bar 2500px off the left. Wait for a real box.
    if (!r || !r.width || !r.height) return;
    s.setProperty('--nbdoc-top', Math.max(0, r.top) + 'px');
    s.setProperty('--nbdoc-bottom', Math.max(0, window.innerHeight - r.bottom) + 'px');
    s.setProperty('--nbdoc-left', Math.max(0, r.left) + 'px');
    s.setProperty('--nbdoc-right', Math.max(0, window.innerWidth - r.right) + 'px');
  }
  function remeasure() { for (var i = 0; i <= 8; i++) setTimeout(measure, i * 40); }
  measure();
  window.addEventListener('resize', measure);
  setInterval(measure, 1000);   // anything else that resizes the panel
  // A sidebar opening resizes the notebook panel in the same frame, and a
  // ResizeObserver on it is what makes the nav move with the sidebar instead of
  // up to a second later. The panel may not exist yet when this runs; keep
  // trying until it does.
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(remeasure);
    var watching = null;
    var watch = function () {
      var p = document.querySelector('.jp-NotebookPanel');
      if (p && p !== watching) { ro.observe(p); watching = p; }
      var dock = document.getElementById('jp-main-dock-panel');
      if (dock && !watch.dock) { ro.observe(dock); watch.dock = true; }
    };
    [0, 1000, 3000, 8000].forEach(function (ms) { setTimeout(watch, ms); });
  }

  // ---------------------------------------------------------------- dock slot
  // toc-layer.js asks whoever owns the layout to make room for a docked sidebar.
  // In a plain page that means a margin on #content. Here the notebook lives in
  // a scroller Lab sizes itself, so padding on the scroller is what moves the
  // text without giving the panel a horizontal scrollbar. Defined before
  // toc-layer.js loads, because it only creates its own if none exists.
  window.__dockLayout = window.__dockLayout || {
    set: function (side, px) {
      var sc = scroller();
      if (!sc || side !== 'left') return;
      sc.style.paddingLeft = px ? (px + 24) + 'px' : '';
    }
  };

  // -------------------------------------------------------------------- zen
  // Every piece of chrome is a Lumino widget, and Lumino gives each one an
  // absolute position — so CSS that collapses a panel leaves its gap behind and
  // only hide()/show() or a Lab command actually relayouts.
  //
  // The panels hang off the shell's own layout. Which ones exist depends on the
  // mode: switching to single-document moves the menu out of #jp-top-panel and
  // into #jp-menu-panel, so the mode has to change first and the panels are
  // read after. Every state is recorded before anything moves and put back
  // verbatim on the way out, so zen never turns on a panel the reader had
  // closed themselves.
  var PANELS = ['jp-top-panel', 'jp-menu-panel', 'jp-bottom-panel'];
  var zenSaved = null;
  var ZEN_LS = LS + ':zen-open';

  function panels() {
    try { return Array.from(app.shell.layout.widgets); } catch (e) { return []; }
  }
  function panel(id) {
    return panels().filter(function (w) { return w.node && w.node.id === id; })[0];
  }

  function zen(on) {
    if (!app) { body.classList.toggle('nbdoc-zen-css', on); remeasure(); return; }
    var sh = app.shell, w = sh.currentWidget, tb = w && w.toolbar;
    if (on) {
      if (!zenSaved) {
        zenSaved = {
          mode: sh.mode,
          status: visible('#jp-main-statusbar'),
          rail: visible('.jp-SideBar'),
          toolbar: !!(tb && !tb.isHidden),
          panels: {}
        };
        PANELS.forEach(function (id) { var p = panel(id); if (p) zenSaved.panels[id] = !p.isHidden; });
      }
      // Written before anything is hidden and cleared only by a clean exit, so
      // a page that dies while zen is on leaves the receipt behind. See zenCrash.
      try { localStorage.setItem(ZEN_LS, JSON.stringify(zenSaved)); } catch (e) {}
      if (sh.mode !== 'single-document') run('application:set-mode', { mode: 'single-document' });
      PANELS.forEach(function (id) { var p = panel(id); if (p) p.hide(); });
      if (zenSaved.status) run('statusbar:toggle');
      if (zenSaved.rail) { run('application:toggle-side-tabbar', { side: 'left' });
                           run('application:toggle-side-tabbar', { side: 'right' }); }
      if (tb) tb.hide();
    } else if (zenSaved) {
      if (sh.mode !== zenSaved.mode) run('application:set-mode', { mode: zenSaved.mode });
      PANELS.forEach(function (id) {
        var p = panel(id);
        if (p) zenSaved.panels[id] ? p.show() : p.hide();
      });
      if (zenSaved.status && !visible('#jp-main-statusbar')) run('statusbar:toggle');
      if (zenSaved.rail && !visible('.jp-SideBar')) {
        run('application:toggle-side-tabbar', { side: 'left' });
        run('application:toggle-side-tabbar', { side: 'right' });
      }
      if (tb && zenSaved.toolbar) tb.show();
      zenSaved = null;
      try { localStorage.removeItem(ZEN_LS); } catch (e) {}
    }
    remeasure();
  }
  // Lab remembers its chrome in the workspace. Put it back before the page goes,
  // or a reload that does not run this script leaves a Lab with no menu bar.
  window.addEventListener('beforeunload', function () {
    if (body.classList.contains('nbdoc-zen')) zen(false);
  });

  // beforeunload does not fire when the server is killed, the tab crashes or the
  // browser is force-quit — and Lab has already written left.visible false and
  // top.simpleVisibility false into its workspace by then, so the next open is a
  // Lab with no menu bar, no side rail, and no zen button to press because zen
  // reads as off. The receipt in localStorage outlives all three, so a load that
  // finds one knows the last session ended mid-zen and puts the chrome back.
  function zenCrash() {
    var raw = null;
    try { raw = localStorage.getItem(ZEN_LS); } catch (e) {}
    if (!raw) return;
    try { zenSaved = JSON.parse(raw); } catch (e) { zenSaved = null; }
    try { localStorage.removeItem(ZEN_LS); } catch (e) {}
    if (zenSaved && app) zen(false);
  }

  // ---------------------------------------------------------------- reveal
  // Every cell is in the DOM under windowingMode "defer", so a scroll handler
  // that measured all 498 of them would be the slowest thing on the page. An
  // IntersectionObserver keeps a small live set of cells near the viewport and
  // only those get their opacity written, once per animation frame.
  var reveal = (function () {
    var near = new Set(), io = null, raf = 0, sc = null, running = false;

    function paint() {
      raf = 0;
      if (!running || !sc) return;
      var cs = getComputedStyle(document.documentElement);
      var doc = isDocScroller(sc);
      var h = doc ? window.innerHeight : sc.clientHeight;
      var line = h * (parseFloat(cs.getPropertyValue('--nbdoc-line')) || 0.42);
      var floor = parseFloat(cs.getPropertyValue('--nbdoc-reveal-floor'));
      if (isNaN(floor)) floor = 0.14;
      var top = doc ? 0 : sc.getBoundingClientRect().top;
      near.forEach(function (el) {
        var y = el.getBoundingClientRect().top - top;   // cell top, in scroller space
        var o = 1;
        if (y > line) {
          // full at the reading line, falling to the floor by the bottom of the
          // viewport and staying there for anything further down
          var t = (h - y) / Math.max(1, h - line);
          o = floor + (1 - floor) * Math.max(0, Math.min(1, t));
        }
        el.style.opacity = o.toFixed(3);
      });
    }
    function tick() { if (!raf) raf = requestAnimationFrame(paint); }

    return {
      start: function () {
        if (running) return;
        sc = scroller();
        if (!sc) return;
        running = true;
        // root:null means the viewport, which is what an IntersectionObserver
        // wants when the document itself is the thing that scrolls.
        io = new IntersectionObserver(function (entries) {
          entries.forEach(function (en) {
            if (en.isIntersecting) near.add(en.target);
            else { near.delete(en.target); en.target.style.opacity = ''; }
          });
          tick();
        }, { root: isDocScroller(sc) ? null : sc, rootMargin: '40% 0px 120% 0px' });
        Array.prototype.forEach.call(cells(), function (c) { io.observe(c); });
        (isDocScroller(sc) ? window : sc).addEventListener('scroll', tick, { passive: true });
        window.addEventListener('resize', tick);
        tick();
      },
      stop: function () {
        running = false;
        if (io) { io.disconnect(); io = null; }
        if (sc) (isDocScroller(sc) ? window : sc).removeEventListener('scroll', tick);
        window.removeEventListener('resize', tick);
        near.clear();
        Array.prototype.forEach.call(cells(), function (c) { c.style.opacity = ''; });
      },
      restart: function () { if (running) { this.stop(); this.start(); } }
    };
  })();

  // ---------------------------------------------------------------- mode bar
  // Zen only appears where there is chrome to hide. Voila and an exported page
  // render the same document with no Lab around it, and a button that does
  // nothing is worse than a missing one.
  var MODES = [
    { key: 'zen',    label: 'Zen',    code: 'KeyZ', persist: false, when: hasChrome,
      title: 'Hide Lab’s chrome (Alt+Z)', on: zen },
    { key: 'focus',  label: 'Focus',  code: 'KeyF', persist: true,
      title: 'Dim every cell except the one you are on (Alt+F)' },
    { key: 'reveal', label: 'Reveal', code: 'KeyR', persist: true,
      title: 'Fade the cells you have not reached yet (Alt+R)',
      on: function (v) { v ? reveal.start() : reveal.stop(); } }
  ].filter(function (m) { return !m.when || m.when(); });

  var bar = document.createElement('div');
  bar.className = 'nbdoc-bar';
  bar.setAttribute('role', 'group');
  bar.setAttribute('aria-label', 'Reading modes');

  var buttons = {};
  MODES.forEach(function (m, i) {
    if (i) bar.appendChild(sep());
    var b = document.createElement('button');
    b.type = 'button'; b.textContent = m.label; b.title = m.title;
    b.setAttribute('aria-pressed', 'false');
    b.addEventListener('click', function () { toggle(m.key); });
    buttons[m.key] = b; bar.appendChild(b);
  });
  // ------------------------------------------------------------------ present
  // Present opens build.py's deck, not RISE. RISE 0.43 deletes 17 of reveal's
  // keybindings (up, down, N, P, H, J, K, L, Esc, O, B, F, Home, End and more)
  // and rebuilds a smaller set as Lab commands, and it copies only eleven keys
  // out of the notebook's `rise` metadata into the Reveal config — a list that
  // does not include navigationMode. With h2 as a slide and h3 as a subslide
  // that leaves the vertical axis with no key at all, and the arrow that still
  // works walks the h2 sections while skipping every h3 under them. None of it
  // is reachable from the notebook, so the fix is to present the file we do
  // configure. The deck is a build artifact, so it shows the last build, not
  // the cell you just typed.
  // Only Lab's own /lab/tree/<path>.ipynb route, because that is the one whose
  // folder the server also publishes under /files/. Voila and build.py's static
  // exports run this same script and have no deck to point at.
  var nbRoute = decodeURIComponent(location.pathname || '')
                  .match(/\/(?:lab|doc)(?:\/workspaces\/[^/]+)?\/tree\/(.*\/)?([^/]+)\.ipynb$/);
  var nbDir = nbRoute ? (nbRoute[1] || '') : '';
  var nbStem = nbRoute ? nbRoute[2] : '';
  // Mirrors deck_name() in build.py. The two have to agree or Present 404s.
  var deckName = !nbStem ? null
    : (nbStem === 'doc' || nbStem.indexOf('doc_') === 0)
      ? 'deck' + nbStem.slice(3) + '.html'
      : nbStem + '-deck.html';

  // Two routes reach the same file, and they do not behave the same. Lab serves
  // /files/ with `Content-Security-Policy: … sandbox allow-scripts`, which puts
  // the page on an opaque origin: window.open returns null, so reveal's `s`
  // speaker view does nothing, and localStorage throws on read. lab.sh runs a
  // plain http.server over this same folder on the next port up, which is an
  // ordinary origin where both work. Prefer it, and keep /files/ for the Lab
  // someone started by hand.
  function deckPath() { return deckName ? nbDir + deckName : null; }

  function filesUrl() {
    return deckName ? location.origin + '/files/' + deckPath() : null;
  }

  function staticUrl() {
    var port = parseInt(location.port, 10);
    return (deckName && port) ? location.protocol + '//' + location.hostname +
                                ':' + (port + 1) + '/' + deckPath() : null;
  }

  // Is that server up? A cross-origin HEAD to a plain http.server carries no CORS
  // headers, so nothing about the response can be read — but `no-cors` still
  // resolves when the connection was made and rejects when it was not, and that
  // is the only bit needed. It says nothing about whether the file is there,
  // which is why existence is settled over Lab's own route first.
  function reachable(url) {
    if (!url || !window.fetch) return Promise.reject();
    var ctl = window.AbortController ? new AbortController() : null;
    var t = setTimeout(function () { if (ctl) ctl.abort(); }, 700);
    return fetch(url, { method: 'HEAD', mode: 'no-cors', cache: 'no-store',
                        signal: ctl ? ctl.signal : undefined })
      .then(function () { clearTimeout(t); },
            function (e) { clearTimeout(t); throw e; });
  }

  function openDeck(url) { window.open(url, '_blank', 'noopener'); }

  function present() {
    if (!deckName) return;
    // A missing deck is the normal state of a folder nobody has built yet, and a
    // blank tab explains nothing. Lab's route is same-origin, so its status is
    // readable; ask it whether the file exists, then pick the origin to open.
    fetch(filesUrl(), { method: 'HEAD', credentials: 'same-origin' }).then(function (r) {
      if (!r.ok) {
        pres.textContent = 'run build.py';
        pres.title = deckName + ' does not exist yet. Run `python build.py ' +
                     nbStem + '.ipynb` in the folder, then press Present again.';
        setTimeout(function () { pres.textContent = 'Present'; }, 4000);
        return;
      }
      reachable(staticUrl()).then(function () { openDeck(staticUrl()); },
                                  function () { openDeck(filesUrl()); });
    }).catch(function () { openDeck(filesUrl()); });
  }

  var pres;
  if (deckName) {
    bar.appendChild(sep());
    pres = document.createElement('button');
    pres.type = 'button'; pres.textContent = 'Present';
    pres.title = 'Open ' + deckName + ' — build.py\u2019s reveal.js deck, in a new tab (Alt+P)';
    pres.addEventListener('click', present);
    bar.appendChild(pres);
  }
  bar.appendChild(sep());
  var helpBtn = document.createElement('button');
  helpBtn.type = 'button'; helpBtn.textContent = '?'; helpBtn.className = 'nbdoc-help-btn';
  helpBtn.title = 'The keys (Alt+?)';
  helpBtn.addEventListener('click', function () { showHelp(); });
  bar.appendChild(helpBtn);
  body.appendChild(bar);

  // ------------------------------------------------------------------- help
  // reveal answers `?` inside the deck with its key list; the notebook answers
  // Alt+? with this one. Built on first use, then toggled.
  var HELP = [
    ['Alt', 'T', 'Contents', 'the floating table of contents'],
    ['Alt', 'F', 'Focus',    'dim every cell except the one you are on'],
    ['Alt', 'R', 'Reveal',   'fade the cells you have not reached yet'],
    ['Alt', 'Z', 'Zen',      'hide JupyterLab\u2019s chrome; again to bring it back'],
    ['Alt', 'P', 'Present',  'open the deck in a new tab'],
    ['Alt', '?', 'Keys',     'this list'],
    ['',    'Esc', '',       'close it']
  ];
  var helpEl = null;
  function buildHelp() {
    var wrap = document.createElement('div');
    wrap.className = 'nbdoc-help';
    wrap.setAttribute('role', 'dialog'); wrap.setAttribute('aria-label', 'Keys');
    var card = document.createElement('div'); card.className = 'nbdoc-help-card';
    var h = document.createElement('h2'); h.textContent = 'Keys'; card.appendChild(h);
    var t = document.createElement('table');
    HELP.forEach(function (row) {
      if (row[1] === 'P' && !deckName) return;   // no deck in this folder, no key for it
      var tr = document.createElement('tr');
      var k = document.createElement('td');
      if (row[0]) { var m = document.createElement('kbd'); m.textContent = row[0]; k.appendChild(m); k.appendChild(document.createTextNode(' ')); }
      var key = document.createElement('kbd'); key.textContent = row[1]; k.appendChild(key);
      var d = document.createElement('td');
      if (row[2]) { var b = document.createElement('b'); b.textContent = row[2]; d.appendChild(b); d.appendChild(document.createTextNode(' \u2014 ')); }
      d.appendChild(document.createTextNode(row[3]));
      tr.appendChild(k); tr.appendChild(d); t.appendChild(tr);
    });
    card.appendChild(t);
    var foot = document.createElement('p'); foot.className = 'nbdoc-help-foot';
    foot.textContent = 'None of these fire while you are typing in a cell. Inside the deck, ? lists reveal\u2019s own keys.';
    card.appendChild(foot);
    wrap.appendChild(card);
    wrap.addEventListener('click', function (e) { if (e.target === wrap) showHelp(false); });
    body.appendChild(wrap);
    return wrap;
  }
  function showHelp(on) {
    if (!helpEl) helpEl = buildHelp();
    if (on === undefined) on = !body.classList.contains('nbdoc-help-open');
    body.classList.toggle('nbdoc-help-open', on);
    helpBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
  }
  function sep() { var s = document.createElement('span'); s.className = 'nbdoc-sep'; return s; }

  function set(key, on) {
    var m = MODES.filter(function (x) { return x.key === key; })[0];
    if (!m) return;
    body.classList.toggle('nbdoc-' + key, on);
    buttons[key].setAttribute('aria-pressed', on ? 'true' : 'false');
    if (m.persist) try { localStorage.setItem(LS + ':' + key, on ? '1' : '0'); } catch (e) {}
    if (m.on) m.on(on);
  }
  function toggle(key) { set(key, !body.classList.contains('nbdoc-' + key)); }

  // ------------------------------------------------------------------- keys
  document.addEventListener('keydown', function (e) {
    var typing = e.target && e.target.closest && e.target.closest('.cm-content, input, textarea');
    // Esc goes through to Lab when there is nothing of ours to close.
    if (e.key === 'Escape' && body.classList.contains('nbdoc-help-open')) { showHelp(false); e.preventDefault(); return; }
    if (!e.altKey || e.metaKey || e.ctrlKey) return;
    if (typing) return;
    var m = MODES.filter(function (x) { return x.code === e.code; })[0];
    if (m) { toggle(m.key); e.preventDefault(); return; }
    if (e.code === 'KeyP' && deckName) { present(); e.preventDefault(); return; }
    // Alt+? — a bare `?` is a character people type, so it stays theirs. Match the
    // physical key: on a Mac, Alt+Shift+/ arrives as `¿`, and Alt+/ as `÷`.
    if (e.code === 'Slash') { showHelp(); e.preventDefault(); return; }
    if (e.code === 'KeyT') {
      var open = body.classList.contains('tl-docked') || body.classList.contains('tl-open');
      var el = document.querySelector(open ? '.toc-layer .tl-close' : '.tl-btn');
      if (el) el.click();
      e.preventDefault();
    }
  });

  // ------------------------------------------- table of contents, once loaded
  // toc-layer.js builds itself from the headings it can see, so it has to run
  // after Lab has attached the cells — with "defer" that takes a few seconds on
  // a 500-cell notebook. Injected as a real <script> element so its data-content
  // attribute is readable through document.currentScript, the way it expects.
  function loadToc() {
    var src = document.getElementById('nbdoc-toc-src');
    if (!src || document.querySelector('.toc-layer')) return;
    var s = document.createElement('script');
    s.setAttribute('data-content', '.jp-Notebook');
    s.textContent = src.textContent;
    document.head.appendChild(s);
    // Lab appends a ¶ anchor link inside every rendered heading. lab.css hides it
    // in the document, but the nav takes its labels from textContent, which sees
    // it regardless.
    Array.prototype.forEach.call(document.querySelectorAll('.toc-layer a'), function (a) {
      a.textContent = a.textContent.replace(/\s*¶\s*$/, '');
    });
    // toc-layer bails without a word when it sees fewer than three headings, so a
    // build that ran a moment too early leaves no nav and no way to know why.
    // Retry while the heading count is still climbing.
    if (!document.querySelector('.toc-layer')) {
      if (loadToc.tries === undefined) loadToc.tries = 0;
      if (++loadToc.tries <= 12) setTimeout(loadToc, 1000);
    }
  }

  // How many cells the notebook actually has, as opposed to how many Lab has
  // attached so far. "defer" attaches them in bursts with pauses between, so a
  // count that merely stopped growing for half a second is not the whole
  // document — the first version of this built a 24-entry nav for a 50-heading
  // paper. The model knows the real number; the plateau rule is the fallback
  // for a Lab started without --expose-app-in-browser.
  // `currentWidget` is null whenever nothing in the main area has focus, which is
  // the normal state for a tab that was opened by a URL and never clicked. Losing
  // the real count there drops us onto the plateau rule during Lab's startup
  // pauses, the nav gets built while two headings are attached, and toc-layer's
  // "fewer than 3 headings" guard then silently produces nothing at all. So fall
  // back to the first main-area widget rather than to zero.
  function notebookWidget() {
    try {
      var w = app.shell.currentWidget;
      if (w && w.content && w.content.model) return w;
      var it = app.shell.widgets('main'), x = it.next();
      while (!x.done) {
        if (x.value && x.value.content && x.value.content.model) return x.value;
        x = it.next();
      }
    } catch (e) {}
    return null;
  }

  function total() {
    var w = notebookWidget();
    try { return w.content.model.cells.length; } catch (e) { return 0; }
  }

  function whenSettled(done) {
    var last = -1, same = 0, tries = 0;
    var t = setInterval(function () {
      var n = cells().length, want = total();
      if (want && n >= want) { clearInterval(t); done(); return; }
      if (n === last && n > 2) { if (++same >= 6) { clearInterval(t); done(); return; } }
      else { same = 0; last = n; }
      if (++tries > 240) { clearInterval(t); done(); }   // 60s cap, then take what we have
    }, 250);
  }

  window.__nbdocLab = {
    set: set, toggle: toggle, reveal: reveal, measure: measure,
    refresh: function () { loadToc(); reveal.restart(); measure(); }
  };

  whenSettled(function () {
    zenCrash();
    loadToc();
    measure();
    MODES.forEach(function (m) {
      if (!m.persist) return;
      var v = null;
      try { v = localStorage.getItem(LS + ':' + m.key); } catch (e) {}
      if (v === '1') set(m.key, true);
    });
  });
})();
