"""Square (2400x2400) Etsy hero, safe for square thumbnails: centered title, big screenshot, one stat card.
Usage: python hero_square.py config.json out.jpg   (keys: brand, dark, light, eyebrow, title, subtitle, stat[label,value], pills[], screenshot)"""
import base64, io, json, subprocess, sys
from PIL import Image, ImageChops
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
im = Image.open(cfg["screenshot"]).convert("RGB")
diff = ImageChops.difference(im, Image.new("RGB", im.size, "white")).convert("L").point(lambda x: 255 if x > 12 else 0)
im = im.crop(diff.getbbox()); h = min(im.height, int(im.width / 1.6)); im = im.crop((0, 0, im.width, h))
buf = io.BytesIO(); im.save(buf, "PNG"); shot = base64.b64encode(buf.getvalue()).decode()
B, D, L = cfg["brand"], cfg["dark"], cfg["light"]
pills = "".join(f'<span class="pill">✓ {p}</span>' for p in cfg["pills"])
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:2400px;height:2400px;overflow:hidden;font-family:Inter,sans-serif;background:radial-gradient(1600px 1300px at 50% 62%,{L},#fbfaf7 72%);position:relative}}
.top{{position:absolute;top:150px;left:0;right:0;text-align:center}}
.eyebrow{{display:inline-block;background:{B};color:#fff;font-weight:800;font-size:54px;letter-spacing:6px;padding:22px 52px;border-radius:999px}}
h1{{font-family:'Inter Display',Inter;font-weight:900;font-size:230px;line-height:.98;letter-spacing:-7px;color:{D};margin-top:60px}}
.sub{{font-size:72px;color:#374151;font-weight:600;margin-top:40px}}
.laptop{{position:absolute;left:200px;width:2000px;top:{cfg.get('laptop_top',1010)}px}}
.screen{{background:#0f172a;border-radius:40px 40px 0 0;padding:38px 38px 46px;box-shadow:0 70px 140px rgba(15,23,42,.28)}}
.screen img{{display:block;width:100%;border-radius:8px;background:#fff}}
.base{{height:56px;margin:0 -80px;background:linear-gradient(#e5e7eb,#9ca3af);border-radius:0 0 48px 48px}}
.stat{{position:absolute;right:110px;top:{cfg.get('laptop_top',1010)-90}px;background:#fff;border-radius:40px;padding:44px 60px;box-shadow:0 40px 90px rgba(15,23,42,.24);border:3px solid #eef0f3;text-align:center}}
.stat .l{{font-size:40px;font-weight:800;letter-spacing:4px;color:#6b7280;text-transform:uppercase}}
.stat .v{{font-family:'Inter Display',Inter;font-size:140px;font-weight:900;color:{B};letter-spacing:-3px;line-height:1.05}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:250px;background:{D};display:flex;align-items:center;justify-content:center;gap:40px}}
.pill{{color:#fff;font-weight:800;font-size:58px;padding:0 20px}}
</style></head><body>
<div class="top"><span class="eyebrow">{cfg['eyebrow']}</span><h1>{cfg['title']}</h1><div class="sub">{cfg['subtitle']}</div></div>
<div class="laptop"><div class="screen"><img src="data:image/png;base64,{shot}"></div><div class="base"></div></div>
<div class="stat"><div class="l">{cfg['stat'][0]}</div><div class="v">{cfg['stat'][1]}</div></div>
<div class="foot">{pills}</div></body></html>"""
open(out + ".html", "w").write(html)
js = "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:2400,height:2400}});await p.goto('file://'+process.argv[1]);await p.waitForTimeout(400);await p.screenshot({path:process.argv[2]});await b.close();})()"
subprocess.run(["node", "-e", js, out + ".html", out + ".png"], check=True)
Image.open(out + ".png").convert("RGB").save(out, quality=92); print("saved", out)
