from sentence_transformers import SentenceTransformer, util
import logging

# https://huggingface.co/sentence-transformers/all-mpnet-base-v2
# Tipo de tokenización    Byte-Pair Encoding


class CosineSimilarity:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
        """
        Load a sentence embedding model from HuggingFace.
        Recommended: all-mpnet-base-v2 (very strong)
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.logger = logging.getLogger()

    def compute(self, text1: str, text2: str) -> float:
        """
        Returns cosine similarity between two texts.
        Result is between -1 and 1.
        """
        emb1 = self.model.encode(text1, convert_to_tensor=True)
        emb2 = self.model.encode(text2, convert_to_tensor=True)
        cosine_score = util.cos_sim(emb1, emb2)
        self.logger.debug(f"Cosine similarity between '{text1}' and '{text2}': {cosine_score.item()}")
        return float(cosine_score.item())
    
    def compute_many(self, texts: list, reference: str) -> list[float]:
        """
        Computes cosine similarity between base_text and every text in the list.

        Returns a list of cosine similarity scores.
        """

        base_emb = self.model.encode(reference, convert_to_tensor=True)

        batch_emb = self.model.encode(texts, convert_to_tensor=True)

        similarities = util.cos_sim(base_emb, batch_emb)[0]

        for text, s in zip(texts, similarities):
            self.logger.debug(f"Cosine similarity between '{reference}' and '{text}': {s.item()}")

        return [float(s.item()) for s in similarities]
