import os,json,urllib.request,urllib.parse,time,statistics,sys
K=os.environ['ETSY_API_KEY']  # keystring:sharedsecret
kws=[l.strip() for l in open(sys.argv[1]) if l.strip()]
out=[]
for kw in kws:
  q=urllib.parse.urlencode({'keywords':kw+' google sheets','limit':100,'sort_on':'score'})
  req=urllib.request.Request('https://openapi.etsy.com/v3/application/listings/active?'+q,headers={'x-api-key':K})
  try: d=json.load(urllib.request.urlopen(req))
  except Exception as e: print(kw,e); continue
  r=d['results']; favs=sorted([x['num_favorers'] for x in r],reverse=True); views=sorted([x.get('views') or 0 for x in r],reverse=True)
  prices=[x['price']['amount']/x['price']['divisor'] for x in r]
  out.append((kw,d['count'],sum(favs[:10]),statistics.median(favs) if favs else 0,sum(views[:10]),statistics.median(prices) if prices else 0))
  time.sleep(0.25)
out.sort(key=lambda x:-x[2])
print(f"{'keyword':38}{'results':>9}{'top10fav':>10}{'medfav':>8}{'top10views':>12}{'medprice':>9}")
for o in out: print(f"{o[0]:38}{o[1]:>9}{o[2]:>10}{o[3]:>8}{o[4]:>12}{o[5]:>9.2f}")
