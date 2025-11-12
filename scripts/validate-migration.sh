#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Validating SRE Agent Migration..."
echo ""

# Check for removed directories
echo "✓ Checking removed directories..."
if [ -d "deployment/" ]; then
  echo "  ❌ deployment/ still exists"
  exit 1
fi
if [ -d "gateway/" ]; then
  echo "  ❌ gateway/ still exists"
  exit 1
fi
echo "  ✅ AgentCore directories removed"

# Check for new Kubernetes structure
echo ""
echo "✓ Checking Kubernetes manifests..."
required_files=(
  "k8s/base/namespace.yaml"
  "k8s/base/sre-agent.deployment.yaml"
  "k8s/base/mcp-k8s.deployment.yaml"
  "k8s/kind/kustomization.yaml"
  "mcp_servers/openapi/Dockerfile"
  "scripts/kind-up.sh"
  "scripts/kind-load.sh"
  "scripts/k8s-apply.sh"
)

for file in "${required_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "  ❌ Missing: $file"
    exit 1
  fi
done
echo "  ✅ All Kubernetes files present"

# Check for gateway references in code
echo ""
echo "✓ Checking for remaining gateway references..."
if grep -r "GATEWAY_ACCESS_TOKEN" sre_agent/ 2>/dev/null | grep -v ".pyc" | grep -v "__pycache__"; then
  echo "  ❌ Found GATEWAY_ACCESS_TOKEN references"
  exit 1
fi
if grep -r "_read_gateway_config" sre_agent/ 2>/dev/null | grep -v ".pyc" | grep -v "__pycache__"; then
  echo "  ❌ Found _read_gateway_config references"
  exit 1
fi
echo "  ✅ No gateway code references found"

# Check for MCP environment variables in .env.example
echo ""
echo "✓ Checking MCP configuration..."
if ! grep -q "MCP_K8S_URI" sre_agent/.env.example; then
  echo "  ❌ MCP_K8S_URI not in .env.example"
  exit 1
fi
if ! grep -q "MCP_LOGS_URI" sre_agent/.env.example; then
  echo "  ❌ MCP_LOGS_URI not in .env.example"
  exit 1
fi
echo "  ✅ MCP environment variables configured"

# Check for new function in multi_agent_langgraph.py
echo ""
echo "✓ Checking MCP client code..."
if ! grep -q "_get_mcp_server_uris" sre_agent/multi_agent_langgraph.py; then
  echo "  ❌ _get_mcp_server_uris function not found"
  exit 1
fi
if grep -q "_read_gateway_config" sre_agent/multi_agent_langgraph.py; then
  echo "  ❌ Old gateway function still exists"
  exit 1
fi
echo "  ✅ MCP client updated correctly"

# Check script permissions
echo ""
echo "✓ Checking script permissions..."
for script in scripts/kind-up.sh scripts/kind-load.sh scripts/k8s-apply.sh; do
  if [ ! -x "$script" ]; then
    echo "  ❌ $script is not executable"
    exit 1
  fi
done
echo "  ✅ All scripts are executable"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Migration validation passed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Review MIGRATION.md for complete changes"
echo "  2. Run: ./scripts/kind-up.sh"
echo "  3. Run: ./scripts/kind-load.sh"
echo "  4. Create secrets:"
echo "     kubectl create secret generic sre-agent-secrets \\"
echo "       -n sre \\"
echo "       --from-literal=GROQ_API_KEY=your-key"
echo "  5. Run: ./scripts/k8s-apply.sh"
echo "  6. Test: kubectl -n sre port-forward svc/sre-agent 8080:8080"
echo ""
