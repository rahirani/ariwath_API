import pandas as pd
from openai import OpenAI
from app.database import engine
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def execute_sql_query(sql_query):
    """
    Execute the given SQL query on the database and return results as a Pandas DataFrame.
    """
    with engine.connect() as connection:
        result = pd.read_sql(sql_query, connection)
    return result

def natural_language_to_sql(natural_language_query):
    """
    Convert a natural language query to an SQL query using OpenAI API.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are an SQL expert. Convert natural language queries into SQL statements."},
            {"role": "user",
             "content": f"Convert the following natural language query to SQL:\n{natural_language_query}"}
        ]
    )
    # Extract SQL from the response
    generated_sql = response.choices[0].message.content.strip()

    # Clean the response to extract SQL code
    if "```sql" in generated_sql:
        generated_sql = generated_sql.split("```sql")[1].split("```")[0].strip()
    elif "```" in generated_sql:
        generated_sql = generated_sql.split("```")[1].strip()

    return generated_sql

def main():
    natural_language_query = "Show me the users who's age is 25."
    sql_query = natural_language_to_sql(natural_language_query)
    print(f"Generated SQL Query:\n{sql_query}")
    query_results = execute_sql_query(sql_query)
    print("Query Results:")
    print(query_results)

if __name__ == "__main__":
    main()