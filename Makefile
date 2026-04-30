.PHONY: install run migrate upgrade import requirements

default: run

install:
	uv sync

run: install
	uv run flask --app app:app run

migrate:
	uv run flask --app app:app db migrate

upgrade:
	uv run flask --app app:app db upgrade

import:
	uv run course-fetcher.py

requirements:
	@uv export --no-dev --no-hashes --no-header --no-annotate --frozen --no-emit-project > requirements.txt

docker:
	docker-compose up --build