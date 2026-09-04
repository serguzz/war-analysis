.PHONY: build run up down shell

build:
	docker compose build

run:
	docker compose run --rm app

read_data:
	docker compose run --rm app python scripts/read_ods.py

month_diagram:
	docker compose run --rm app python scripts/month_diagram.py

ualosses_demo:
	docker compose run --rm app python scripts/ualosses_demo.py

up:
	docker compose up

down:
	docker compose down

shell:
	docker compose run --rm app bash