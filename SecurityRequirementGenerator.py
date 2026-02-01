from models.Model import Model
import logging
from toon import decode

class SecurityRequirementGenerator:
    
    def __init__(self, model:Model, user_prompt:str):
        self.model:Model = model
        self.user_prompt = user_prompt
        self.logger = logging.getLogger()

    def generate(self, context:str, requirement:str):
        prompt = self.user_prompt.replace("<CONTEXT>", context).replace("<REQUIREMENT>", requirement)
        self.logger.info(f"Generating security requirement for: \n\t{requirement}")
        raw_response = self.model.query(prompt)
        self.logger.info(f"Model response: {raw_response}")
        response = raw_response.replace("```toon", "").replace("```TOON", "").replace("```", "")
        response_json = decode(response)
        response_json = {
            'raw_response': raw_response,
            'parsed_response': response_json
        }
        return response_json