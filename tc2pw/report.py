"""convert.json + results.json → README 에 붙일 markdown (변환 표 · 실행 표).

두 표를 한 숫자로 합치지 않는다. 실행 표의 합계는 convert.json 의 확인 블록 전체와 맞아야 한다.
"""
import json
from collections import Counter
from pathlib import Path

VERDICTS = ["PASS", "FAIL", "BLOCKED", "INCONCLUSIVE", "NOT_RUN"]


def pct(a, b):
    return f"{a}/{b} = {a / b:.0%}" if b else f"{a}/0 = n/a"


def conversion(tcs):
    steps = sum(t["steps"] for t in tcs)
    done = sum(t["converted"] for t in tcs)
    full = sum(t["grade"] == "FULL" for t in tcs)
    out = ["### 변환 (정적 · 브라우저 불필요)", "",
           "| TC | FULL | PARTIAL | 스텝 | 변환된 스텝 | 스텝 변환률 | TC 변환률 (FULL/전체) |",
           "|---|---|---|---|---|---|---|",
           f"| {len(tcs)} | {full} | {len(tcs) - full} | {steps} | {done} | {pct(done, steps)} | {pct(full, len(tcs))} |"]
    todo = [(t["src"], d) for t in tcs for d in t["todo"]]
    if todo:
        out += ["", "변환하지 못한 스텝 (생성 코드에 `# TODO(unsupported)` + `raise Unsupported` 로 남는다):", "",
                "| 위치 | 사유 | 원문 |", "|---|---|---|"]
        out += [f"| `{src}:{d['line']}` | {d['reason']} | {d['raw']} |" for src, d in todo]
    return out


def execution(tcs, res):
    rows, meta = res["rows"], res["meta"]
    expected = {(t["module"], name) for t in tcs for name in t["tests"]}
    got = [(r["module"], r["test"]) for r in rows]
    if sorted(got) != sorted(expected):
        raise SystemExit(f"합계 불일치: convert.json 확인 블록 {len(expected)}개, "
                         f"results.json 기록 {len(got)}개 — 일부만 실행했으면 전체를 다시 실행한다")
    c = Counter(r["verdict"] for r in rows)
    assert sum(c[v] for v in VERDICTS) == len(rows), f"알 수 없는 판정: {c}"
    ran = len(rows) - c["NOT_RUN"]
    out = [f"### 실행 (확인 블록 {len(rows)}개 · {meta['started']} · {meta['browser']} · "
           f"{meta['platform']} · Python {meta['python']} · 커밋 {meta['commit'] or '없음'})", "",
           "| " + " | ".join(VERDICTS) + " | PASS/(PASS+FAIL) | PASS/실행 전체 |",
           "|" + "---|" * (len(VERDICTS) + 2),
           "| " + " | ".join(str(c[v]) for v in VERDICTS)
           + f" | {pct(c['PASS'], c['PASS'] + c['FAIL'])} | {pct(c['PASS'], ran)} |",
           "", "실행 전체 = NOT_RUN 을 뺀 블록 수.", "",
           "| TC | 확인 블록 | 판정 | 사유·단계 | 예외 | 멈춘 스텝 |", "|---|---|---|---|---|---|"]
    for r in rows:
        why = r["reason"] or r["phase"] or ""
        step = f"{r['fail_step']} ({r['fail_kind']})" if r["fail_step"] else ""
        out.append(f"| {r['module'].removeprefix('test_')} | {r['test'].removeprefix('test_')} | "
                   f"{r['verdict']} | {why} | {r['error_type'] or ''} | {step} |")
    return out


def render(out_dir):
    out = Path(out_dir)
    tcs = json.loads((out / "convert.json").read_text(encoding="utf-8"))["tcs"]
    lines = conversion(tcs) + [""]
    results = out / "results.json"
    if results.exists():
        lines += execution(tcs, json.loads(results.read_text(encoding="utf-8")))
    else:
        lines.append("### 실행: results.json 없음 — 아직 실행하지 않았다")
    return "\n".join(lines)
