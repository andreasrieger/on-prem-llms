import os
from langchain.tools import tool
from langchain_ollama import ChatOllama
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.utilities import SQLDatabase
from mypackage import finder, userinput

data_dir = os.path.join(finder.get_git_root(), "data")
db_name = 'products.db'
db_path = os.path.join(data_dir, db_name)

# Connect to the database
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# print(f"Dialect: {db.dialect}")
# print(f"Available tables: {db.get_usable_table_names()}")
# print(f'Sample output: {db.run("SELECT * FROM products LIMIT 3;")}')


@tool
def search_database(query: str, limit: int = 3) -> str:
    """Search the customer database for records matching the query.

    Args:
        query: Search terms to look for
        limit: Maximum number of results to return
    """
    return f"Found {limit} results for '{query}'"


def main():

    exit_conditions = (":q", "quit", "exit")

    # Initialize the model
    model = ChatOllama(
        model="llama3.2",
        validate_model_on_init=True,
        temperature=0,
        num_predict=256,
    ).bind_tools([search_database])

    system_msg = SystemMessage("""
        You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct {dialect} query to run,
        then look at the results of the query and return the answer. Unless the user
        specifies a specific number of examples they wish to obtain, always limit your
        query to at most {top_k} results.
        
        You can order the results by a relevant column to return the most interesting
        examples in the database. Never query for all the columns from a specific table,
        only ask for the relevant columns given the question.
        
        You MUST double check your query before executing it. If you get an error while
        executing a query, rewrite the query and try again.
        
        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
        database.
        
        To start you should ALWAYS look at the tables in the database to see what you
        can query. Do NOT skip this step.
        
        Then you should query the schema for the products table.
    """)

    while True:
        user_input = userinput.get_user_input(
            "Stelle deine Frage:",
            default="How much products are in the database?"
        )
        human_msg = HumanMessage(content=user_input)

        if user_input in exit_conditions:
            break
        else:
            messages = [system_msg, human_msg]
            response = model.invoke(messages)

            if isinstance(response, AIMessage) and response.tool_calls:
                print(response.tool_calls)
                print(response.content)

if __name__ == "__main__":
    main()