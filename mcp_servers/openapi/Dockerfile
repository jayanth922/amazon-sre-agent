FROM node:20-alpine

WORKDIR /app

# Install the @ivotoby/openapi-mcp-server package globally
RUN npm install -g @ivotoby/openapi-mcp-server@latest

EXPOSE 3000

# Environment variables expected:
# - TRANSPORT_TYPE=http
# - HTTP_PORT=3000
# - ENDPOINT_PATH=/mcp
# - API_BASE_URL=<backend URL>
# - OPENAPI_SPEC_PATH=<path to OpenAPI spec file>

ENTRYPOINT ["openapi-mcp-server"]
