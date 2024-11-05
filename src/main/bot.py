import os
import logging
from utils.embedding import create_embedding
from main.db import DatabaseManager
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import MessagesPlaceholder,ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory



# Logging configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv(find_dotenv(), override=True)

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]



class Chatbot():

    def __init__(self,user_id):

        """
        Initialize the Chatbot instance, configuring LangChain with GroqLLM and setting up memory.

        Args:
            user_id (str): User ID as a string.
        """
        self.user_id = user_id
        self.logger = logging.getLogger("Chatbot")
        self.db_manager = DatabaseManager()
        self.client = ChatGroq(model="llama3-8b-8192")
        self.store = {}

    def get_session_history(self,session_id: str) -> BaseChatMessageHistory:
            if session_id not in self.store:
                self.store[session_id] = InMemoryChatMessageHistory()
            return self.store[session_id]

    def identify_tone(self, user_input):

        """
        Identifies the tone of the user input.

        :param user_input: The user's input text.
        :return: The identified tone ('formal' or 'informal').
        """

        # Update and store the user's response tone preference

        statement = f"Identify the tone of this text: '{user_input}'. Return 'formal' or 'informal'."
        mensage = [HumanMessage(content=statement)]
        config = {"configurable": {"thread_id": "abc123"}}
        response = self.client.invoke(mensage,config)

        tone_value = response.content.lower() if hasattr(response, "content") else ""

        tone = "informal" if "informal" in tone_value else "formal"
        self.logger.info(f"Tone returned: {tone}")
        return tone

    def generate_response(self, user_input):

        """
        Generates a response based on the user's input and the identified tone.

        :param user_input: The user's input text.
        :return: The generated response text.
        """

        tone = self.identify_tone(user_input)

        # Create the prompt considering the tone and context
        message = f"Respond in a {tone} manner. User's question: {user_input}"

        session_id = "firstchat"

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | self.client

        model_with_memory=RunnableWithMessageHistory(chain,self.get_session_history)

        config = {"configurable": {"session_id": session_id}}


        response = model_with_memory.invoke([HumanMessage(content=message)],config=config).content

        self.logger.info(f"Generated response: {response}")
        self.logger.info(f"Generated  store: {self.get_session_history(session_id)}")
        self.logger.info(f"Session History: {self.store}")

        return response

    def process_input(self, user_input):

        """
        Processes the user's input, identifying tone and generating a response.

        :param user_input: The user's input text.
        :return: The generated response text.
        """

        #Checks the veracity of a statement
        self.check_fact(user_input)

        # Identify the tone using the LLM
        tone = self.identify_tone(user_input)

        # Generate response with LangChain
        response_text = self.generate_response(user_input=user_input)

        return response_text


    def check_fact(self, statement):

        """
        Checks the veracity of a statement using the LLM.

        :param statement: The statement to verify.
        :return: A dictionary with the veracity and explanation.
        """

        # Create a prompt for fact-checking
        prompt = f"Verify whether the following statement is true or false: '{statement}'. Explain your answer."

        # Call the LLM to check the veracity of the statement

        mensage = [HumanMessage(content=prompt)]
        config = {"configurable": {"thread_id": "abc123"}}
        response = self.client.invoke(mensage,config)
        self.logger.info(f"response invoke: {response.content}")
        logging.info(f"response for check veracity: {response.content}")

        # Identify the tone using the LLM
        tone = self.identify_tone(statement)

        # Extract the verification result (true/false) and explanation

        veracity_value = response.content.lower() if hasattr(response, "content") else ""
        self.logger.info(f"Response veracity: {veracity_value}")
        veracity = "true" if "true" in veracity_value else "false" if "false" in veracity_value else "uncertain"
        # Log the veracity result
        logging.info(f"Veracity: {veracity}")

        # Store in Qdrant for historical tracking only if veracity is true
        if veracity == "true":
            embedding = create_embedding(statement)
            self.db_manager.store_interaction(statement, embedding, tone, response=response)
            logging.info("Interaction saved in the database.")
        else:
            logging.info("Interaction not saved in the database due to veracity being false or uncertain.")

        return {"veracity": veracity, "explanation": response}
