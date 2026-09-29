"""pytest 플러그인: 확인 블록(테스트 함수) 하나마다 판정 1개를 results.json 에 남긴다.

PASS          예외 없음 + 본문 단언 1개 이상
FAIL          본문에서 AssertionError (Playwright expect 실패 포함). 이것만 FAIL 이다
BLOCKED       그 밖의 모든 예외 — 준비 구간 예외, 타임아웃, strict 위반, EnvMissing, fixture 오류
INCONCLUSIVE  예외 없음 + 본문 단언 0 (reason=no_assert)
NOT_RUN       실행 대상에서 뺀 블록 (PARTIAL TC, reason=partial)

pytest 의 passed/failed 와 이 판정은 따로 간다. 보고는 이 판정을 기준으로 한다.
"""
import datetime
import json
import platform
import subprocess
from pathlib import Path

import pytest

from tc2pw import runtime

ROWS, META = [], {}


def pytest_addoption(parser):
    parser.addoption("--results", default="generated/results.json", help="판정 기록 파일")


def pytest_sessionstart(session):
    ROWS.clear()
    META.clear()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    META.update(started=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                platform=platform.platform(), python=platform.python_version(),
                commit=commit.stdout.strip() or None, browser=None)


def pytest_runtest_setup(item):
    runtime.CURRENT = None


def judge(item, call, rep):
    r = runtime.CURRENT
    row = {"module": item.path.stem, "test": item.originalname, "verdict": None, "reason": None,
           "phase": None, "error_type": None, "message": None, "fail_step": None,
           "fail_kind": None, "asserts": r.asserts if r else 0, "elapsed_s": round(rep.duration, 2)}
    exc = call.excinfo
    if rep.skipped:
        row.update(verdict="NOT_RUN", reason=str(rep.longrepr[2]).removeprefix("Skipped: ").split(":")[0])
    elif exc is None:
        row.update(verdict="PASS" if row["asserts"] else "INCONCLUSIVE",
                   reason=None if row["asserts"] else "no_assert")
    else:
        in_body = rep.when == "call" and r is not None and r.in_body
        failed = in_body and isinstance(exc.value, AssertionError)
        row.update(verdict="FAIL" if failed else "BLOCKED",
                   phase=("body" if in_body else "prep") if rep.when == "call" else rep.when,
                   error_type=exc.typename, message=(str(exc.value).strip().splitlines() or [""])[0][:200],
                   fail_step=r and r.step_no, fail_kind=r and r.kind)
    return row


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    browser = getattr(item, "funcargs", {}).get("browser")  # pytest-playwright fixture
    if browser is not None and META.get("browser") is None:
        META["browser"] = f"{browser.browser_type.name} {browser.version}"
    if rep.when == "call" or (rep.when == "setup" and not rep.passed):
        ROWS.append(judge(item, call, rep))
    elif rep.when == "teardown" and rep.failed and ROWS:
        last = ROWS[-1]
        # 정리 단계 오류가 PASS 뒤에 숨지 않게 한다.
        if (last["module"], last["test"], last["verdict"]) == (item.path.stem, item.originalname, "PASS"):
            last.update(verdict="BLOCKED", phase="teardown", error_type=call.excinfo.typename)


def pytest_sessionfinish(session):
    out = Path(session.config.getoption("--results"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"meta": META, "rows": ROWS}, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
