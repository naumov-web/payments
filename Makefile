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

shell:
	docker compose exec app bash

test:
	docker compose exec app pytest