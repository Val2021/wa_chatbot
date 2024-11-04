
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
import numpy as np
import logging
from uuid import uuid4
from datetime import datetime


# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:

    def __init__(self):

        # Connect to Qdrant
        self.client = QdrantClient(url="http://localhost:6333")

        # Initialize the collection for storing user data
        self.collection_name = "user_data"

        # Vector configurations
        vectors_config = VectorParams(size=768, distance="Cosine")  # Adjust size and distance metric as needed

        # Create or recreate the collection
        self.client.recreate_collection(
            collection_name=self.collection_name,
            vectors_config=vectors_config
        )

    def get_last_tone(self, user_id):

        logging.info(f"Retrieving last tone for user: {user_id}")

        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=np.zeros(768).tolist(),  # Adjust query vector as necessary
            limit=1  # Limit the search to 1 result
        )

        if result and len(result) > 0:
            return result[0].payload.get("tone", "formal")  # Return the tone or "formal" as default

        logging.warning(f"No previous tone found for user: {user_id}. Defaulting to 'formal'.")
        return "formal"  # Default return if no tone found

    def store_interaction(self, user_id, text, embedding, tone, response=None):

        logging.info(f"Storing interaction for user: {user_id}")

        point = {
            "id": str(uuid4()),  # Generate a UUID and convert to string
            "vector": embedding,
            "payload": {
                "user_id": user_id,
                "input": text,
                "tone": tone,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),  # Store the timestamp in UTC format
            },
        }

        try:
            self.client.upsert(collection_name=self.collection_name, points=[point])
            logging.info(f"Interaction stored successfully for user: {user_id}.")
        except Exception as e:
            logging.error(f"Error storing interaction in Qdrant: {e}")

    def retrieve_history(self, user_id):

        logging.info(f"Retrieving history for user: {user_id}")

        result = self.client.search(
            collection_name=self.collection_name,
            query_vector=np.zeros(768).tolist(),
            limit=10,
            query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]}
        )

        history = [{"text": hit.payload["input"], "tone": hit.payload["tone"]} for hit in result]
        logging.info(f"Retrieved {len(history)} interactions for user: {user_id}.")
        return history
