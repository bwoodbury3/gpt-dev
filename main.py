import argparse
from argparse import Namespace as Args
import openai
from repo import Repo

API_KEY_PATH = "../secret/openai.key"
API_KEY = None
"""
The API key for OpenAI.
"""


class BaseModel:
    name = "code-davinci-edit-001"
    temperature = 0.7


def read_api_key(path: str = API_KEY_PATH) -> str:
    """
    Gets the API key.
    """
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except RuntimeError as e:
        print(f"Error: missing API key at {path}")
        raise e


def try_feature_request(args: Args):
    """
    Try to execute a feature request from a prompt.
    """
    repo = Repo(args.repo_path)
    file_to_modify = args.file_to_modify

    input_text = repo.read(file_to_modify)
    instruction = args.feature

    print("INPUT FILE:")
    for line in input_text.split("\n"):
        print(f"\t{line}")

    resp = openai.Edit.create(
        model=args.model,
        input=input_text,
        instruction=instruction,
    )

    output_text = resp.choices[0].text

    print("OUTPUT FILE:")
    for line in output_text.split("\n"):
        print(f"\t{line}")

    repo.write(file_to_modify, output_text)


def main():
    parser = argparse.ArgumentParser(description="Process repository path")

    # Add an argument to the parser for the repository path.
    parser.add_argument(
        "--repo-path", type=str, required=True, help="path to repository"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="the name of the model to use",
        default=BaseModel.name,
    )
    parser.add_argument(
        "--feature", type=str, required=True, help="The feature you want to add."
    )
    parser.add_argument(
        "--file-to-modify",
        type=str,
        help="The file you want to modify",
        default="public/index.html",
    )

    # Parse the arguments from the command line
    args: Args = parser.parse_args()
    try_feature_request(args)

    # print(openai.Model.list())


if __name__ == "__main__":
    # Initialize openai.
    API_KEY = read_api_key(path=API_KEY_PATH)
    openai.organization = "org-CZlqMk5CNooARJxSncJjcPxX"
    openai.api_key = API_KEY

    # go!
    main()
