#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="sre"

echo "Building SRE Agent image..."
docker build -t ghcr.io/jayanth922/sre-agent:local .

echo "Loading SRE Agent image into kind cluster..."
kind load docker-image ghcr.io/jayanth922/sre-agent:local --name ${CLUSTER_NAME}

echo "Building MCP OpenAPI server image..."
docker build -t ghcr.io/jayanth922/mcp-openapi:local mcp_servers/openapi

echo "Loading MCP OpenAPI server image into kind cluster..."
kind load docker-image ghcr.io/jayanth922/mcp-openapi:local --name ${CLUSTER_NAME}

echo "✅ Images loaded successfully!"
echo "Next step: Run ./scripts/k8s-apply.sh to deploy"
