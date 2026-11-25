def rank_careers(careers):

    for career in careers:

        match = career["match_score"]
        exposure = career["ai_exposure"]

        career["final_score"] = round(
            0.6 * match + 0.4 * (1 - exposure),
            3
        )

    return sorted(
        careers,
        key=lambda x: x["final_score"],
        reverse=True
    )