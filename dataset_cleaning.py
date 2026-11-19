import pandas as pd
import numpy as np

#1. read data
occupations_ESCO = pd.read_csv("raw ESCO/occupations_en.csv")
ISCO_groups = pd.read_csv("raw ESCO/ISCOGroups_en.csv")
skills_ESCO = pd.read_csv("raw ESCO/skills_en.csv")
occupation_skills_ESCO = pd.read_csv("raw ESCO/occupationSkillRelations_en.csv")
transversal_skills_ESCO = pd.read_csv("raw ESCO/transversalSkillsCollection_en.csv")
tasks_ONET = pd.read_csv("ONET_task_statements.csv")
ILO = pd.read_excel("ILO_dataset.xlsx")
openai = pd.read_csv("openai_dataset.tsv", sep="\t")
antropic_occupations= pd.read_csv("antropic_robot_exposure_occupations.csv")
antropic_tasks = pd.read_csv("antropic_robot_exposure_tasks.csv")


#1. sectors table
it_ISCO08 = [1211, 1213, 1330, 2151, 2152, 2153, 2411, 2412, 2413, 2414, 2421, 2422, 2423, 2424, 2431, 2432, 2433, 2434, 2511, 2512, 2513, 2514, 2519, 3113, 3114, 3311, 3312, 3313, 3314, 3315, 3321, 3322, 3323, 3324, 3331, 3341, 3511, 3512, 3513, 3514, 3521, 3522]
ISCO_groups = ISCO_groups[ISCO_groups["code"].isin(it_ISCO08)].copy() #filter occupations database for only it
sectors_table = ISCO_groups.filter(["code", "preferredLabel"]).rename(columns={"code": "sector_id", "preferredLabel":"sector_name"})

#2. occupations table

occupations_ESCO = occupations_ESCO[occupations_ESCO["iscoGroup"].isin(it_ISCO08)].copy() #filter occupations database for only it
occupations_ESCO["description_clean"] = (occupations_ESCO["description"].str.replace(r"\s+", " ", regex=True)) #clean description
occupation_id = occupations_ESCO.filter(["code"]).rename(columns={"code": "occupation_id"}) #ISCO-08 id for each it occupation
canonical_title = occupations_ESCO.filter(["preferredLabel"]).rename(columns={"preferredLabel": "canonical_title"}) #occupations name from esco 
occupation_description = occupations_ESCO.filter(["description_clean"]).rename(columns={"description_clean": "occupation_description"}) 

occupations_table = pd.concat([occupation_id, canonical_title, occupation_description], axis = 1)

#tasks O*NET table
crosswalk_ESCO_ONET = pd.read_csv("esco_onet_crosswalk.csv")
occupation_id_onet = crosswalk_ESCO_ONET.filter(["occupation_id_onet"]) #onet occupations filtered for IT
occupation_id_onet_list = crosswalk_ESCO_ONET.filter(["occupation_id_onet"]).squeeze().tolist() #onet occupations filtered for IT

tasks_ONET_IT = tasks_ONET[tasks_ONET["O*NET-SOC Code"].isin(occupation_id_onet_list)].copy() #tasks for it filtered
task_id = tasks_ONET_IT.filter(["Task ID"]).rename(columns={"Task ID": "task_id"})
task_description = tasks_ONET_IT.filter(["Task"]).rename(columns={"Task": "task_description"})
tasks_table = crosswalk_ESCO_ONET.merge(tasks_ONET_IT, left_on="occupation_id_onet", right_on="O*NET-SOC Code",how="inner",).rename(columns={"Task ID": "task_id", "Task": "task_description"}).rename(columns={"occupation_code":"occupation_id"})

tasks_table = tasks_table[["occupation_id", "occupation_id_onet", "task_id", "task_description"]]


#occupation_skills table
canonical_title_list= canonical_title.squeeze().tolist()
skills_it = occupation_skills_ESCO[occupation_skills_ESCO["occupationLabel"].isin(canonical_title_list)].filter(["occupationLabel","skillLabel","relationType"])

