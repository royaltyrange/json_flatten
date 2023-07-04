from app.objects.flatten_json import FlattenJson


def get_arguments():
    retry = True
    while retry:
        try:
            # Input Folder
            json_folder_path = input("[REQUIRED] Please enter input JSON folder path: ").strip()
            if not json_folder_path or json_folder_path == "":
                raise ValueError("Input JSON folder path can't be empty.")
            # File Name
            csv_file_name = input("[REQUIRED] Please enter output file name: ").strip()
            if not csv_file_name or csv_file_name == "":
                raise ValueError("Output file name can't be empty.")

            # Amount of examples
            print("\nIf you want to change amount of examples, please write count.")
            print("By default process will collect 1000 examples, if you don't want to change it - press enter.")
            amount_of_examples = input("[OPTIONAL] Please amount of examples (count): ").strip()
            if not amount_of_examples or amount_of_examples == "" or int(amount_of_examples) == 0:
                amount_of_examples = 1000
            else:
                amount_of_examples = int(amount_of_examples)
            return json_folder_path, csv_file_name, amount_of_examples
        except Exception as exception_reason:
            print(f"ERROR: {str(exception_reason)}")
            retry_output = input("Retry? Y/N:").lower().strip()
            if retry_output.find("y") >= 0:
                retry = True
            else:
                retry = False


def main():
    json_folder_path, csv_file_name, amount_of_examples = get_arguments()
    flatten_json = FlattenJson(folder_path=json_folder_path, encoding="utf-8", amount_of_examples=amount_of_examples)
    flatten_json.read_files()
    flatten_json.get_flatten_json()
    flatten_json.save_flatten_json_to_csv(csv_file_name)


if __name__ == "__main__":
    main()
