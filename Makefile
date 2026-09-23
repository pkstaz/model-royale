.PHONY: api web up helm-template helm-lint

api:
	cd apps/api && .venv/bin/uvicorn app.main:app --reload --reload-dir app --port 8000

web:
	cd apps/web && npm run dev

up:
	docker compose up --build

helm-template:
	helm template model-royale deploy/helm/model-royale --namespace model-royale -f deploy/helm/model-royale/values-openshift.yaml

helm-lint:
	helm lint deploy/helm/model-royale
