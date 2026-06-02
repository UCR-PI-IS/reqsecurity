from bert_score import BERTScorer
import logging
import re

# 10.48550/arXiv.1904.09675

# | Modelo                           | Lenguaje                   | Tokenizador      | Algoritmo de tokenización |
# | ---------------------------------| -------------------------- | ---------------- | --------------------------|
# | roberta-large                    | Inglés (en)                | RobertaTokenizer | Byte-Pair Encoding        |
# | allenai/scibert_scivocab_uncased | Inglés científico (en-sci) | BertTokenizer    | WordPiece                 |
# | bert-base-chinese                | Chino (zh)                 | BertTokenizer    | WordPiece                 |
# | dbmdz/bert-base-turkish-cased    | Turco (tr)                 | BertTokenizer    | WordPiece                 |
# | bert-base-multilingual-cased     | Múltiples idiomas (others) | BertTokenizer    | WordPiece                 |



# @inproceedings{bert-score,
#   title={BERTScore: Evaluating Text Generation with BERT},
#   author={Tianyi Zhang* and Varsha Kishore* and Felix Wu* and Kilian Q. Weinberger and Yoav Artzi},
#   booktitle={International Conference on Learning Representations},
#   year={2020},
#   url={https://openreview.net/forum?id=SkeHuCVFDr}
# }

class BertScore:
    def __init__(self, model_type="facebook/bart-large-mnli", lang="en"):
        """
        Initializes the calculator.

        Parameters:
        model:
            - "es" uses a suitable multilingual model for Spanish.
            - You can also specify a model like "xlm-roberta-large".
        """
        self.model_type = model_type
        self.lang = lang
        self.model = BERTScorer(
            model_type=self.model_type, 
            lang=self.lang, 
            nthreads=6)
        self.logger = logging.getLogger()
        
    def compute(self, text1: str, text2: str) -> dict:
        """
        Computes BERTScore between two texts.
        
        Returns a dictionary containing:
            - precision
            - recall
            - f1
        """
        text1 = re.sub(r' +', ' ', text1)
        text2 = re.sub(r' +', ' ', text2)
        P, R, F1 = self.model.score(
            [text1], 
            [text2]
        )
        self.logger.info(f"BERTScore between '{text1}' and '{text2}' - Precision: {P.item()}, Recall: {R.item()}, F1: {F1.item()}")
        return {
            "precision": P.item(),
            "recall": R.item(),
            "f1": F1.item()
        }

    def compute_many(self, texts: list, reference: str) -> list:
        """
        Computes BERTScore between many texts and a single reference text
        using a single batch (much more efficient than calling compute() N times).

        Parameters:
            texts: list of texts to compare.
            reference: the reference text to compare all texts against.

        Returns:
            A list of dictionaries, each containing precision, recall and f1.
        """
        if not texts:
            return []
        
        reference = re.sub(r' +', ' ', reference)
        texts = [re.sub(r' +', ' ', text) for text in texts]

        references = [reference] * len(texts)

        P, R, F1 = self.model.score(
            texts, 
            references
        )

        results = []
        for i in range(len(texts)):
            results.append({
                "precision": float(P[i]),
                "recall": float(R[i]),
                "f1": float(F1[i])
            })
            self.logger.info(f"BERTScore between '{texts[i]}' and '{reference}' - Precision: {P[i].item()}, Recall: {R[i].item()}, F1: {F1[i].item()}")
        return results