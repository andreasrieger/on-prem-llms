from mypackage import userinput, finder
from langchain_ollama import ChatOllama


def get_use_cases():
    return [
        "Retrieve from existing database",
        "Update database with own data"
    ]


use_cases = get_use_cases()
finder.print_enumerated_list(use_cases)

user_choice = userinput.get_user_input("Select use case", default="1")
print(f"You selected: '{use_cases[int(user_choice) - 1]}'")


llm = ChatOllama(
    model="llama3.2",
    temperature=0.1,
)
