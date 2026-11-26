/* Fintech Radar: "Simulate for Birbank" reports.
   Each item carries a brief of planning assumptions (low / base / high). This script turns a brief
   into 12-month KPI estimates using Birbank's baselines: public values from the build, overridden by
   numbers the reader enters, which are kept in this browser's localStorage only.
   All text from feeds is inserted with textContent, never as HTML. */
(function () {
  "use strict";
  var dialog = document.querySelector("[data-sim-dialog]");
  if (!dialog) return;
  var body = dialog.querySelector("[data-sim-body]");
  function readJSON(id) { var el = document.getElementById(id); try { return el ? JSON.parse(el.textContent) : {}; } catch (e) { return {}; } }
  var SIMS = readJSON("radar-sims"), BASE = readJSON("radar-baseline"), T = readJSON("radar-sim-strings");
  var STORE = "fintech-radar.baseline.v1";
  var SCEN = ["low", "base", "high"];
  var KEYS = ["adoption_pct", "activation_pct", "extra_tx", "fee_azn", "acquisition_pct", "nps_points", "uptime_pp"];
  var state = { id: null, scenario: 1, edits: {} };

  function t(k) { return T[k] || k; }
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "text") n.textContent = attrs[k];
      else if (k === "class") n.className = attrs[k];
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }

  /* ---- baselines: build values, overridden by this browser's saved numbers ---- */
  function saved() { try { return JSON.parse(localStorage.getItem(STORE) || "{}"); } catch (e) { return {}; } }
  function baseline() {
    var out = {}, mine = saved();
    Object.keys(BASE).forEach(function (k) {
      var v = mine[k] != null && mine[k] !== "" ? mine[k] : BASE[k].value;
      out[k] = v == null || v === "" || isNaN(+v) ? null : +v;
    });
    return out;
  }

  /* ---- formatting ---- */
  function num(v, digits) {
    return v.toLocaleString("en-GB", { maximumFractionDigits: digits == null ? 1 : digits, minimumFractionDigits: 0 });
  }
  function users(k) { return k >= 1000 ? num(k / 1000, 2) + " mln" : num(k, k < 10 ? 1 : 0) + "k"; }
  function azn(v) {
    var a = Math.abs(v), s = v < 0 ? "−" : "+";
    if (a >= 1e6) return s + num(a / 1e6, 1) + " mln AZN";
    if (a >= 1e3) return s + num(a / 1e3, 0) + "k AZN";
    return s + num(a, 0) + " AZN";
  }
  function pct(v) { return num(v, v < 1 ? 2 : 1) + "%"; }

  /* ---- the model ---- */
  function assumptions(sim) {
    var a = {};
    KEYS.forEach(function (k) {
      var v = sim[k] ? sim[k][state.scenario] : 0;
      a[k] = state.edits[k] != null ? state.edits[k] : v;
    });
    return a;
  }

  function compute(sim, b) {
    var a = assumptions(sim), rows = [];
    var adoptersK = b.app_mau != null ? b.app_mau * a.adoption_pct / 100 : null;

    var newMtu = adoptersK != null ? adoptersK * a.activation_pct / 100 : null;
    rows.push({ kpi: t("kpi_mtu"),
      value: newMtu == null ? null : "+" + users(newMtu) + " users" + (b.mtu ? " (" + pct(newMtu / b.mtu * 100) + ")" : ""),
      how: pct(a.adoption_pct) + " of active users adopt × " + pct(a.activation_pct) + " start transacting monthly",
      needs: newMtu == null ? [BASE.app_mau && BASE.app_mau.label] : (b.mtu ? [] : [])
    });

    var extraTxK = adoptersK != null ? adoptersK * a.extra_tx : null;
    rows.push({ kpi: t("kpi_noncash"),
      value: extraTxK == null ? null : "+" + users(extraTxK).replace(/k$/, "k") + " a month" + (b.non_cash_tx ? " (" + pct(extraTxK / b.non_cash_tx * 100) + ")" : ""),
      how: "adopters × " + num(a.extra_tx) + " extra transactions a month each",
      needs: extraTxK == null ? [BASE.app_mau && BASE.app_mau.label] : []
    });

    var margin = b.revenue_per_tx != null ? b.revenue_per_tx - (b.cost_per_tx || 0) : null;
    var profit = null, profitNeeds = [];
    if (adoptersK == null) profitNeeds.push(BASE.app_mau && BASE.app_mau.label);
    if (margin == null && a.extra_tx > 0) profitNeeds.push(BASE.revenue_per_tx && BASE.revenue_per_tx.label);
    if (!profitNeeds.length) profit = 12 * adoptersK * 1000 * ((margin || 0) * a.extra_tx + a.fee_azn);
    rows.push({ kpi: t("kpi_profit"),
      value: profit == null ? null : azn(profit) + " a year",
      how: "12 months × adopters × (extra transactions × net margin per transaction + " + num(a.fee_azn, 2) + " AZN new fees a month)",
      needs: profitNeeds
    });

    var growth = b.new_customers != null ? b.new_customers * a.acquisition_pct / 100 : null;
    rows.push({ kpi: t("kpi_growth"),
      value: a.acquisition_pct === 0 ? t("sim_no_effect") : growth == null ? null : "+" + users(growth * 12) + " customers a year",
      how: pct(a.acquisition_pct) + " more new customers each month",
      needs: a.acquisition_pct === 0 || growth != null ? [] : [BASE.new_customers && BASE.new_customers.label]
    });

    rows.push({ kpi: t("kpi_nps"),
      value: a.nps_points === 0 ? t("sim_no_effect") : (a.nps_points > 0 ? "+" : "−") + num(Math.abs(a.nps_points)) + (Math.abs(a.nps_points) === 1 ? " point" : " points") + (b.nps != null ? " (to " + num(b.nps + a.nps_points) + ")" : ""),
      how: "judgement from the feature's effect on friction and delight", needs: [] });

    rows.push({ kpi: t("kpi_uptime"),
      value: a.uptime_pp === 0 ? t("sim_no_effect") : "+" + num(a.uptime_pp, 2) + " pp" + (b.uptime != null ? " (to " + num(Math.min(100, b.uptime + a.uptime_pp), 2) + "%)" : ""),
      how: "only reliability features change availability", needs: [] });

    var summary;
    if (adoptersK != null) {
      summary = "About " + users(adoptersK) + " active users use it after a year. " +
        (newMtu ? "Roughly " + users(newMtu) + " of them become new monthly transactors, " : "") +
        (extraTxK ? "adding " + users(extraTxK) + " non-cash transactions a month" : "") +
        (profit != null ? ", worth " + azn(profit).replace(/^\+/, "") + " a year in net payments revenue." : ".");
    } else {
      summary = pct(a.adoption_pct) + " of active users adopt it in the " + t(["sim_low", "sim_base", "sim_high"][state.scenario]).toLowerCase() +
        " case, and " + pct(a.adoption_pct * a.activation_pct / 100) + " of active users become new monthly transactors. " + t("sim_numbers_missing");
    }
    return { rows: rows, summary: summary, assumptions: a };
  }

  /* ---- rendering ---- */
  function render() {
    var sim = SIMS[state.id];
    if (!sim) return;
    var b = baseline(), r = compute(sim, b);
    body.textContent = "";

    var head = el("header", { class: "sim__head" }, [
      el("div", { class: "sim__kicker-row" }, [
        el("span", { class: "chip chip--" + String(sim.region).toLowerCase(), text: sim.place || sim.region }),
        el("span", { class: "chip chip--cat", text: sim.category }),
        el("span", { class: "sim__source sim__source--" + sim.source, text: t(sim.source === "claude" ? "sim_brief_claude" : "sim_brief_default") })
      ]),
      el("h2", { id: "sim-title", class: "sim__title", text: t("sim_title") }),
      el("p", { class: "sim__idea", text: sim.idea }),
      el("p", { class: "sim__sub" }, [t("sim_subtitle") + " ", el("a", { href: sim.url, target: "_blank", rel: "noopener", text: t("sim_source_link") + ": " + sim.title })]),
      el("button", { type: "button", class: "sim__close", "aria-label": t("sim_close"), onclick: close }, [svgX()])
    ]);

    var seg = el("div", { class: "sim__seg", role: "radiogroup", "aria-label": t("sim_scenario") });
    ["sim_low", "sim_base", "sim_high"].forEach(function (k, i) {
      seg.appendChild(el("button", { type: "button", role: "radio", "aria-checked": String(i === state.scenario), class: i === state.scenario ? "is-on" : "",
        text: t(k), onclick: function () { state.scenario = i; state.edits = {}; render(); } }));
    });

    var summary = el("p", { class: "sim__summary" }, [el("b", { text: t("sim_summary_label") + ": " }), r.summary]);

    var table = el("table", { class: "sim__table" }, [
      el("thead", null, [el("tr", null, [el("th", { scope: "col", text: t("sim_col_kpi") }), el("th", { scope: "col", text: t("sim_col_impact") }), el("th", { scope: "col", text: t("sim_col_how") })])]),
      el("tbody", null, r.rows.map(function (row) {
        var cell = row.value != null ? el("td", { class: "sim__val" + (row.value === t("sim_no_effect") ? " sim__val--none" : ""), text: row.value })
          : el("td", { class: "sim__val sim__val--needs" }, [el("button", { type: "button", class: "sim__needs", onclick: openNumbers,
              text: t("sim_needs") + ": " + row.needs.filter(Boolean).join(", ") })]);
        return el("tr", null, [el("th", { scope: "row", text: row.kpi }), cell, el("td", { class: "sim__how", text: row.how })]);
      }))
    ]);

    var form = el("div", { class: "sim__assume" });
    KEYS.forEach(function (k) {
      var input = el("input", { type: "number", step: "any", min: "0", value: String(r.assumptions[k]), "aria-label": t("sim_a_" + k) });
      if (k === "nps_points") input.removeAttribute("min");
      input.addEventListener("change", function () { var v = parseFloat(input.value); if (!isNaN(v)) { state.edits[k] = v; render(); focusField(k); } });
      input.dataset.key = k;
      form.appendChild(el("label", { class: "sim__field" }, [el("span", { text: t("sim_a_" + k) }), input]));
    });

    var delivery = el("dl", { class: "sim__dl" }, [
      el("dt", { text: t("sim_mechanism") }), el("dd", { text: sim.mechanism }),
      el("dt", { text: t("sim_segment") }), el("dd", { text: sim.segment }),
      el("dt", { text: t("sim_effort") }), el("dd", { text: t("sim_effort_" + sim.effort) }),
      el("dt", { text: t("sim_time") }), el("dd", { text: sim.months[0] + "–" + sim.months[1] + " " + t("sim_months") }),
      el("dt", { text: t("sim_dependencies") }), el("dd", null, [list(sim.dependencies)]),
      el("dt", { text: t("sim_risks") }), el("dd", null, [list(sim.risks)]),
      el("dt", { text: t("sim_pilot") }), el("dd", { text: sim.pilot })
    ]);

    var numbers = el("details", { class: "sim__numbers", "data-sim-numbers": "" }, [
      el("summary", { text: t("sim_numbers") }),
      el("p", { class: "sim__hint", text: t("sim_numbers_hint") })
    ]);
    var mine = saved(), grid = el("div", { class: "sim__assume" });
    Object.keys(BASE).forEach(function (k) {
      var m = BASE[k], input = el("input", { type: "number", step: "any", name: k, value: mine[k] != null ? String(mine[k]) : (m.value != null ? String(m.value) : ""), placeholder: m.unit });
      grid.appendChild(el("label", { class: "sim__field" }, [el("span", { text: m.label + " (" + m.unit + ")" }), input]));
    });
    numbers.appendChild(grid);
    var status = el("span", { class: "sim__status", "aria-live": "polite" });
    numbers.appendChild(el("div", { class: "sim__actions" }, [
      el("button", { type: "button", class: "btn", text: t("sim_save"), onclick: function () {
        var out = {};
        grid.querySelectorAll("input").forEach(function (i) { if (i.value !== "" && !isNaN(+i.value)) out[i.name] = +i.value; });
        try { localStorage.setItem(STORE, JSON.stringify(out)); } catch (e) { /* private mode */ }
        render(); var d = body.querySelector("[data-sim-numbers]"); if (d) { d.open = true; d.querySelector(".sim__status").textContent = t("sim_saved"); }
      } }),
      el("button", { type: "button", class: "btn btn--quiet", text: t("sim_clear"), onclick: function () {
        try { localStorage.removeItem(STORE); } catch (e) { /* ignore */ }
        render(); var d = body.querySelector("[data-sim-numbers]"); if (d) d.open = true;
      } }),
      status
    ]));

    var copyBtn = el("button", { type: "button", class: "btn btn--quiet", text: t("sim_copy"), onclick: function () {
      var text = reportText(sim, r);
      var done = function () { copyBtn.textContent = t("sim_copied"); setTimeout(function () { copyBtn.textContent = t("sim_copy"); }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
      else { fallbackCopy(text); done(); }
    } });

    body.appendChild(head);
    body.appendChild(el("section", { class: "sim__section" }, [
      el("div", { class: "sim__bar" }, [el("h3", { text: t("sim_impact") }), seg]), summary, table]));
    body.appendChild(el("section", { class: "sim__section" }, [
      el("div", { class: "sim__bar" }, [el("h3", { text: t("sim_assumptions") }),
        el("button", { type: "button", class: "sim__link", text: t("sim_reset"), onclick: function () { state.edits = {}; render(); } })]),
      el("p", { class: "sim__hint", text: t("sim_assumptions_hint") }), form]));
    body.appendChild(el("section", { class: "sim__section" }, [el("h3", { text: t("sim_delivery") }), delivery]));
    body.appendChild(el("section", { class: "sim__section" }, [numbers]));
    body.appendChild(el("footer", { class: "sim__foot" }, [
      el("p", { class: "sim__hint", text: t("sim_disclaimer") }),
      el("div", { class: "sim__actions" }, [copyBtn, el("button", { type: "button", class: "btn btn--quiet", text: t("sim_print"), onclick: function () { window.print(); } })])
    ]));
  }

  function list(items) { return el("ul", null, (items || []).map(function (x) { return el("li", { text: x }); })); }
  function svgX() {
    var s = document.createElementNS("http://www.w3.org/2000/svg", "svg"); s.setAttribute("viewBox", "0 0 16 16"); s.setAttribute("aria-hidden", "true");
    var p = document.createElementNS("http://www.w3.org/2000/svg", "path"); p.setAttribute("d", "M4 4l8 8M12 4l-8 8"); s.appendChild(p); return s;
  }
  function focusField(k) { var i = body.querySelector('input[data-key="' + k + '"]'); if (i) i.focus(); }
  function openNumbers() { var d = body.querySelector("[data-sim-numbers]"); if (d) { d.open = true; d.scrollIntoView({ block: "nearest" }); var i = d.querySelector("input"); if (i) i.focus(); } }
  function fallbackCopy(text) {
    var ta = el("textarea", { class: "vh" }); ta.value = text; body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) { /* ignore */ } ta.remove();
  }
  function reportText(sim, r) {
    var lines = [t("sim_title") + ": " + sim.idea, sim.title + " (" + sim.publisher + ") " + sim.url,
      t("sim_scenario") + ": " + t(["sim_low", "sim_base", "sim_high"][state.scenario]), "", r.summary, "", t("sim_impact") + ":"];
    r.rows.forEach(function (row) { lines.push("- " + row.kpi + ": " + (row.value || t("sim_needs") + " " + row.needs.filter(Boolean).join(", ")) + " (" + row.how + ")"); });
    lines.push("", t("sim_mechanism") + ": " + sim.mechanism, t("sim_effort") + ": " + t("sim_effort_" + sim.effort) + ", " + sim.months[0] + "–" + sim.months[1] + " " + t("sim_months"),
      t("sim_dependencies") + ": " + sim.dependencies.join("; "), t("sim_risks") + ": " + sim.risks.join("; "), t("sim_pilot") + ": " + sim.pilot, "", t("sim_disclaimer"));
    return lines.join("\n");
  }

  var opener = null;
  function open(id, from) {
    if (!SIMS[id]) return;
    opener = from || null;
    state = { id: id, scenario: 1, edits: {} };
    render();
    if (typeof dialog.showModal === "function") dialog.showModal(); else dialog.setAttribute("open", "");
    document.documentElement.classList.add("has-dialog");
    var c = dialog.querySelector(".sim__close"); if (c) c.focus();
  }
  function close() {
    if (typeof dialog.close === "function" && dialog.open) dialog.close(); else dialog.removeAttribute("open");
  }
  dialog.addEventListener("close", function () { document.documentElement.classList.remove("has-dialog"); if (opener) opener.focus(); });
  dialog.addEventListener("click", function (e) { if (e.target === dialog) close(); });
  document.addEventListener("click", function (e) {
    var btn = e.target.closest ? e.target.closest("[data-sim-open]") : null;
    if (btn) { e.preventDefault(); open(btn.getAttribute("data-sim-open"), btn); }
  });
})();
