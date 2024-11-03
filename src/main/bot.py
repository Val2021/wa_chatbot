import os
import logging
from utils.embedding import create_embedding
from main.db import DatabaseManager
from dotenv import load_dotenv, find_dotenv
import requests
import uuid

# Logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv(find_dotenv(), override=True)

class Chatbot:
    def __init__(self, user_id):

        self.logger = logging.getLogger("Chatbot")
        self.db_manager = DatabaseManager()
        if not isinstance(user_id, int):
            try:
                # Try to convert to UUID
                self.user_id = uuid.UUID(user_id)
            except ValueError:
                # Generate a random UUID if user_id is not a valid UUID
                self.user_id = uuid.uuid4()
        else:
            self.user_id = user_id

    def call_llm(self, prompt):
        """
        Calls the language model API with the given prompt.

        :param prompt: The prompt to send to the language model.
        :return: The response text from the language model.
        """
        url = "https://api.groq.com/v1/completions"  # Example endpoint for Groq, adjust as needed
        headers = {
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "prompt": prompt,
            "max_tokens": 100,  # Adjust as needed
            "temperature": 0.7
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("text", "").strip()
        except requests.RequestException as e:
            self.logger.error(f"Error calling the Groq LLM: {e}")
            return "Sorry, there was an error accessing the LLM."

    def get_tone_from_llm(self, text):
        """
        Calls the language model to identify the tone based on the text.

        :param text: The input text to analyze.
        :return: A dictionary containing the identified tone.
        """
        prompt = f"Identify the tone of the following text: '{text}'. Respond only with 'formal' or 'informal'."
        response = self.call_llm(prompt)

        # Analyze the tone from the LLM's response, defaulting to "formal" if not identified
        tone = "informal" if "informal" in response.lower() else "formal"
        return {"tone": tone}

    def process_input(self, user_input):

        # Identify the tone using the LLM
        tone = self.identify_tone(user_input)

        # Create embedding and store it with tone in Qdrant
        embedding = create_embedding(user_input)
        self.db_manager.store_interaction(self.user_id, user_input, embedding, tone)

        # Generate the response
        response_text = self.generate_response(user_input)
        return response_text

    def check_fact(self, statement):

        # Create a prompt for fact-checking
        prompt = f"Verify whether the following statement is true or false: '{statement}'. Explain your answer."

        # Call the LLM to check the veracity of the statement
        response = self.call_llm(prompt)

        # Extract the verification result (true/false) and explanation
        veracity = "true" if "true" in response.lower() else "false" if "false" in response.lower() else "uncertain"

        # Store in Qdrant for historical tracking
        embedding = create_embedding(statement)
        self.db_manager.store_fact(self.user_id, statement, embedding, veracity, response)

        return {"veracity": veracity, "explanation": response}


    def generate_response(self, user_input):

         # Retrieve the most recent stored tone (or use current tone if new)
        tone = self.db_manager.get_last_tone(self.user_id) or "formal"

        # Create the prompt considering the tone and context
        prompt = f"Respond in a {tone} manner. User's question: {user_input}"

        # Generate response using the LLM, passing the tone as part of the context
        response = self.call_llm(prompt)

        # Store the response and context in Qdrant
        embedding = create_embedding(user_input)
        self.db_manager.store_interaction(self.user_id, user_input, embedding, tone, response)

        return response


    def identify_tone(self, user_input):

        # Update and store the user's response tone preference
        response = self.get_tone_from_llm(user_input)
        tone = response.get("tone", "formal")  # Default return is "formal" if tone is not identified
        return tone
