import openai
import pandas as pd
from fastapi import HTTPException
from .file_processing import read_concatenated_file
import os
from dotenv import load_dotenv
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import logging





# Set up logger for query_handler.py
def setup_logger():
    logger = logging.getLogger("query_handler")
    logger.setLevel(logging.ERROR)

    handler = logging.FileHandler("logs/query_handler.log")
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger




logger = setup_logger()




# Load the .env file to read environment variables
load_dotenv()






# Load the OpenAI API key from the .env file
openai.api_key = os.getenv("OPENAI_API_KEY")





# Initialize LangChain LLM
def create_langchain_agent(df):
    """
    Creates a LangChain agent using the OpenAI API and a Pandas DataFrame.
    """
    llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo") 
    agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True)
    return agent






def run_langchain_agent(agent, query):
    """
    Runs the LangChain agent and returns the final output for the query.
    """
    try:
        return agent.run(query).strip()
    except Exception as e:
        logger.error("LangChain agent query failed. Query: %s, Error: %s", query, str(e))
        raise HTTPException(status_code=500, detail=f"LLM Query Failed: {e}")









def identify_relevant_columns(df_columns, query):
    """
    Asks the LLM to identify relevant columns based on df.columns and query.
    """
    llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo")  # Use a lower temperature for more focused responses
    prompt = f"""Here's the df.columns: {df_columns}.

    My query is: {query}.
    
    If the query is out of context for the DataFrame, return ''.
    Based on the query, identify all the columns related to the query's context.
    If the query is about something like 'total cost' or 'average impressions' for a particular entity, 
    return the entity identifier columns (like campaign_name, campaign_id) and the associated measure columns (like cost, impressions).
    Only return a comma-separated list of column names that exactly match those from df.columns, case-sensitive.
    



    Better to include all possible relevant columns than to miss some."""
    
    response = llm.predict(prompt)
    if response is None or response == "''":
        columns=[]
        print("columns:", columns, df_columns, query)
    else:
        columns = [col.strip() for col in response.split(",")]
        print("columns:", columns, df_columns, query)
    return columns





def handle_user_query(prompt: str, df) -> str:
    """
    Handles the user's query by dynamically selecting relevant columns and sending them to the LLM.
    """
    try:
        df = read_concatenated_file()
        if df is None:
            print("No concatenated file found when processing query: %s", prompt)
            logger.error("Concatenated file not found or unreadable.")
            raise HTTPException(status_code=500, detail="Concatenated file not found or unreadable.")

        # Identify relevant columns using the LLM
        relevant_columns = identify_relevant_columns(df.columns, prompt)
        
        # Check if the query is out of context
        if relevant_columns is None or len(relevant_columns) == 0: 
            logger.warning("Query out of context or no relevant columns identified. Query: %s", prompt)
            return "I'm sorry, I can't answer that question based on the data you provided."

        # Filter the DataFrame based on relevant columns
        filtered_df = df[relevant_columns]
        print("Total rows in filtered_df:", len(filtered_df))
        # Create the LangChain agent with the DataFrame
        agent = create_langchain_agent(filtered_df)
    
        # Run the query using the agent and return the result
        return run_langchain_agent(agent, prompt)

    except HTTPException as he:
        # Handle HTTP exceptions
        logger.error(f"HTTPException occurred: {str(he.detail)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

    except Exception as e:
        # Catch any other unexpected errors
        logger.error("Error in handling user query. Query: %s, Error: %s", prompt, str(e))
        raise HTTPException(status_code=500, detail=f"LLM Query Failed: {e}")













