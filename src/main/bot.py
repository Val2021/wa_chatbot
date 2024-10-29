import os
import logging
from groq import Groq
from main.db import DatabaseManager
from dotenv import load_dotenv, find_dotenv

# Logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv(find_dotenv(), override=True)

class Chatbot:
    def __init__(self, user_id):
        # Set up a specific logger for this class
        self.logger = logging.getLogger("Chatbot")
        self.logger.setLevel(logging.DEBUG)  # Only this class displays DEBUG logs
        self.user_id = user_id
        self.db_manager = DatabaseManager()

        # Initialize the Groq client
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        # Load user preferences (e.g., response tone)
        user_data = self.db_manager.load_user_preferences(self.user_id)
        self.response_tone = user_data.get("response_tone", "informal")  # default to informal
        logging.info(f"User {self.user_id} loaded with response tone preference: {self.response_tone}")

    def process_input(self, user_input):
       pass
    def verify_truth(self, statement):
        pass
    def generate_response(self, user_input, tone):
        pass
    def set_response_tone(self, tone):
        pass
