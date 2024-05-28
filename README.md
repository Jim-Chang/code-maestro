# Code Maestro

## Python

Use pyenv to install python 3.11.6 and set it as the local version.

```bash
pyenv install 3.11.6
pyenv local 3.11.6
```

## Install dependencies

Use poetry to manage dependencies.

```bash
poetry env use 3.11.6
poetry install
```

## Install pre-commit hooks

```bash
poetry run pre-commit install
```

## Run server

```bash
./start.sh
```
