#!/usr/bin/env bash
set -euo pipefail

OVERLAY="${1:-kind}"  # Default to 'kind', pass 'minikube' as arg if needed

echo "Applying Kubernetes manifests with overlay: ${OVERLAY}..."

# Apply kustomization (includes namespace)
kubectl apply -k k8s/${OVERLAY}

echo "Waiting for MCP servers to be ready..."
kubectl -n sre rollout status deploy/mcp-k8s --timeout=120s
kubectl -n sre rollout status deploy/mcp-logs --timeout=120s
kubectl -n sre rollout status deploy/mcp-metrics --timeout=120s
kubectl -n sre rollout status deploy/mcp-runbooks --timeout=120s

echo "Waiting for SRE Agent to be ready..."
kubectl -n sre rollout status deploy/sre-agent --timeout=120s

echo "✅ All deployments are ready!"
echo ""
echo "To access the agent:"
if [ "${OVERLAY}" = "kind" ]; then
  echo "  kubectl -n sre port-forward svc/sre-agent 8080:8080"
  echo "  curl http://localhost:8080/invocations -H 'content-type: application/json' -d '{\"input\":{\"prompt\":\"list pods\"}}'"
elif [ "${OVERLAY}" = "minikube" ]; then
  echo "  Add '127.0.0.1 sre.local' to /etc/hosts"
  echo "  minikube tunnel  # in another terminal"
  echo "  curl http://sre.local/invocations -H 'content-type: application/json' -d '{\"input\":{\"prompt\":\"list pods\"}}'"
fi
echo ""
echo "To view logs:"
echo "  kubectl -n sre logs -f deploy/sre-agent"
echo "  kubectl -n sre logs -f deploy/mcp-k8s"
