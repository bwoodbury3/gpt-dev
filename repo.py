"""
Module for handling a brand new repo.
"""

from gitignore_parser import parse_gitignore
import os
import random
import re
import requests
import string
import subprocess


class GithubRepo:
    """
    Handles a github repository
    """

    def __init__(self, url: str):
        """
        Initialize a new github repository.

        Args:
            url: The url to the repository.
                 e.g.: "https://github.com/bwoodbury3/gpt-dev"
        """
        self.url = url
        self.api_url = re.sub(
            r"(https://github.com/)([\w-]+)/([\w-]+)(/.*)?",
            r"https://api.github.com/repos/\2/\3/issues",
            self.url,
        )
        self.dir = None
        self.branch = None

    @property
    def files(self):
        if not self.dir:
            raise ValueError("Repository has not been checked out.")

        # Use the git ls-files command to get a list of all files in the repository
        result = subprocess.run(
            ["git", "-C", self.dir, "ls-files"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise ValueError("Could not get list of files in repository.")

        # Decode the byte string output and return a list of files
        return result.stdout.decode("utf-8").splitlines()

    def _git(self, subcommand: list) -> str:
        """
        Run a git command on behalf of a local repository.

        Args:
            subcommand: The git subcommand, e.g. ["show", "HEAD"]
        """
        git_command = ["git", "-C", self.dir] + subcommand
        result = subprocess.run(
            git_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise ValueError(f"Could not execute: {git_command}")

    def clone(self, dir: str):
        """
        Clone out the repository.

        Args:
            dir: The directory at which to clone.
        """
        if os.path.isdir(os.path.join(dir, ".git")):
            self.dir = dir
        else:
            # Clone the repository into the given directory
            result = subprocess.run(
                ["git", "clone", self.url, dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode != 0:
                raise ValueError("Could not check out repository.")
            self.dir = dir

        # TODO: Find the default branch (master/main) and force reset onto HEAD.
        self.branch = "main"

        # Start from a clean slate.
        self._git(["reset", "--hard", "HEAD"])
        self._git(["checkout", self.branch])
        self._git(["fetch"])
        self._git(["reset", "--hard", f"origin/{self.branch}"])

    def get_issues(self):
        # Make the API request to get the issues
        response = requests.get(self.api_url)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Could not get issues from {self.api_url}")
            raise ValueError("Could not search for issues.")

        # Parse the JSON response and extract the issue titles
        return response.json()

    def new_branch(self, branchname: str = None):
        """
        Checkout a new branch.

        Args:
            branchname: The name of the branch. Will just be a random string if
                        unspecified.
        """
        if not branchname:
            branchname = "".join(random.sample(string.ascii_lowercase, 15))
        branchname = f"gpt-feature/{branchname}"
        self._git(["checkout", "-B", branchname])
        self.branch = branchname

    def commit_and_push(self, commit_msg: str):
        """
        Push local branch upstream.
        """
        self._git(["commit", "-am", commit_msg])
        self._git(["push", "--set-upstream", "origin", self.branch])

    def read(self, filename: str) -> str:
        """
        Reads the contents of a file in the repository.

        Args:
            filename: The filename to query.
        """
        with open(os.path.join(self.dir, filename), "r") as f:
            return f.read()

    def write(self, filename: str, text: str) -> str:
        """
        Writes the contents to a file in the repository.

        Args:
            filename: The filename to query.
            text: The text to write.
        """
        with open(os.path.join(self.dir, filename), "w") as f:
            f.write(text)
