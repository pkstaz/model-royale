# GitOps — solo el juego

El despliegue canónico es **Helm**. La guía de instalación limpia está en el [README raíz](../README.md#instalación-con-helm-openshift).

Argo CD sincroniza `deploy/helm/model-royale`. Eso levanta web y API (SQLite en un PVC). **No hay Deployment ni ServingRuntime de modelos.** El admin pega la URL del InferenceService en `/admin`.

`deploy/k8s/` queda como referencia Kustomize, no como la vía recomendada.
