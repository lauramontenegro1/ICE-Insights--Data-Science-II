"""
TaskBridge - third cleaning: duplicate removals
entry : taskbridge_tables.xlsx (from dataset_prep)
out   : clean_data           (clean table without duplicates, with clean text and match key for skills) 
          clean_data/_removed  (removed duplicates)
          clean_data/clean_data_report.csv    (overall)
"""
from pathlib import Path
import pandas as pd

IN_FILE = "taskbridge_tables.xlsx"
OUT = Path("cleaning_data"); (OUT / "_removed").mkdir(parents=True, exist_ok=True)
from text_standardization import clean_text, match_key
# 
criteria = {
    "sectors":                     {"key": ["sector_id"]}, #check duplicates by id
    "occupations":                 {"key": ["occupation_id"]},
    "tasks":                       {"key": ["occupation_id", "occupation_id_onet", "task_id"]},
    "skills":                      {"key": ["skill_label"], "match": ["skill_label"], #check duplicates by text 
                                    "prefer_filled": ["skill_type", "reuse_level", "resuse_level"]}, #chooses duplicate with more columns filled
    "occupation_skills":           {"key": ["occupation_id", "skill_label"], "match": ["skill_label"]}, #id and text
    "ESCO_task_ai_exposure":       {"key": None}, #check whole line
    "ONET_task_ai_exposure":       {"key": ["occupation_id_onet", "task_id"]}, #by id
    "ONET_occupation_ai_exposure": {"key": ["occupation_id_onet"]}, #by id
}

# standardize text reading: consider null spaces
def text (s: pd.Series) -> pd.Series:
    return s.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()

def remove_duplicates(df: pd.DataFrame, rule: dict):
    key = rule["key"] or list(df.columns)
    match_cols = set(rule.get("match", []))
    tmp = df.copy()
    cmp_cols = [] #to compare which dup is fuller
    for c in key:
        col = f"__k_{c}"
        tmp[col] = match_key(tmp[c]) if c in match_cols else tmp[c]
        cmp_cols.append(col)
    pref = [c for c in rule.get("prefer_filled", []) if c in tmp.columns]
    tmp["__filled"] = tmp[pref].notna().sum(axis=1) if pref else tmp.notna().sum(axis=1)
    tmp = tmp.sort_values("__filled", ascending=False, kind="stable")
    is_dup = tmp.duplicated(subset=cmp_cols, keep="first")
    kept = tmp[~is_dup].sort_index()
    removed = tmp[is_dup].sort_index()
    key_cols = {f"__k_{c}": f"{c}_key" for c in key if c in match_cols}
    drop_kept = ["__filled"] + [c for c in cmp_cols if c not in key_cols]
    kept = kept.drop(columns=drop_kept).rename(columns=key_cols)
    removed = removed.drop(columns=["__filled"] + cmp_cols)
    return kept, removed


tables = pd.read_excel(IN_FILE, sheet_name=None, dtype=str) #standard id reading no float so 2.1 equals to 2.10
report = []
for name, df in tables.items():
    for c in df.columns:                       
        df[c] = clean_text(df[c])
    kept, removed = remove_duplicates(df, criteria[name])
    kept.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8")
    if len(removed):
        removed.to_csv(OUT / "_removed" / f"{name}.csv", index=False, encoding="utf-8")
    report.append({"table": name, "rows_before": len(df), "removed": len(removed),
                   "rows_after": len(kept)})
    print(f"{name:30s} {len(df):>6} -> {len(kept):>6}  (-{len(removed)})")

pd.DataFrame(report).to_csv(OUT / "clean_data_report.csv", index=False)



