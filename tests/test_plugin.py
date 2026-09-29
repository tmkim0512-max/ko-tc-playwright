"""판정 규칙을 브라우저 없이 확인한다: 가짜 page 와 가짜 예외로 판정 5종 매핑을 본다."""
import json

pytest_plugins = ["pytester"]

FAKE = '''
import pytest
from tc2pw.runtime import R, EnvMissing

class FakePage:
    def set_default_timeout(self, ms): pass

class TimeoutError(Exception): pass  # Playwright TimeoutError 는 AssertionError 가 아니다

@pytest.fixture
def page():
    return FakePage()

def _prep_ok(page, r): r.step(1, "open")
def _prep_broken(page, r):
    r.step(1, "open"); raise TimeoutError("goto timed out")

def test_pass(page):
    r = R(page); _prep_ok(page, r); r.enter_body()
    r.step(2, "see"); r.asserts += 1

def test_fail(page):
    r = R(page); _prep_ok(page, r); r.enter_body()
    r.step(3, "text_has"); r.asserts += 1; raise AssertionError("expected 'a' got 'b'")

def test_timeout_in_body_is_blocked(page):
    r = R(page); _prep_ok(page, r); r.enter_body()
    r.step(4, "click"); raise TimeoutError("click timed out")

def test_assertion_in_prep_is_blocked(page):
    r = R(page); r.step(1, "screen_is"); r.asserts += 1; raise AssertionError("prep check")

def test_prep_error_is_blocked(page):
    r = R(page); _prep_broken(page, r); r.enter_body()

def test_env_missing_is_blocked(page):
    r = R(page); _prep_ok(page, r); r.enter_body()
    r.step(5, "type"); r.env("SURELY_NOT_SET_12345")

def test_prep_asserts_do_not_count(page):
    r = R(page); r.asserts += 1; r.enter_body()
    r.step(6, "click")

@pytest.fixture
def broken_fixture():
    raise RuntimeError("browser launch failed")

def test_fixture_error_is_blocked(page, broken_fixture):
    pass

@pytest.mark.skip(reason="partial: 미지원 스텝 1개")
def test_partial(page):
    raise AssertionError("never runs")
'''


def test_verdict_mapping(pytester):
    pytester.makepyfile(test_fake=FAKE)
    out = pytester.path / "results.json"
    pytester.runpytest("-p", "tc2pw.plugin", "-p", "no:playwright", "--results", str(out))
    rows = {r["test"]: r for r in json.loads(out.read_text(encoding="utf-8"))["rows"]}
    got = {name: (r["verdict"], r["reason"], r["phase"], r["error_type"]) for name, r in rows.items()}
    assert got == {
        "test_pass": ("PASS", None, None, None),
        "test_fail": ("FAIL", None, "body", "AssertionError"),
        "test_timeout_in_body_is_blocked": ("BLOCKED", None, "body", "TimeoutError"),
        "test_assertion_in_prep_is_blocked": ("BLOCKED", None, "prep", "AssertionError"),
        "test_prep_error_is_blocked": ("BLOCKED", None, "prep", "TimeoutError"),
        "test_env_missing_is_blocked": ("BLOCKED", None, "body", "EnvMissing"),
        "test_prep_asserts_do_not_count": ("INCONCLUSIVE", "no_assert", None, None),
        "test_fixture_error_is_blocked": ("BLOCKED", None, "setup", "RuntimeError"),
        "test_partial": ("NOT_RUN", "partial", None, None),
    }
    assert (rows["test_fail"]["fail_step"], rows["test_fail"]["fail_kind"]) == (3, "text_has")
    assert rows["test_pass"]["asserts"] == 1
