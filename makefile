run:
	python src/run.py

compose-dev:
	docker compose -f compose.dev.yaml up --build

compose:
	docker compose up -d

.PHONY: run
