# 원본: examples/tc/06_no_assert.tc | 변환: 2/2 스텝 | 등급: FULL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
from tc2pw.runtime import R


def _prep(page, r):
    r.step(7, 'open'); page.goto('https://the-internet.herokuapp.com/dropdown')


def test_옵션을_고른다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(10, 'choose'); page.locator('#dropdown').select_option(label='Option 1')
