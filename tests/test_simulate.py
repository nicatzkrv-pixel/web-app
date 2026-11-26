import json
from types import SimpleNamespace

from radar import config, simulate
from radar.build import build_site


def item(i=1, category="Payments", **kw):
    return {"id": f"id{i}", "title": "Bank launches QR payments", "summary": "s", "idea": "We could add QR.",
            "category": category, "region": "Global", "country": "UK", "kpi": "MTU", "url": "https://x.example/a", **kw}


def test_every_category_has_a_sane_default():
    assert set(simulate.DEFAULTS) == set(config.CATEGORIES)
    for cat, brief in simulate.DEFAULTS.items():
        for key in simulate.RANGE_KEYS:
            lo, base, hi = brief[key]
            assert lo <= base <= hi, (cat, key)
            assert simulate.BOUNDS[key][0] <= lo and hi <= simulate.BOUNDS[key][1], (cat, key)
        assert brief["effort"] in simulate.EFFORTS and brief["pilot"] and brief["risks"]


def test_default_brief_uses_item_idea_and_is_marked():
    b = simulate.default_brief(item(category="Cards"))
    assert b["source"] == "default" and b["mechanism"] == "We could add QR."
    assert b["adoption_pct"] == simulate.DEFAULTS["Cards"]["adoption_pct"]


def test_clean_brief_clamps_and_sorts():
    raw = {"adoption_pct": [500, 2, 10], "nps_points": [-50, 1, 2], "effort": "XL", "months": [40, 0],
           "risks": ["  ", "Fraud"], "pilot": "Try it"}
    b = simulate.clean_brief(raw, item())
    assert b["adoption_pct"] == [2.0, 10.0, 100.0]
    assert b["nps_points"][0] == -5
    assert b["effort"] == simulate.DEFAULTS["Payments"]["effort"]  # invalid value ignored
    assert b["months"] == [1, 36]
    assert b["risks"] == ["Fraud"] and b["pilot"] == "Try it"


class FakeClient:
    def __init__(self, fail=False):
        self.calls, self.fail = [], fail
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        if self.fail:
            raise RuntimeError("down")
        content = kw["messages"][0]["content"]
        ids = [i["id"] for i in json.loads(content.split("<items>\n", 1)[1].rsplit("\n</items>", 1)[0])]
        briefs = [{"id": i, "mechanism": "m", "segment": "s", "adoption_pct": [1, 2, 3], "activation_pct": [1, 2, 3],
                   "extra_tx": [1, 1, 1], "fee_azn": [0, 0, 0], "acquisition_pct": [0, 0, 0], "nps_points": [0, 1, 2],
                   "uptime_pp": [0, 0, 0], "effort": "S", "months": [2, 4], "dependencies": ["CBA"],
                   "risks": ["r"], "pilot": "p"} for i in ids[:-1]]  # leave the last one out
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps({"briefs": briefs}))], stop_reason="end_turn")


def test_claude_briefs_with_per_item_fallback():
    items = [item(i) for i in range(3)]
    client = FakeClient()
    counts = simulate.add_briefs(items, simulate.ClaudeSimulator(client=client, context="CTX"))
    assert counts == {"claude": 2, "default": 1}
    assert items[0]["sim"]["source"] == "claude" and items[0]["sim"]["adoption_pct"] == [1.0, 2.0, 3.0]
    assert items[2]["sim"]["source"] == "default"
    call = client.calls[0]
    assert call["system"][0]["cache_control"] == {"type": "ephemeral"} and "CTX" in call["system"][0]["text"]
    assert "untrusted data" in call["messages"][0]["content"]


def test_failed_batch_uses_defaults():
    items = [item(1)]
    assert simulate.add_briefs(items, simulate.ClaudeSimulator(client=FakeClient(fail=True), context=""))["default"] == 1


def test_no_key_means_defaults(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert simulate.make_simulator() is None


def test_baseline_file_is_public_safe():
    base = simulate.load_baseline()
    assert {"app_mau", "mtu", "non_cash_tx", "revenue_per_tx", "new_customers"} <= set(base)
    assert all(m["value"] is None for m in base.values()), "keep real Birbank numbers out of the public repo"


def test_site_embeds_briefs_and_buttons(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    doc = {"date": "2026-03-10", "items": [{**item(1), "publisher": "P", "score": 8.0, "applicability": 8, "novelty": 7,
                                            "bonus": 0, "penalty": 0, "launch_status": "launched", "scored_by": "keyword"}]}
    (data / "2026-03-10.json").write_text(json.dumps(doc))
    site = build_site(data, tmp_path / "site")
    html = (site / "index.html").read_text()
    assert 'data-sim-open="id1"' in html and 'id="radar-sims"' in html and "data-sim-dialog" in html
    sims = json.loads(html.split('id="radar-sims">', 1)[1].split("</script>", 1)[0])
    assert sims["id1"]["source"] == "default" and len(sims["id1"]["adoption_pct"]) == 3
    assert (site / "assets" / "radar-sim.js").exists()
