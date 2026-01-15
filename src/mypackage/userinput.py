from typing import Optional

# Get user input
def get_user_query() -> str:
    # Get and validate user input
    qry = get_user_input("Enter search term")
    if validate_search_term(qry):
        # Proceed with search
        pass
    return qry


def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """
    Get input from user with optional default value.

    Args:
        prompt: Prompt message to display
        default: Default value if user presses Enter

    Returns:
        User input string
    """

    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()


def validate_search_term(search_term: str) -> bool:
    """
    Validate search term input.

    Args:
        search_term: Search term to validate

    Returns:
        True if valid, False otherwise
    """
    if not search_term or len(search_term.strip()) == 0:
        print("Error: Search term cannot be empty")
        return False

    if len(search_term) < 2:
        print("Warning: Search term is very short, results may not be accurate")

    return True