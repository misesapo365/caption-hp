from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

S = 2
W = 430 * S

INK = (35, 27, 21)
MUTED = (118, 103, 90)
PAPER = (248, 242, 232)
PAPER2 = (255, 250, 241)
COFFEE = (58, 36, 23)
GOLD = (185, 138, 74)
WHITE = (255, 250, 240)
LINE = (214, 202, 185)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
GOTHIC = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"


def font(size, gothic=False):
    return ImageFont.truetype(GOTHIC if gothic else MINCHO, size * S)


def sc(v):
    return int(round(v * S))


def canvas(h, dark=False):
    img = Image.new("RGB", (W, sc(h)), (20, 14, 10) if dark else PAPER)
    if not dark:
        d = ImageDraw.Draw(img, "RGBA")
        for y in range(img.height):
            t = y / max(1, img.height - 1)
            r = int(PAPER2[0] * (1 - t) + PAPER[0] * t)
            g = int(PAPER2[1] * (1 - t) + PAPER[1] * t)
            b = int(PAPER2[2] * (1 - t) + PAPER[2] * t)
            d.line([(0, y), (W, y)], fill=(r, g, b, 255))
        d.ellipse((sc(-110), sc(-90), sc(240), sc(250)), fill=(255, 255, 255, 95))
    return img


def cover(path, size):
    im = Image.open(path).convert("RGB")
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    return im.crop(((nw - tw) // 2, (nh - th) // 2, (nw + tw) // 2, (nh + th) // 2))


def paste_round(base, im, xy, radius=8, shadow=True):
    x, y = map(sc, xy)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle((0, 0, im.width, im.height), radius=sc(radius), fill=(40, 24, 10, 58))
        sh = sh.filter(ImageFilter.GaussianBlur(sc(12)))
        base.paste(sh, (x, y + sc(6)), sh)
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, im.width, im.height), radius=sc(radius), fill=255)
    base.paste(im, (x, y), mask)


def text(draw, xy, s, size=13, fill=INK, gothic=False, spacing=8, max_width=None, line_h=1.75):
    x, y = map(sc, xy)
    f = font(size, gothic)
    lines = []
    for raw in s.split("\n"):
        if not max_width:
            lines.append(raw)
            continue
        cur = ""
        for ch in raw:
            test = cur + ch
            if draw.textlength(test, font=f) <= sc(max_width) or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = ch
        lines.append(cur)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += int(size * S * line_h) + sc(spacing)
    return y // S


def button(draw, xy, label, dark=False, w=214):
    x, y = map(sc, xy)
    h = sc(46)
    fill = WHITE if dark else (255, 255, 255, 206)
    outline = (255, 255, 255, 0) if dark else (70, 50, 35, 145)
    draw.rounded_rectangle((x, y, x + sc(w), y + h), radius=h // 2, fill=fill, outline=outline, width=sc(1))
    f = font(13, gothic=True)
    tw = draw.textlength(label, font=f)
    draw.text((x + (sc(w) - tw) / 2 - sc(8), y + sc(14)), label, font=f, fill=COFFEE if dark else INK)
    draw.text((x + sc(w) - sc(44), y + sc(12)), "→", font=font(15, gothic=True), fill=COFFEE if dark else INK)


def overlay_gradient(im, left_dark=True, alpha=185):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for x in range(im.width):
        t = x / max(1, im.width - 1)
        a = int(alpha * (1 - t * .72 if left_dark else t))
        d.line([(x, 0), (x, im.height)], fill=(0, 0, 0, a))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def logo(draw, y=24, dark=True):
    col = WHITE if dark else INK
    x = sc(26)
    cy = sc(y + 14)
    r = sc(14)
    draw.ellipse((x, cy - r, x + 2 * r, cy + r), outline=col, width=sc(2))
    draw.line((x + sc(5), cy - sc(9), x + sc(23), cy + sc(9)), fill=col, width=sc(2))
    draw.line((x + sc(5), cy + sc(9), x + sc(23), cy - sc(9)), fill=col, width=sc(2))
    draw.text((sc(64), sc(y + 2)), "喫茶キャプテン", font=font(16), fill=col)
    draw.line((sc(814), sc(y + 4), sc(834), sc(y + 4)), fill=col, width=sc(1))
    draw.line((sc(814), sc(y + 12), sc(834), sc(y + 12)), fill=col, width=sc(1))
    draw.line((sc(814), sc(y + 20), sc(834), sc(y + 20)), fill=col, width=sc(1))


def save(img, name):
    path = OUT / name
    img.save(path, quality=96)
    return path


paths = []

# 01 Hero
img = cover(ASSETS / "hero.jpg", (W, sc(760)))
img = overlay_gradient(img, True, 215)
d = ImageDraw.Draw(img, "RGBA")
logo(d)
text(d, (35, 134), "那珂川の風景に、\n静かに寄り添う\n喫茶店。", 30, fill=WHITE, spacing=5, line_h=1.25)
text(d, (35, 330), "1980年から続く、変わらない時間。\n地域の皆さまの毎日に、ほっと息をつける一杯を。", 13, fill=(245, 232, 215), spacing=4)
button(d, (35, 642), "お店の雰囲気を見る", dark=True)
d.rounded_rectangle((0, sc(710), W, sc(760)), radius=sc(8), fill=(255, 250, 241, 246))
text(d, (28, 727), "お知らせ", 11, fill=INK, gothic=True)
text(d, (98, 727), "2026.05.21　季節のケーキが変わりました。", 11, fill=MUTED, gothic=True)
text(d, (360, 727), "一覧へ →", 11, fill=INK, gothic=True)
paths.append(save(img, "01-first-view.png"))

# 02 Story
img = canvas(620)
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 31), "ABOUT", 12, fill=GOLD, gothic=True)
text(d, (28, 60), "お店のこと", 25, fill=INK, spacing=2)
text(d, (28, 118), "1980年、船乗りだった初代がこの地で「喫茶キャプテン」を開きました。ゆっくりと過ごせる空間と、昔ながらのメニューを大切にしています。", 13, fill=MUTED, max_width=374, spacing=2)
paste_round(img, cover(ASSETS / "interior.jpg", (sc(374), sc(225))), (28, 245))
d.line((sc(28), sc(502), sc(402), sc(502)), fill=LINE, width=sc(1))
text(d, (28, 526), "窓の外に広がる川の景色、木の温もり、やわらかな照明。はじめての方にも、いつもの方にも、肩の力が抜ける場所でありたいと考えています。", 13, fill=INK, max_width=374, spacing=1)
paths.append(save(img, "02-story.png"))

