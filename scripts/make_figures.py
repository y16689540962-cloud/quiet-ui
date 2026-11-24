#!/usr/bin/env python3
"""Rebuild the README figures from the screenshots in /tmp/fig.

Labels are bilingual on purpose: one set of images serves README.md,
README.en.md and README.ja.md.

    python3 scripts/make_figures.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

SRC = "/tmp/fig"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT = "/System/Library/Fonts/PingFang.ttc"

BG = (245, 244, 241)
CARD = (255, 255, 255)
LINE = (219, 217, 211)
RED = (209, 66, 53)
GREEN = (41, 116, 80)
AMBER = (163, 105, 28)
INK = (38, 38, 35)
MUTE = (122, 120, 115)
ARROW = (72, 71, 67)


def font(size, bold=False):
    for idx in ((4, 1) if bold else (0,)):
        try:
            return ImageFont.truetype(FONT, size, index=idx)
        except Exception:
            pass
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", size)


def width(draw, text, f):
    return draw.textbbox((0, 0), text, font=f)[2]


def pair(left, right, cap_l, cap_r, note_l, note_r, out):
    """Before/after pair with a label, an arrow and a short reading of each side."""
    li = Image.open(left).convert("RGB")
    ri = Image.open(right).convert("RGB")
    col, pad, gap = 600, 30, 176
    fit = lambda im: im.resize((col, int(im.height * col / im.width)), Image.LANCZOS)
    li, ri = fit(li), fit(ri)
    top = 86
    canvas = Image.new("RGB", (pad * 2 + col * 2 + gap, top + max(li.height, ri.height) + pad), BG)
    d = ImageDraw.Draw(canvas)
    f_cap, f_note, f_arrow = font(22, True), font(15), font(15)

    for i, (im, cap, note, colour) in enumerate(((li, cap_l, note_l, RED), (ri, cap_r, note_r, GREEN))):
        x = pad + i * (col + gap)
        d.text((x, pad - 4), cap, font=f_cap, fill=colour)
        d.text((x + width(d, cap, f_cap) + 10, pad + 6), note, font=f_note, fill=colour)
        d.rectangle([x - 1, top - 1, x + col + 1, top + im.height + 1], fill=CARD, outline=LINE)
        canvas.paste(im, (x, top))

    ymid = top + min(li.height, ri.height) // 2
    x1, x2 = pad + col + 20, pad + col + gap - 20
    d.line([(x1, ymid), (x2 - 16, ymid)], fill=ARROW, width=3)
    d.polygon([(x2, ymid), (x2 - 17, ymid - 9), (x2 - 17, ymid + 9)], fill=ARROW)
    for text, dy in (("same prompt", -42), ("one standing rule added", 18)):
        d.text((x1 + (x2 - x1 - width(d, text, f_arrow)) // 2, ymid + dy), text, font=f_arrow, fill=MUTE)

    canvas.save(os.path.join(OUT, out), optimize=True)
    print(out, canvas.size)


def missed(rows, out):
    """Three traces the scanner cannot see, cropped out of the raw screenshots."""
    iw, pad, txt, gap = 460, 28, 540, 16
    height = pad * 2 + 78 + sum(max(int(im.height * iw / im.width), 84) + gap for _, im, _ in rows) - gap
    canvas = Image.new("RGB", (pad * 2 + iw + 36 + txt, height), BG)
    d = ImageDraw.Draw(canvas)

    d.text((pad, pad), "The scanner reported 4. These three were missed.", font=font(19, True), fill=INK)
    d.text((pad, pad + 30), "扫描器报了 4 条，这三处都没报。", font=font(14), fill=MUTE)

    y = pad + 78
    for title_cn, im, note in rows:
        h = int(im.height * iw / im.width)
        im = im.resize((iw, h), Image.LANCZOS)
        d.rectangle([pad - 1, y - 1, pad + iw + 1, y + im.height + 1], fill=CARD, outline=LINE)
        canvas.paste(im, (pad, y))
        tx = pad + iw + 36
        d.text((tx, y + 2), title_cn, font=font(16, True), fill=AMBER)
        line, lines = "", []
        for ch in note:
            if width(d, line + ch, font(14)) > txt:
                lines.append(line)
                line = ch
            else:
                line += ch
        lines.append(line)
        for i, ln in enumerate(lines[:3]):
            d.text((tx, y + 32 + i * 22), ln, font=font(14), fill=INK)
        y += max(im.height, 84) + gap

    d.text((pad, height - pad - 14), "0 hits is not the same as clean. 0 条不等于干净。", font=font(14), fill=MUTE)
    canvas.save(os.path.join(OUT, out), optimize=True)
    print(out, canvas.size)


def main():
    if not os.path.isdir(SRC):
        sys.exit("screenshots not found: " + SRC + " (run the capture step first)")

    pair(os.path.join(SRC, "A-landing-clean.png"), os.path.join(SRC, "B-landing.png"),
         "Before", "After", "44 visible text runs", "15",
         "landing-annotated.png")
    pair(os.path.join(SRC, "A-auth.png"), os.path.join(SRC, "B-auth.png"),
         "Before", "After", "3 hits", "0",
         "auth-annotated.png")

    L = Image.open(os.path.join(SRC, "A-landing-clean.png")).convert("RGB")
    A = Image.open(os.path.join(SRC, "A-auth.png")).convert("RGB")
    missed([
        ("↓ arrow / 箭头", L.crop((60, 438, 560, 497)), "箭头是 CSS 伪元素画的，不是文本，扫描器读不到"),
        ("✓ bullets / 要点列表", A.crop((44, 428, 540, 565)), "三行带勾的卖点有文本，但没有对应规则"),
        ("footer line / 页脚标语", L.crop((860, 1740, 1260, 1806)), "有文本，在页脚，但不在 Made with / Powered by 那组词里"),
    ], "missed-by-scanner.png")


if __name__ == "__main__":
    main()
