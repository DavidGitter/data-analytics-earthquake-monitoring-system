{{/*
Expand the name of the chart.
*/}}
{{- define "eq-monitoring-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "eq-monitoring-chart.fullname" -}}
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

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "eq-monitoring-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "eq-monitoring-chart.labels" -}}
helm.sh/chart: {{ include "eq-monitoring-chart.chart" . }}
{{ include "eq-monitoring-chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "eq-monitoring-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "eq-monitoring-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "eq-monitoring-chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "eq-monitoring-chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Converts a yaml list to a comma seperated string
*/}}
{{- define "list_to_string" -}}
{{- $len := len . -}}
{{- range $index, $item := . -}}
{{ $item.name }}
{{- if ne $index (sub $len 1) -}}, {{- end -}}
{{- end -}}
{{- end -}}