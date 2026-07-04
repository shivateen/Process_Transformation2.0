/* ProcessIQ — Cognitive Cockpit (Module 3)
 * Renders the Sense->Diagnose->Decide->Act loop + three-layer brain + action DAG
 * for the selected invoice. Registers with the shell as PIQ.modules.cockpit. */
(function () {
  "use strict";
  var E = window.ProcessIQEngine;
  var patterns = window.PIQ.patterns;
  var meta = window.PIQ.meta;
  var book = window.PIQ.book;
  var selected = null;
  var PRIO_COLOR = meta.priorityLegend;

  function erp() { return window.PIQ.erp; }
  function money(x) { return E._money(x); }
  function el(tag, cls, html) { var n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; }
  function risk(iv) {
    if (!iv.groundTruthFeature) return null;
    var p = patterns.filter(function (x) { return x.featureSlug === iv.groundTruthFeature; })[0];
    return p ? p.priority : "Medium";
  }

  /* ---------- worklist ---------- */
  function renderList() {
    var list = document.getElementById("invList");
    if (!list) return;
    list.innerHTML = "";
    var sorted = book.invoices.slice().sort(function (a, b) {
      var ra = E.run(a, patterns).diagnosis, rb = E.run(b, patterns).diagnosis;
      return (rb.confidence - ra.confidence) || (b.amount - a.amount);
    });
    sorted.forEach(function (iv) {
      var r = E.run(iv, patterns).diagnosis;
      var pr = risk(iv);
      var node = el("div", "inv" + (selected && selected.belnr === iv.belnr ? " sel" : ""));
      var pill = pr ? '<span class="riskpill" style="background:' + PRIO_COLOR[pr] + '">' + pr + '</span>'
        : '<span class="riskpill clean">Clean</span>';
      node.innerHTML =
        '<div class="r1"><span class="cust">' + iv.customer + '</span><span class="amt">' + money(iv.amount) + '</span></div>' +
        '<div class="r2"><span class="mono">' + iv.invoiceId + ' · ' + iv.terms + '</span><span class="dpd">' + iv.dpd + ' DPD</span></div>' +
        '<div class="r2" style="margin-top:6px">' + pill +
        (r.fired ? '<span class="mono" style="font-size:11px;color:var(--diag)">' + (r.confidence * 100 | 0) + '% ' + r.top.pattern.name + '</span>' : '<span class="mono" style="font-size:11px">no pattern</span>') +
        '</div>';
      node.onclick = function () { selected = iv; renderList(); renderCockpit(); };
      list.appendChild(node);
    });
  }

  /* ---------- confidence gauge (SVG) ---------- */
  function gauge(pct) {
    var r = 34, c = 2 * Math.PI * r, off = c * (1 - pct);
    var col = pct > 0.85 ? "#8e44ad" : pct > 0.6 ? "#d68910" : "#9aa7b5";
    return '<svg class="gauge" width="92" height="92" viewBox="0 0 92 92">' +
      '<circle cx="46" cy="46" r="' + r + '" fill="none" stroke="#eef2f6" stroke-width="9"/>' +
      '<circle cx="46" cy="46" r="' + r + '" fill="none" stroke="' + col + '" stroke-width="9" stroke-linecap="round" ' +
      'stroke-dasharray="' + c + '" stroke-dashoffset="' + off + '" transform="rotate(-90 46 46)"/>' +
      '<text x="46" y="44" text-anchor="middle" font-size="21" font-weight="800" fill="' + col + '">' + (pct * 100 | 0) + '</text>' +
      '<text x="46" y="60" text-anchor="middle" font-size="10" fill="#5d6b7d">% CONF</text></svg>';
  }

  /* ---------- main cockpit ---------- */
  function renderCockpit() {
    var c = document.getElementById("cockpit");
    if (!c) return;
    if (!selected) { c.innerHTML = EMPTY; return; }
    var iv = selected;
    var res = E.run(iv, patterns);
    var d = res.diagnosis, dec = res.decision;
    var pat = d.fired ? d.top.pattern : null;

    c.innerHTML = "";
    var head = el("div", "inv-head");
    head.innerHTML =
      '<div><div class="kv">INVOICE</div><div class="big">' + iv.invoiceId + '</div></div>' +
      kv("Customer", iv.customer + ' <span class="mono" style="color:var(--muted)">' + iv.kunnr + '</span>') +
      kv("Amount", money(iv.amount)) + kv("Terms", iv.terms) +
      kv("Days Past Due", iv.dpd + 'd') + kv("Vertical", iv.vertical);
    c.appendChild(head);

    var loop = el("div", "loop");
    loop.innerHTML =
      stage("sense", "S", "SENSE", d.fired ? '<b>' + d.top.result.features.length + ' signals</b> detected in the transaction record' : 'Scanning event series — <b>no anomaly</b>') +
      stage("diag", "D", "DIAGNOSE", pat ? 'Pattern <b>#' + pat.id + ' — ' + pat.name + '</b> (' + (d.confidence * 100 | 0) + '%)' : 'No behavioural pattern matches') +
      stage("decide", "R", "DECIDE", dec ? 'Counter-strategy: <b>' + tierLabel(dec.branch.tier) + '</b>' + (dec.requiresHITL ? ' · HITL gate' : '') : 'Standard dunning — no intervention') +
      stage("act", "A", "ACT", dec ? '<b>' + countActions(res.actionDAG) + ' actions</b> assembled as a rollback-ready DAG' : 'Monitor only', true);
    c.appendChild(loop);

    if (!d.fired) { c.appendChild(cleanCard(iv)); c.appendChild(note()); animateStages(); return; }

    var grid = el("div", "grid");
    grid.appendChild(brainCard(iv, pat, d));
    var right = el("div"); right.style.display = "flex"; right.style.flexDirection = "column"; right.style.gap = "18px";
    right.appendChild(diagnosisCard(pat, d));
    right.appendChild(decisionCard(pat, dec));
    grid.appendChild(right);
    c.appendChild(grid);

    var actionWrap = el("div"); actionWrap.style.marginTop = "18px";
    actionWrap.appendChild(actionCard(pat, dec, res));
    c.appendChild(actionWrap);
    c.appendChild(note());
    animateStages();
  }

  function kv(k, v) { return '<div><div class="kv">' + k + '</div><b>' + v + '</b></div>'; }
  function stage(s, ic, tag, body, last) {
    return '<div class="stage s-' + s + '"><div class="tag"><span class="ic">' + ic + '</span>' + tag + '</div>' +
      '<div class="body">' + body + '</div>' + (last ? '' : '<span class="arrow">→</span>') + '</div>';
  }
  function tierLabel(t) { return { primary: "Assisted nudge", escalation: "Escalate & enforce", immediate: "Immediate block", default: "Standard action" }[t] || t; }
  function countActions(dag) { var n = 0; dag.forEach(function (s) { n += s.actions.length; }); return n; }
  function animateStages() {
    var st = document.querySelectorAll(".stage");
    st.forEach(function (s, i) { setTimeout(function () { s.classList.add("on"); }, 120 + i * 260); });
  }

  function brainCard(iv, pat, d) {
    var card = el("div", "card");
    card.innerHTML = '<h4><span class="num">B</span>The Three-Layer Semantic Brain</h4>';
    var tables = (erp() === "sap" ? pat.sources.sap : pat.sources.oracle);
    var tchips = tables.map(function (t) { return '<span class="tbl">' + escapeHtml(t) + '</span>'; }).join("");
    var l1 = el("div", "layer");
    l1.innerHTML = '<div class="lh"><span class="ln">1</span>Logical Mapping</div>' +
      '<div class="ld">' + escapeHtml(pat.layer1_logicalMapping) + '</div>' +
      '<div class="tables">' + tchips + '</div>';
    card.appendChild(l1);
    var l2 = el("div", "layer");
    var tl = iv.eventSeries.map(function (e, i) {
      var flag = i === iv.eventSeries.length - 1 ? " flag" : "";
      return '<div class="tl' + flag + '"><div class="d">Day ' + e.day + '</div><div class="l">' + escapeHtml(e.label) + '</div></div>';
    }).join("");
    l2.innerHTML = '<div class="lh"><span class="ln">2</span>Event Series</div>' +
      '<div class="ld">' + escapeHtml(pat.layer2_eventSeries) + '</div>' +
      '<div class="timeline">' + tl + '</div>';
    card.appendChild(l2);
    var l3 = el("div", "layer");
    var rows = d.top.result.features.map(function (ft) {
      return '<div class="fv">' + ft.value + '</div><div><div class="fn">' + ft.name + '</div><div class="fh">' + escapeHtml(ft.hint || "") + '</div></div>';
    }).join("");
    l3.innerHTML = '<div class="lh"><span class="ln">3</span>AI Features — Expert Triggers</div>' +
      '<div class="ld">Pre-calculated triggers that drive cognitive reasoning.</div>' +
      '<div class="feat">' + rows + '</div>';
    card.appendChild(l3);
    return card;
  }

  function diagnosisCard(pat, d) {
    var card = el("div", "card");
    card.innerHTML = '<h4><span class="num">D</span>Diagnosis</h4>';
    var pad = el("div", "pad");
    pad.innerHTML = '<div class="diag-top">' + gauge(d.confidence) +
      '<div class="diag-meta"><div class="pat">#' + pat.id + ' · ' + pat.name + '</div>' +
      '<div class="cat">' + pat.category + '</div>' +
      '<span class="badge" style="background:' + PRIO_COLOR[pat.priority] + '">' + pat.priority + ' priority</span></div></div>' +
      '<div class="mental">“' + escapeHtml(pat.mentalModel) + '”<span class="who">— the 25-year expert\'s reasoning, codified</span></div>';
    card.appendChild(pad);
    return card;
  }

  function decisionCard(pat, dec) {
    var card = el("div", "card");
    card.innerHTML = '<h4><span class="num">R</span>Decision & Governance</h4>';
    var pad = el("div", "pad");
    var tiers = ["primary", "escalation", "immediate"];
    var present = {}; (pat.branchingDAG || []).forEach(function (b) { present[b.tier] = true; });
    var tbar = tiers.filter(function (t) { return present[t]; }).map(function (t) {
      var on = dec.branch.tier === t;
      return '<div class="t' + (on ? " on" + (t === "immediate" ? " immediate" : "") : "") + '">' + tierLabel(t) + '</div>';
    }).join("");
    var html = '<div class="branchsel"><div class="cond">' + escapeHtml(dec.branch.condition) + '</div></div>' +
      '<div class="tierbar">' + tbar + '</div>' +
      '<div style="font-size:12px;color:var(--muted)">Severity score <b style="color:var(--decide)">' + dec.severity.toFixed(2) + '</b> selects the response tier. The system acts proportionally to value at risk.</div>';
    if (dec.requiresHITL) {
      html += '<div class="hitl"><span class="lock">🔒</span><div class="txt"><b>Human-in-the-Loop gate</b>' + escapeHtml(dec.hitl) + '</div></div>';
    }
    pad.innerHTML = html;
    card.appendChild(pad);
    return card;
  }

  function actionCard(pat, dec, res) {
    var card = el("div", "card");
    card.innerHTML = '<h4><span class="num">A</span>Action DAG — Deterministic, Rollback-Ready Execution</h4>';
    var pad = el("div", "pad");
    var dag = el("div", "dag");
    res.actionDAG.forEach(function (s) {
      var node = el("div", "dnode");
      var verbs = s.actions.map(function (a) {
        var cls = "verb" + (a.mutating ? " write" : "");
        var sg = a.compensable ? '<span class="sg">↺ SAGA</span>' : '';
        return '<span class="' + cls + '">' + escapeHtml(a.verb) + sg + '</span>';
      }).join("");
      node.innerHTML = '<span class="sn">' + s.step + '</span><div class="dverbs">' + verbs + '</div>';
      dag.appendChild(node);
    });
    pad.appendChild(dag);
    var saga = el("div", "saga-row");
    saga.innerHTML = chip("↺", "Saga: write-steps auto-rollback") + chip("⟳", "Idempotent retry on locked records") +
      chip("⊕", "SAP remains system of record") + chip("⊘", "Deterministic API blocks — no hallucination");
    pad.appendChild(saga);
    var exec = el("div", "exec");
    if (dec.requiresHITL) {
      exec.innerHTML = '<button class="btn approve" id="approveBtn">🔒 Approve &amp; Execute DAG</button><button class="btn ghost">Edit payload</button>';
    } else {
      exec.innerHTML = '<button class="btn go" id="approveBtn">Execute DAG</button><button class="btn ghost">Queue for review</button>';
    }
    pad.appendChild(exec);
    var gov = el("div", "gov-note");
    gov.innerHTML = '<span>Mode: <b>' + (dec.requiresHITL ? "Assisted (HITL)" : "Policy-approved") + '</b></span>' +
      '<span>Outcome attribution: <b>ON</b></span><span>Audit log: <b>cryptographic</b></span>';
    pad.appendChild(gov);
    card.appendChild(pad);
    setTimeout(function () {
      var b = document.getElementById("approveBtn");
      if (b) b.onclick = function () {
        b.textContent = "✓ Executed — " + countActions(res.actionDAG) + " steps committed, attribution tracking";
        b.className = "btn ghost"; b.disabled = true;
      };
    }, 10);
    return card;
  }

  function chip(ic, txt) { return '<span class="chip">' + ic + ' ' + txt + '</span>'; }
  function cleanCard(iv) {
    var card = el("div", "card");
    card.innerHTML = '<h4><span class="num">✓</span>No Behavioural Pattern Detected</h4>' +
      '<div class="pad"><p style="margin:0 0 8px">This invoice is paying within normal parameters — the cognitive loop found no float-extension, dispute-manipulation, or credit-risk tactic. Standard dunning applies; the analyst\'s attention is freed for the items that matter.</p>' +
      '<div class="saga-row">' + chip("", "Payment ratio nominal") + chip("", "No dispute proximity") + chip("", "DPD within terms") + '</div></div>';
    return card;
  }
  function note() {
    return el("div", "note", "Cognitive Cockpit — Module 3. Engine runs on-device from the AR Pattern Library v2 (" + meta.patternCount + " patterns). Live-Claude diagnosis narrative is a pluggable layer.");
  }
  function escapeHtml(s) { return (s == null ? "" : String(s)).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  /* ---------- Cross-process compound signals (collective intelligence) ----------
   * After the worklist runs the engine on every invoice, we record each fired
   * pattern into the engine's per-entity firing history (keyed by customer), then
   * correlate that history against the compound rules. Compounds surface behaviour
   * no single process sees. Rendered as red alert cards above the worklist. */
  var compounds = (window.PROCESSIQ_COMPOUNDS && window.PROCESSIQ_COMPOUNDS.compounds) || [];

  // Deterministic demo history: the same accounts exhibited these patterns in OTHER
  // processes (Cash App, Credit) earlier in the window. The collections worklist is
  // only one process, so without this the cross-process layer has nothing to cross.
  var PRIOR_FIRINGS = [
    { cust: "Halberd Industrial Group", pid: 22, conf: 0.88 },   // + #1 (worklist) → CP-001
    { cust: "Halberd Industrial Group", pid: 25, conf: 0.84 },
    { cust: "Quanta Semiconductors", pid: 20, conf: 0.82 },      // + #19 (worklist) → CP-003
    { cust: "Quanta Semiconductors", pid: 22, conf: 0.79 },
    { cust: "Crestfall Retail Holdings", pid: 4, conf: 0.80 },   // + #3 (worklist) → CP-002
    { cust: "Vanta Pharma Distribution", pid: 1, conf: 0.83 },   // + #20 (worklist) → CP-007
  ];

  function patternById(id) { return patterns.filter(function (p) { return p.id === id; })[0]; }

  // Build the firing history from the worklist (+ demo priors), then correlate.
  function scanCompounds() {
    if (!E.correlate || !compounds.length) return [];
    E.resetFiringHistory();
    var evidence = {};   // customer -> [{patternId, invoice}]  (invoice=null for priors)
    function addEvidence(cust, pid, iv) { (evidence[cust] = evidence[cust] || []).push({ patternId: pid, invoice: iv }); }

    // (1) real firings from the current worklist
    book.invoices.forEach(function (iv) {
      var d = E.run(iv, patterns).diagnosis;
      if (d.fired && d.top && d.top.pattern) {
        E.recordFiring(iv.customer, d.top.pattern.id, d.confidence);
        addEvidence(iv.customer, d.top.pattern.id, iv);
      }
    });
    // (2) synthetic prior cross-process firings (demo)
    PRIOR_FIRINGS.forEach(function (s) {
      E.recordFiring(s.cust, s.pid, s.conf);
      addEvidence(s.cust, s.pid, null);
    });
    // (3) correlate per unique customer
    var seen = {}, signals = [];
    book.invoices.forEach(function (iv) {
      if (seen[iv.customer]) return; seen[iv.customer] = 1;
      E.correlate(iv.customer, compounds).forEach(function (sig) {
        signals.push({ customer: iv.customer, sig: sig, evidence: evidence[iv.customer] || [] });
      });
    });
    // most severe first
    var rank = { critical: 0, high: 1, medium: 2, low: 3 };
    function rk(s) { return s.sig.severity in rank ? rank[s.sig.severity] : 9; }
    signals.sort(function (a, b) { return rk(a) - rk(b); });
    return signals;
  }

  function renderCompoundSection() {
    var signals = scanCompounds();
    if (!signals.length) return "";
    return '<div class="compound-band"><div class="cb-head">' +
      '<span class="cb-title">⚠ Cross-Process Compound Signals</span>' +
      '<span class="cb-count">' + signals.length + '</span>' +
      '<span class="cb-sub">Collective intelligence — behaviour no single process sees, correlated across Collections, Credit &amp; Cash App for the same customer.</span>' +
      '</div>' + signals.map(compoundCard).join("") + '</div>';
  }

  function compoundCard(s) {
    var cp = s.sig.compound, matched = s.sig.matchedComponentIds;
    var comps = cp.componentPatternIds.map(function (pid) {
      var p = patternById(pid);
      var isM = matched.indexOf(pid) >= 0;
      var ev = (s.evidence || []).filter(function (e) { return e.patternId === pid; })[0];
      var clickable = !!(ev && ev.invoice);
      return '<span class="ca-component' + (isM ? " matched" : "") + (clickable ? " link" : "") + '"' +
        (clickable ? ' data-belnr="' + ev.invoice.belnr + '" title="Open the invoice evidence"' : ' title="' + (isM ? "Prior signal from another process" : "Not yet fired") + '"') + '>' +
        (isM ? "● " : "○ ") + "#" + pid + " " + escapeHtml(p ? p.name : "Pattern " + pid) + '</span>';
    }).join("");
    return '<div class="compound-alert sev-' + escapeHtml(cp.severity) + '">' +
      '<div class="ca-head"><span class="ca-title">' + escapeHtml(cp.name) + '</span>' +
      '<span class="ca-sev ' + escapeHtml(cp.severity) + '">' + escapeHtml(cp.severity.toUpperCase()) + '</span></div>' +
      '<div class="ca-meta"><b>' + escapeHtml(s.customer) + '</b> · ' + matched.length + ' of ' +
      cp.componentPatternIds.length + ' patterns · ' + (s.sig.confidence * 100 | 0) + '% confidence · ' +
      cp.windowDays + 'd window</div>' +
      '<div class="ca-desc">' + escapeHtml(cp.description) + '</div>' +
      '<div class="ca-components">' + comps + '</div>' +
      '<div class="ca-rec"><b>Recommendation.</b> ' + escapeHtml(cp.recommendation) + '</div>' +
      '<div class="ca-foot"><span class="ca-exposure">Est. exposure ' + money(cp.estimatedExposure) + '</span>' +
      ((cp.kpiImpact || []).length ? '<span class="ca-kpi">Impacts: ' + cp.kpiImpact.map(escapeHtml).join(" · ") + '</span>' : "") +
      '</div></div>';
  }

  function wireCompoundLinks() {
    document.querySelectorAll(".ca-component.link").forEach(function (elm) {
      elm.onclick = function () {
        var belnr = elm.getAttribute("data-belnr");
        var iv = book.invoices.filter(function (x) { return String(x.belnr) === String(belnr); })[0];
        if (iv) { selected = iv; renderList(); renderCockpit(); window.scrollTo(0, 0); }
      };
    });
  }

  var EMPTY =
    '<div class="empty"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3">' +
    '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>' +
    '<div><b>Select an invoice</b> to watch the cognitive loop diagnose it.</div>' +
    '<div style="font-size:12px;max-width:340px">Each open item carries an event timeline. ProcessIQ senses the signals, names the behavioural pattern, and assembles a governance-approved action.</div></div>';

  /* ---------- module registration ---------- */
  window.PIQ.modules.cockpit = {
    render: function (view) {
      // honor a deep-link from the Pattern Library ("see it live")
      if (window.PIQ._jumpInvoice) {
        selected = book.invoices.filter(function (iv) { return iv.belnr === window.PIQ._jumpInvoice; })[0] || selected;
        window.PIQ._jumpInvoice = null;
      }
      view.innerHTML =
        renderCompoundSection() +
        '<div class="wrap"><aside class="worklist"><h3>Collections Worklist</h3><div id="invList"></div></aside>' +
        '<main class="cockpit" id="cockpit"></main></div>';
      renderList();
      renderCockpit();
      wireCompoundLinks();
    },
  };
  window.PIQ.onErp(function () { if (window.PIQ.active === "cockpit") { renderList(); renderCockpit(); } });
})();
