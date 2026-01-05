from my_package import usecases, userinput, storage


def main():

    # Set locale for consistent behavior
    import locale
    locale.setlocale(locale.LC_ALL, '')

    # Initialize Qdrant client
    client = storage.get_qdrant_client()


    # Get use case from user
    use_cases = usecases.get_use_cases()
    usecases.print_enumerated_use_cases_list(use_cases)
    selected_usecase = userinput.get_user_input("Select use case by number", default="1")
    selected_usecase = usecases.get_use_cases()[int(selected_usecase) - 1]
    print(f"Selected use case: {selected_usecase["name"]}")

    # Perform the selected use case
    operation_info = usecases.init_use_case(selected_usecase["id"], client)
    print(f"Data stored. Operation Info: {operation_info}")


if __name__ == "__main__":
    main()