from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
SLICES = ROOT / "assets" / "slices"
OUT = ROOT / "out_hp_exact"
MATERIALS = Path("/Users/hanadashoya/Desktop/ミセサポ事業/お客様/キャプテンHP/素材")
SOURCE = Path("/Users/hanadashoya/Desktop/ミセサポ事業/お客様/キャプテンHP/キャプテンUI.png")


def fill_from_rows(img, box):
    x1, y1, x2, y2 = box
    draw = ImageDraw.Draw(img)
    for y in range(y1, y2):
        samples = []
        for sx in (max(0, x1 - 18), min(img.width - 1, x2 + 18)):
            samples.append(img.getpixel((sx, min(img.height - 1, y))))
        col = tuple(sum(c[i] for c in samples) // len(samples) for i in range(3))
        draw.line((x1, y, x2, y), fill=col)


def feather_patch(img, box, blur=6):
    x1, y1, x2, y2 = box
    patch = img.crop((x1, y1, x2, y2)).filter(ImageFilter.GaussianBlur(blur))
    mask = Image.new("L", patch.size, 255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    img.paste(patch, (x1, y1), mask)


def restore_slice(y1, y2):
    return Image.open(SOURCE).convert("RGB").crop((0, y1, 863, y2))


def cover(path, size, focus=(0.5, 0.5)):
    im = Image.open(path).convert("RGB")
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = round(nw * focus[0]), round(nh * focus[1])
    left = max(0, min(nw - tw, cx - tw // 2))
    top = max(0, min(nh - th, cy - th // 2))
    return im.crop((left, top, left + tw, top + th))


def paste_round(img, patch, xy, radius=5):
    x, y = xy
    mask = Image.new("L", patch.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, patch.width, patch.height), radius=radius, fill=255)
    img.paste(patch, (x, y), mask)


def font(size, bold=False):
    path = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc" if bold else "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
    return ImageFont.truetype(path, size)


def paper_canvas(w, h):
    img = Image.new("RGB", (w, h), (250, 246, 238))
    d = ImageDraw.Draw(img)
    for y in range(h):
        edge = min(abs(y - h * 0.45) / (h * 0.55), 1)
        shade = int(8 * edge)
        d.line((0, y, w, y), fill=(250 - shade, 246 - shade, 238 - shade))
    return img


def erase_dark_text(img, box, samples=(24, 34, 44)):
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(img)
    for y in range(y1, y2):
        cols = [img.getpixel((x, max(0, min(img.height - 1, y)))) for x in samples]
        col = tuple(sum(c[i] for c in cols) // len(cols) for i in range(3))
        d.line((x1, y, x2, y), fill=col)


def draw_multiline(draw, xy, lines, fnt, fill, line_gap):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap


# 01: remove the "Scroll" label and small arrow by trimming the
# bottom guide area. This keeps the hero clean without visible retouching.
hero = restore_slice(0, 270)
hero.save(SLICES / "01-first-view.png")
hero.save(OUT / "01-first-view.png")

# 04: remove the small "コンセプト" eyebrow.
concept = restore_slice(652, 866)
clone = concept.crop((160, 18, 250, 46)).filter(ImageFilter.GaussianBlur(2))
mask = Image.new("L", clone.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, clone.width, clone.height), radius=12, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(4))
concept.paste(clone, (66, 18), mask)
concept.save(SLICES / "04-concept.png")
concept.save(OUT / "04-concept.png")

# 05: remove the ginger pork card and center the two remaining menu cards.
menu = restore_slice(866, 1175)
card1 = menu.crop((92, 56, 298, 242))
card2 = menu.crop((326, 56, 532, 242))
card3 = menu.crop((563, 56, 769, 242))
coffee_photo = cover(MATERIALS / "2021-04-08-12.jpg", (206, 111), focus=(0.5, 0.52))
pasta_photo = cover(MATERIALS / "2021-04-08-12-1.jpg", (206, 111), focus=(0.52, 0.55))
blend_photo = cover(MATERIALS / "18-2.jpg", (206, 111), focus=(0.58, 0.50))
paste_round(card1, coffee_photo, (0, 0), radius=5)
paste_round(card2, pasta_photo, (0, 0), radius=5)
paste_round(card3, blend_photo, (0, 0), radius=5)
card_draw = ImageDraw.Draw(card2)
card_draw.rectangle((0, 112, 206, 186), fill=(255, 252, 246))
card_draw.text((4, 124), "なつかしのあのナポリタン", font=font(11), fill=(35, 27, 21))
card_draw.text((4, 152), "サラダ・スープ付き", font=font(11), fill=(55, 44, 35))
card_draw.text((164, 174), "¥850", font=font(13), fill=(35, 27, 21))
card_draw = ImageDraw.Draw(card3)
card_draw.rectangle((0, 112, 206, 186), fill=(255, 252, 246))
card_draw.text((4, 124), "キャプテンブレンド", font=font(13), fill=(35, 27, 21))
card_draw.text((4, 152), "定番のブレンドコーヒー", font=font(11), fill=(55, 44, 35))
card_draw.text((162, 174), "¥500", font=font(13), fill=(35, 27, 21))
menu.paste(card1, (92, 56))
menu.paste(card2, (326, 56))
menu.paste(card3, (563, 56))
menu.save(SLICES / "05-menu.png")
menu.save(OUT / "05-menu.png")

# 07: make every gallery thumbnail a distinct real shop scene and rebuild
# the section with more breathing room.
original_gallery = restore_slice(1485, 1823)
gallery = paper_canvas(863, 400)
gd = ImageDraw.Draw(gallery)
gd.text((78, 16), "キャプテンのある風景", font=font(20), fill=(35, 27, 21))
thumbs = [
    (MATERIALS / "6-2.jpg", (78, 58), (0.52, 0.52)),
    (MATERIALS / "4-2.jpg", (218, 58), (0.48, 0.55)),
    (MATERIALS / "coffeeshop-captain_05.jpg", (358, 58), (0.50, 0.55)),
    (MATERIALS / "coffeeshop-captain_04.jpg", (498, 58), (0.50, 0.45)),
    (MATERIALS / "coffeeshop-captain_03.jpg", (638, 58), (0.50, 0.48)),
]
for path, xy, focus in thumbs:
    patch = cover(path, (126, 80), focus=focus)
    paste_round(gallery, patch, xy, radius=4)
gallery.paste(original_gallery.crop((78, 142, 786, 260)), (78, 176))
gallery.paste(original_gallery.crop((78, 270, 786, 338)), (78, 318))
gallery.save(SLICES / "07-gallery-access-footer.png")
gallery.save(OUT / "07-gallery-access-footer.png")

# Rebuild joined preview without the news slice.
names = [
    "01-first-view.png",
    "03-about-shop.png",
    "04-concept.png",
    "05-menu.png",
    "06-staff.png",
    "07-gallery-access-footer.png",
]
parts = [Image.open(SLICES / name).convert("RGB") for name in names]
joined = Image.new("RGB", (parts[0].width, sum(p.height for p in parts)), (255, 250, 241))
y = 0
for part in parts:
    joined.paste(part, (0, y))
    y += part.height
joined.save(OUT / "captain-ui-rejoined-preview.png")
joined.save(OUT / "captain-ui-rejoined-no-news.png")

for name in names:
    print((SLICES / name).resolve())
print((OUT / "captain-ui-rejoined-no-news.png").resolve(), joined.size)
