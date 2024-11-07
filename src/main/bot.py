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



logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv(find_dotenv(), override=True)

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]


logger = logging.getLogger()
db_manager = DatabaseManager()
client = ChatGroq(model="llama3-8b-8192")
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in store:
            store[session_id] = InMemoryChatMessageHistory()
        return store[session_id]

def identify_tone(user_input):

    """
    Identifies the tone of the user input.

    :param user_input: The user's input text.
    :return: The identified tone ('formal' or 'informal').
    """

    # Update and store the user's response tone preference

    statement = f"Identify the tone of this text. Return 'informal' only if the text contains expressions that indicate a more casual conversation, such as 'bro,' 'man,' etc.: '{user_input}'. Return 'formal' or 'informal'."
    mensage = [HumanMessage(content=statement)]
    config = {"configurable": {"thread_id": "abc123"}}
    response = client.invoke(mensage,config)

    tone_value = response.content.lower() if hasattr(response, "content") else ""
    logger.info(f"tone_value returned: {response}")

    tone = "informal" if "informal" in tone_value else "formal"
    logger.info(f"tone returned: {tone}")
    return tone

def generate_response(user_input):

    """
    Generates a response based on the user's input and the identified tone.

    :param user_input: The user's input text.
    :return: The generated response text.
    """

    tone = identify_tone(user_input)

    message = f"Respond in a {tone} manner. User's question: {user_input}"

    session_id = "firstchat"

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Answer all questions to the best of your ability."),
        MessagesPlaceholder(variable_name="messages"),
    ])

    chain = prompt | client

    model_with_memory=RunnableWithMessageHistory(chain,get_session_history)

    config = {"configurable": {"session_id": session_id}}


    response = model_with_memory.invoke([HumanMessage(content=message)],config=config).content

    logger.info(f"Generated response: {response}")
    logger.info(f"Generated  store: {get_session_history(session_id)}")
    logger.info(f"Session History: {store}")

    return response

def process_input(user_input):

    """
    Processes the user's input, identifying tone and generating a response.

    :param user_input: The user's input text.
    :return: The generated response text.
    """

    check_fact(user_input)

    tone = identify_tone(user_input)

    response_text = generate_response(user_input=user_input)

    return response_text


def check_fact(statement):

    """
    Checks the veracity of a statement using the LLM.

    :param statement: The statement to verify.
    :return: A dictionary with the veracity and explanation.
    """

    prompt = f"Verify whether the following statement is true or false: '{statement}'. Explain your answer."

    mensage = [HumanMessage(content=prompt)]
    config = {"configurable": {"thread_id": "abc123"}}
    response = client.invoke(mensage,config)
    logger.info(f"response invoke: {response.content}")
    logging.info(f"response for check veracity: {response.content}")

    tone = identify_tone(statement)

    veracity_value = response.content.lower() if hasattr(response, "content") else ""
    logger.info(f"Response veracity: {veracity_value}")
    veracity = "true" if "true" in veracity_value else "false" if "false" in veracity_value else "uncertain"
    logging.info(f"veracity: {veracity}")

    # store in Qdrant for historical tracking only if veracity is true
    if veracity == "true":
        embedding = create_embedding(statement)
        db_manager.store_interaction(statement, embedding, tone, response=response)
        logging.info("Interaction saved in the database.")
    else:
        logging.info("Interaction not saved in the database due to veracity being false or uncertain.")

    return {"veracity": veracity, "explanation": response}
