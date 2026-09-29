# 원본: examples/tc/05_old_selector.tc | 변환: 5/5 스텝 | 등급: FULL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
from tc2pw.runtime import R


def _prep(page, r):
    r.step(8, 'open'); page.goto('https://the-internet.herokuapp.com/login')


def test_옛_버튼_이름으로_로그인하면_보안_화면으로_간다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(11, 'type'); page.locator('#username').fill('tomsmith')
    r.step(12, 'type'); page.locator('#password').fill(r.env('TI_PASSWORD'))
    r.step(13, 'click'); page.locator('#login-submit').click()
    r.step(14, 'screen_is'); r.expect_url_endswith('/secure')
