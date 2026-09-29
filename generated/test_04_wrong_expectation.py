# 원본: examples/tc/04_wrong_expectation.tc | 변환: 5/5 스텝 | 등급: FULL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
from tc2pw.runtime import R


def _prep(page, r):
    r.step(8, 'open'); page.goto('https://the-internet.herokuapp.com/login')


def test_비밀번호가_틀리면_아이디_오류_문구가_보인다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(11, 'type'); page.locator('#username').fill('tomsmith')
    r.step(12, 'type'); page.locator('#password').fill('wrong-password')
    r.step(13, 'click'); page.locator('button[type=submit]').click()
    r.step(14, 'text_has'); r.expect(page.locator('#flash')).to_contain_text('Your username is invalid!')
