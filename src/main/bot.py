import os
import logging
from groq import Groq
from utils.embedding import create_embedding
from main.db import DatabaseManager
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
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
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        # Load user preferences (e.g., response tone)
        user_data = self.db_manager.load_user_preferences(self.user_id)
        self.response_tone = user_data.get("response_tone", "informal")  # default to informal
        logging.info(f"User {self.user_id} loaded with response tone preference: {self.response_tone}")

    def process_input(self, user_input):
        # Check and store only if the statement is true
        if self.verify_truth(user_input):
            embedding = create_embedding(user_input)
            print(f"Generated embedding shape: {len(embedding)}")  # Deve imprimir 768
            self.db_manager.store_true_statement(self.user_id, user_input, embedding)
            logging.info(f"Stored true statement for user {self.user_id}: {user_input}")
        else:
            logging.info(f"Statement '{user_input}' deemed false and not stored for user {self.user_id}")

        # Respond to the user considering the response tone
        response = self.generate_response(user_input, self.response_tone)
        return response

    def verify_truth(self, statement):

        try:
            # Configurar a prompt para verificação
            prompt_template = PromptTemplate(input_variables=["statement"], template="Is the statement '{statement}' correct? Answer 'Yes' or 'No'.")
            chain = LLMChain(llm=self.client, prompt=prompt_template)

            response = chain.run(statement=statement)
            response_content = response.lower().strip()
            is_true = "yes" in response_content
            logging.info(f"Truth verification for statement '{statement}': {is_true}")

            return is_true
        except Exception as e:
            logging.error(f"Error verifying truth for statement '{statement}': {e}")
            return None  # Use None to differentiate an error from a false response

    def generate_response(self, user_input, tone):

        try:
            
            prompt_template = PromptTemplate(input_variables=["user_input", "tone"], template="Respond in a {tone} manner: {user_input}")
            chain = LLMChain(llm=self.client, prompt=prompt_template)

            response = chain.run(user_input=user_input, tone="formal" if tone == "formal" else "informal")
            return response
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "Sorry, there was an error trying to access Groq."

    def set_response_tone(self, tone):
        # Update and store the user's response tone preference
        self.response_tone = tone
        self.db_manager.update_user_preferences(self.user_id, {"response_tone": tone})
        logging.info(f"Updated response tone preference for user {self.user_id} to: {tone}")
