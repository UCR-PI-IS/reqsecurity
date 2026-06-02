
from abc import ABC, abstractmethod

class Model(ABC):
    def __init__(self, 
        api_key: str, 
        model:str, 
        role: str="user",
        temperature: float=0.7,
        top_p: float=1.0,
        top_k: float=40.0,
        seed:int=None
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.role = role
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.seed = seed

    @abstractmethod
    def query(self, prompt: str) -> str:
        """
        Sends a request to a Large Language Model (LLM) with the given prompt and returns the response.

        Args:
            prompt (str): The input prompt to send to the LLM.

        Returns:
            str: The response from the LLM.
        """
        pass