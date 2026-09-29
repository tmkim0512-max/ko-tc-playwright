# ko-tc-playwright

한국어로 쓴 수동 테스트 케이스를 규칙표로 분류해 Playwright(pytest) 코드로 바꾸고,
**변환률과 실제 실행 결과를 따로 보고하는** 작은 변환기.

- 미지원 문장은 버리지 않는다. 생성 코드에 `# TODO(unsupported)` + `raise Unsupported` 로 남고, 변환 표에 위치와 사유가 나온다.
- 실행 판정은 5가지로 나눈다. 기대와 달라서 실패한 것(FAIL)과, 확인 단계까지 가지 못한 것(BLOCKED)을 구분한다.
- "변환 91%" 는 "자동화 91%" 가 아니다. 두 숫자를 합치지 않는다.

## 입력 한 건 → 생성 코드

`examples/tc/01_login_ok.tc`

```
# 제목: 로그인 성공
화면맵: the-internet
태그: 읽기

## 준비
<로그인>을 연다.

## 확인: 올바른 계정이면 보안 화면으로 간다
[아이디 칸]에 "tomsmith"를 입력한다.
[비밀번호 칸]에 {env:TI_PASSWORD}를 입력한다.
[로그인 버튼]을 누른다.
<보안 화면> 화면인지 확인한다.
[알림 메시지]에 "You logged into a secure area!"가 있는지 확인한다.
```

`generated/test_01_login_ok.py` (변환기 출력 그대로)

```python
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
```

셀렉터와 URL 은 `examples/uimap.yaml` 에서 찾아 생성 시점에 코드에 넣는다. 환경변수만 실행 시점에 읽는다.
`r.step(n, kind)` 의 `n` 은 `.tc` 파일의 줄 번호다. 실패하면 판정 기록에 그 줄이 남는다.

## 판정 규칙

| 판정 | 조건 |
|---|---|
| PASS | 예외 없음, 확인 블록 본문의 단언이 1개 이상 |
| FAIL | 본문에서 `AssertionError` (Playwright `expect` 실패 포함). **FAIL 은 이 경우뿐이다** |
| BLOCKED | 그 밖의 모든 예외: 준비 구간 오류, 타임아웃, strict 위반, 환경변수 없음, fixture 오류 |
| INCONCLUSIVE | 예외 없음, 본문 단언 0개 (`reason=no_assert`). PASS 로 세지 않는다 |
| NOT_RUN | 미지원 스텝이 있는 TC(PARTIAL)의 블록 (`reason=partial`) |

pytest 의 passed/failed 와는 따로 센다. 준비 구간의 단언은 PASS 근거에 넣지 않는다.
보고서는 `convert.json` 의 확인 블록 목록과 `results.json` 의 기록이 정확히 일치하지 않으면 멈춘다(`pytest -k` 로 일부만 돌린 결과를 전체처럼 보고하지 않게).

## 실측 결과

- 일시: 2026-09-29 (KST), 환경: macOS 26.3 arm64 · Python 3.14.7 · Playwright 1.63.0 · Chromium 153.0.8010.12 (headless)
- 대상: 공개 연습 사이트 `the-internet.herokuapp.com`
- 명령:
  ```
  python -m tc2pw convert examples/tc --uimap examples/uimap.yaml --out generated
  TI_PASSWORD='SuperSecretPassword!' pytest generated -p tc2pw.plugin
  python -m tc2pw report generated > reports/latest.md
  ```

예제 8건 중 04~08 은 **의도적 재현 케이스**다. 판정 종류가 실제로 나뉘는 것을 보여 주려고 만들었다.
04: 기대 문구를 일부러 틀리게 적음(FAIL), 05: 화면에 없는 셀렉터(BLOCKED), 06: 확인 스텝 없음(INCONCLUSIVE), 07: 규칙 없는 문장(PARTIAL), 08: UI맵에 없는 요소(PARTIAL).

### 변환 (정적 · 브라우저 불필요)

| TC | FULL | PARTIAL | 스텝 | 변환된 스텝 | 스텝 변환률 | TC 변환률 (FULL/전체) |
|---|---|---|---|---|---|---|
| 8 | 6 | 2 | 34 | 31 | 31/34 = 91% | 6/8 = 75% |

### 실행 (커밋된 `generated/results.json`, 커밋 6de4e28 기준)

| PASS | FAIL | BLOCKED | INCONCLUSIVE | NOT_RUN | PASS/(PASS+FAIL) | PASS/실행 전체 |
|---|---|---|---|---|---|---|
| 3 | 1 | 2 | 1 | 2 | 3/4 = 75% | 3/7 = 43% |

블록별 판정은 [`reports/latest.md`](reports/latest.md) 에 있다. 이 회차의 BLOCKED 2건 중 1건은 의도한 05 이고,
1건은 02 첫 블록의 `page.goto` 가 10초 안에 끝나지 않은 **네트워크 타임아웃**이다. 결과를 고르지 않고 그대로 커밋했다.

### 같은 명령 4회 반복 (같은 날, 같은 환경)

| 회차 | PASS | FAIL | BLOCKED | INCONCLUSIVE | NOT_RUN | 의도 외 BLOCKED |
|---|---|---|---|---|---|---|
| 1 | 4 | 1 | 1 | 1 | 2 | 없음 |
| 2 | 3 | 1 | 2 | 1 | 2 | 02 준비 구간 `goto` 타임아웃 (05 도 준비 구간에서 타임아웃) |
| 3 | 4 | 1 | 1 | 1 | 2 | 없음 |
| 4 (커밋본) | 3 | 1 | 2 | 1 | 2 | 02 준비 구간 `goto` 타임아웃 |

