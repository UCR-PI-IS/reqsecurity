from constants import SYSTEM_PROMPT, SYSTEM_PATTERN_PROMPT, USER_PATTERN_PROMPT, USER_PROMPT
from constants import API_KEY, FUNCTIONAL_REQUIREMENTS, SYSTEM_CONTEXTS 
from SecurityRequirementGenerator import SecurityRequirementGenerator
from models.Claude import Claude
import random, json, logging, time, os

def execute(
    model:str, 
    temperature:float,
    top_k:float,
    user_prompt:str,
    sys_prompt:str):
    model = Claude(
        api_key=API_KEY,
        model=model,
        role=sys_prompt,
        temperature=temperature,
        top_k=top_k
    )
    generator = SecurityRequirementGenerator(model, user_prompt)
    results = []
    functional_requirements = FUNCTIONAL_REQUIREMENTS.copy()
    random.shuffle(functional_requirements)
    start_time = time.time()

    for requirement in functional_requirements:
        logger.info(f"Processing Use Case ID: {requirement['use_case_id']}, Sentence ID: {requirement['sentence_id']}")
        context = SYSTEM_CONTEXTS.get(requirement['use_case_id'], "")
        result = generator.generate(context, requirement['sentence_text'])
        results.append({
            'use_case_id': requirement['use_case_id'],
            'sentence_id': requirement['sentence_id'],
            **result
        })
        logger.info(f"Result: {json.dumps(result, indent=2)}")

    end_time = time.time()
    execution_time = end_time - start_time
    logger.info(f"Execution time: {execution_time:.2f} seconds")

    results = {
        'execution_time_seconds': execution_time,
        'results': results
    }
    return results

def get_logger(id:str):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f"logs/{id}.log", encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

if __name__ == "__main__":
    model = "claude-haiku-4-5-20251001"
    temperature = 0.7
    top_k = 0.5
    n = 15
    id = "UCR26d"
    logger = get_logger(id)
    logger.info(f"Using model: {model} temperature: {temperature} top_k: {top_k} n: {n}")

    results = {
        'model': model,
        'temperature': temperature,
        'top_k': top_k,
        'n': n,
        'treatment': {},
        'control': {}
    }

    for i in range(11, n):
        # Treatment group
        logger.info(f"Starting treatment group execution, iteration {i+1}/{n}.")
        treatment = execute(
            model=model,
            top_k=top_k,
            temperature=temperature,
            user_prompt=USER_PATTERN_PROMPT,
            sys_prompt=SYSTEM_PATTERN_PROMPT
        )

        # Control group
        logger.info(f"Starting control group execution, iteration {i+1}/{n}.")
        control = execute(
            model=model,
            top_k=top_k,
            temperature=temperature,
            user_prompt=USER_PROMPT,
            sys_prompt=SYSTEM_PROMPT
        )
        results['treatment'] = treatment
        results['control'] = control
        file_name = f'results/{id}/results_iteration_{i+1}.json'
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved results to {file_name}")
    logger.info("All iterations completed.")