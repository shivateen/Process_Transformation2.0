/* Stage 3 · Build — Action Block Configuration (BPT integration layer)
 * Two sub-views:
 *   workshop  — the Block Workshop: every action block in the composition, its
 *               technology-fitment mix, and whether it is decomposed.
 *   blueprint — the Activity Blueprint: one block decomposed into concrete
 *               activities with SIPOC, fitment, and optimization opportunities.
 * Reads window.PROCESSIQ_BUILD (build.json). ES5 / IIFE, mirrors the other modules. */
(function () {
  "use strict";
  var BUILD = window.PROCESSIQ_BUILD;
  var decomps = BUILD ? BUILD.decompositions : {};

  var selectedBlock = null;   // block key currently inspected
  var showOptimized = false;  // as-is vs optimized
  var sipocOpen = {};         // seq -> bool

  function el(t, c, h) { var n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; }
  function esc(s) { return (s == null ? "" : String(s)).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function C() { return window.PIQ.composition; }

  var FIT = {
    agentic: { cls: "agentic", label: "Agentic AI", color: "#27ae60" },
    workflow: { cls: "workflow", label: "Workflow", color: "#e67e22" },
    rpa: { cls: "rpa", label: "RPA / Rule-based", color: "#2980b9" },
    manual: { cls: "manual", label: "Manual", color: "#c0392b" }
  };
  var ORDER = ["agentic", "workflow", "rpa", "manual"];

  // tally activities by fitment across a set of block keys
  function fitCounts(keys) {
    var c = { agentic: 0, workflow: 0, rpa: 0, manual: 0 }, total = 0;
    keys.forEach(function (k) {
      var d = decomps[k]; if (!d) return;
      d.activities.forEach(function (a) { if (c[a.fitment] != null) { c[a.fitment]++; total++; } });
    });
    return { c: c, total: total };
  }

  /* ================= Sub-view 1 · Block Workshop ================= */
  function renderWorkshop(view) {
    if (!C().patternIds.length) { view.appendChild(emptyWorkshop()); return; }
    var blocks = window.PIQ.collectBlocks(C().patternIds);
    var keys = blocks.map(function (b) { return b.key; });
    var fc = fitCounts(keys);
    var decomposed = blocks.filter(function (b) { return decomps[b.key]; }).length;
    var autoPct = fc.total ? Math.round(100 * (fc.c.agentic + fc.c.rpa) / fc.total) : 0;
    var agenticPct = fc.total ? Math.round(100 * fc.c.agentic / fc.total) : 0;
    var f = window.PIQ.fn(), p = window.PIQ.proc();

    var root = el("div", "build");
    root.appendChild(el("div", "build-head",
      '<div class="kv">Stage 3 · Build — Action Block Configuration</div>' +
      '<h2>' + esc(f ? f.name : "") + ' <span style="color:var(--muted)">›</span> ' + esc(p ? p.name : "") + '</h2>' +
      '<p>Each action block is an abstract operation in the pattern library. Build decomposes it into concrete ' +
      'activities with SIPOC, assigns technology, and optimizes the workflow.</p>' +
      '<div class="build-kpis">' + bkpi(blocks.length, "blocks") + bkpi(decomposed, "decomposed") +
      bkpi(autoPct + "%", "automatable") + '</div>'));

    root.appendChild(distBar(fc));

    var grid = el("div", "build-grid");
    blocks.forEach(function (b) { grid.appendChild(blockCard(b)); });
    root.appendChild(grid);

    var gl = el("div", "build-golive",
      '<div><b>Ready to operate.</b> ' + decomposed + ' blocks decomposed across ' + fc.total + ' activities. ' +
      agenticPct + '% of activities can run as Agentic AI.</div>' +
      '<button class="btn go" id="bPromote">Promote to Runtime →</button>');
    root.appendChild(gl);
    view.appendChild(root);

    var pb = document.getElementById("bPromote");
    if (pb) pb.onclick = function () {
      C().live = true;
      if (window.PIQ.persistComposition) window.PIQ.persistComposition();
      window.PIQ.go("runtime");
    };
  }

  function bkpi(v, l) { return '<div class="bkpi"><b>' + v + '</b><span>' + l + '</span></div>'; }

  function distBar(fc) {
    var bar = ORDER.map(function (k) {
      var n = fc.c[k];
      return n ? '<i style="flex:' + n + ';background:' + FIT[k].color + '" title="' + FIT[k].label + '"></i>' : "";
    }).join("");
    var legend = ORDER.map(function (k) {
      return '<span><i style="background:' + FIT[k].color + '"></i>' + FIT[k].label + ' · <b>' + fc.c[k] + '</b></span>';
    }).join("");
    return el("div", "bpt-dist",
      '<div class="bd-h">Technology fitment across ' + fc.total + ' activities</div>' +
      '<div class="bd-bar">' + bar + '</div><div class="bd-legend">' + legend + '</div>');
  }

  function blockCard(block) {
    var d = decomps[block.key];
    var card = el("div", "build-block" + (d ? " decomposed" : ""));
    var fit = window.PIQ.fitment(block);
    var srcCls = block.source === "happy" ? "happy" : "vary";
    var srcLbl = block.source === "happy" ? "happy path" : "variation";
    var html =
      '<div class="bb-name">' + esc(window.PIQ.prettify(block.key)) + '</div>' +
      '<div class="bb-key">' + esc(block.key) + '</div>' +
      '<div class="bb-row"><span class="bb-src ' + srcCls + '"></span>' + srcLbl +
      '<span class="bpt-fit" style="margin-left:auto;background:#f3eef8;color:#6d4b9c">' + esc(fit.tier) + '</span></div>';
    if (d) {
      var fc = fitCounts([block.key]);
      var bar = ORDER.map(function (k) { var n = fc.c[k]; return n ? '<i style="flex:' + n + ';background:' + FIT[k].color + '"></i>' : ""; }).join("");
      html +=
        '<div class="bb-acts">' + d.activities.length + ' activities · ' + d.optimized.automationRate + '% automatable</div>' +
        '<div class="bb-minibar">' + bar + '</div>' +
        '<div class="bb-row"><span class="bb-status ready">Decomposed</span>' +
        '<span class="bb-link" style="margin-left:auto">View Blueprint →</span></div>';
      card.onclick = function () { selectedBlock = block.key; showOptimized = false; sipocOpen = {}; window.PIQ.go("blueprint"); };
    } else {
      html +=
        '<div class="bb-acts">Awaiting BPT decomposition</div>' +
        '<div class="bb-row"><span class="bb-status pending">Pending</span></div>';
      card.style.cursor = "default";
    }
    card.innerHTML = html;
    return card;
  }

  function emptyWorkshop() {
    var d = el("div", "build-empty",
      '<div class="kv">Stage 3 · Build</div><h2>Nothing to build yet</h2>' +
      '<p>Compose a process in the <b>Studio</b> and run it through <b>Discover &amp; Fit</b>. ' +
      'Its action blocks are decomposed into executable activity blueprints here.</p>' +
      '<button class="btn go" id="toStudioB">← Go to Studio</button>');
    d.querySelector("#toStudioB").onclick = function () { window.PIQ.go("studio"); };
    return d;
  }

  /* ================= Sub-view 2 · Activity Blueprint ================= */
  function renderBlueprint(view) {
    if (!selectedBlock || !decomps[selectedBlock]) { view.appendChild(emptyBlueprint()); return; }
    var d = decomps[selectedBlock];
    var blocks = window.PIQ.collectBlocks(C().patternIds);
    var block = blocks.filter(function (b) { return b.key === selectedBlock; })[0] || null;

    var root = el("div", "bp");
    var back = el("span", "bp-back", "← Back to Workshop");
    back.onclick = function () { window.PIQ.go("workshop"); };
    root.appendChild(back);

    var srcLbl = block ? (block.source === "happy" ? "Happy path" : "Variation") : "";
    root.appendChild(el("div", "bp-head",
      '<h2>' + esc(d.label) + '</h2>' +
      '<div class="bp-meta"><span class="bpt-fit" style="background:#efeae1;color:var(--brand)">' + esc(d.category) + '</span>' +
      (srcLbl ? '<span>' + srcLbl + '</span>' : "") + '<span>' + d.activities.length + ' activities</span></div>'));

    var tb = el("div", "bp-togglebar",
      '<button data-o="0" class="' + (!showOptimized ? "on" : "") + '">As-Is Activities</button>' +
      '<button data-o="1" class="' + (showOptimized ? "on" : "") + '">Optimized</button>');
    tb.querySelectorAll("button").forEach(function (btn) {
      btn.onclick = function () {
        showOptimized = btn.getAttribute("data-o") === "1";
        var v = document.getElementById("view"); v.innerHTML = ""; renderBlueprint(v);
      };
    });
    root.appendChild(tb);

    if (showOptimized) root.appendChild(oppPanel(d));
    root.appendChild(flow(d));
    if (showOptimized) root.appendChild(metrics(d));
    root.appendChild(patternsSection(block));

    view.appendChild(root);
    wireBlueprint(root);
  }

  function flow(d) {
    var wrap = el("div", "bp-flow");
    var elim = showOptimized ? (d.optimized.eliminatedSteps || []) : [];
    var n = 0;
    d.activities.forEach(function (a) {
      var isElim = elim.indexOf(a.name) >= 0;
      var fit = FIT[a.fitment] || FIT.agentic;
      var seqNum = isElim ? "×" : (showOptimized ? (++n) : a.seq);
      var open = !!sipocOpen[a.seq];
      var card = el("div", "bp-act" + (isElim ? " eliminated" : ""),
        '<span class="bp-seq ' + (isElim ? "manual" : fit.cls) + '">' + seqNum + '</span>' +
        '<div class="bp-act-top"><div><div class="bp-act-name">' + esc(a.name) +
          (isElim ? ' <span class="bb-status pending">Eliminated</span>' : "") + '</div>' +
          '<div class="bp-act-meta"><span>Role: ' + esc(a.role) + '</span><span>Duration: ' + esc(a.duration) + '</span></div></div>' +
          '<span class="bpt-fit ' + fit.cls + '">' + esc(a.fitmentLabel) + '</span></div>' +
        '<div class="bp-act-reason">' + esc(a.fitmentReason) + '</div>' +
        '<span class="bp-sipoc-toggle" data-sip="' + a.seq + '">⊞ SIPOC</span>' +
        '<div class="bp-sipoc' + (open ? " open" : "") + '" id="sip' + a.seq + '">' + sipocRows(a.sipoc) + '</div>');
      wrap.appendChild(card);
    });
    return wrap;
  }

  function sipocRows(s) {
    var rows = [["S", "Supplier"], ["I", "Input"], ["P", "Process"], ["O", "Output"], ["C", "Customer"]];
    s = s || {};
    return rows.map(function (r) {
      return '<div class="bp-sipoc-row"><span class="bp-sipoc-key">' + r[0] + '</span>' +
        '<span class="bp-sipoc-val"><b>' + r[1] + '</b> — ' + esc(s[r[0]] || "—") + '</span></div>';
    }).join("");
  }

  function oppPanel(d) {
    var opps = d.optimized.opportunities || [];
    var wrap = el("div", "bp-opt", "<h4>Optimization Opportunities</h4>");
    if (!opps.length) {
      wrap.innerHTML += '<div class="bp-opp"><div class="bp-opp-desc">No further optimization opportunities identified — this block is already lean.</div></div>';
      return wrap;
    }
    wrap.innerHTML += opps.map(function (o) {
      return '<div class="bp-opp"><div style="flex:1">' +
        '<div class="bp-opp-type">' + esc(o.label) + '</div>' +
        '<div class="bp-opp-desc">' + esc(o.description) + '</div>' +
        '<div class="bp-opp-desc" style="margin-top:4px">Lever: <b>' + esc(o.lever) + '</b></div></div>' +
        '<span class="bp-opp-impact ' + esc(o.impact) + '">' + esc(o.impact) + '</span></div>';
    }).join("");
    return wrap;
  }

  function metrics(d) {
    var asIs = d.asIsStepCount, opt = d.optimized.stepCount;
    var red = asIs ? Math.round(100 * (asIs - opt) / asIs) : 0;
    return el("div", "bp-metrics",
      metric(asIs + " → " + opt, "Steps (" + (red > 0 ? "−" + red + "%" : "no change") + ")") +
      metric(d.asIsAutomationRate + "% → " + d.optimized.automationRate + "%", "Automation rate"));
  }
  function metric(v, l) { return '<div class="bp-metric"><b>' + v + '</b><span>' + l + '</span></div>'; }

  function patternsSection(block) {
    var ids = block ? block.patterns : [];
    var wrap = el("div", "bp-pats", '<h4>Used by ' + ids.length + ' pattern' + (ids.length !== 1 ? "s" : "") + '</h4>');
    var pills = ids.map(function (id) {
      var p = window.PIQ.pattern(id);
      return '<span class="bp-pat-pill" data-pat="' + id + '">#' + id + (p ? " " + esc(p.name) : "") + '</span>';
    }).join("");
    wrap.appendChild(el("div", null, pills));
    return wrap;
  }

  function wireBlueprint(root) {
    root.querySelectorAll("[data-sip]").forEach(function (t) {
      t.onclick = function () {
        var id = t.getAttribute("data-sip");
        sipocOpen[id] = !sipocOpen[id];
        var pane = document.getElementById("sip" + id);
        if (pane) pane.classList.toggle("open");
      };
    });
    root.querySelectorAll(".bp-pat-pill").forEach(function (pill) {
      pill.onclick = function () {
        var id = +pill.getAttribute("data-pat");
        var p = window.PIQ.pattern(id), book = window.PIQ.book;
        if (p && book) {
          var iv = (book.invoices || []).filter(function (x) { return x.groundTruthFeature === p.featureSlug; })[0];
          if (iv) window.PIQ._jumpInvoice = iv.belnr;
        }
        window.PIQ.go("cockpit");
      };
    });
  }

  function emptyBlueprint() {
    var d = el("div", "bp-empty",
      '<h2>No block selected</h2>' +
      '<p>Select an action block from the <b>Block Workshop</b> to view its activity blueprint.</p>' +
      '<button class="btn go" id="toWorkshop">← Back to Workshop</button>');
    d.querySelector("#toWorkshop").onclick = function () { window.PIQ.go("workshop"); };
    return d;
  }

  /* ---- module registration ---- */
  window.PIQ.modules.workshop = { render: function (view) { view.innerHTML = ""; renderWorkshop(view); } };
  window.PIQ.modules.blueprint = { render: function (view) { view.innerHTML = ""; renderBlueprint(view); } };
  window.PIQ.onErp(function () {
    var v = document.getElementById("view");
    if (window.PIQ.active === "workshop") { v.innerHTML = ""; renderWorkshop(v); }
    else if (window.PIQ.active === "blueprint") { v.innerHTML = ""; renderBlueprint(v); }
  });
})();
