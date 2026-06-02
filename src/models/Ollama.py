import requests
from models.Model import Model
import logging

class Ollama(Model):
    def __init__(self, 
        api_key: str = None,  
        model: str="deepseek-v3.1:671b-cloud", 
        role: str="user", 
        temperature: float=0.7,
        top_p: float=1.0,
        top_k: float=40.0,
        seed: int=42,
        url = 'http://localhost:11434/api/generate',
    ) -> None:
        super().__init__(api_key, model, role, temperature, top_p, top_k, seed)
        self.url = url
        self.logger = logging.getLogger()
       
    def query(self, prompt: str, files: list=[]) -> str:
        """
        Query the Ollama model locally with the given prompt.
        
        Args:
            prompt (str): The input prompt to send to the model
            files (list): Optional list of files (not supported for local text models)
            
        Returns:
            str: The model's response text
        """
        self.logger.info(f"Prompt: {prompt}")
        data = {
            "model": self.model,
            "system": self.role,
            "prompt": prompt,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": int(self.top_k),
            "seed": self.seed,
            "stream": False  # Desactivar streaming para obtener respuesta completa
        }
        
        response = requests.post(self.url, json=data)
        response.raise_for_status()  # Lanzar error si hay problema con la petición
        
        response_json = response.json()
        self.logger.info(f"Response: {response_json['response']}")
        return response_json['response']
