# 원본: examples/tc/01_login_ok.tc | 변환: 6/6 스텝 | 등급: FULL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
from tc2pw.runtime import R


def _prep(page, r):
    r.step(6, 'open'); page.goto('https://the-internet.herokuapp.com/login')


def test_올바른_계정이면_보안_화면으로_간다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(9, 'type'); page.locator('#username').fill('tomsmith')
    r.step(10, 'type'); page.locator('#password').fill(r.env('TI_PASSWORD'))
    r.step(11, 'click'); page.locator('button[type=submit]').click()
    r.step(12, 'screen_is'); r.expect_url_endswith('/secure')
    r.step(13, 'text_has'); r.expect(page.locator('#flash')).to_contain_text('You logged into a secure area!')
