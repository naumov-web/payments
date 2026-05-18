.PHONY: up down build rebuild logs app shell test lint format check

up:
	docker compose up

down:
	docker compose down

build:
	docker compose build

rebuild:
	docker compose down -v
	docker compose up --build

logs:
	docker compose logs -f

app:
	docker compose up app

shell:
	docker compose exec app bash

test:
	docker compose exec app pytest

lint:
	docker compose exec app ruff check .

format:
	docker compose exec app ruff format .

check:
	docker compose exec app mypy .