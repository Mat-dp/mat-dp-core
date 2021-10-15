#!/bin/sh
set -e
poetry run black .
poetry run isort .
poetry run autoflake -r --in-place --remove-unused-variables .
poetry run pre-commit run --all-files
