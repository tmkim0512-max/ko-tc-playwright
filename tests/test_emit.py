import json
from pathlib import Path

import yaml

from tc2pw.emit import convert, convert_dir
from tc2pw.grammar import parse

ROOT = Path(__file__).resolve().parent.parent
UIMAP = yaml.safe_load((ROOT / "examples/uimap.yaml").read_text(encoding="utf-8"))


def _convert(name):
    src = f"examples/tc/{name}.tc"
    return convert(parse((ROOT / src).read_text(encoding="utf-8"), src), UIMAP, src)


def test_committed_generated_files_are_up_to_date(tmp_path, monkeypatch):
    # 저장소에 커밋된 generated/ 가 지금 변환기 출력과 바이트 단위로 같아야 한다(골든 비교).
    monkeypatch.chdir(ROOT)
    code = convert_dir("examples/tc", "examples/uimap.yaml", tmp_path)
    assert code == 1  # 07, 08 이 의도적 PARTIAL
    produced = sorted(f.name for f in tmp_path.iterdir())
    committed = [*(ROOT / "generated").glob("test_*.py"), ROOT / "generated/convert.json"]
    assert produced == sorted(f.name for f in committed)
    for name in produced:
        assert (tmp_path / name).read_bytes() == (ROOT / "generated" / name).read_bytes(), name


def test_generation_is_deterministic(tmp_path):
    convert_dir(ROOT / "examples/tc", ROOT / "examples/uimap.yaml", tmp_path / "a")
    convert_dir(ROOT / "examples/tc", ROOT / "examples/uimap.yaml", tmp_path / "b")
    for f in (tmp_path / "a").iterdir():
        assert f.read_bytes() == (tmp_path / "b" / f.name).read_bytes()


def test_full_tc_bakes_selectors_and_keeps_env_at_runtime():
    code, s = _convert("01_login_ok")
    assert (s["grade"], s["steps"], s["converted"], s["todo"]) == ("FULL", 6, 6, [])
    assert "page.goto('https://the-internet.herokuapp.com/login')" in code
    assert "page.locator('#password').fill(r.env('TI_PASSWORD'))" in code
    assert "SuperSecret" not in code
    assert "skip" not in code


def test_unsupported_step_is_visible_not_dropped():
    code, s = _convert("07_drag_and_drop")
    assert s["grade"] == "PARTIAL" and s["converted"] == s["steps"] - 1
    assert s["todo"] == [{"line": 10, "reason": "no_rule", "raw": "[A 칸]을 [B 칸]으로 끌어다 놓는다."}]
    assert "# TODO(unsupported): [A 칸]을 [B 칸]으로 끌어다 놓는다." in code
    assert "raise Unsupported('no_rule')" in code
    assert "pytestmark = pytest.mark.skip(reason='partial: 미지원 스텝 1개')" in code


def test_element_resolves_only_on_current_screen():
    # [알림 메시지] 는 로그인·보안 화면 둘 다 있지만 [로그아웃 버튼] 은 보안 화면에만 있다.
    text = """# 제목: t
화면맵: the-internet
태그: 읽기
## 준비
<로그인>을 연다.
## 확인: a
[로그아웃 버튼]을 누른다.
<보안 화면> 화면인지 확인한다.
[로그아웃 버튼]을 누른다.
"""
    code, s = convert(parse(text), UIMAP, "t.tc")
    assert [t["line"] for t in s["todo"]] == [7]
    assert "unresolved: [로그아웃 버튼] 요소가 현재 화면 <로그인> 에 없다" in s["todo"][0]["reason"]
    assert "r.step(9, 'click'); page.locator(\"a[href='/logout']\").click()" in code


def test_convert_json_lists_every_block():
    data = json.loads((ROOT / "generated/convert.json").read_text(encoding="utf-8"))
    assert sum(len(t["tests"]) for t in data["tcs"]) == 9
