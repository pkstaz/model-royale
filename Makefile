.PHONY: api web up

api:
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --reload-dir app --port 8000

web:
	cd apps/web && npm run dev

up:
	docker compose up --build
