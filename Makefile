
install:
	uv sync

run:
	uv run flask --app app:app run

migrate:
	uv run flask --app app:app db migrate

upgrade:
	uv run flask --app app:app db upgrade

import:
	uv run course-fetcher.py