{{/*
Expand the name of the chart.
*/}}
{{- define "model-royale.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "model-royale.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "model-royale.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "model-royale.labels" -}}
helm.sh/chart: {{ include "model-royale.chart" . }}
{{ include "model-royale.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: model-royale
{{- end }}

{{- define "model-royale.selectorLabels" -}}
app.kubernetes.io/name: {{ include "model-royale.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "model-royale.webSelectorLabels" -}}
{{ include "model-royale.selectorLabels" . }}
app.kubernetes.io/component: web
{{- end }}

{{- define "model-royale.apiSelectorLabels" -}}
{{ include "model-royale.selectorLabels" . }}
app.kubernetes.io/component: api
{{- end }}

{{- define "model-royale.postgresSelectorLabels" -}}
{{ include "model-royale.selectorLabels" . }}
app.kubernetes.io/component: postgres
{{- end }}

{{- define "model-royale.webName" -}}
{{- printf "%s-web" (include "model-royale.fullname" .) }}
{{- end }}

{{- define "model-royale.apiName" -}}
{{- printf "%s-api" (include "model-royale.fullname" .) }}
{{- end }}

{{- define "model-royale.postgresName" -}}
{{- printf "%s-postgres" (include "model-royale.fullname" .) }}
{{- end }}

{{- define "model-royale.secretName" -}}
{{- if .Values.secrets.existingSecret }}
{{- .Values.secrets.existingSecret }}
{{- else }}
{{- printf "%s-secret" (include "model-royale.fullname" .) }}
{{- end }}
{{- end }}

{{- define "model-royale.webImage" -}}
{{- $tag := .Values.web.image.tag | default .Chart.AppVersion }}
{{- if .Values.openshift.imageRegistry }}
{{- printf "%s/%s/web:%s" .Values.openshift.imageRegistry (include "model-royale.imageNamespace" .) $tag }}
{{- else }}
{{- printf "%s:%s" .Values.web.image.repository $tag }}
{{- end }}
{{- end }}

{{- define "model-royale.apiImage" -}}
{{- $tag := .Values.api.image.tag | default .Chart.AppVersion }}
{{- if .Values.openshift.imageRegistry }}
{{- printf "%s/%s/api:%s" .Values.openshift.imageRegistry (include "model-royale.imageNamespace" .) $tag }}
{{- else }}
{{- printf "%s:%s" .Values.api.image.repository $tag }}
{{- end }}
{{- end }}

{{- define "model-royale.imageNamespace" -}}
{{- $ns := .Values.openshift.imageNamespace }}
{{- if not $ns }}
{{- fail "Set openshift.imageNamespace to the game project (model-royale). Do not build or install into default." }}
{{- end }}
{{- $ns }}
{{- end }}
