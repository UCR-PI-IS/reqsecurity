import json
import logging

logger = logging.getLogger()

# Load prompts
GEVAL_PROMPT = open('resources/prompts/GEvalPrompt.MD','r').read()
SYSTEM_PROMPT = open('resources/prompts/SystemPrompt.MD','r').read()
SYSTEM_PATTERN_PROMPT = open('resources/prompts/SystemPatternPrompt.MD','r').read()
USER_PATTERN_PROMPT = open('resources/prompts/UserPatternPrompt.MD','r').read()
USER_PROMPT = open('resources/prompts/UserPrompt.MD','r').read()
MCP_INSTRUCTIONS = open('resources/prompts/MCPInstructions.MD','r').read()
logger.info(f"SYSTEM PATTERN PROMPT: \n{SYSTEM_PATTERN_PROMPT}")
logger.info(f"USER PATTERN PROMPT: \n{USER_PATTERN_PROMPT}")
logger.info(f"SYSTEM PROMPT: \n{SYSTEM_PROMPT}")
logger.info(f"USER PROMPT: \n{USER_PROMPT}")

USE_CASES = [
    json.loads(open('resources/usecases/UC1-Health.json','r').read()),
    json.loads(open('resources/usecases/UC2-Health.json','r').read()),
    json.loads(open('resources/usecases/UC3-Health.json','r').read()),
    json.loads(open('resources/usecases/UC1-Mobile.json','r').read()),
    json.loads(open('resources/usecases/UC2-Mobile.json','r').read())
]
logger.info(f"USE CASES: \n{json.dumps(USE_CASES, indent=2)}")
    
SYSTEM_CONTEXTS = {use_case["use_case"] : use_case["context"] for use_case in USE_CASES}
logger.info(f"SYSTEM CONTEXTS: \n{json.dumps(SYSTEM_CONTEXTS, indent=2)}")


FUNCTIONAL_REQUIREMENTS = [req for use_case in USE_CASES for req in use_case["functional_requirements"]]
logger.info(f"FUNCTIONAL REQUIREMENTS: \n{json.dumps(FUNCTIONAL_REQUIREMENTS, indent=2)}")


API_KEY = ""