의도한 분포(PASS 4 · FAIL 1 · BLOCKED 1 · INCONCLUSIVE 1 · NOT_RUN 2)는 4회 중 2회 나왔다.
나머지 2회는 네트워크 지연이 BLOCKED 로 잡혔고, FAIL 로 섞이지 않았다.

## TC 문법

- 머리글 3줄: `# 제목:`, `화면맵:`(UI맵 사이트 키), `태그:`(`읽기` | `쓰기`, 보고 분류용)
- 블록: `## 준비` 0~1개, `## 확인: <이름>` 1개 이상. 확인 블록 하나가 pytest 함수 하나가 되고, 함수마다 준비 블록을 먼저 실행한다. 블록끼리 상태를 공유하지 않는다.
- 참조: `[요소]`, `<화면>`, `"값"`(안의 따옴표는 `\"`), `{env:NAME}`(없으면 BLOCKED). `//` 뒤는 주석.
- 조사는 받침에 따른 두 형태(을/를, 이/가)를 모두 받는다.

분류표 (위에서부터 검사, 첫 매치 채택. 확인 문장을 조작 문장보다 먼저 검사한다):

| kind | 문장 | 생성 동작 |
|---|---|---|
| `see` | `[X]가 보이는지 확인한다` | `to_be_visible` |
| `text_has` | `[X]에 "V"가 있는지 확인한다` | `to_contain_text` |
| `value_is` | `[X]의 값이 "V"인지 확인한다` | `to_have_value` |
| `checked` | `[X]가 체크되어 / 체크 해제되어 있는지 확인한다` | `to_be_checked` |
| `screen_is` | `<화면> 화면인지 확인한다` | URL 이 화면 path 로 끝나는지 |
| `open` | `<화면>을 연다` | `goto(base_url + path)` |
| `click` | `[X]을 누른다` | `click` |
| `type` | `[X]에 "V" / {env:N}를 입력한다` | `fill` |
| `choose` | `[X]에서 "V"를 고른다` | `select_option(label=V)` |
| `set_check` | `[X]을 체크한다 / 체크 해제한다` | `check` / `uncheck` |
| `unsupported` | 위 어디에도 맞지 않는 줄, 또는 UI맵에서 못 찾은 참조 | `# TODO(unsupported)` + `raise Unsupported` |

요소는 **현재 화면**(가장 최근에 `open` 하거나 `screen_is` 로 확인한 화면)의 UI맵에서만 찾는다.
셀렉터 문자열은 `page.locator()` 에 그대로 넘긴다. 여러 개가 잡히면 strict 위반으로 BLOCKED 가 된다.

## 지표 정의

- 스텝 변환률 = 변환된 스텝 / 전체 스텝. TC 등급은 FULL(미지원 0) 또는 PARTIAL. TC 변환률 = FULL / 전체 TC.
- 실행은 확인 블록 단위로 센다. PASS 율은 `PASS/(PASS+FAIL)` 과 `PASS/실행 전체`(NOT_RUN 제외)를 함께 적는다.
- `convert` 종료 코드: 0 전부 FULL, 1 PARTIAL 있음(생성은 끝까지 함), 2 파싱 오류.

## 구조

```
tc2pw/grammar.py   104  .tc 파서, 분류 규칙표
tc2pw/emit.py      117  UI맵 해석, 코드 생성, convert.json
tc2pw/runtime.py    45  생성 코드가 쓰는 R: 스텝 기록, 단언 횟수, 환경변수
tc2pw/plugin.py     81  pytest 판정 플러그인 → results.json
tc2pw/report.py     67  변환 표 + 실행 표
tests/                  단위 테스트 39개 (브라우저 없이 실행)
examples/               TC 8건 + uimap.yaml
generated/              생성 코드, convert.json, results.json (커밋함)
```

```
pip install -e . && python -m playwright install chromium
pytest            # 단위 테스트
```

CI 는 push·PR 마다 단위 테스트를 돌리고, `generated/` 가 변환기 출력과 같은지 확인한다. 라이브 실행은 수동(`workflow_dispatch`, `live=true`)일 때만 돈다.

## 한계

- 외부 데모 사이트에 의존한다. 위 반복 실측처럼 네트워크 상태에 따라 BLOCKED 가 늘 수 있다. 동작 타임아웃은 10초다(`R(page, timeout_ms=…)`).
- 자연어 이해가 아니라 규칙 매칭이다. 분류표에 없는 문장은 변환하지 않는다.
- 조건 분기, 반복, 대화상자, 새 창, 파일 업로드, 변수 저장은 넣지 않았다. 필요한 TC 가 생기면 규칙과 런타임을 한 줄씩 늘리는 구조다.
- 병렬 실행을 지원하지 않는다(판정 플러그인이 현재 테스트 상태를 전역 1개로 읽는다).
- BLOCKED 에 남는 예외 이름과 멈춘 줄은 원인 분류의 입력으로 쓸 수 있지만, 자동 재시도나 자동 수정은 하지 않는다.

## Related

- [pom-scout](https://github.com/tmkim0512-max/pom-scout) — 웹 앱을 탐색해 화면 모델(Page Object JSON)과 유일성 검증된 셀렉터 수집
- [evidence-gated-e2e-loop](https://github.com/tmkim0512-max/evidence-gated-e2e-loop) — AI가 쓴 Playwright 테스트를 파일 증거로만 채택하고 AI 없이 재실행
- [false-green-guard](https://github.com/tmkim0512-max/false-green-guard) — 테스트를 무력화해 초록불을 만드는 diff를 탐지하고, 격리 사본에서 수정을 재판정
- [parking-api-qa-lab](https://github.com/tmkim0512-max/parking-api-qa-lab) — 주차 API를 pytest·자체 Mock 서버·k6 합격 기준·GitHub Actions로 검증하는 QA 실습

## License

MIT © Taemin Kim
