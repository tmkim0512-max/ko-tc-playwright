# 원본: examples/tc/08_unknown_element.tc | 변환: 1/3 스텝 | 등급: PARTIAL
# 생성물 — 직접 고치지 말고 .tc 를 고친 뒤 다시 변환한다.
import pytest
from tc2pw.runtime import R, Unsupported

pytestmark = pytest.mark.skip(reason='partial: 미지원 스텝 2개')


def _prep(page, r):
    r.step(7, 'open'); page.goto('https://the-internet.herokuapp.com/login')


def test_아이디_저장을_체크하면_체크_상태가_된다(page):
    r = R(page); _prep(page, r); r.enter_body()
    # TODO(unsupported): [아이디 저장]을 체크한다.
    r.step(10, 'unsupported'); raise Unsupported('unresolved: [아이디 저장] 요소가 현재 화면 <로그인> 에 없다')
    # TODO(unsupported): [아이디 저장]이 체크되어 있는지 확인한다.
    r.step(11, 'unsupported'); raise Unsupported('unresolved: [아이디 저장] 요소가 현재 화면 <로그인> 에 없다')
