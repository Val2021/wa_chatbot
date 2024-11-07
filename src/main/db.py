
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
import logging
from uuid import uuid4
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:

    def __init__(self):

        """
        Initialize the DatabaseManager, connecting to Qdrant and setting up the collection.
        """

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



    def store_interaction(self,text, embedding, tone, response=None):

        """
        Store a user's interaction in the database.

        Args:
            user_id (str): The ID of the user.
            text (str): The input text from the user.
            embedding (list): The embedding vector for the input text.
            tone (str): The tone of the interaction.
            response (str, optional): The chatbot's response. Defaults to None.
        """

        logging.info(f"Storing interaction for user")

        point = {
            "id": str(uuid4()),  # Generate a UUID and convert to string
            "vector": embedding,
            "payload": {
                "input": text,
                "tone": tone,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),  # Store the timestamp in UTC format
            },
        }

        try:
            self.client.upsert(collection_name=self.collection_name, points=[point])
            logging.info(f"Interaction stored successfully for user.")
        except Exception as e:
            logging.error(f"Error storing interaction in Qdrant: {e}")
