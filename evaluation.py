from metrics.CosineSimilarity import CosineSimilarity
from transformers import AutoTokenizer
from constants import USE_CASES, API_KEY
from metrics.BERTScore import BertScore
from models.Claude import Claude
from metrics.GEval import GEval
import concurrent.futures
import pandas as pd
import logging
import json
import os

AutoTokenizer.from_pretrained("facebook/bart-large-mnli")

#region Logger Configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f"logs/metrics.log", encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
#endregion

#region Model and Metrics Initialization
logger.info("Initializing models and metrics calculators...")

model = Claude(
    api_key=API_KEY,
    model="claude-haiku-4-5-20251001",
    temperature=1.0,
    top_p=1.0
)
logger.info(f"Claude model initialized with model: {model.model}, temperature: {model.temperature}, top_p: {model.top_p}")
bert_score = BertScore(
    model_type="facebook/bart-large-mnli",
    lang="en"
)
logger.info(f"BertScore initialized with model_type: {bert_score.model_type}, lang: {bert_score.lang}")
cosine_similarity = CosineSimilarity(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
logger.info(f"CosineSimilarity initialized with model_name: {cosine_similarity.model_name}")
g_eval = GEval(model)
#endregion

#region Helper Functions
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
            oracle[req["use_case_id"]][req["sentence_id"]] = {}
            for key, value in req["security_objectives"].items():
                oracle[req["use_case_id"]][req["sentence_id"]][key] = value
    return oracle

def calculate_metrics(
    results:dict, 
    oracle:dict, 
    group:str,
    run:str,
    model:str,
    temperature:str,
    top_k:str,
    experiment_group:str,
    use_case:str, 
    sentence:str,
    execution_time:float
    ):
    metric = {
        "id": group,
        "run": run,
        "model": model,
        "temperature": temperature,
        "top_k": top_k,
        "use_case": use_case,
        "sentence": sentence,
        "group": experiment_group,
        "execution_time": execution_time,
    }
    oracle_ids = set(oracle[use_case][sentence].keys())
    metric["TP"] = len([r for r in results if r in oracle_ids])
    metric["FP"] = len([r for r in results if r not in oracle_ids])
    metric["FN"] = len(oracle_ids - set(results))
    return metric
#endregion

#region Main Functions
def get_determinism(groups):
    results = []

    for group in groups:
        for run in groups[group]:
            for result in run["treatment"]["results"]:
                results.append({
                    "id": group,
                    "use_case": result["use_case_id"],
                    "sentence": result["sentence_id"],
                    "group": "treatment",
                    "response": result["raw_response"],
                })
            for result in run["control"]["results"]:
                results.append({
                    "id": group,
                    "use_case": result["use_case_id"],
                    "sentence": result["sentence_id"],
                    "group": "control",
                    "response": result["raw_response"],
                })

    df = pd.DataFrame(results)

    groups = df.groupby(['id', 'use_case', 'sentence', 'group'])['response'].apply(list).reset_index()
    
    metrics = []

    for _, row in groups.iterrows():
        responses = row['response']
        cosine_scores = cosine_similarity.compute_many(responses[1:], responses[0])
        bert_scores = bert_score.compute_many(responses[1:], responses[0])
        g_eval_scores = [g_eval.evaluate(responses[0], response) for response in responses[1:]]
        for bert, cosine, g_eval_score in zip(bert_scores, cosine_scores, g_eval_scores):
            metrics.append({
                "id": row['id'],
                "use_case": row['use_case'],
                "sentence": row['sentence'],
                "group": row['group'],
                "bertscore_precision": bert["precision"],
                "bertscore_recall": bert["recall"],
                "bertscore_f1": bert["f1"],
                "cosine_similarity": cosine,
                "g_eval": g_eval_score
            })
    metrics = pd.DataFrame(metrics)
    return metrics

def compute_metrics_by_id(groups, oracle):
    metrics = []
    for group in groups:
        for run in groups[group]:
            for result in run["treatment"]["results"]:
                results = [f"{r["objective_id"]}:{r["pattern_id"]}" for r in  result["parsed_response"]]
                metrics.append(calculate_metrics(
                    results,
                    oracle,
                    group,
                    run["run"],
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
                    run["run"],
                    run["model"],
                    run["temperature"],
                    run["top_k"],
                    "control",
                    result["use_case_id"],
                    result["sentence_id"],
                    run["control"]["execution_time_seconds"]
                ))
    metrics = pd.DataFrame(metrics)
    return metrics

def compute_metrics_by_similitude(groups, oracle):
    requirements = []
    metrics = []
    for group in groups:
        for run in groups[group]:
            for result in run["treatment"]["results"]:
                for requirement in result["parsed_response"]:
                    requirements.append({
                        "id": group,
                        "run": run["run"],
                        "use_case": result["use_case_id"],
                        "sentence": result["sentence_id"],
                        "group": "treatment",
                        "requirement": requirement["requirement"],
                    })
                ids = [ r["objective_id"] + ":" + r["pattern_id"] for r in result["parsed_response"] ]
                for _ in set(oracle[result["use_case_id"]][result["sentence_id"]].keys()) - set(ids):
                    metrics.append({
                        "id": group,
                        "run": run["run"],
                        "use_case": result["use_case_id"],
                        "sentence": result["sentence_id"],
                        "group": "treatment",
                        "objective": requirement["objective_id"],
                        "pattern": requirement["pattern_id"],
                        "bertscore_precision": 0,
                        "bertscore_recall": 0,
                        "bertscore_f1": 0,
                        "cosine_similarity": 0,
                        "g_eval": 0,
                        "exception": "FN"
                    })
            for result in run["control"]["results"]:
                for requirement in result["parsed_response"]:
                    requirements.append({
                        "id": group,
                        "run": run["run"],
                        "use_case": result["use_case_id"],
                        "sentence": result["sentence_id"],
                        "group": "control",
                        "objective": requirement["objective_id"],
                        "pattern": requirement["pattern_id"],
                        "requirement": requirement["requirement"],
                    })
                ids = [ r["objective_id"] + ":" + r["pattern_id"] for r in result["parsed_response"] ]
                for _ in set(oracle[result["use_case_id"]][result["sentence_id"]].keys()) - set(ids):
                    metrics.append({
                        "id": group,
                        "run": run["run"],
                        "use_case": result["use_case_id"],
                        "sentence": result["sentence_id"],
                        "group": "control",
                        "objective": requirement["objective_id"],
                        "pattern": requirement["pattern_id"],
                        "bertscore_precision": 0,
                        "bertscore_recall": 0,
                        "bertscore_f1": 0,
                        "cosine_similarity": 0,
                        "g_eval": 0,
                        "exception": "FN"
                    })  

    df = pd.DataFrame(requirements)
    groups = df.groupby(
        ['id', 'run', 'use_case', 'sentence', 'group', 'objective', 'pattern']
    ).agg({'requirement': list}).reset_index()

    for _, row in groups.iterrows():
        id = f"{row['objective']}:{row['pattern']}"
        generated_requirements = row['requirement']
        metric = {
            "id": row['id'],
            "run": row['run'],
            "use_case": row['use_case'],
            "sentence": row['sentence'],
            "group": row['group'],
            "objective": row['objective'],
            "pattern": row['pattern'],
            "bertscore_precision": 0,
            "bertscore_recall": 0,
            "bertscore_f1": 0,
            "cosine_similarity": 0,
            "g_eval": 0,
            "exception": None
        }
        if id not in oracle[row['use_case']][row['sentence']]:
            # False Positive
            metric["exception"] = "FP"
            metrics.extend([metric.copy() for _ in range(len(generated_requirements))])
            continue
        oracle_requirement = oracle[row['use_case']][row['sentence']][id]
        cosine_scores = cosine_similarity.compute_many(generated_requirements, oracle_requirement)
        bertscores = bert_score.compute_many(generated_requirements, oracle_requirement)
        g_eval_scores = [g_eval.evaluate(oracle_requirement, req) for req in row['requirement']]
        
        for cosine, bert, geval in zip(cosine_scores, bertscores, g_eval_scores):
            metric["cosine_similarity"] = cosine
            metric["bertscore_precision"] = bert["precision"]
            metric["bertscore_recall"] = bert["recall"]
            metric["bertscore_f1"] = bert["f1"]
            metric["g_eval"] = geval
            metrics.append(metric.copy())
    return pd.DataFrame(metrics)

#endregion

if __name__ == "__main__":
    studies = json.loads(open('resources/riaz_results.json','r').read())
    results = get_results()
    oracle = get_oracle()


    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        similarity_future = executor.submit(compute_metrics_by_similitude, results, oracle)
        # metrics_future = executor.submit(compute_metrics_by_id, results, oracle)
        # determinism_future = executor.submit(get_determinism, results)
        similarity_results = similarity_future.result()
        # metrics_results = metrics_future.result()
        # determinism_results = determinism_future.result()

        # Save results to excel
        with pd.ExcelWriter('metrics.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            similarity_results.to_excel(writer, sheet_name='Similarity Metrics', index=False)
            # metrics_results.to_excel(writer, sheet_name='Metrics by ID', index=False)
            # determinism_results.to_excel(writer, sheet_name='Determinism Metrics', index=False)