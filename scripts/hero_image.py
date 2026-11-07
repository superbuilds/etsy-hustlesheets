"""Render a 2700x2025 Etsy hero image from a config JSON.
Usage: python hero_image.py config.json out.jpg
Config: brand, dark, light (hex), eyebrow, title, subtitle, features[], stats[[label,value],..] (2), tabs[], screenshot (png path)."""
import base64, io, json, sys
from PIL import Image, ImageChops
import subprocess

cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
im = Image.open(cfg["screenshot"]).convert("RGB")
diff = ImageChops.difference(im, Image.new("RGB", im.size, "white")).convert("L").point(lambda x: 255 if x > 12 else 0)
im = im.crop(diff.getbbox())
h = min(im.height, int(im.width / 1.6)); im = im.crop((0, 0, im.width, h))  # 16:10 screen
buf = io.BytesIO(); im.save(buf, "PNG"); shot = base64.b64encode(buf.getvalue()).decode()
check = '<svg viewBox="0 0 24 24" width="46" height="46"><circle cx="12" cy="12" r="12" fill="{c}"/><path d="M7 12.5l3.2 3.2L17 9" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'.format(c=cfg["brand"])
feats = "".join(f'<li>{check}<span>{f}</span></li>' for f in cfg["features"])
pills = "".join(f'<span class="pill">{x}</span>' for x in cfg.get('pills', [])) 
tabs = "".join(f'<span class="tab">{t}</span>' for t in cfg["tabs"])
s1, s2 = cfg["stats"]
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:2700px;height:2025px;font-family:Inter,sans-serif;color:#14202b;overflow:hidden;
 background:radial-gradient(1400px 1100px at 78% 42%, {cfg['light']} 0%, #fbfaf7 62%);position:relative}}
.blob{{position:absolute;border-radius:50%;filter:blur(2px)}}
.left{{position:absolute;left:150px;top:200px;width:1000px}}
.eyebrow{{display:inline-block;background:{cfg['brand']};color:#fff;font-weight:700;font-size:40px;letter-spacing:4px;padding:18px 34px;border-radius:999px}}
h1{{font-family:'Inter Display',Inter;font-weight:900;font-size:150px;line-height:1.0;letter-spacing:-4px;margin-top:60px;color:{cfg['dark']}}}
.sub{{font-size:52px;line-height:1.3;color:#4b5563;margin-top:44px;font-weight:500}}
ul{{list-style:none;margin-top:70px}}
li{{display:flex;align-items:center;gap:30px;font-size:50px;font-weight:600;margin:0 0 34px}}
li svg{{flex:none}}
.right{{position:absolute;left:1210px;top:420px;width:1360px}}
.laptop .screen{{background:#0f172a;border-radius:34px 34px 0 0;padding:34px 34px 40px;box-shadow:0 60px 120px rgba(15,23,42,.28)}}
.laptop .screen img{{display:block;width:100%;border-radius:6px;background:#fff}}
.laptop .base{{height:46px;margin:0 -60px;background:linear-gradient(#e5e7eb,#9ca3af);border-radius:0 0 40px 40px;position:relative}}
.laptop .base:after{{content:'';position:absolute;left:50%;top:0;width:260px;height:18px;margin-left:-130px;background:#cbd5e1;border-radius:0 0 18px 18px}}
.stat{{position:absolute;background:#fff;border-radius:34px;padding:40px 54px;box-shadow:0 40px 90px rgba(15,23,42,.22);border:2px solid #eef0f3}}
.stat .l{{font-size:34px;font-weight:700;letter-spacing:3px;color:#6b7280;text-transform:uppercase}}
.stat .v{{font-family:'Inter Display',Inter;font-size:104px;font-weight:800;color:{cfg['brand']};margin-top:8px;letter-spacing:-2px}}
.s1{{left:-110px;top:760px}} .s2{{right:-10px;top:-150px}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:230px;background:{cfg['dark']};display:flex;align-items:center;justify-content:center;gap:28px}}
.foot .lab{{color:#fff;font-weight:800;font-size:46px;margin-right:18px}}
.tab{{color:#fff;font-weight:600;font-size:40px;padding:20px 38px;border:3px solid rgba(255,255,255,.45);border-radius:999px}}
.pills{{position:absolute;left:1210px;width:1360px;top:1500px;display:flex;justify-content:center;gap:26px}}
.pill{{background:#fff;border:3px solid {cfg['brand']};color:{cfg['dark']};font-weight:700;font-size:38px;padding:20px 36px;white-space:nowrap;border-radius:999px;box-shadow:0 14px 34px rgba(15,23,42,.10)}}
</style></head><body>
<div class="left"><span class="eyebrow">{cfg['eyebrow']}</span><h1>{cfg['title']}</h1><p class="sub">{cfg['subtitle']}</p><ul>{feats}</ul></div>
<div class="right"><div class="laptop"><div class="screen"><img src="data:image/png;base64,{shot}"></div><div class="base"></div></div>
<div class="stat s1"><div class="l">{s1[0]}</div><div class="v">{s1[1]}</div></div>
<div class="stat s2"><div class="l">{s2[0]}</div><div class="v">{s2[1]}</div></div></div>
<div class="pills">{pills}</div>
<div class="foot"><span class="lab">Includes:</span>{tabs}</div>
</body></html>"""
open(out + ".html", "w").write(html)
js = "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:2700,height:2025},deviceScaleFactor:1});await p.goto('file://'+process.argv[1]);await p.waitForTimeout(400);await p.screenshot({path:process.argv[2]});await b.close();})()"
subprocess.run(["node", "-e", js, out + ".html", out + ".png"], check=True)
Image.open(out + ".png").convert("RGB").save(out, quality=93); print("saved", out)
