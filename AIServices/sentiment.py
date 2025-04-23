import os
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

class SentimentAnalyzer:
    def __init__(self, model_dir):
        """
        Initialize the SentimentAnalyzer with a pretrained DistilBERT model.
        """
        try:
            self.tokenizer = DistilBertTokenizer.from_pretrained(model_dir)
            self.model = DistilBertForSequenceClassification.from_pretrained(model_dir)
            self.model.eval()
        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")

        # Define label mapping (0 -> Negative, 1 -> Positive)
        self.label_map = {0: "Negative", 1: "Positive"}
        
        # Initialize device - use CUDA if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    async def predict(self, text):
        """
        Predict sentiment for a single string input asynchronously.

        :param text: Input text from frontend.
        :return: Dictionary with predicted label and confidence score.
        """
        if not isinstance(text, str) or text.strip() == "":
            return {"error": "Invalid input. Provide a non-empty string."}

        try:
            # Tokenize and preprocess input
            inputs = self.tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
            
            # Move inputs to the same device as the model
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Perform inference
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Get logits and convert to probabilities
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)

            # Get predicted class and confidence score
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence_score = probabilities[0][predicted_class].item()

            # Map predicted class to label
            sentiment_label = self.label_map[predicted_class]

            return {
                "text": text,
                "predicted_label": sentiment_label,
                "confidence_score": round(confidence_score * 100, 2)
            }

        except Exception as e:
            return {"error": f"Prediction error: {e}"}