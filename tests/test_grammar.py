import pytest

from tc2pw.grammar import KINDS, ParseError, classify, parse

POSITIVE = [
    ('[로그인 버튼]이 보이는지 확인한다.', "see", {"el": "로그인 버튼"}),
    ('[메뉴]가 보이는지 확인한다', "see", {"el": "메뉴"}),
    ('[알림]에 "안녕 \\"친구\\""가 있는지 확인한다.', "text_has", {"el": "알림", "val": '안녕 "친구"'}),
    ('[금액 칸]의 값이 "1,000"인지 확인한다.', "value_is", {"el": "금액 칸", "val": "1,000"}),
    ('[동의]가 체크되어 있는지 확인한다.', "checked", {"el": "동의", "state": "체크"}),
    ('[동의]가 체크 해제되어 있는지 확인한다.', "checked", {"el": "동의", "state": "체크 해제"}),
    ('<보안 화면> 화면인지 확인한다.', "screen_is", {"sc": "보안 화면"}),
    ('<로그인>을 연다.', "open", {"sc": "로그인"}),
    ('<체크박스>를 연다', "open", {"sc": "체크박스"}),
    ('[저장 버튼]을 누른다.', "click", {"el": "저장 버튼"}),
    ('[아이디 칸]에 "tomsmith"를 입력한다.', "type", {"el": "아이디 칸", "val": "tomsmith"}),
    ('[비밀번호 칸]에 {env:TI_PASSWORD}를 입력한다.', "type", {"el": "비밀번호 칸", "env": "TI_PASSWORD"}),
    ('[옵션 목록]에서 "Option 2"를 고른다.', "choose", {"el": "옵션 목록", "val": "Option 2"}),
    ('[동의]를 체크한다.', "set_check", {"el": "동의", "state": "체크"}),
    ('[동의]를 체크 해제한다.', "set_check", {"el": "동의", "state": "체크 해제"}),
]


@pytest.mark.parametrize("line,kind,args", POSITIVE)
def test_classify_positive(line, kind, args):
    step = classify(line)
    assert (step.kind, step.args) == (kind, args)


def test_every_rule_kind_has_a_positive_case():
    assert {k for _, k, _ in POSITIVE} == set(KINDS) - {"unsupported"}


@pytest.mark.parametrize("line", [
    "[A 칸]을 [B 칸]으로 끌어다 놓는다.",     # 규칙 없는 동작
    "로그인 버튼을 누른다.",                   # [요소] 표기 없음
    '[아이디 칸]에 tomsmith를 입력한다.',       # 값에 따옴표 없음
    "[저장 버튼]을 누르고 확인한다.",           # 문장 끝이 규칙과 다름
    '[알림]에 "x"가 있는지 본다.',
])
def test_classify_negative_is_unsupported(line):
    step = classify(line)
    assert (step.kind, step.args) == ("unsupported", {"reason": "no_rule"})


def test_check_rule_wins_over_manipulation_rule():
    # '체크' 가 들어간 확인 문장이 조작(set_check)으로 잘못 분류되면 단언이 사라진다.
    assert classify("[동의]가 체크되어 있는지 확인한다.").kind == "checked"


TC = """# 제목: 예시
화면맵: site
태그: 읽기

## 준비
<로그인>을 연다.   // 줄 끝 주석
// 줄 전체 주석
## 확인: 첫째
[버튼]을 누른다.
## 확인: 둘째
[버튼]이 보이는지 확인한다.
"""


def test_parse_blocks_and_line_numbers():
    tc = parse(TC)
    assert (tc.title, tc.site, tc.tag) == ("예시", "site", "읽기")
    assert [(s.n, s.kind) for s in tc.prep.steps] == [(6, "open")]
    assert [b.name for b in tc.checks] == ["첫째", "둘째"]
    assert [(s.n, s.kind) for s in tc.checks[1].steps] == [(11, "see")]


@pytest.mark.parametrize("text,msg", [
    (TC.replace("## 준비\n", ""), "블록 밖의 스텝"),
    (TC.replace("태그: 읽기\n", ""), "머리글 누락: 태그"),
    (TC.replace("태그: 읽기", "태그: 기타"), "태그는 읽기 또는 쓰기"),
    (TC.replace("## 확인: 둘째", "## 확인: 첫째"), "확인 블록 이름 중복"),
    (TC.split("## 확인")[0], "확인 블록이 하나 이상"),
    (TC + "## 준비\n", "준비 블록은 맨 앞에"),
])
def test_parse_errors(text, msg):
    with pytest.raises(ParseError, match=msg):
        parse(text)
