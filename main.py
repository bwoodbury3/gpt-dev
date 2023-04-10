import argparse
from argparse import Namespace as Args
import mimetypes
import openai
from repo import GithubRepo
import time

API_KEY_PATH = "../secret/openai.key"
API_KEY = None
"""
The API key for OpenAI.
"""


class EditModel:
    name = "code-davinci-edit-001"
    temperature = 0.7


class FilesModel:
    name = "text-davinci-003"
    temperature = 0.2


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


def is_text_file(path: str):
    """
    Checks whether the file is a text file.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read()
            return True
    except UnicodeDecodeError:
        return False


def get_relevant_files(instruction: str, files: list) -> list:
    """
    Ask OpenAI which files in a repository are relevant to this query.

    Args:
        instruction: The instruction query.
        files: The full list of files in the repository.
    """
    full_prompt = (
        f"List only the files relevant to this query as a comma separated list. "
        f'Query="{instruction}", Files={files}'
    )
    resp = openai.Completion.create(
        model=FilesModel.name,
        prompt=full_prompt,
        max_tokens=500,
        temperature=FilesModel.temperature,
        presence_penalty=2.0,
    )
    text = resp.choices[0].text
    out = [path.strip().replace("'", "").replace('"', "") for path in text.split(",")]
    return out


def try_feature_request(issue: dict, instruction: str, repo: GithubRepo):
    """
    Try to execute a feature request from a prompt.
    """
    files = repo.files
    relevant_files = get_relevant_files(instruction, files)

    for filename in relevant_files:
        # TODO: DALL-E integration for image files, lol.
        if not is_text_file(filename):
            continue

        print(f"INPUT FILE: {filename}")
        input_text = repo.read(filename)
        for line in input_text.split("\n"):
            print(f"\t{line}")

        resp = openai.Edit.create(
            model=EditModel.name,
            input=input_text,
            instruction=instruction,
        )

        output_text = resp.choices[0].text

        print(f"OUTPUT FILE: {filename}")
        for line in output_text.split("\n"):
            print(f"\t{line}")

        repo.write(filename, output_text)


def poll_issues(repo: GithubRepo, interval: float = 1) -> list:
    """
    Poll github for issues.

    Args:
        repo: The repository.
        interval: The interval in seconds.
    """
    while True:
        issues = repo.get_issues()
        if len(issues) > 0:
            return issues
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Process repository path")

    # Add an argument to the parser for the repository path.
    parser.add_argument("--url", type=str, required=True, help="The github repo URL")

    # Parse the arguments from the command line
    args: Args = parser.parse_args()

    repo = GithubRepo(args.url)
    repo.checkout("/tmp/checkout")

    # TODO: Call this in a loop.
    issues = poll_issues(repo)
    issue = issues[0]
    query = f"{issue['title']}: {issue['body']}"
    print(f"Tackling issue: {query}")
    try_feature_request(issue, query, repo)


if __name__ == "__main__":
    # Initialize openai.
    API_KEY = read_api_key(path=API_KEY_PATH)
    openai.organization = "org-CZlqMk5CNooARJxSncJjcPxX"
    openai.api_key = API_KEY

    # go!
    main()
