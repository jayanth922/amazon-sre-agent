#!/usr/bin/env bash
set -euo pipefail

echo "Creating kind cluster 'sre'..."
kind create cluster --name sre --wait 60s

echo "Creating namespace 'sre'..."
kubectl create namespace sre || true

echo "✅ Kind cluster is ready!"
echo "Next steps:"
echo "  1. Run ./scripts/kind-load.sh to build and load images"
echo "  2. Run ./scripts/k8s-apply.sh to deploy the agent"
