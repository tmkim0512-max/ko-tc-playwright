""".tc → test_*.py 생성과 convert.json 집계.

셀렉터와 URL 은 생성 시점에 코드에 박는다. 요소는 '현재 화면'(가장 최근에 open 하거나
screen_is 로 확인한 화면)의 UI맵에서만 찾는다. 못 찾으면 unsupported(unresolved) 로 처리한다.
"""
import json
import re
import sys
from pathlib import Path

import yaml

from tc2pw.grammar import ParseError, parse

ELEMENT_CODE = {
    "click":     "{loc}.click()",
    "type":      "{loc}.fill({val})",
    "choose":    "{loc}.select_option(label={val})",
    "set_check": "{loc}.{check}()",
    "see":       "r.expect({loc}).to_be_visible()",
    "text_has":  "r.expect({loc}).to_contain_text({val})",
    "value_is":  "r.expect({loc}).to_have_value({val})",
    "checked":   "r.expect({loc}).to_be_checked(checked={is_checked})",
}


def _line(step, site, screen):
    """(코드 한 줄, 새 현재 화면) 을 돌려준다. 해석 못 하면 코드 대신 사유 문자열을 예외로 올린다."""
    a = step.args
    if step.kind == "unsupported":
        raise LookupError("no_rule")
    if "sc" in a:
        target = site["screens"].get(a["sc"])
        if target is None:
            raise LookupError(f"unresolved: <{a['sc']}> 화면이 UI맵에 없다")
        if step.kind == "open":
            return f"page.goto({site['base_url'] + target['path']!r})", a["sc"]
        return f"r.expect_url_endswith({target['path']!r})", a["sc"]
    selector = site["screens"].get(screen, {}).get("elements", {}).get(a["el"])
    if selector is None:
        raise LookupError(f"unresolved: [{a['el']}] 요소가 현재 화면 <{screen}> 에 없다")
    val = f"r.env({a['env']!r})" if "env" in a else repr(a.get("val"))
    code = ELEMENT_CODE[step.kind].format(
        loc=f"page.locator({selector!r})", val=val,
        check="check" if a.get("state") == "체크" else "uncheck",
        is_checked=a.get("state") == "체크")
    return code, screen


def _body(steps, site, screen, todo):
    out = []
    for s in steps:
        try:
            code, screen = _line(s, site, screen)
            out.append(f"    r.step({s.n}, {s.kind!r}); {code}")
        except LookupError as e:
            reason = str(e)
            todo.append({"line": s.n, "reason": reason, "raw": s.raw})
            out += [f"    # TODO(unsupported): {s.raw}",
                    f"    r.step({s.n}, 'unsupported'); raise Unsupported({reason!r})"]
    return out, screen


def fn_name(block_name):
    return "test_" + re.sub(r"\W+", "_", block_name).strip("_")


def convert(tc, uimap, src):
    """TC 1건 → (생성 코드 문자열, 요약 dict)."""
    if tc.site not in uimap:
        raise ParseError(f"{src}: 화면맵 '{tc.site}' 이 UI맵에 없다")
    site, todo = uimap[tc.site], []
    prep_steps = tc.prep.steps if tc.prep else []
    prep_lines, screen = _body(prep_steps, site, None, todo)
    funcs = []
    for block in tc.checks:
        lines, _ = _body(block.steps, site, screen, todo)
        funcs.append([f"def {fn_name(block.name)}(page):",
                      "    r = R(page); _prep(page, r); r.enter_body()", *lines])
    total = len(prep_steps) + sum(len(b.steps) for b in tc.checks)
    grade = "PARTIAL" if todo else "FULL"
    head = [f"# 원본: {src} | 변환: {total - len(todo)}/{total} 스텝 | 등급: {grade}",
            "# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다."]
    if todo:
        head += ["import pytest", "from tc2pw.runtime import R, Unsupported", "",
                 f"pytestmark = pytest.mark.skip(reason='partial: 미지원 스텝 {len(todo)}개')"]
    else:
        head += ["from tc2pw.runtime import R"]
    parts = ["\n".join(head), "\n".join(["def _prep(page, r):", *(prep_lines or ["    pass"])])]
    parts += ["\n".join(f) for f in funcs]
    summary = {"src": src, "title": tc.title, "tag": tc.tag, "grade": grade,
               "steps": total, "converted": total - len(todo),
               "tests": [fn_name(b.name) for b in tc.checks], "todo": todo}
    return "\n\n\n".join(parts) + "\n", summary


def convert_dir(tc_dir, uimap_path, out_dir):
    """종료 코드: 0 = 전부 FULL, 1 = PARTIAL 있음(생성은 끝까지 한다), 2 = 파싱 오류."""
    uimap = yaml.safe_load(Path(uimap_path).read_text(encoding="utf-8"))
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    summaries, parse_failed = [], False
    for path in sorted(Path(tc_dir).glob("*.tc")):
        try:
            code, summary = convert(parse(path.read_text(encoding="utf-8"), str(path)), uimap, path.as_posix())
        except ParseError as e:
            print(f"파싱 오류: {e}", file=sys.stderr)
            parse_failed = True
            continue
        summary["module"] = f"test_{path.stem}"
        (out / f"{summary['module']}.py").write_text(code, encoding="utf-8")
        summaries.append(summary)
    (out / "convert.json").write_text(
        json.dumps({"tcs": summaries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if parse_failed:
        return 2
    return 1 if any(s["grade"] == "PARTIAL" for s in summaries) else 0
