"""생성 코드가 부르는 런타임. 현재 스텝, 본문 진입 여부, 본문 단언 횟수를 기록한다."""
import os
import re

from playwright.sync_api import expect as _expect


class EnvMissing(Exception):
    pass


class Unsupported(Exception):
    pass


# 판정 플러그인이 읽는다. ponytail: 전역 1개 — 병렬 워커를 넣으면 워커별로 분리해야 한다.
CURRENT = None


class R:
    def __init__(self, page, timeout_ms=10_000):
        global CURRENT
        CURRENT = self
        self.page, self.asserts, self.in_body = page, 0, False
        self.step_no, self.kind = None, None
        page.set_default_timeout(timeout_ms)

    def step(self, n, kind):
        self.step_no, self.kind = n, kind

    def enter_body(self):
        # 준비 구간의 단언은 PASS 근거로 세지 않는다.
        self.in_body, self.asserts = True, 0

    def env(self, name):
        if (value := os.environ.get(name)) is None:
            raise EnvMissing(name)
        return value

    def expect(self, target):
        self.asserts += 1
        return _expect(target)

    def expect_url_endswith(self, path):
        self.expect(self.page).to_have_url(re.compile(re.escape(path) + r"$"))
