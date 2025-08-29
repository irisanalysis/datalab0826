#!/bin/sh
PORT=${PORT:-8000}
uv run python -u -m flask --app main run -p $PORT --debug