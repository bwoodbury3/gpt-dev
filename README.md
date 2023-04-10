# GPT-DEV

Prototype with gpt-3 `code-davinci-edit-001` that scrapes issues from a github
repository and automatically submits a pull request. It's kinda meteocre with
lots of shortcomings, but definitely fun to play with!

## Quick start
```
$ mkdir ../secret
$ echo "${OPENAI_API_KEY}" > ../secret/openai.key
$ python3 -m venv gpt-dev-venv
$ pip3 install -r requirements.txt
```

## Usage:
```bash
$ python main.py --url https://github.com/bwoodbury3/gpt-dev
```

# Example

Created a static website with an `index.html`.

![before](img/readme-before.png "Before")

Running gpt-dev against a repository to add a new button.
```bash
$ python main.py --url https://github.com/bwoodbury3/{repo}
```

![after](img/readme-after.png "After")
