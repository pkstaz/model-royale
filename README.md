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

Con `MOCK_INFERENCE=true` (default local) no hace falta ningún modelo: el motor simula jugadas a partir de la estrategia escrita. El idioma se fija con `APP_LANG=en` (o `es` / `pt`) en `.env`; no hay selector en la UI.

```bash
docker compose up --build
```

## Instalación con Helm (OpenShift)

Instalación limpia en el proyecto **`model-royale`**: builds, imágenes, Route y el release. No uses `default`. El chart no despliega modelos; en OpenShift la base es SQLite (un PVC en el API).

Requisitos: `oc` autenticado en el cluster, Helm 3, este repo clonado.

```bash
# 1. Proyecto del juego
oc new-project model-royale
oc project model-royale

# 2. Imágenes en ese mismo namespace
oc new-build --name=api --binary --strategy=docker -n model-royale
oc start-build api --from-dir=apps/api --follow -n model-royale
oc new-build --name=web --binary --strategy=docker -n model-royale
oc start-build web --from-dir=apps/web --follow -n model-royale

# 3. Release (inglés por defecto)
helm upgrade --install model-royale deploy/helm/model-royale \
  --namespace model-royale --create-namespace \
  -f deploy/helm/model-royale/values-openshift.yaml
```

Para español o portugués (UI, errores, seed y prompts de los modelos), añade `--set lang=es` o `--set lang=pt`. El idioma no se cambia después en la UI.

Clave de admin (si no la fijaste con `--set secrets.adminPassword=…`) y URL:

```bash
oc get secret model-royale-secret -n model-royale \
  -o jsonpath='{.data.ADMIN_PASSWORD}' | base64 -d; echo

oc get route model-royale -n model-royale
```

| Ruta | Uso |
| --- | --- |
| `https://<host>/` | Jugador |
| `https://<host>/admin` | Mantenedor |
| `https://<host>/tablero/TALLER` | Tablero del evento seed |

Las URLs de InferenceService se pegan en `/admin`, no en el chart.

Para volver a instalar de cero: `oc delete project model-royale`, espera a que desaparezca, y repite los tres pasos.

Chart: `deploy/helm/model-royale`. GitOps opcional: `deploy/argocd/application.yaml` (completa `repoURL`).

## Stack

| Capa | Tecnología |
| --- | --- |
| API | FastAPI, SQLAlchemy, SQLite (OpenShift) / Postgres opcional |
| Web | React 18, Vite, tema OpenShift + Red Hat |
| Inferencia | HTTP OpenAI-compatible hacia endpoints externos |
| GitOps | Helm + Argo CD |
