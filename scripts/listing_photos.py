"""Compose Etsy listing photos (2700x2025) from rendered sheet PNGs.
Usage: python listing_photos.py config.json   (config: {"brand":[r,g,b],"dark":[...],"light":[...],"footer":"...","cards":[[src,head,sub,out],...]})"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
cfg = json.load(open(sys.argv[1]))
B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'; R = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
if not os.path.exists(B): B = R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BRAND, DARK, LIGHT = map(tuple, (cfg["brand"], cfg["dark"], cfg["light"])); CREAM = (250, 248, 243); W, H = 2700, 2025
def crop(img):
    diff = ImageChops.difference(img, Image.new(img.mode, img.size, (255, 255, 255))).convert('L').point(lambda x: 255 if x > 12 else 0)
    return img.crop(diff.getbbox())
for src, head, sub, out in cfg["cards"]:
    c = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W, 330], fill=BRAND)
    d.text((W // 2, 130), head, font=ImageFont.truetype(B, 104), fill='white', anchor='mm')
    d.text((W // 2, 250), sub, font=ImageFont.truetype(R, 56), fill=LIGHT, anchor='mm')
    im = crop(Image.open(src).convert('RGB')); maxw, maxh = W - 200, H - 330 - 230
    s = min(maxw / im.width, maxh / im.height); im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = (W - im.width) // 2; y = 330 + 60 + (maxh - im.height) // 2
    sh = Image.new('RGBA', (im.width + 60, im.height + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 30, im.width + 30, im.height + 30], fill=(0, 0, 0, 60))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); c.paste(sh, (x - 22, y - 18), sh)
    c.paste(im, (x, y)); d.rectangle([x, y, x + im.width, y + im.height], outline=(210, 210, 210), width=3)
    d.text((W // 2, H - 85), cfg["footer"], font=ImageFont.truetype(B, 50), fill=DARK, anchor='mm')
    c.save(out, quality=92); print(out)
