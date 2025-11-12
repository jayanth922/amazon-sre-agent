# Kubernetes Deployment for SRE Agent

This directory contains Kubernetes manifests for deploying the SRE Agent with open-source MCP servers on a local Kubernetes cluster (kind or minikube).

## Architecture

```
┌─────────────┐
│  SRE Agent  │  FastAPI runtime + LangGraph orchestration
│  (Groq LLM) │  Port 8080
└──────┬──────┘
       │
       │ HTTP (MCP Streamable HTTP)
       │
       ├───────┬───────┬───────┬────────┐
       │       │       │       │        │
   ┌───▼───┐ ┌▼───┐ ┌─▼────┐ ┌▼──────┐ │
   │ MCP   │ │MCP │ │ MCP  │ │  MCP  │ │
   │  K8s  │ │Logs│ │Metrics│ │Runbooks│
   │:3000  │ │:3000│ │:3000 │ │ :3000 │ │
   └───┬───┘ └┬───┘ └─┬────┘ └┬──────┘ │
       │      │       │       │        │
       │ OpenAPI→MCP (ivotoby/openapi-mcp-server)
       │      │       │       │        │
   ┌───▼──────▼───────▼───────▼────────▼┐
   │     Backend Services (Demo)        │
   │  K8s API / Logs / Metrics / etc.   │
   └─────────────────────────────────────┘
```

## Quick Start

### Prerequisites

1. **Docker** - For building images
2. **kubectl** - For interacting with Kubernetes
3. **kind** or **minikube** - For local cluster

Install kind:
```bash
brew install kind  # macOS
# or: https://kind.sigs.k8s.io/docs/user/quick-start/#installation
```

Install minikube (alternative):
```bash
brew install minikube  # macOS
# or: https://minikube.sigs.k8s.io/docs/start/
```

### Deploy to kind (Recommended)

```bash
# 1. Create cluster
./scripts/kind-up.sh

# 2. Build and load images
./scripts/kind-load.sh

# 3. Deploy all manifests
./scripts/k8s-apply.sh

# 4. Access the agent (in another terminal)
kubectl -n sre port-forward svc/sre-agent 8080:8080

# 5. Test
curl http://localhost:8080/invocations \
  -H "content-type: application/json" \
  -d '{"input":{"prompt":"list the pods in namespace default"}}'
```

### Deploy to minikube

```bash
# 1. Start minikube
minikube start

# 2. Build images (minikube uses local Docker)
eval $(minikube docker-env)
docker build -t ghcr.io/jayanth922/sre-agent:local .
docker build -t ghcr.io/jayanth922/mcp-openapi:local mcp_servers/openapi

# 3. Enable ingress addon
minikube addons enable ingress

# 4. Deploy
./scripts/k8s-apply.sh minikube

# 5. Access (in another terminal)
minikube tunnel

# 6. Add to /etc/hosts
echo "127.0.0.1 sre.local" | sudo tee -a /etc/hosts

# 7. Test
curl http://sre.local/invocations \
  -H "content-type: application/json" \
  -d '{"input":{"prompt":"list pods"}}'
```

## Directory Structure

```
k8s/
├── base/                          # Base manifests
│   ├── namespace.yaml             # 'sre' namespace
│   ├── sre-agent.configmap.yaml   # Environment configuration
│   ├── sre-agent.deployment.yaml  # SRE Agent deployment
│   ├── sre-agent.service.yaml     # SRE Agent service
│   ├── mcp.services.yaml          # Services for all MCP servers
│   ├── mcp-k8s.deployment.yaml    # K8s MCP server + spec
│   ├── mcp-logs.deployment.yaml   # Logs MCP server + spec
│   ├── mcp-metrics.deployment.yaml # Metrics MCP server + spec
│   └── mcp-runbooks.deployment.yaml # Runbooks MCP server + spec
├── kind/                          # kind overlay
│   ├── kustomization.yaml         # Kustomize for kind
│   └── patch-nodeport.yaml        # NodePort patch (port 30080)
└── minikube/                      # minikube overlay
    ├── kustomization.yaml         # Kustomize for minikube
    └── ingress.yaml               # Ingress (sre.local)
```

## Configuration

### Environment Variables (ConfigMap)

Edit `k8s/base/sre-agent.configmap.yaml`:

```yaml
data:
  LLM_PROVIDER: "groq"
  MCP_K8S_URI: "http://mcp-k8s.sre.svc.cluster.local:3000/mcp"
  MCP_LOGS_URI: "http://mcp-logs.sre.svc.cluster.local:3000/mcp"
  MCP_METRICS_URI: "http://mcp-metrics.svc.cluster.local:3000/mcp"
  MCP_RUNBOOKS_URI: "http://mcp-runbooks.sre.svc.cluster.local:3000/mcp"
```

### Secrets (API Keys)

Create a secret for Groq/Anthropic API keys:

```bash
kubectl create secret generic sre-agent-secrets \
  -n sre \
  --from-literal=GROQ_API_KEY=your-key-here \
  --from-literal=ANTHROPIC_API_KEY=your-key-here
```

### OpenAPI Specs

The MCP servers need OpenAPI specs. Update the ConfigMaps in each `mcp-*.deployment.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-k8s-spec
  namespace: sre
data:
  k8s-openapi.yaml: |
    openapi: 3.0.0
    info:
      title: Kubernetes API
      version: "1.0"
    # ... your actual K8s OpenAPI spec
```

Or use a script to generate ConfigMaps from `backend/openapi_specs/`:

```bash
kubectl create configmap mcp-k8s-spec \
  -n sre \
  --from-file=k8s-openapi.yaml=backend/openapi_specs/k8s_api.yaml \
  --dry-run=client -o yaml | kubectl apply -f -
```

## Troubleshooting

### Check logs

```bash
# Agent logs
kubectl -n sre logs -f deploy/sre-agent

# MCP server logs
kubectl -n sre logs -f deploy/mcp-k8s
kubectl -n sre logs -f deploy/mcp-logs
kubectl -n sre logs -f deploy/mcp-metrics
kubectl -n sre logs -f deploy/mcp-runbooks
```

### Check MCP server health

```bash
# Port-forward to MCP server
kubectl -n sre port-forward svc/mcp-k8s 3000:3000

# Test MCP endpoint
curl http://localhost:3000/mcp -X POST \
  -H "content-type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

### Restart deployments

```bash
kubectl -n sre rollout restart deploy/sre-agent
kubectl -n sre rollout restart deploy/mcp-k8s
```

### Delete and redeploy

```bash
kubectl delete namespace sre
./scripts/k8s-apply.sh
```

## Production Considerations

This setup is for **local development only**. For production:

1. **Use proper secrets management** (AWS Secrets Manager, Vault, etc.)
2. **Configure resource limits** appropriately
3. **Add health checks and readiness probes**
4. **Use ingress with TLS** (cert-manager + Let's Encrypt)
5. **Implement authentication** (OAuth2, JWT, mTLS)
6. **Add monitoring** (Prometheus, Grafana)
7. **Use persistent storage** for stateful components
8. **Implement rate limiting** and request throttling
9. **Deploy to a managed Kubernetes cluster** (EKS, GKE, AKS)
10. **Use CI/CD** for automated deployments

## References

- [kind Documentation](https://kind.sigs.k8s.io/)
- [minikube Documentation](https://minikube.sigs.k8s.io/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [@ivotoby/openapi-mcp-server](https://github.com/ivotoby/openapi-mcp-server)
