.PHONY: build run up down shell

build:
	docker compose build

run:
	docker compose run --rm app

up:
	docker compose up

down:
	docker compose down

shell:
	docker compose run --rm app bash