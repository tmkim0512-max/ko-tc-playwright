import json

import pytest

from tc2pw.report import render

TCS = {"tcs": [
    {"src": "a.tc", "module": "test_a", "grade": "FULL", "steps": 4, "converted": 4,
     "tests": ["test_x", "test_y", "test_z"], "todo": []},
    {"src": "b.tc", "module": "test_b", "grade": "PARTIAL", "steps": 2, "converted": 1,
     "tests": ["test_w"], "todo": [{"line": 5, "reason": "no_rule", "raw": "뭔가 한다."}]},
]}
META = {"started": "2026-01-01T00:00:00+09:00", "browser": "chromium 1", "platform": "p",
        "python": "3", "commit": "abc1234"}


def _row(module, test, verdict):
    return {"module": module, "test": test, "verdict": verdict, "reason": None, "phase": None,
            "error_type": None, "fail_step": None, "fail_kind": None}


def _write(tmp_path, rows):
    (tmp_path / "convert.json").write_text(json.dumps(TCS), encoding="utf-8")
    (tmp_path / "results.json").write_text(json.dumps({"meta": META, "rows": rows}), encoding="utf-8")


def test_two_tables_with_both_denominators(tmp_path):
    _write(tmp_path, [_row("test_a", "test_x", "PASS"), _row("test_a", "test_y", "FAIL"),
                      _row("test_a", "test_z", "INCONCLUSIVE"), _row("test_b", "test_w", "NOT_RUN")])
    md = render(tmp_path)
    assert "| 2 | 1 | 1 | 6 | 5 | 5/6 = 83% | 1/2 = 50% |" in md
    assert "| `a.tc:5` |" not in md and "| `b.tc:5` | no_rule | 뭔가 한다. |" in md
    assert "| 1 | 1 | 0 | 1 | 1 | 1/2 = 50% | 1/3 = 33% |" in md


def test_missing_block_breaks_the_total_check(tmp_path):
    _write(tmp_path, [_row("test_a", "test_x", "PASS")])  # 예: pytest -k 로 일부만 실행
    with pytest.raises(SystemExit, match="합계 불일치"):
        render(tmp_path)


def test_duplicate_row_breaks_the_total_check(tmp_path):
    rows = [_row("test_a", t, "PASS") for t in ("test_x", "test_y", "test_z")]
    _write(tmp_path, rows + [_row("test_b", "test_w", "NOT_RUN"), _row("test_a", "test_x", "FAIL")])
    with pytest.raises(SystemExit, match="합계 불일치"):
        render(tmp_path)
