from models.Model import Model
import logging
from openai import OpenAI

class GPT(Model):
    def __init__(self, 
        api_key: str, 
        model: str="gpt-5-mini-2025-08-07", 
        role: str="user", 
        temperature: float=0.7,
        top_p: float=1.0,
        top_k: float=40.0,
        seed: int=42
    ) -> None:
        super().__init__(api_key, model, role, temperature, top_p, top_k, seed)
        self.client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger()

        

    def query(self, prompt: str, files: list=[]) -> str:
        self.logger.info(f"Prompt: {prompt}")
        response = self.client.chat.completions.create(
            model=self.model, 
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            top_p=self.top_p,
            seed=self.seed
        )
        self.logger.info(f"Response: {response.choices[0].message.content}")
        return response.choices[0].message.content