/* ProcessIQ — Executive Themes (Run & Govern sub-view)
 * The CFO-level rollup: flat per-process KPIs (roi.json) composed into outcome
 * themes (themes.json). Each theme shows its composite KPI (before→after + delta),
 * an expandable breakdown of the contributing function KPIs, and the patterns that
 * drive it as clickable pills that deep-link to the Cognitive Cockpit. */
(function () {
  "use strict";
  var E = window.ProcessIQEngine;
  var THEMES = (window.PROCESSIQ_THEMES && window.PROCESSIQ_THEMES.themes) || [];
  var book = window.PIQ.book;

  var expanded = {};   // themeId -> bool (breakdown open?)

  function money(x) { return E._money(x); }
  function el(t, c, h) { var n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; }
  function esc(s) { return (s == null ? "" : String(s)).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function pat(id) { return window.PIQ.pattern ? window.PIQ.pattern(id) : null; }

  var FN_COLOR = { o2c: "var(--brand2)", p2p: "#7c4dff", sc: "#0aa3a3", credit: "#c0392b" };
  function fnColor(id) { return FN_COLOR[id] || "var(--sense)"; }

  function render(view) {
    view.innerHTML = '<div class="roi"><div class="themes-view"></div></div>';
    var root = view.querySelector(".themes-view");
    root.appendChild(el("div", "gov-head themes-head",
      '<div class="kv">The Executive Layer · KPIs roll up to outcomes</div>' +
      '<h2 style="font-size:22px;margin:2px 0 4px">Executive Themes</h2>' +
      '<p style="margin:0;color:var(--muted);max-width:820px">A CFO doesn\'t steer by DSO and DPO separately — they steer by outcomes. ' +
      'Each theme composes per-process KPIs across functions into one number, and every one traces back to the patterns that move it.</p>'));

    if (!THEMES.length) {
      root.appendChild(el("div", "modstub-card", "<p>No executive themes configured.</p>"));
      return;
    }
    THEMES.forEach(function (t) { root.appendChild(themeCard(t)); });
    wire(root);
  }

  function themeCard(t) {
    var card = el("div", "theme-card");
    card.setAttribute("data-theme", t.id);
    var k = (t.themeKPIs || [])[0] || {};
    var open = !!expanded[t.id];

    // composite delta — signed change of the metric, coloured by whether it's an improvement
    var goodDir = k.unit === "%" ? "up" : "down";     // %/rate: higher better; days/index: lower better
    var before = k.compositeBefore, after = k.compositeAfter;
    var base = Math.abs(before) || 1;
    var rawChange = Math.round((after - before) / base * 100);
    var good = goodDir === "down" ? (after < before) : (after > before);
    var deltaLabel = (rawChange >= 0 ? "+" : "−") + Math.abs(rawChange) + "%";

    var comps = (k.components || []).map(function (c) {
      var arrow = c.after < c.before ? "↓" : (c.after > c.before ? "↑" : "→");
      return '<div class="theme-comp-row">' +
        '<span class="theme-comp-fn">' + esc(c.kpiId) + ' <span class="muted" style="font-weight:500">' + esc(c.functionName) + '</span></span>' +
        '<div class="theme-comp-bar"><div class="theme-comp-fill" style="width:' + Math.round((c.weight || 0) * 100) + '%;background:' + fnColor(c.functionId) + '"></div></div>' +
        '<span class="theme-comp-val">' + esc(c.before) + ' → ' + esc(c.after) + ' ' + arrow +
        ' <span class="muted">· ' + Math.round((c.weight || 0) * 100) + '%</span></span>' +
        '</div>';
    }).join("");

    var pills = (k.patternContributors || []).map(function (id) {
      var p = pat(id);
      return '<span class="theme-pat-pill" data-pat="' + id + '" title="Open in the Cognitive Cockpit">#' + id +
        (p ? " " + esc(p.name) : "") + '</span>';
    }).join("");

    card.innerHTML =
      '<div class="theme-name"><span class="theme-icon">' + esc(t.icon || "◆") + '</span>' + esc(t.name) + '</div>' +
      '<div class="theme-q">' + esc(t.executiveQuestion) + '</div>' +
      '<div class="theme-kpi">' +
        '<span class="theme-kpi-name">' + esc(k.name) + ' <span class="theme-formula">' + esc(k.formula) + '</span></span>' +
        '<span class="kpi-val">' + esc(before) + ' → ' + esc(after) + ' <small style="font-size:14px;color:var(--muted)">' + esc(k.unit) + '</small></span>' +
        '<span class="kpi-delta ' + (good ? "good" : "bad") + '">' + deltaLabel + '</span>' +
      '</div>' +
      '<button class="theme-toggle" data-toggle="' + t.id + '">' + (open ? "▾ Hide breakdown" : "▸ Show breakdown") + '</button>' +
      '<div class="theme-components" style="' + (open ? "" : "display:none") + '">' +
        comps +
        '<div class="theme-patterns">' + pills + '</div>' +
      '</div>' +
      '<div class="theme-impact">Annual impact <b>' + money(t.annualImpact) + '</b></div>';
    return card;
  }

  function wire(root) {
    root.querySelectorAll("[data-toggle]").forEach(function (b) {
      b.onclick = function () {
        var id = b.getAttribute("data-toggle");
        expanded[id] = !expanded[id];
        // re-render just this card
        var view = document.getElementById("view");
        render(view);
      };
    });
    root.querySelectorAll(".theme-pat-pill").forEach(function (pill) {
      pill.onclick = function () {
        var id = +pill.getAttribute("data-pat");
        var p = pat(id);
        // deep-link to the cockpit: preselect an invoice that triggers this pattern
        if (p && book) {
          var iv = (book.invoices || []).filter(function (x) { return x.groundTruthFeature === p.featureSlug; })[0];
          if (iv) window.PIQ._jumpInvoice = iv.belnr;
        }
        window.PIQ.go("cockpit");
      };
    });
  }

  window.PIQ.modules.themes = { render: render };
})();
