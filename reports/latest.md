### 변환 (정적 · 브라우저 불필요)

| TC | FULL | PARTIAL | 스텝 | 변환된 스텝 | 스텝 변환률 | TC 변환률 (FULL/전체) |
|---|---|---|---|---|---|---|
| 8 | 6 | 2 | 34 | 31 | 31/34 = 91% | 6/8 = 75% |

변환하지 못한 스텝 (생성 코드에 `# TODO(unsupported)` + `raise Unsupported` 로 남는다):

| 위치 | 사유 | 원문 |
|---|---|---|
| `examples/tc/07_drag_and_drop.tc:10` | no_rule | [A 칸]을 [B 칸]으로 끌어다 놓는다. |
| `examples/tc/08_unknown_element.tc:10` | unresolved: [아이디 저장] 요소가 현재 화면 <로그인> 에 없다 | [아이디 저장]을 체크한다. |
| `examples/tc/08_unknown_element.tc:11` | unresolved: [아이디 저장] 요소가 현재 화면 <로그인> 에 없다 | [아이디 저장]이 체크되어 있는지 확인한다. |

### 실행 (확인 블록 9개 · 2026-09-29T16:33:29+09:00 · chromium 153.0.8010.12 · macOS-26.3-arm64-arm-64bit-Mach-O · Python 3.14.7 · 커밋 6de4e28)

| PASS | FAIL | BLOCKED | INCONCLUSIVE | NOT_RUN | PASS/(PASS+FAIL) | PASS/실행 전체 |
|---|---|---|---|---|---|---|
| 3 | 1 | 2 | 1 | 2 | 3/4 = 75% | 3/7 = 43% |

실행 전체 = NOT_RUN 을 뺀 블록 수.

| TC | 확인 블록 | 판정 | 사유·단계 | 예외 | 멈춘 스텝 |
|---|---|---|---|---|---|
| 01_login_ok | 올바른_계정이면_보안_화면으로_간다 | PASS |  |  |  |
| 02_checkboxes | 첫_번째_체크박스를_체크할_수_있다 | BLOCKED | prep | TimeoutError | 6 (open) |
| 02_checkboxes | 두_번째_체크박스를_해제할_수_있다 | PASS |  |  |  |
| 03_dropdown | 옵션을_고르면_값이_바뀐다 | PASS |  |  |  |
| 04_wrong_expectation | 비밀번호가_틀리면_아이디_오류_문구가_보인다 | FAIL | body | AssertionError | 14 (text_has) |
| 05_old_selector | 옛_버튼_이름으로_로그인하면_보안_화면으로_간다 | BLOCKED | body | TimeoutError | 13 (click) |
| 06_no_assert | 옵션을_고른다 | INCONCLUSIVE | no_assert |  |  |
| 07_drag_and_drop | A_칸을_B_칸으로_옮기면_순서가_바뀐다 | NOT_RUN | partial |  |  |
| 08_unknown_element | 아이디_저장을_체크하면_체크_상태가_된다 | NOT_RUN | partial |  |  |
