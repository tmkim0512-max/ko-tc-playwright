# 원본: examples/tc/02_checkboxes.tc | 변환: 7/7 스텝 | 등급: FULL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
from tc2pw.runtime import R


def _prep(page, r):
    r.step(6, 'open'); page.goto('https://the-internet.herokuapp.com/checkboxes')


def test_첫_번째_체크박스를_체크할_수_있다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(9, 'checked'); r.expect(page.locator('#checkboxes input >> nth=0')).to_be_checked(checked=False)
    r.step(10, 'set_check'); page.locator('#checkboxes input >> nth=0').check()
    r.step(11, 'checked'); r.expect(page.locator('#checkboxes input >> nth=0')).to_be_checked(checked=True)


def test_두_번째_체크박스를_해제할_수_있다(page):
    r = R(page); _prep(page, r); r.enter_body()
    r.step(14, 'checked'); r.expect(page.locator('#checkboxes input >> nth=1')).to_be_checked(checked=True)
    r.step(15, 'set_check'); page.locator('#checkboxes input >> nth=1').uncheck()
    r.step(16, 'checked'); r.expect(page.locator('#checkboxes input >> nth=1')).to_be_checked(checked=False)