# 03 Video / proof
img = cover(ASSETS / "concept.jpg", (W, sc(620)))
img = overlay_gradient(img, True, 230)
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 32), "MOVIE / TRUST", 12, fill=GOLD, gothic=True)
text(d, (28, 62), "時間がゆっくり流れる、\n特別な場所へ。", 25, fill=WHITE, spacing=5, line_h=1.35)
text(d, (28, 165), "店内の雰囲気や人気メニューを、短い動画でご覧いただけます。地域の方に長く通っていただいている理由を感じてください。", 13, fill=(243, 228, 207), max_width=360, spacing=2)
vid = cover(ASSETS / "concept.jpg", (sc(374), sc(210))).filter(ImageFilter.GaussianBlur(sc(.5)))
paste_round(img, vid, (28, 376), radius=8, shadow=True)
d.ellipse((sc(182), sc(448), sc(248), sc(514)), fill=(255, 250, 241, 225))
d.polygon([(sc(207), sc(468)), (sc(207), sc(494)), (sc(229), sc(481))], fill=COFFEE)
button(d, (108, 295), "動画を見る", dark=True)
paths.append(save(img, "03-proof-video.png"))

# 04 Benefits
img = canvas(680)
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 31), "MENU & BENEFIT", 12, fill=GOLD, gothic=True)
text(d, (28, 60), "日常のなかに、\n小さな楽しみを。", 25, fill=INK, spacing=5, line_h=1.35)
items = [
    ("coffee.jpg", "ウインナー\nコーヒー", "濃厚クリームと深煎り"),
    ("pasta.jpg", "なつかしのあの\nナポリタン", "サラダ・スープ付き"),
    ("meal.jpg", "生姜焼き\n定食", "ごはん・味噌汁付き"),
    ("interior.jpg", "静かな\n店内", "一人でも家族でも"),
]
for i, (pic, title, cap) in enumerate(items):
    x = 28 + (i % 2) * 193
    y = 180 + (i // 2) * 188
    d.rounded_rectangle((sc(x), sc(y), sc(x+181), sc(y+170)), radius=sc(8), fill=(255,255,255,210), outline=LINE, width=sc(1))
    paste_round(img, cover(ASSETS / pic, (sc(181), sc(92))), (x, y), radius=8, shadow=False)
    text(d, (x+11, y+105), title, 14, fill=INK, spacing=0, line_h=1.15)
    text(d, (x+11, y+145), cap, 10, fill=MUTED, gothic=True, spacing=0)
button(d, (108, 590), "メニューを見る", dark=False)
paths.append(save(img, "04-benefits.png"))

# 05 Recommend
img = cover(ASSETS / "interior.jpg", (W, sc(610)))
ov = Image.new("RGBA", img.size, (24, 16, 11, 142))
img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 34), "RECOMMEND", 12, fill=GOLD, gothic=True)
text(d, (28, 64), "こんな方に\nおすすめです。", 25, fill=WHITE, spacing=5, line_h=1.35)
checks = [
    "落ち着いた場所で、ゆっくりコーヒーを飲みたい方",
    "地域で長く愛されるお店を探している方",
    "家族や友人と、気取らず食事を楽しみたい方",
    "那珂川の散歩やお出かけの途中に立ち寄りたい方",
]
for i, c in enumerate(checks):
    y = 210 + i * 78
    d.rounded_rectangle((sc(28), sc(y), sc(402), sc(y+58)), radius=sc(8), fill=(255,250,241,28), outline=(255,255,255,45), width=sc(1))
    d.line((sc(43), sc(y+30), sc(50), sc(y+38)), fill=GOLD, width=sc(3))
    d.line((sc(50), sc(y+38), sc(63), sc(y+20)), fill=GOLD, width=sc(3))
    text(d, (76, y+12), c, 13, fill=WHITE, max_width=305, spacing=0)
