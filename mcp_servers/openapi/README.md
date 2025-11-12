# OpenAPI → MCP Server

This directory contains the Dockerfile for building an open-source OpenAPI-to-MCP server using [@ivotoby/openapi-mcp-server](https://github.com/ivotoby/openapi-mcp-server).

## Overview

This server automatically exposes any OpenAPI spec as MCP tools over HTTP, allowing the SRE agent to discover and call backend APIs through the Model Context Protocol.

## Building

```bash
docker build -t ghcr.io/jayanth922/mcp-openapi:local .
```

## Configuration

The server is configured via environment variables:

- `TRANSPORT_TYPE`: Set to `http` for HTTP transport
- `HTTP_PORT`: Port to listen on (default: 3000)
- `ENDPOINT_PATH`: HTTP endpoint path (default: /mcp)
- `API_BASE_URL`: Base URL of the backend API to proxy to
- `OPENAPI_SPEC_PATH`: Path to the OpenAPI specification file

## Running Locally

```bash
docker run -p 3000:3000 \
  -e TRANSPORT_TYPE=http \
  -e HTTP_PORT=3000 \
  -e ENDPOINT_PATH=/mcp \
  -e API_BASE_URL=http://localhost:8000 \
  -e OPENAPI_SPEC_PATH=/specs/api.yaml \
  -v $(pwd)/specs:/specs \
  ghcr.io/jayanth922/mcp-openapi:local
```

## Kubernetes Deployment

In Kubernetes, each domain (K8s, Logs, Metrics, Runbooks) gets its own deployment with:

1. A ConfigMap containing the OpenAPI spec
2. A Deployment running this image with appropriate env vars
3. A Service exposing port 3000

See `k8s/base/mcp-*.deployment.yaml` for examples.

## Connecting from Python

The SRE agent connects using the MCP Python SDK with streamable HTTP transport:

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Connect to MCP server
read, write, _ = await streamablehttp_client("http://mcp-k8s.sre.svc.cluster.local:3000/mcp").__aenter__()
session = ClientSession(read, write)
await session.initialize()

# List available tools
tools = await session.list_tools()
```

## Alternative Implementations

If you prefer a different OpenAPI→MCP server:

- **Python**: Write your own using `mcp` + `fastapi` + OpenAPI parser
- **Go**: Use Go MCP SDK + OpenAPI generator
- **Custom**: Any MCP-compliant server that reads OpenAPI specs

The key requirement is HTTP transport support for in-cluster connectivity.
