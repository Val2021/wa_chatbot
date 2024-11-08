from transformers import AutoTokenizer, TFAutoModel
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = TFAutoModel.from_pretrained("distilbert-base-uncased")

def create_embedding(text):
    """
    Create an embedding for the given text using the DistilBERT model.

    Args:
        text (str): The input text to create an embedding for.

    Returns:
        list: A list representing the mean embedding vector for the input text.
    """
    logging.info(f"Creating embedding for text: {text}")
    inputs = tokenizer(text, return_tensors="tf", truncation=True, padding=True)
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.numpy().mean(axis=1).squeeze().tolist()
    return embedding
