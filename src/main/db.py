import faiss
import numpy as np
import logging
import json
import os

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    def __init__(self, dimension=512, db_file='user_data.json'):
        # Initializes the FAISS index for similarity search
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # Index based on L2 distance
        self.user_data = {}  # Dictionary to store user preferences and history
        self.db_file = db_file

        # Load data from JSON file if it exists
        self.load_user_data()

        logging.info("DatabaseManager initialized with FAISS index.")

    def load_user_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                self.user_data = json.load(f)
            logging.info("User data loaded from JSON file.")

    def save_user_data(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.user_data, f)
        logging.info("User data saved to JSON file.")

    def store_true_statement(self, user_id, statement, embedding):
        embedding = np.array(embedding).astype("float32").reshape(1, -1)
        if embedding.shape[1] != self.dimension:
            raise ValueError("Embedding dimension incompatible with FAISS index.")

        if user_id not in self.user_data:
            self.user_data[user_id] = {"statements": [], "embeddings": [], "preferences": {}}

        self.user_data[user_id]["statements"].append(statement)
        self.user_data[user_id]["embeddings"].append(embedding)
        self.index.add(embedding)
        self.save_user_data()  # Save after each storage
        logging.info(f"Stored true statement for user {user_id}: {statement}")

    def load_user_preferences(self, user_id):
        preferences = self.user_data.get(user_id, {}).get("preferences", {})
        logging.debug(f"Loaded preferences for user {user_id}: {preferences}")
        return preferences

    def update_user_preferences(self, user_id, preferences):
        if user_id not in self.user_data:
            self.user_data[user_id] = {"statements": [], "embeddings": [], "preferences": {}}

        self.user_data[user_id]["preferences"].update(preferences)
        self.save_user_data()  # Save after each update
        logging.info(f"Updated preferences for user {user_id}: {preferences}")