occupations_skills_table = occupations_table[["occupation_id", "canonical_title"]].merge(skills_it,left_on="canonical_title",right_on="occupationLabel",how="inner",)
occupations_skills_table = occupations_skills_table[["occupation_id", "canonical_title", "skillLabel", "relationType"]].rename(columns={"skillLabel":"skill_label","relationType":"occupation_skill_relation_type"})

#skills table
skills_it_list = skills_it["skillLabel"].squeeze().tolist()
skills_table = skills_ESCO[skills_ESCO["preferredLabel"].isin(skills_it_list)].filter(["preferredLabel","skillType","reuseLevel", "definition"]).rename(columns={"preferredLabel":"skill_label", "skillType":"skill_type", "reuseLevel":"resuse_level"})
print(skills_table)

#exposure-ILO
ILO = ILO[ILO["ISCO_08"].isin(it_ISCO08)].copy()
exposure_ILO = ILO.filter(["ISCO_08", "Title", "Task_ISCO", "mean_score_2025"]).rename(columns = {"ISCO_08": "occupation_group", "Title": "canonical_title", "Task_ISCO": "task_description_ISCO", "mean_score_2025": "ilo_exposure_score"})


#exposure- antropic
antropic_tasks = antropic_tasks[antropic_tasks["Fonetsoc_code"].isin(occupation_id_onet_list)]
exposure_antropic_tasks =  antropic_tasks.filter(["task_id","time_share"])
exposure_antropic_tasks["task_id"] = exposure_antropic_tasks["task_id"].astype(str).str.strip()

antropic_occupations = antropic_occupations[antropic_occupations["onetsoc_code"].isin(occupation_id_onet_list)]
exposure_antropic_occupations =  antropic_occupations.filter(["onetsoc_code","occupation_title","robot_exposure_index"]).rename(columns={"onetsoc_code":"occupation_id_onet","occupation_title":"canonical_title_onet","robot_exposure_index":"antropic_occupation_exposure_score"})

#exposure- openai
openai = openai[openai["O*NET-SOC Code"].isin(occupation_id_onet_list)]
exposure_openai = openai.filter(["O*NET-SOC Code", "Title", "Task ID", "Task", "beta"]).rename(columns={"O*NET-SOC Code": "occupation_id_onet", "Title": "canonical_title_onet", "Task ID": "task_id", "Task":"task_description","beta":"openai_exposure_score"})
exposure_openai["task_id"] = exposure_openai["task_id"].astype(str).str.strip()
for d in (exposure_openai, exposure_antropic_tasks):
    d["task_id"] = d["task_id"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

onet_exposure_table = exposure_openai.merge(exposure_antropic_tasks.rename(columns={"time_share": "antropic_task_exposure_score"}),on="task_id",how="left",)
onet_exposure_table = onet_exposure_table[["occupation_id_onet", "canonical_title_onet","task_id", "task_description", "openai_exposure_score", "antropic_task_exposure_score" ]]



#output csv com abas das tables e os datasets gerais
with pd.ExcelWriter("taskbridge_tables.xlsx", engine="openpyxl") as writer:
    sectors_table.to_excel(writer, sheet_name="sectors", index=False)
    occupations_table.to_excel(writer, sheet_name="occupations", index=False)
    tasks_table.to_excel(writer, sheet_name="tasks", index=False)
    skills_table.to_excel(writer, sheet_name="skills", index=False)
    occupations_skills_table.to_excel(writer, sheet_name="occupation_skills", index=False)
    exposure_ILO.to_excel(writer, sheet_name="ESCO_task_ai_exposure", index=False)
    onet_exposure_table.to_excel(writer, sheet_name="ONET_task_ai_exposure", index=False)
    exposure_antropic_occupations.to_excel(writer, sheet_name="ONET_occupation_ai_exposure", index = False)
