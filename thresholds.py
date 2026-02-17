import pandas as pd

df = pd.read_excel('metrics.xlsx', sheet_name='Similarity Metrics')
records = df.to_dict('records')

bertscore_precision_threshold=0.80
bertscore_recall_threshold=0.82
bertscore_f1_threshold=0.83
cosine_similarity_threshold=0.75
g_eval_threshold=85

bertscore_results = []
cosine_similarity_results = []
g_eval_results = []

for record in records:
    FN =int(record['exception'] == "FN")
    TP = int(record['bertscore_precision'] >= bertscore_precision_threshold
          and record['bertscore_recall'] >= bertscore_recall_threshold
          and record['bertscore_f1'] >= bertscore_f1_threshold)
    FP = int(record['exception'] == "FP" or (not TP and not FN))
    bertscore_results.append({
        'id': record['id'],
        'run': record['run'],
        'use_case': record['use_case'],
        'sentence': record['sentence'],
        'group': record['group'],
        'objective': record['objective'],
        'pattern': record['pattern'],
        'FN': FN, 
        'TP': TP, 
        'FP': FP
    })
    FN =int(record['exception'] == "FN")
    TP = int(record['bertscore_recall'] >= bertscore_recall_threshold)
    FP = int(record['exception'] == "FP" or (not TP and not FN))
    cosine_similarity_results.append({
        'id': record['id'],
        'run': record['run'],
        'use_case': record['use_case'],
        'sentence': record['sentence'],
        'group': record['group'],
        'objective': record['objective'],
        'pattern': record['pattern'],
        'FN': FN, 
        'TP': TP, 
        'FP': FP
    })
    FN =int(record['exception'] == "FN")
    TP = int(record['g_eval'] >= g_eval_threshold)
    FP = int(record['exception'] == "FP" or (not TP and not FN))
    g_eval_results.append({
        'id': record['id'],
        'run': record['run'],
        'use_case': record['use_case'],
        'sentence': record['sentence'],
        'group': record['group'],
        'objective': record['objective'],
        'pattern': record['pattern'],
        'FN': FN, 
        'TP': TP, 
        'FP': FP
    })

# Create a df
bertscore_df = pd.DataFrame(bertscore_results)
cosine_similarity_df = pd.DataFrame(cosine_similarity_results)
g_eval_df = pd.DataFrame(g_eval_results)

# Save into excel as new sheets
# mode='a' para agregar (append), si no existe engine='openpyxl' puede dar error en append
# if_sheet_exists='replace' reemplaza la hoja si ya existe
with pd.ExcelWriter('metrics.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    bertscore_df.to_excel(writer, sheet_name='BERTScore_Evaluated', index=False)
    cosine_similarity_df.to_excel(writer, sheet_name='Cosine_Similarity_Evaluated', index=False)
    g_eval_df.to_excel(writer, sheet_name='GEval_Evaluated', index=False)

