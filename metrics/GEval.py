from constants import GEVAL_PROMPT
from models.Model import Model
import logging
import json
import re

# 10.48550/arXiv.2303.16634

class GEval:
    def __init__(self, model:Model):
        self.model:Model = model
        self.logger = logging.getLogger()
        self.logger.info("GEval initialized with model: {}".format(type(model).__name__))
        self.logger.info(f"GEval prompt template: \n{GEVAL_PROMPT}")

    def evaluate(self, reference, generated):
        self.logger.info(f"Evaluating text with GEval.\nReference: {reference}\nGenerated: {generated}")
        prompt = GEVAL_PROMPT.format(
            reference=reference,
            generated=generated,
        )
        result = self.model.query(prompt)
        match = re.search(r'\d+', str(result))
        score = int(match.group())
        self.logger.info(f"GEval score between reference '{reference}' and generated '{generated}': {score}")
        return score
    