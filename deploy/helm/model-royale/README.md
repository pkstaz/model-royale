# Helm — Model Royale

Chart: `deploy/helm/model-royale`. Publica **solo el juego** (web + API). En OpenShift usa SQLite, no Postgres.

La instalación de cero en cluster está documentada en el [README del repo](../../README.md#instalación-con-helm-openshift).

## Idioma

`lang`: `en` (default), `es` o `pt`. Se fija al instalar; no hay selector en la UI.

```bash
--set lang=es
```

Si cambias el idioma sobre datos ya sembrados, borra el PVC de la API para que el seed se regenere.

## Kubernetes (sin Route de OpenShift)

```bash
helm upgrade --install model-royale deploy/helm/model-royale \
  --namespace model-royale --create-namespace \
  --set route.enabled=false \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=model-royale.example.com
```

## Secretos

Si no pasas claves, Helm las genera en el primer install y las reutiliza en el upgrade:

```bash
--set secrets.adminPassword='…' \
--set secrets.secretKey='…'
```

`api.replicaCount` debe quedarse en **1**: el motor de combates y el hub SSE viven en el proceso.

## Argo CD

`deploy/argocd/application.yaml` apunta a este chart. Completa `repoURL`. Los InferenceServices de OpenShift AI van en otro Application / otro repo.
