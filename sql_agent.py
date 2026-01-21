import os
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
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

model = init_chat_model(
    model = "ministral-3",
    model_provider = "ollama",
    verbose = True,
    stop = ["\n\n"],
    temperature = 0.0,
    max_tokens = 1024,
)

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# for tool in tools:
#     print(f"Tool name: {tool.name}, description: {tool.description}")

system_prompt = """
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
    
    Then you should query the schema of the most relevant tables.
""".format(
        dialect=db.dialect,
        top_k=3,
)

agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt
)

def main():

    print("Starting SQL agent...")

    # Initialize chatbot
    exit_conditions = (":q", "quit", "exit")
    while True:
        # Get user query
        user_query = userinput.get_user_input("Post your question! (Or quit with ':q')",
                                              default="How much products are in the products table?")
        if user_query in exit_conditions:
            break
        else:
            input = {"messages": [{"role": "user", "content": user_query}]}
            for event in agent.stream(input=input, stream_mode="values"):
                event["messages"][-1].pretty_print()



if __name__ == "__main__":
    main()
