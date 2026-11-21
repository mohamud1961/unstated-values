"""End-to-end runner check with a fake backend (no network): every variant runs, summaries and the headline build,
unfinished replies are counted apart. Run: python3 -m pytest -q tests/"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run  # noqa: E402


def test_variants_end_to_end(tmp_path, monkeypatch):
    n = {"i": 0}

    def fake(_):
        def gen(prompt):
            n["i"] += 1
            return ("Not stated" if n["i"] % 2 else "PO-1"), "", n["i"] % 7 != 0
        return gen

    monkeypatch.setattr(run, "openai_backend", fake)
    for variant in run.VARIANTS:
        monkeypatch.setattr(sys, "argv", ["run.py", "openai", "--model", f"t-{tmp_path.name}", "--limit", "60",
                                          "--sets", "natural3,worldq", "--variant", variant])
        run.main()
        slug = f"openai_t-{tmp_path.name}" + ("" if variant == "format" else f"_{variant}")
        d = json.loads((run.HERE / "results" / slug / "summary.json").read_text())
        assert d["variant"] == variant and d["headline"]["n_templates"] == 1
        assert d["natural_unfinished"] > 0
    import shutil
    shutil.rmtree(run.HERE / "results")
