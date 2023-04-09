"""
Module for handling a brand new repo.
"""

from gitignore_parser import parse_gitignore
import os


class Repo:
    """
    Handles a new repository.
    """

    def __init__(self, path: str, gitcontext: bool = True):
        """
        Initialize a new repository.

        Args:
            path: The path to the repository.
            gitcontext: Whether to train on the git context. Probably want to
                        turn this one off for gigantic repos.
        """
        self.repo_path = os.path.abspath(path)
        self.repo_name = os.path.basename(self.repo_path)
        self.files = []

        print(f"Indexing repository: {self.repo_name} (@{self.repo_path})")

        gitignore_file = os.path.join(self.repo_path, ".gitignore")
        if not os.path.exists(gitignore_file):
            raise ValueError("No .gitignore file found in repository")
        matches = parse_gitignore(gitignore_file, base_dir=self.repo_path)

        # Index all files in this repository. Ignore anything in the .gitignore
        # or .git directory.
        for root, _, files in os.walk(self.repo_path):
            for filename in files:
                full_path = os.path.join(root, filename)
                if ".git/" in full_path:
                    continue
                elif not matches(full_path):
                    self.files.append(full_path)

    def _get_file(self, filename: str) -> str:
        """
        Query a file from the repo, return a path to that file.

        Args:
            filename: The filename to search for.
        """
        matches = [
            file
            for file in self.files
            if file.endswith(filename)
            and os.path.basename(file) == os.path.basename(filename)
        ]
        if len(matches) > 1:
            raise ValueError(f"Filename {filename} is ambiguous: {matches}")
        elif len(matches) == 0:
            raise ValueError(f"Could not find file {filename} in {self.files}")
        else:
            return matches[0]

    def read(self, filename: str) -> str:
        """
        Reads the contents of a file in the repository.

        Args:
            filename: The filename to query.
        """
        path = self._get_file(filename)
        with open(path, "r") as f:
            return f.read()

    def write(self, filename: str, text: str):
        """
        Writes the contents to a file in the repository.

        Args:
            filename: The filename to query.
            text: The text to write.
        """
        path = self._get_file(filename)
        with open(path, "w") as f:
            f.write(text)
