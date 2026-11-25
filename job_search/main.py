from jooble_api import search_jobs
from career_ranking import rank_careers

# Mock data: 后续替换为真实模型输出
careers = [
    {
        "title": "Data Analyst",
        "match_score": 0.85,
        "ai_exposure": 0.60
    },
    {
        "title": "Data Engineer",
        "match_score": 0.75,
        "ai_exposure": 0.25
    },
    {
        "title": "BI Analyst",
        "match_score": 0.90,
        "ai_exposure": 0.70
    }
]

ranked_careers = rank_careers(careers)

for career in ranked_careers:

    career["job_market"] = search_jobs(
        keywords=career["title"],
        location="Germany",
        limit=5
    )

print(ranked_careers)