from constants import USE_CASES
import pandas as pd
import json
import os

def get_results():
    results_dir = 'results/'
    results = {}
    for folder_name in os.listdir(results_dir):
        folder_path = os.path.join(results_dir, folder_name)
        results[folder_name] = []
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    results[folder_name].append(json.load(f))
    return results

def get_oracle():
    oracle = {}
    for use_case in USE_CASES:
        oracle[use_case["use_case"]] = {}
        for req in use_case["functional_requirements"]:
            oracle[req["use_case_id"]][req["sentence_id"]] = list(req["security_objectives"].keys())
    return oracle

def calculate_metrics(
    results:dict, 
    oracle:dict, 
    group:str,
    model:str,
    temperature:str,
    top_k:str,
    experiment_group:str,
    use_case:str, 
    sentence:str,
    execution_time:float
    ):
    metric = {
        "group": group,
        "model": model,
        "temperature": temperature,
        "top_k": top_k,
        "experiment_group": experiment_group,
        "use_case": use_case,
        "sentence": sentence,
        "execution_time": execution_time,
        "n": 1
    }
    metric["TP"] = len(set(oracle[use_case][sentence]) & set(results))
    metric["FP"] = len(set(results) - set(oracle[use_case][sentence]))
    metric["FN"] = len(set(oracle[use_case][sentence]) - set(results))
    return metric

# Load results
studies = json.loads(open('resources/riaz_results.json','r').read())
groups = get_results()
oracle = get_oracle()

metrics = []

for group in groups:
    for run in groups[group]:
        for result in run["treatment"]["results"]:
            results = [f"{r["objective_id"]}:{r["pattern_id"]}" for r in  result["parsed_response"]]
            metrics.append(calculate_metrics(
                results,
                oracle,
                group,
                run["model"],
                run["temperature"],
                run["top_k"],
                "treatment",
                result["use_case_id"],
                result["sentence_id"],
                run["treatment"]["execution_time_seconds"]
            ))
        for result in run["control"]["results"]:
            results = [f"{r["objective_id"]}:{r["pattern_id"]}" for r in  result["parsed_response"]]
            metrics.append(calculate_metrics(
                results,
                oracle,
                group,
                run["model"],
                run["temperature"],
                run["top_k"],
                "control",
                result["use_case_id"],
                result["sentence_id"],
                run["control"]["execution_time_seconds"]
            ))
            

metrics = pd.DataFrame(metrics)

group_metrics = metrics.groupby(["group","model","temperature","top_k",
    "experiment_group","use_case", "sentence"]).sum().reset_index()
group_metrics = group_metrics[["group","model","temperature","top_k", 
    "experiment_group","use_case", "execution_time", "n", "TP", "FP", "FN"]]
group_metrics = group_metrics.groupby(["group","model","temperature","top_k",
    "experiment_group","use_case", "execution_time", "n"]).sum().reset_index()

group_metrics["Relevance"] = group_metrics["TP"] / (group_metrics["TP"] + group_metrics["FP"])
group_metrics["Coverage"] = group_metrics["TP"] / (group_metrics["TP"] + group_metrics["FN"])
group_metrics["Efficiency"] = group_metrics["TP"] / (group_metrics["execution_time"] / 60.0)


group_metrics = group_metrics[["group", "experiment_group", "use_case", "execution_time", "n", "Relevance", "Coverage", "Efficiency"]]


for row in group_metrics.itertuples():
    studies.append({
        "id": row.group,
        "use_case": row.use_case,
        "group" : row.experiment_group,
        "relevance": row.Relevance,
        "coverage": row.Coverage,
        "eficiency": row.Efficiency,
        "quality": 0,
        "n": row.n,
    })

studies = pd.DataFrame(studies)
studies = studies[['use_case', 'group', 'id', 'relevance', 'coverage', 'eficiency', 'quality', 'n']]
studies = studies.sort_values(by=['use_case', 'group']).reset_index(drop=True)
studies.to_csv('all_study_metrics.csv')
