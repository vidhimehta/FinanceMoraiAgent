"""
FinBERT sentiment analysis model.
"""

import torch
from typing import List, Dict, Optional
from loguru import logger

from ...utils.exceptions import ModelException


class FinBERTAnalyzer:
    """
    Financial sentiment analysis using FinBERT model.
    """

    def __init__(
        self,
        model_name: str = "ProsusAI/finbert",
        device: Optional[str] = None,
    ):
        """
        Initialize FinBERT analyzer.

        Args:
            model_name: HuggingFace model name
            device: Device to use (cpu, cuda, mps)
        """
        self.model_name = model_name
        self.device = self._get_device(device)
        self.model = None
        self.tokenizer = None
        
        logger.info(f"FinBERT analyzer initialized on {self.device}")

    def _get_device(self, device: Optional[str] = None) -> str:
        """Determine best device to use."""
        if device:
            return device

        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def load_model(self) -> None:
        """
        Load FinBERT model from HuggingFace.

        Raises:
            ModelException: If model loading fails
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            logger.info(f"Loading FinBERT model: {self.model_name}")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

            # Move to device
            if self.device != "cpu":
                self.model = self.model.to(self.device)

            self.model.eval()  # Set to evaluation mode

            logger.info("✓ FinBERT model loaded successfully")

        except ImportError:
            raise ModelException(
                "transformers library not installed. "
                "Install with: pip install transformers"
            )
        except Exception as e:
            raise ModelException(f"Failed to load FinBERT model: {e}")

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores and label
        """
        if self.model is None:
            self.load_model()

        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            # Move to device
            if self.device != "cpu":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Extract scores
            scores = predictions[0].cpu().tolist()

            # FinBERT outputs: [positive, negative, neutral]
            result = {
                "positive": scores[0],
                "negative": scores[1],
                "neutral": scores[2],
                "compound": scores[0] - scores[1],  # Positive - Negative
                "label": self._get_label(scores),
            }

            return result

        except Exception as e:
            logger.error(f"FinBERT sentiment analysis failed: {e}")
            return {
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0,
                "compound": 0.0,
                "label": "neutral",
                "error": str(e),
            }

    def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict]:
        """
        Analyze sentiment of multiple texts.

        Args:
            texts: List of texts
            batch_size: Batch size for processing

        Returns:
            List of sentiment results
        """
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                result = self.analyze_sentiment(text)
                results.append(result)

        return results

    def _get_label(self, scores: List[float]) -> str:
        """Get sentiment label from scores."""
        max_idx = scores.index(max(scores))
        labels = ["positive", "negative", "neutral"]
        return labels[max_idx]

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
