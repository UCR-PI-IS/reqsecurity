from models.Model import Model
from google import genai
from google.genai import types
import logging

class Gemini(Model):
    def __init__(self, 
        api_key: str, 
        model: str="gemini-1.5-turbo", 
        role: str="user", 
        temperature: float=0.7,
        top_p: float=1.0,
        top_k: float=40.0,
        seed: int=42
    ) -> None:
        super().__init__(api_key, model, role, temperature, top_p, top_k, seed)
        self.client = genai.Client(api_key=self.api_key)
        self.logger = logging.getLogger()

        

    def query(self, prompt: str, files: list=[]) -> str:
        self.logger.info(f"Prompt: {prompt}")
        response = self.client.models.generate_content(
            model=self.model, 
            contents=[prompt, *files],
            config=types.GenerateContentConfig(
                system_instruction=self.role,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                seed=self.seed
            )
        )
        self.logger.info(f"Response: {response.text}")
        return response.text