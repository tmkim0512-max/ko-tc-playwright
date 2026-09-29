""".tc 파일 파서와 분류 규칙표.

한 줄은 정확히 한 kind 가 된다. 규칙표를 위에서 아래로 검사해 첫 매치를 채택하고,
어떤 규칙에도 맞지 않으면 unsupported 가 된다. 확인 계열을 조작 계열보다 먼저 검사한다.
"""
import re
from dataclasses import dataclass, field


class ParseError(ValueError):
    pass


EL = r"\[(?P<el>[^\]]+)\]"                      # [요소]
SC = r"<(?P<sc>[^>]+)>"                         # <화면>
STR = r'"(?P<val>(?:[^"\\]|\\.)*)"'             # "값" — 안의 따옴표는 \"
VAL = rf"(?:{STR}|\{{env:(?P<env>[A-Za-z_]\w*)\}})"


def _j(a, b):  # 받침 유무에 따른 조사 두 형태
    return f"(?:{a}|{b})"


RULES = [(kind, re.compile(pattern + r"\.?")) for kind, pattern in [
    ("see",       rf"{EL}{_j('이', '가')} 보이는지 확인한다"),
    ("text_has",  rf"{EL}에 {STR}{_j('이', '가')} 있는지 확인한다"),
    ("value_is",  rf"{EL}의 값이 {STR}인지 확인한다"),
    ("checked",   rf"{EL}{_j('이', '가')} (?P<state>체크|체크 해제)되어 있는지 확인한다"),
    ("screen_is", rf"{SC} 화면인지 확인한다"),
    ("open",      rf"{SC}{_j('을', '를')} 연다"),
    ("click",     rf"{EL}{_j('을', '를')} 누른다"),
    ("type",      rf"{EL}에 {VAL}{_j('을', '를')} 입력한다"),
    ("choose",    rf"{EL}에서 {STR}{_j('을', '를')} 고른다"),
    ("set_check", rf"{EL}{_j('을', '를')} (?P<state>체크|체크 해제)한다"),
]]
KINDS = [k for k, _ in RULES] + ["unsupported"]


@dataclass
class Step:
    n: int                 # .tc 파일의 줄 번호
    raw: str
    kind: str
    args: dict


@dataclass
class Block:
    name: str | None       # None = 준비 블록
    steps: list = field(default_factory=list)


@dataclass
class TC:
    title: str
    site: str
    tag: str
    prep: Block | None
    checks: list


def classify(line, n=0):
    for kind, rx in RULES:
        if m := rx.fullmatch(line):
            args = {k: v for k, v in m.groupdict().items() if v is not None}
            if "val" in args:
                args["val"] = re.sub(r"\\(.)", r"\1", args["val"])
            return Step(n, line, kind, args)
    return Step(n, line, "unsupported", {"reason": "no_rule"})


def parse(text, name="<tc>"):
    head, prep, checks, cur = {}, None, [], None
    for n, line in enumerate(text.splitlines(), 1):
        line = re.sub(r"(^|\s)//.*$", "", line).strip()
        if not line:
            continue
        if m := re.fullmatch(r"#\s*제목:\s*(.+)", line):
            head["제목"] = m[1]
        elif m := re.fullmatch(r"(화면맵|태그):\s*(.+)", line):
            head[m[1]] = m[2]
        elif line == "## 준비":
            if prep or checks:
                raise ParseError(f"{name}:{n}: 준비 블록은 맨 앞에 한 번만 올 수 있다")
            cur = prep = Block(None)
        elif m := re.fullmatch(r"## 확인:\s*(.+)", line):
            if any(b.name == m[1] for b in checks):
                raise ParseError(f"{name}:{n}: 확인 블록 이름 중복: {m[1]}")
            cur = Block(m[1])
            checks.append(cur)
        elif line.startswith("#"):
            raise ParseError(f"{name}:{n}: 알 수 없는 머리글: {line}")
        elif cur is None:
            raise ParseError(f"{name}:{n}: 블록 밖의 스텝: {line}")
        else:
            cur.steps.append(classify(line, n))
    missing = [k for k in ("제목", "화면맵", "태그") if k not in head]
    if missing:
        raise ParseError(f"{name}: 머리글 누락: {', '.join(missing)}")
    if head["태그"] not in ("읽기", "쓰기"):
        raise ParseError(f"{name}: 태그는 읽기 또는 쓰기: {head['태그']}")
    if not checks:
        raise ParseError(f"{name}: 확인 블록이 하나 이상 있어야 한다")
    return TC(head["제목"], head["화면맵"], head["태그"], prep, checks)
