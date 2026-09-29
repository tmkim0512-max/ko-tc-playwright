import argparse
import sys

from tc2pw.emit import convert_dir
from tc2pw.report import render

p = argparse.ArgumentParser(prog="tc2pw", description="한국어 TC → Playwright pytest 변환기")
sub = p.add_subparsers(dest="cmd", required=True)
c = sub.add_parser("convert", help=".tc 디렉터리 → test_*.py + convert.json")
c.add_argument("tc_dir")
c.add_argument("--uimap", required=True)
c.add_argument("--out", required=True)
r = sub.add_parser("report", help="convert.json + results.json → markdown 표")
r.add_argument("out_dir")
args = p.parse_args()

if args.cmd == "convert":
    sys.exit(convert_dir(args.tc_dir, args.uimap, args.out))
print(render(args.out_dir))
