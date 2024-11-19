from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI LLM with API key
llm = OpenAI(temperature=0, openai_api_key=api_key)

# Create a prompt template for SQL generation
prompt_template = PromptTemplate(
    input_variables=["query"],
    template="Convert the following natural language query into SQL: {query}"
)

# Initialize the chain using RunnableSequence
sql_chain = RunnableSequence(prompt_template | llm)

# Database connection
conn = psycopg2.connect(
    dbname="airawath_db",
    user="postgres",  # This is the user
    password="password",  # Password from the URL
    host="localhost",  # Host from the URL
    port="5432"  # Port from the URL
)
cursor = conn.cursor()

# Function to convert text to SQL and execute
def text_to_sql(text):
    try:
        # Generate SQL query from text
        sql_query = sql_chain.invoke({"query": text})

        # Execute the SQL query
        cursor.execute(sql_query)

        # Fetch and return the results
        results = cursor.fetchall()
        return results
    except psycopg2.Error as db_error:
        return f"Database error: {db_error}"
    except Exception as e:
        return f"Error: {e}"


# Example usage
if __name__ == "__main__":
    prompt = "Show all users whose age is 25"
    results = text_to_sql(prompt)
    print(results)

    # Close the database connection
    cursor.close()
    conn.close()
