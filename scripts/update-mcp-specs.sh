#!/usr/bin/env bash
set -euo pipefail

echo "📦 Updating MCP server ConfigMaps with OpenAPI specs..."

# Generate OpenAPI specs if they don't exist
if [ ! -f "backend/openapi_specs/k8s_api.yaml" ]; then
  echo "Generating OpenAPI specs..."
  cd backend/openapi_specs && BACKEND_DOMAIN="localhost:8000" bash generate_specs.sh && cd ../..
fi

# Update ConfigMaps with actual specs
kubectl create configmap mcp-k8s-spec \
  -n sre \
  --from-file=k8s-openapi.yaml=backend/openapi_specs/k8s_api.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap mcp-logs-spec \
  -n sre \
  --from-file=logs-openapi.yaml=backend/openapi_specs/logs_api.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap mcp-metrics-spec \
  -n sre \
  --from-file=metrics-openapi.yaml=backend/openapi_specs/metrics_api.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create configmap mcp-runbooks-spec \
  -n sre \
  --from-file=runbooks-openapi.yaml=backend/openapi_specs/runbooks_api.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

echo "✅ ConfigMaps updated!"
echo ""
echo "Restarting MCP server deployments..."
kubectl -n sre rollout restart deploy/mcp-k8s
kubectl -n sre rollout restart deploy/mcp-logs
kubectl -n sre rollout restart deploy/mcp-metrics
kubectl -n sre rollout restart deploy/mcp-runbooks

echo ""
echo "Waiting for pods to be ready..."
kubectl -n sre rollout status deploy/mcp-k8s
kubectl -n sre rollout status deploy/mcp-logs
kubectl -n sre rollout status deploy/mcp-metrics
kubectl -n sre rollout status deploy/mcp-runbooks

echo ""
echo "✅ All MCP servers are running with updated specs!"
