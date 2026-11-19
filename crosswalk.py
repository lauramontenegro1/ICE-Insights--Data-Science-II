import pandas as pd
import urllib.request
import urllib.parse
import re
import time

df = pd.read_csv("raw ESCO/occupations_en.csv")
groups = [1211, 1213, 1330, 2151, 2152, 2153, 2411, 2412, 2413, 2414, 2421, 2422, 2423, 2424, 2431, 2432, 2433, 2434, 2511, 2512, 2513, 2514, 2519, 3113, 3114, 3311, 3312, 3313, 3314, 3315, 3321, 3322, 3323, 3324, 3331, 3341, 3511, 3512, 3513, 3514, 3521, 3522]
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


