# GPT-DEV

Prototype with gpt-3 `code-davinci-edit-001` that takes feature requests
and modifies files in-place. When it's actually good enough, integrate with
github. For now, a command line tool.

## Quick start
```
$ mkdir ../secret
$ echo "${OPENAI_API_KEY}" > ../secret/openai.key
$ python3 -m venv gpt-dev-venv
$ pip3 install -r requirements.txt
```

## Usage:
```
$ python main.py \
    --repo-path=local/path/to/repo \
    --file-to-modify=server.js \
    --feature="Fix this bug: Error: SQLITE_ERROR: table suggestions already exists"
```
