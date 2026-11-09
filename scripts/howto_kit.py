"""Generate a 'How It Works' listing image (2700x2025) and a Quick Start Guide PDF from a JSON config.
Usage: python howto_kit.py config.json outdir
Config keys: brand, dark, light (hex); product; tagline; copy_link; how_steps [[title, text, img, [crop]]];
guide_sections [[title, html, img|null, [crop]|null]]; tip; faq [[q, a]]; footer"""
import base64, io, json, os, subprocess, sys
from PIL import Image
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
B, D, Lt = cfg["brand"], cfg["dark"], cfg["light"]
def b64(path, crop, w=900):
    im = Image.open(path).convert("RGB")
    if crop: im = im.crop(tuple(crop))
    im = im.resize((w, int(im.height * w / im.width))); buf = io.BytesIO(); im.save(buf, "JPEG", quality=88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
CSS = "*{box-sizing:border-box;margin:0;padding:0}body{font-family:Inter,sans-serif;color:#14202b}"
cards = "".join(f'<div class="card"><div class="n">{i+1}</div><h3>{t}</h3><p>{x}</p><div class="shot"><img src="{b64(img, crop)}"></div></div>'
                for i, (t, x, img, crop) in enumerate(cfg["how_steps"]))
how = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:2700px;height:2025px;background:radial-gradient(1500px 1000px at 50% 40%,{Lt},#fbfaf7 70%);overflow:hidden}}
h1{{text-align:center;font-family:'Inter Display',Inter;font-weight:900;font-size:130px;letter-spacing:-3px;color:{D};margin-top:120px}}
.sub{{text-align:center;font-size:54px;color:#4b5563;margin-top:24px;font-weight:500}}
.row{{display:flex;gap:70px;justify-content:center;margin-top:110px;padding:0 120px}}
.card{{background:#fff;border-radius:44px;padding:56px 50px;width:760px;box-shadow:0 40px 90px rgba(15,23,42,.14);position:relative}}
.n{{width:110px;height:110px;border-radius:50%;background:{B};color:#fff;font-weight:900;font-size:64px;display:flex;align-items:center;justify-content:center;position:absolute;top:-55px;left:50px}}
h3{{font-size:62px;font-weight:800;margin-top:50px;color:{D}}} p{{font-size:40px;line-height:1.35;color:#4b5563;margin-top:18px;min-height:162px}}
.shot{{margin-top:34px;border-radius:22px;overflow:hidden;border:3px solid {Lt};height:520px;background:#f8fafc}}
.shot img{{width:100%;height:100%;object-fit:cover;object-position:top left}}
.foot{{position:absolute;bottom:0;left:0;right:0;height:200px;background:{D};color:#fff;display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:700;gap:60px}}
</style></head><body><h1>How It Works</h1><div class="sub">Up and running in under 5 minutes - no formulas, no setup.</div><div class="row">{cards}</div>
<div class="foot"><span>✓ Free Google account</span><span>✓ Saves to your sheet instantly</span><span>✓ Lifetime access</span></div></body></html>'''
def sec(n, t, body, img, crop):
    im = f'<img class="im" src="{b64(img, crop)}">' if img else ""
    return f'<div class="sec"><div class="sn">{n}</div><div class="sb"><h2>{t}</h2>{body}{im}</div></div>'
secs = [sec(i + 1, *s) for i, s in enumerate(cfg["guide_sections"])]
split = cfg.get("page_split", 3)
L = cfg["copy_link"]
faq = "".join(f"<p><b>{q}</b> {a}</p>" for q, a in cfg["faq"])
guide = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
@page{{size:Letter;margin:0}} .page{{width:8.5in;height:11in;padding:.6in .7in;position:relative;page-break-after:always}}
.top{{background:linear-gradient(135deg,{B},{D});color:#fff;border-radius:22px;padding:34px 36px}}
.top .e{{font-size:12px;font-weight:800;letter-spacing:3px;opacity:.85}} .top h1{{font-size:40px;font-weight:900;letter-spacing:-1px;margin-top:8px;line-height:1.05}} .top p{{font-size:15px;opacity:.9;margin-top:10px}}
.cta{{margin:26px 0 8px;text-align:center}} .btn{{display:inline-block;background:{B};color:#fff;font-weight:800;font-size:22px;padding:18px 44px;border-radius:999px;text-decoration:none}}
.small{{font-size:11.5px;color:#6b7280;text-align:center;margin-top:8px}}
.sec{{display:flex;gap:16px;margin-top:15px}} .sn{{flex:none;width:36px;height:36px;border-radius:50%;background:{Lt};color:{B};font-weight:900;display:flex;align-items:center;justify-content:center;font-size:17px}}
.sb h2{{font-size:18px;font-weight:800;color:{D};margin-top:5px}} .sb p,.sb li{{font-size:13px;line-height:1.55;color:#374151;margin-top:5px}} .sb ul{{margin-left:18px}}
.im{{width:100%;max-height:{cfg.get('img_max','2.6in')};object-fit:cover;object-position:top;border-radius:12px;border:1px solid #e5e7eb;margin-top:10px}}
.tip{{background:#FFF7D6;border-radius:12px;padding:12px 16px;font-size:12.5px;color:#713f12;margin-top:14px;line-height:1.5}}
h3.f{{font-size:16px;color:{D};margin-top:12px;font-weight:800}} .faq p{{font-size:12.5px;color:#374151;line-height:1.5;margin-top:3px}}
.ft{{position:absolute;bottom:.28in;left:.7in;right:.7in;font-size:11px;color:#9ca3af;display:flex;justify-content:space-between}}
</style></head><body>
<div class="page"><div class="top"><div class="e">QUICK START GUIDE</div><h1>{cfg["product"]}</h1><p>{cfg["tagline"]}</p></div>
<div class="cta"><a class="btn" href="{L}">Make My Copy →</a><div class="small">Opens Google Sheets and asks "Make a copy?" - click <b>Make a copy</b>. Works with any free Google account.</div>
<div class="small" style="margin-top:6px">Button not working? Copy this link into your browser:<br><a href="{L}" style="color:{B};word-break:break-all">{L}</a></div></div>
{"".join(secs[:split])}<div class="ft"><span>{cfg["footer"]}</span><span>Page 1</span></div></div>
<div class="page">{"".join(secs[split:])}<div class="tip"><b>Tip:</b> {cfg["tip"]}</div><h3 class="f">FAQ</h3><div class="faq">{faq}</div>
<div class="ft"><span>{cfg["footer"]}</span><span>Page 2</span></div></div></body></html>'''
open(f"{out}/how.html", "w").write(how); open(f"{out}/guide.html", "w").write(guide)
js = """const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const o=process.argv[1];
const p=await b.newPage({viewport:{width:2700,height:2025}});await p.goto('file://'+o+'/how.html');await p.waitForTimeout(400);await p.screenshot({path:o+'/how.png'});
const g=await b.newPage();await g.goto('file://'+o+'/guide.html');await g.waitForTimeout(400);await g.pdf({path:o+'/guide.pdf',format:'Letter',printBackground:true});await b.close();})()"""
subprocess.run(["node", "-e", js, os.path.abspath(out)], check=True)
Image.open(f"{out}/how.png").convert("RGB").save(f"{out}/how.jpg", quality=92)
pages = subprocess.run(["pdfinfo", f"{out}/guide.pdf"], capture_output=True, text=True).stdout
print("done;", [l for l in pages.splitlines() if l.startswith("Pages")])
