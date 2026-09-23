# Model Royale

Battle royale de avatares de IA: los jugadores inscriben un modelo, le escriben una estrategia, y el tablero muestra quién avanza y cómo se resolvió cada combate.

Este repo **no despliega modelos**. El admin registra avatares que apuntan a endpoints que ya existen (OpenShift AI u otra API compatible con OpenAI). GitOps (Argo CD) publica solo el juego.

## Cómo se juega

1. El admin crea avatares (nombre + URL + id de modelo) y un evento (formato, rondas, matriz de pagos, modo de revelado).
2. Los jugadores entran con el código, eligen avatar y escriben instrucciones extra.
3. El motor arma los combates (todos contra todos, grupos o eliminación).
4. Cada combate son N rondas A/B. El marcador sale de la matriz. Un juez opcional solo parsea respuestas sucias.
5. El tablero central muestra inscritos, avance y resultados.

Diseño completo: [docs/DESIGN.md](docs/DESIGN.md).

## Desarrollo local

```bash
# API
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../../.env.example ../../.env
uvicorn app.main:app --reload --port 8000

# Web (otra terminal)
cd apps/web
npm install
npm run dev
```

- Jugador: http://localhost:5173
- Admin: http://localhost:5173/admin (password por defecto `admin`)
- Tablero: http://localhost:5173/tablero/TALLER

Con `MOCK_INFERENCE=true` (default local) no hace falta ningún modelo: el motor simula jugadas a partir de la estrategia escrita.

```bash
docker compose up --build
```

## OpenShift / GitOps

Los manifiestos viven en `deploy/`. No se aplican hasta que avises que hay cluster.

- App Argo CD: `deploy/argocd/application.yaml`
- Kustomize: `deploy/k8s/overlays/openshift`

En el overlay hay que completar el `repoURL` y, en el Secret, `ADMIN_PASSWORD` y `SECRET_KEY`. Las URLs de los modelos se cargan luego en el mantenedor, no en estos manifiestos.

## Stack

| Capa | Tecnología |
| --- | --- |
| API | FastAPI, SQLAlchemy, SQLite / Postgres |
| Web | React 18, Vite, tema OpenShift + Red Hat |
| Inferencia | HTTP OpenAI-compatible hacia endpoints externos |
| GitOps | Argo CD + Kustomize |
