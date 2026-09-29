# 원본: examples/tc/07_drag_and_drop.tc | 변환: 2/3 스텝 | 등급: PARTIAL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
import pytest
from tc2pw.runtime import R, Unsupported

pytestmark = pytest.mark.skip(reason='partial: 미지원 스텝 1개')


def _prep(page, r):
    r.step(7, 'open'); page.goto('https://the-internet.herokuapp.com/drag_and_drop')


def test_A_칸을_B_칸으로_옮기면_순서가_바뀐다(page):
    r = R(page); _prep(page, r); r.enter_body()
    # TODO(unsupported): [A 칸]을 [B 칸]으로 끌어다 놓는다.
    r.step(10, 'unsupported'); raise Unsupported('no_rule')
    r.step(11, 'text_has'); r.expect(page.locator('#column-a header')).to_contain_text('B')
