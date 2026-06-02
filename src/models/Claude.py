from models.Model import Model
from anthropic import Anthropic
import logging

class Claude(Model):
    def __init__(self, 
        api_key: str, 
        model: str="claude-haiku-4-5-20251001", 
        role: str="user", 
        temperature: float=0.7,
        top_p: float=1.0,
        top_k: float=40.0,
        seed: int=42,
    ) -> None:
        super().__init__(api_key, model, role, temperature, top_p, top_k, seed)
        self.client:Anthropic = Anthropic(api_key=api_key)
        self.logger = logging.getLogger()

    def query(self, prompt: str, files: list=[]) -> str:
        self.logger.info(f"Prompt: {prompt}")
        response = self.client.messages.create(
            max_tokens=64000,
            model=self.model,
            stream=True,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            top_k=int(self.top_k),
            system=self.role,
        )

        
        # Collect the streamed response
        full_response = ""
        for chunk in response:
            if chunk.type == "content_block_delta":
                if hasattr(chunk.delta, "text"):
                    full_response += chunk.delta.text
        
        full_response = full_response.replace(',"\n', '\n').strip()

        self.logger.info(f"Response: {full_response}")

        return full_response