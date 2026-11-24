/* Fintech Radar: filters and search for "All items". No dependencies. */
(function () {
  "use strict";
  var form = document.querySelector("[data-filters]");
  if (!form) return;
  var list = document.querySelector("[data-list]");
  var rows = Array.prototype.slice.call(list.querySelectorAll("[data-item]"));
  var counter = form.querySelector("[data-count]");
  var empty = document.querySelector("[data-empty]");
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var last = rows.length;

  function value(name) {
    var field = form.elements[name];
    if (!field) return "";
    if (field.length && field[0] && field[0].type === "radio") {
      for (var i = 0; i < field.length; i++) if (field[i].checked) return field[i].value;
      return "";
    }
    return field.value;
  }

  function apply() {
    var q = value("q").trim().toLowerCase();
    var region = value("region");
    var category = value("category");
    var min = parseFloat(value("min")) || 0;
    var terms = q ? q.split(/\s+/) : [];
    var shown = 0;
    rows.forEach(function (row) {
      var ok = (!region || row.dataset.region === region) &&
        (!category || row.dataset.category === category) &&
        parseFloat(row.dataset.score) >= min &&
        terms.every(function (term) { return row.dataset.search.indexOf(term) !== -1; });
      row.hidden = !ok;
      if (ok) shown++;
    });
    empty.hidden = shown !== 0;
    list.hidden = shown === 0;
    if (shown !== last) {
      counter.textContent = shown;
      if (!reduceMotion) {
        counter.classList.remove("is-flipping");
        void counter.offsetWidth; // restart the flip
        counter.classList.add("is-flipping");
      }
      last = shown;
    }
    syncUrl({ q: q, region: region, category: category, min: min > 6 ? String(min) : "" });
  }

  function syncUrl(state) {
    if (!window.history || !window.URLSearchParams) return;
    var params = new URLSearchParams();
    Object.keys(state).forEach(function (k) { if (state[k]) params.set(k, state[k]); });
    var query = params.toString();
    try {
      history.replaceState(null, "", query ? "?" + query : location.pathname);
    } catch (e) { /* file:// in some browsers */ }
  }

  function restore() {
    if (!window.URLSearchParams) return;
    var params = new URLSearchParams(location.search);
    if (params.get("q")) form.elements.q.value = params.get("q");
    if (params.get("category")) form.elements.category.value = params.get("category");
    if (params.get("min")) form.elements.min.value = params.get("min");
    var region = params.get("region");
    if (region) {
      var radios = form.elements.region;
      for (var i = 0; i < radios.length; i++) radios[i].checked = radios[i].value === region;
    }
  }

  function reset(evt) {
    if (evt) evt.preventDefault();
    form.reset();
    apply();
  }

  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  form.addEventListener("submit", function (evt) { evt.preventDefault(); apply(); });
  document.querySelectorAll("[data-reset]").forEach(function (btn) { btn.addEventListener("click", reset); });
  restore();
  apply();
})();
