import pandas as pd
import urllib.request
import urllib.parse
import re
import time

df = pd.read_csv("raw ESCO/occupations_en.csv")
groups = [1330, 2151, 2152, 2153, 2511, 2512, 2513, 2514, 2519, 3114]
sub = df[df["iscoGroup"].isin(groups)].copy()

results = []
for _, row in sub.iterrows():
    code = str(row["code"])
    label = str(row["preferredLabel"])
    query = urllib.parse.quote(code)
    url = f"https://www.onetonline.org/crosswalk/ESCO?s={query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
        onet_codes = sorted(set(re.findall(r"\d{2}-\d{4}\.\d{2}", html)))
    except Exception:
        onet_codes = []
    
    # Grava uma linha separada para cada código O*NET encontrado
    for onet_code in onet_codes:
        results.append({
            "iscoGroup": row["iscoGroup"],
            "occupation_code": code,
            "preferredLabel": label,
            "occupation_id_onet": onet_code
        })
        
    time.sleep(0.3)

out = pd.DataFrame(results)
out.to_csv("esco_onet_crosswalk.csv", index=False)


