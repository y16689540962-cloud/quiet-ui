#!/usr/bin/env python3
"""Annotate a page using the scanner's own findings, never a hand-picked list.

Usage: mark.py <page.html> <out.html>
"""
import json
import pathlib
import subprocess
import sys

JS = """
<script>
(function(){
  var marks = %s, placed = 0, W = document.documentElement.clientWidth;
  marks.forEach(function(m){
    var best = null, area = Infinity;
    document.querySelectorAll('body *').forEach(function(el){
      if (/^(SCRIPT|STYLE|SVG|PATH)$/.test(el.tagName)) return;
      var t = (el.textContent || '').trim();
      if (t.indexOf(m.key) === -1) return;
      var r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return;
      var a = r.width * r.height;
      if (a < area) { area = a; best = el; }
    });
    if (!best) return;
    placed++;
    var r = best.getBoundingClientRect();
    best.style.outline = '1.5px dashed #d94a3d';
    best.style.outlineOffset = '3px';
    var b = document.createElement('span');
    b.textContent = m.rule;
    b.style.cssText = 'position:absolute;z-index:99999;font:600 11px/1 ui-monospace,monospace;'
      + 'background:#d94a3d;color:#fff;padding:2px 5px;border-radius:3px;pointer-events:none;white-space:nowrap;';
    var left = scrollX + r.right + 5;
    if (left + 40 > W) left = scrollX + Math.max(r.left - 44, 2);
    b.style.left = left + 'px';
    b.style.top = (scrollY + r.top - 7) + 'px';
    document.body.appendChild(b);
  });
  var s = document.createElement('div');
  s.textContent = placed + ' 处命中';
  s.style.cssText = 'position:fixed;right:12px;top:12px;z-index:99998;font:600 12px/1.4 ui-monospace,monospace;'
    + 'background:#d94a3d;color:#fff;padding:4px 9px;border-radius:4px;';
  document.body.appendChild(s);
})();
</script>
"""


def main(page, out):
    audit = pathlib.Path(__file__).with_name("audit_copy.py")
    raw = subprocess.run([sys.executable, str(audit), page, "--json"],
                         capture_output=True, text=True, check=True).stdout
    findings = json.loads(raw)[0]["findings"]
    marks = []
    for f in findings:
        text = f["text"].strip()
        key = text[:14] if len(text) > 14 else text
        marks.append({"key": key, "rule": f["rule"].split("-")[0]})
    html = pathlib.Path(page).read_text(encoding="utf-8")
    html = html.replace("</body>", JS % json.dumps(marks, ensure_ascii=False) + "</body>")
    html = html.replace("</head>", "<style>*,*::before,*::after{animation:none!important;"
                                    "transition:none!important;opacity:1!important}</style></head>")
    pathlib.Path(out).write_text(html, encoding="utf-8")
    print("{}: {} findings -> {}".format(page, len(findings), out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
