# 원본: examples/tc/03_dropdown.tc | 변환: 3/3 스텝 | 등급: FULL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
from tc2pw.runtime import R


def _prep(page, r):
    r.step(6, 'open'); page.goto('https://the-internet.herokuapp.com/dropdown')


def test_옵션을_고르면_값이_바뀐다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(9, 'choose'); page.locator('#dropdown').select_option(label='Option 2')
    r.step(10, 'value_is'); r.expect(page.locator('#dropdown')).to_have_value('2')