paths.append(save(img, "05-recommend.png"))

# 06 Flow
img = canvas(680)
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 31), "HOW TO ENJOY", 12, fill=GOLD, gothic=True)
text(d, (28, 60), "キャプテンで過ごす\nいつもの流れ。", 25, fill=INK, spacing=5, line_h=1.35)
steps = [
    ("1", "まずは席へ", "窓際、テーブル、ひとり席。空いている席でゆっくりお過ごしください。"),
    ("2", "メニューを選ぶ", "コーヒー、喫茶ごはん、季節のケーキまで幅広くご用意しています。"),
    ("3", "景色と一緒に味わう", "那珂川の風景と、店内の穏やかな空気も一緒にお楽しみください。"),
    ("4", "また来たくなる時間へ", "特別すぎない、でも少し満たされる時間をお届けします。"),
]
for i, (n, ttl, body) in enumerate(steps):
    y = 180 + i * 112
    d.ellipse((sc(28), sc(y), sc(74), sc(y+46)), fill=COFFEE)
    tw = d.textlength(n, font=font(18))
    d.text((sc(51)-tw/2, sc(y+10)), n, font=font(18), fill=WHITE)
    text(d, (88, y), ttl, 17, fill=INK, spacing=0)
    text(d, (88, y+35), body, 12, fill=MUTED, max_width=300, spacing=0)
    d.line((sc(88), sc(y+94), sc(402), sc(y+94)), fill=LINE, width=sc(1))
paths.append(save(img, "06-flow.png"))

# 07 People
img = canvas(700)
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 31), "STAFF", 12, fill=GOLD, gothic=True)
text(d, (28, 60), "私たちの想いと、\n働く人たち。", 25, fill=INK, spacing=5, line_h=1.35)
people = [
    ("owner.jpg", "オーナー", "木藤 宏太", "船乗りの経験を胸に、地域にとって心地よい場所を、次の世代につないでいきたい。"),
    ("manager.jpg", "店長", "有吉 史朗", "ここに来るとほっとする場所。心がふくろうな時間を、今日も変わらず届けます。"),
]
for i, (pic, role, name, body) in enumerate(people):
    y = 172 + i * 250
    d.rounded_rectangle((sc(28), sc(y), sc(402), sc(y+222)), radius=sc(8), fill=(255,255,255,210), outline=LINE, width=sc(1))
    paste_round(img, cover(ASSETS / pic, (sc(374), sc(126))), (28, y), radius=8, shadow=False)
    text(d, (45, y+142), role, 11, fill=GOLD, gothic=True, spacing=0)
    text(d, (45, y+162), name, 22, fill=INK, spacing=0)
    text(d, (45, y+198), body, 11, fill=INK, max_width=335, spacing=0)
button(d, (88, 635), "スタッフについて詳しく見る", dark=False, w=254)
paths.append(save(img, "07-people.png"))

# 08 Final CTA
img = cover(ASSETS / "exterior.jpg", (W, sc(760)))
ov = Image.new("RGBA", img.size, (23, 16, 11, 175))
img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")
text(d, (28, 35), "ACCESS", 12, fill=GOLD, gothic=True)
text(d, (28, 66), "那珂川のそばで、\nお待ちしています。", 25, fill=WHITE, spacing=5, line_h=1.35)
text(d, (28, 170), "お近くにお越しの際は、ぜひ気軽にお立ち寄りください。はじめての方も、いつもの方も歓迎します。", 13, fill=(243,228,207), max_width=360, spacing=2)
d.rounded_rectangle((sc(28), sc(300), sc(402), sc(620)), radius=sc(8), fill=(255,250,241,235))
paste_round(img, cover(ASSETS / "map.jpg", (sc(374), sc(120))), (28, 300), radius=8, shadow=False)
text(d, (46, 440), "喫茶キャプテン", 18, fill=INK, spacing=0)
text(d, (46, 476), "福岡県那珂川市松木1-1\n092-953-0985\n営業時間 10:00 - 18:00（L.O.17:30）\n定休日　火曜日・第2水曜日", 12, fill=INK, spacing=1)
button(d, (80, 560), "アクセスを見る", dark=False, w=270)
text(d, (28, 660), "CTA・動画枠・地図部分は、後からHTMLでボタンやリンクを重ねやすい位置に配置しています。", 10, fill=(255,250,241,205), gothic=True, max_width=374, spacing=0)
paths.append(save(img, "08-final-cta.png"))

# Full preview
full_h = sum(Image.open(p).height for p in paths)
full = Image.new("RGB", (W, full_h), PAPER)
y = 0
for p in paths:
    im = Image.open(p).convert("RGB")
    full.paste(im, (0, y))
    y += im.height
full.save(OUT / "captain-mobile-full-preview.png", quality=96)

for p in paths:
    print(p.resolve())
print((OUT / "captain-mobile-full-preview.png").resolve())
