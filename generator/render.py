"""Render Pattern Perfection social posts (1080x1350 JPEG) from a week spec JSON.

Usage:
    python3 generator/render.py weeks/2026-10-26.json [--out posts]

Each post in the spec becomes posts/<date>/01.jpg, 02.jpg, ...
Slide types: cover, point, cta, single_tip, question.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H = 1080, 1350
M = 96  # side margin

TEAL = (21, 80, 92)
TEAL_DARK = (14, 58, 68)
PINK = (244, 182, 166)
CORAL = (238, 139, 122)
CREAM = (251, 245, 238)
GRID = (238, 226, 214)
INK_SOFT = (70, 104, 112)


def serif(size):
    return ImageFont.truetype(str(FONTS / "DMSerifDisplay-Regular.ttf"), size)


def sans(size, weight=500):
    f = ImageFont.truetype(str(FONTS / "Montserrat[wght].ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def hand(size, weight=600):
    f = ImageFont.truetype(str(FONTS / "Caveat[wght].ttf"), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def symbol(size):
    return ImageFont.truetype(str(FONTS / "DejaVuSans.ttf"), size)


# ---------- helpers ----------

def wrap(draw, text, font, width):
    lines = []
    for para in text.split("\n"):
        words, cur = para.split(), ""
        for w in words:
            t = (cur + " " + w).strip()
            if draw.textlength(t, font=font) <= width:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def fit_text(draw, text, make_font, width, max_lines, start, minimum):
    size = start
    while size > minimum:
        f = make_font(size)
        lines = wrap(draw, text, f, width)
        if len(lines) <= max_lines:
            return f, lines, size
        size -= 4
    f = make_font(minimum)
    return f, wrap(draw, text, f, width), minimum


def fit_block(draw, text, make_font, width, top, bottom, spacing, start, minimum):
    """Largest font size whose wrapped text fits between top and bottom."""
    size = start
    while True:
        f = make_font(size)
        lines = wrap(draw, text, f, width)
        if len(lines) * int(size * spacing) <= bottom - top or size <= minimum:
            return f, lines, size
        size -= 2


def arrow(d, x, y, length, color, direction="right", width=5):
    if direction == "right":
        d.line([(x, y), (x + length, y)], fill=color, width=width)
        d.line([(x + length - 18, y - 14), (x + length, y), (x + length - 18, y + 14)], fill=color, width=width, joint="curve")
    else:
        d.line([(x, y), (x, y + length)], fill=color, width=width)
        d.line([(x - 14, y + length - 18), (x, y + length), (x + 14, y + length - 18)], fill=color, width=width, joint="curve")


def draw_lines(draw, lines, font, x, y, fill, spacing=1.18, size=None, align="left"):
    size = size or font.size
    for ln in lines:
        if align == "center":
            lx = (W - draw.textlength(ln, font=font)) / 2
        else:
            lx = x
        draw.text((lx, y), ln, font=font, fill=fill)
        y += int(size * spacing)
    return y


def paper(img, color=CREAM, grid=GRID):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=color)
    step = 54
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=grid, width=1)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=grid, width=1)
    for x in range(0, W, step * 4):
        d.line([(x, 0), (x, H)], fill=tuple(max(c - 10, 0) for c in grid), width=2)
    return d


def dashed(d, x1, x2, y, color, dash=18, gap=12, width=4):
    x = x1
    while x < x2:
        d.line([(x, y), (min(x + dash, x2), y)], fill=color, width=width)
        x += dash + gap


def cut_line(d, y, color=CORAL):
    d.text((M - 6, y - 30), "✂", font=symbol(46), fill=color)
    dashed(d, M + 56, W - M, y, color)


def pill(d, text, x, y, bg=PINK, fg=TEAL_DARK, size=26):
    f = sans(size, 700)
    t = text.upper()
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([x, y, x + tw + 44, y + size + 26], radius=(size + 26) // 2, fill=bg)
    d.text((x + 22, y + 11), t, font=f, fill=fg)
    return x + tw + 44


def logo(img, width, center_x, top, recolor=None):
    lg = Image.open(ROOT / "assets" / "logo.png").convert("RGBA")
    if recolor:
        r, g, b = recolor
        alpha = lg.split()[3]
        solid = Image.new("RGBA", lg.size, (r, g, b, 255))
        solid.putalpha(alpha)
        lg = solid
    h = int(lg.height * width / lg.width)
    lg = lg.resize((width, h), Image.LANCZOS)
    img.alpha_composite(lg, (int(center_x - width / 2), top))
    return top + h


def footer(d, page=None, total=None, fg=TEAL):
    f = sans(26, 600)
    d.text((M, H - 92), "@pattern_perfection", font=f, fill=fg)
    right = f"{page} / {total}" if page else "patternperfection.store"
    d.text((W - M - d.textlength(right, font=f), H - 92), right, font=f, fill=fg)


# ---------- icons (simple pattern-paper symbols) ----------

def icon(d, name, cx, cy, s=150, color=TEAL, accent=CORAL):
    w = 7
    if name == "grainline":
        d.line([(cx, cy - s), (cx, cy + s)], fill=color, width=w)
        for sgn in (-1, 1):
            tip = cy + sgn * s
            d.polygon([(cx, tip + sgn * 6), (cx - 26, tip - sgn * 44), (cx + 26, tip - sgn * 44)], fill=color)
    elif name == "fold":
        d.line([(cx - s, cy - s * 0.8), (cx - s, cy + s * 0.8)], fill=color, width=w)
        d.line([(cx - s, cy - s * 0.6), (cx + s * 0.6, cy - s * 0.6), (cx + s * 0.6, cy + s * 0.6), (cx - s, cy + s * 0.6)], fill=color, width=w)
        for yy in (cy - s * 0.6, cy + s * 0.6):
            d.polygon([(cx - s + 4, yy), (cx - s + 44, yy - 22), (cx - s + 44, yy + 22)], fill=accent)
        d.text((cx - s * 0.75, cy - 26), "FOLD", font=sans(44, 700), fill=accent)
    elif name == "notch":
        dashed(d, cx - s, cx + s, cy - 40, color, width=w)
        for nx in (cx - 40, cx + 40):
            d.polygon([(nx - 28, cy - 40), (nx + 28, cy - 40), (nx, cy + 30)], fill=accent)
        d.line([(cx - s, cy + 110), (cx + s, cy + 110)], fill=color, width=w)
        d.polygon([(cx - 28, cy + 110), (cx + 28, cy + 110), (cx, cy + 40)], fill=accent)
    elif name == "dart":
        d.line([(cx - s, cy + s * 0.7), (cx + s, cy + s * 0.7)], fill=color, width=w)
        top = (cx, cy - s * 0.8)
        dashed_tri = [((cx - 70, cy + s * 0.7), top), ((cx + 70, cy + s * 0.7), top)]
        for (a, b) in dashed_tri:
            n = 9
            for i in range(n):
                if i % 2 == 0:
                    p1 = (a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n)
                    p2 = (a[0] + (b[0] - a[0]) * (i + 1) / n, a[1] + (b[1] - a[1]) * (i + 1) / n)
                    d.line([p1, p2], fill=accent, width=w)
        d.ellipse([top[0] - 12, top[1] - 12, top[0] + 12, top[1] + 12], fill=color)
    elif name == "lengthen":
        d.line([(cx - s, cy - 30), (cx + s, cy - 30)], fill=color, width=w)
        d.line([(cx - s, cy + 30), (cx + s, cy + 30)], fill=color, width=w)
        d.text((cx - 150, cy - 112), "LENGTHEN / SHORTEN", font=sans(28, 700), fill=accent)
        d.line([(cx, cy - 150), (cx, cy + 150)], fill=accent, width=4)
    elif name == "grade":
        f = sans(30, 700)
        for i, (lab, off) in enumerate((("S", -60), ("M", 60))):
            dashed(d, cx - s, cx + s, cy + off, color if i else INK_SOFT, width=5)
            d.text((cx + s + 16, cy + off - 20), lab, font=f, fill=color)
        pts = []
        for i in range(41):
            t = i / 40
            x = cx - s + 2 * s * t
            y = cy - 60 + 120 * (3 * t * t - 2 * t * t * t)
            pts.append((x, y))
        d.line(pts, fill=accent, width=9, joint="curve")
    elif name == "dots":
        for (dx, dy, r) in ((-90, -60, 30), (70, -20, 22), (-10, 90, 38)):
            d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], outline=color, width=w)
            d.ellipse([cx + dx - 8, cy + dy - 8, cx + dx + 8, cy + dy + 8], fill=accent)
    elif name == "tape":
        d.rounded_rectangle([cx - s, cy - 40, cx + s, cy + 40], radius=12, fill=PINK, outline=color, width=4)
        for i in range(0, int(2 * s), 20):
            hgt = 28 if i % 100 == 0 else 14
            d.line([(cx - s + i, cy - 40), (cx - s + i, cy - 40 + hgt)], fill=color, width=3)
    elif name == "wash":
        d.line([(cx - s, cy - 60), (cx - s * 0.8, cy + 90), (cx + s * 0.8, cy + 90), (cx + s, cy - 60)], fill=color, width=w)
        for k in range(2):
            pts = [(cx - s * 0.85 + i * 8, cy - 20 + k * 40 + 14 * math.sin(i / 3)) for i in range(int(s * 1.7 / 8))]
            d.line(pts, fill=accent, width=6)
        d.text((cx - 32, cy + 110), "30°", font=sans(44, 700), fill=color)
    elif name == "question":
        d.text((cx - 70, cy - 170), "?", font=serif(300), fill=color)
    elif name == "scissors":
        d.text((cx - 110, cy - 130), "✂", font=symbol(220), fill=color)
    elif name == "hanger":
        d.arc([cx - 30, cy - s, cx + 30, cy - s + 60], 180, 90, fill=color, width=w)
        d.line([(cx, cy - s + 60), (cx - s, cy + 40), (cx + s, cy + 40), (cx, cy - s + 60)], fill=color, width=w)
    elif name == "size":
        f = sans(40, 700)
        for i, lab in enumerate(["XS", "S", "M", "L", "XL"]):
            x0 = cx - s - 30 + i * 72
            hh = 60 + i * 30
            d.rounded_rectangle([x0, cy + 90 - hh, x0 + 56, cy + 90], radius=8, fill=PINK if i % 2 else TEAL)
            tw = d.textlength(lab, font=sans(26, 700))
            d.text((x0 + 28 - tw / 2, cy + 104), lab, font=sans(26, 700), fill=color)


# ---------- slides ----------

def slide_cover(s, series):
    img = Image.new("RGBA", (W, H))
    d = paper(img)
    y = logo(img, 300, W / 2, 96)
    pill(d, series, M, y + 70)
    tf, tl, ts = fit_text(d, s["title"], serif, W - 2 * M, 4, 118, 70)
    y = draw_lines(d, tl, tf, M, y + 150, TEAL, 1.08, ts)
    cut_line(d, y + 40)
    if s.get("subtitle"):
        sf, sl, ss = fit_text(d, s["subtitle"], lambda z: sans(z, 500), W - 2 * M, 4, 38, 28)
        y = draw_lines(d, sl, sf, M, y + 90, INK_SOFT, 1.4, ss)
    free_top, free_bottom = y + 40, H - 220
    if s.get("icon") and free_bottom - free_top >= 300:
        icon(d, s["icon"], W - M - 190, (free_top + free_bottom) / 2, min(130, (free_bottom - free_top) / 2 - 20))
    hf = hand(64)
    d.text((M, H - 200), "Swipe", font=hf, fill=CORAL)
    arrow(d, M + d.textlength("Swipe", font=hf) + 18, H - 158, 70, CORAL)
    footer(d)
    return img


def slide_point(s, series, page, total):
    img = Image.new("RGBA", (W, H))
    d = paper(img)
    pill(d, series, M, 96)
    num = str(s.get("number", page - 1))
    d.ellipse([M, 200, M + 130, 330], fill=PINK)
    nw = d.textlength(num, font=serif(84))
    d.text((M + 65 - nw / 2, 212), num, font=serif(84), fill=TEAL)
    tf, tl, ts = fit_text(d, s["title"], serif, W - 2 * M, 3, 84, 56)
    y = draw_lines(d, tl, tf, M, 380, TEAL, 1.1, ts)
    if s.get("icon"):
        icon(d, s["icon"], W / 2, y + 200, 140)
        y += 410
    else:
        y += 40
    bf, bl, bs = fit_block(d, s["body"], lambda z: sans(z, 500), W - 2 * M, y + 20, H - 150, 1.45, 40, 26)
    draw_lines(d, bl, bf, M, y + 20, TEAL_DARK, 1.45, bs)
    footer(d, page, total)
    return img


def slide_cta(s, series, page, total):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=TEAL)
    for x in range(0, W, 54):
        d.line([(x, 0), (x, H)], fill=(31, 92, 104), width=1)
    for y in range(0, H, 54):
        d.line([(0, y), (W, y)], fill=(31, 92, 104), width=1)
    y = logo(img, 360, W / 2, 140, recolor=CREAM)
    tf, tl, ts = fit_text(d, s["title"], serif, W - 2 * M, 4, 96, 60)
    y = draw_lines(d, tl, tf, M, y + 130, CREAM, 1.1, ts, align="center")
    dashed(d, M + 80, W - M - 80, y + 40, PINK)
    bf, bl, bs = fit_text(d, s.get("body", ""), lambda z: sans(z, 500), W - 2 * M - 40, 6, 36, 28)
    y = draw_lines(d, bl, bf, M, y + 90, CREAM, 1.45, bs, align="center")
    btn = s.get("button", "patternperfection.store")
    f = sans(34, 700)
    tw = d.textlength(btn, font=f)
    bx = (W - tw) / 2 - 40
    d.rounded_rectangle([bx, H - 300, bx + tw + 80, H - 300 + 84], radius=42, fill=PINK)
    d.text((bx + 40, H - 300 + 22), btn, font=f, fill=TEAL_DARK)
    footer(d, page, total, fg=CREAM)
    return img


def slide_single_tip(s, series):
    img = Image.new("RGBA", (W, H))
    d = paper(img)
    pill(d, series, M, 96)
    tf, tl, ts = fit_text(d, s["title"], serif, W - 2 * M, 4, 104, 64)
    y = draw_lines(d, tl, tf, M, 200, TEAL, 1.08, ts)
    cut_line(d, y + 40)
    if s.get("icon"):
        icon(d, s["icon"], W / 2, y + 220, 130)
        y += 420
    else:
        y += 90
    card_top = y
    bf, bl, bs = fit_block(d, s["body"], lambda z: sans(z, 500), W - 2 * M - 80, card_top + 40, H - 170, 1.45, 38, 26)
    card_h = len(bl) * int(bs * 1.45) + 80
    d.rounded_rectangle([M, card_top, W - M, card_top + card_h], radius=28, fill=(255, 255, 255), outline=PINK, width=4)
    draw_lines(d, bl, bf, M + 40, card_top + 40, TEAL_DARK, 1.45, bs)
    footer(d)
    return img


def slide_question(s, series):
    img = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=PINK)
    for x in range(0, W, 54):
        d.line([(x, 0), (x, H)], fill=(236, 170, 154), width=1)
    for y in range(0, H, 54):
        d.line([(0, y), (W, y)], fill=(236, 170, 154), width=1)
    pill(d, series, M, 96, bg=TEAL, fg=CREAM)
    d.text((W - M - 190, 40), "?", font=serif(360), fill=(236, 160, 142))
    tf, tl, ts = fit_text(d, s["title"], serif, W - 2 * M, 5, 100, 62)
    y = draw_lines(d, tl, tf, M, 300, TEAL_DARK, 1.1, ts)
    dashed(d, M, W - M, y + 50, TEAL)
    if s.get("body"):
        bf, bl, bs = fit_text(d, s["body"], lambda z: sans(z, 600), W - 2 * M, 6, 38, 28)
        y = draw_lines(d, bl, bf, M, y + 100, TEAL_DARK, 1.45, bs)
    hf = hand(62)
    prompt = s.get("prompt", "Tell us in the comments").replace("↓", "").replace("→", "").strip()
    d.text((M, H - 210), prompt, font=hf, fill=TEAL)
    arrow(d, M + d.textlength(prompt, font=hf) + 30, H - 200, 50, TEAL, direction="down")
    footer(d, fg=TEAL_DARK)
    return img


def render_post(post, out_dir):
    out = Path(out_dir) / post["date"]
    out.mkdir(parents=True, exist_ok=True)
    series = post.get("series", "")
    slides = post["slides"]
    total = len(slides)
    paths = []
    for i, s in enumerate(slides, start=1):
        t = s["type"]
        if t == "cover":
            img = slide_cover(s, series)
        elif t == "point":
            img = slide_point(s, series, i, total)
        elif t == "cta":
            img = slide_cta(s, series, i, total)
        elif t == "single_tip":
            img = slide_single_tip(s, series)
        elif t == "question":
            img = slide_question(s, series)
        else:
            raise ValueError(f"unknown slide type {t}")
        p = out / f"{i:02d}.jpg"
        img.convert("RGB").save(p, "JPEG", quality=90, optimize=True, progressive=False)
        paths.append(p)
    return paths


def validate(post):
    fmt = post["format"]
    n = len(post["slides"])
    if fmt == "carousel" and n != 5:
        raise ValueError(f"{post['date']}: carousel must have exactly 5 slides, has {n}")
    if fmt == "single" and n != 1:
        raise ValueError(f"{post['date']}: single post must have exactly 1 slide, has {n}")
    tags = post["caption_ig"].count("#")
    if tags > 5:
        raise ValueError(f"{post['date']}: Instagram caption has {tags} hashtags, max 5")


def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    out_dir = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else str(ROOT / "posts")
    for post in spec["posts"]:
        validate(post)
        for p in render_post(post, out_dir):
            print(p)


if __name__ == "__main__":
    main()
