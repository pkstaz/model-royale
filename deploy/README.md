# GitOps — solo el juego

Argo CD sincroniza `deploy/k8s/overlays/openshift`. Eso levanta:

- `web` (SPA + proxy `/api`)
- `api` (motor, tablero, mantenedor)
- `postgres`

**No hay Deployment ni ServingRuntime de modelos.** El admin, en `/admin/avatares`, pega la URL `https://<predictor>.<ns>.svc.cluster.local:8080/v1` (o la Route) de un modelo que ya existe en OpenShift AI.

## Cuando haya cluster

1. Construir y pushear imágenes `api` y `web` al Image Registry del cluster (o a Quay) y ajustar `images:` en el overlay.
2. Editar el Secret `ADMIN_PASSWORD` / `SECRET_KEY` / `DATABASE_URL` (Sealed Secrets o External Secrets, más adelante).
3. Poner el `repoURL` real en `deploy/argocd/application.yaml`.
4. `kubectl apply -f deploy/argocd/application.yaml` (o crearlo desde la UI de Argo CD).

Hasta entonces este directorio es el contrato, no se aplica.
