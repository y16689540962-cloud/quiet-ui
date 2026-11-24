#!/usr/bin/env python3
"""Self-checks for quiet-ui's audit script.

Each fixture states what must and must not be reported, so a change to the
heuristics that silently loses a rule shows up as a failing test instead of a
quietly smaller number.

    python3 tests/run_tests.py
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
AUDIT = os.path.join(SKILL, "scripts", "audit_copy.py")
FIXTURES = os.path.join(HERE, "fixtures")

# fixture -> (rules that must appear, expected total tells)
CASES = {
    "t-shadcn.tsx": ({"R20-description"}, 1),
    "t-notice.html": ({"R19-notice"}, 1),
    "t-arrow.html": ({"R21-arrow"}, 1),
    "t-clean.html": (set(), 0),
}


def run(path):
    out = subprocess.run([sys.executable, AUDIT, path, "--json"],
                         capture_output=True, text=True)
    if out.returncode not in (0, 1):
        raise SystemExit("audit failed on {}:\n{}".format(path, out.stderr))
    return json.loads(out.stdout)[0]


def main():
    failed = 0
    for name, (must, total) in sorted(CASES.items()):
        path = os.path.join(FIXTURES, name)
        report = run(path)
        rules = {f["rule"] for f in report["findings"]}
        problems = []
        for rule in sorted(must - rules):
            problems.append("missing " + rule)
        for rule in sorted(rules - must):
            problems.append("unexpected " + rule)
        if report["tells"] != total:
            problems.append("tells={} want {}".format(report["tells"], total))
        status = "FAIL" if problems else "ok  "
        if problems:
            failed += 1
        print("{}  {:<18} {}".format(status, name, "; ".join(problems) or "as expected"))
    print("\n{}/{} passed".format(len(CASES) - failed, len(CASES)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
