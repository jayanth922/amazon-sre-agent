# Executive Summary: Amazon SRE Agent (Manjunath Branch)

## Quick Overview

The **Amazon SRE Agent** is an advanced AI-powered troubleshooting assistant for Site Reliability Engineers. It uses **5 specialized AI agents** that work together to investigate infrastructure problems, analyze logs, monitor performance, and provide operational guidance.

## What It Does

When you ask a question like *"Why is my payment service failing?"*, the system:

1. **Plans** the investigation (Supervisor Agent)
2. **Checks** pod status (Kubernetes Agent)
3. **Analyzes** error logs (Logs Agent)
4. **Reviews** metrics (Metrics Agent)
5. **Recommends** fixes from runbooks (Runbooks Agent)
6. **Generates** a comprehensive report with root cause and remediation steps

## How It Works

### The 5 Agents

1. **Supervisor Agent** 🧭
   - Orchestrates the investigation
   - Creates investigation plans
   - Routes queries to specialist agents
   - Combines results into final report

2. **Kubernetes Agent** ☸️
   - Checks pod status and health
   - Reviews deployments and services
   - Analyzes cluster events
   - Monitors resource usage

3. **Logs Agent** 📋
   - Searches application logs
   - Identifies error patterns
   - Analyzes log trends
   - Finds relevant log entries

4. **Metrics Agent** 📊
   - Reviews performance metrics
   - Checks error rates
   - Monitors availability
   - Analyzes metric trends

5. **Runbooks Agent** 📚
   - Provides incident playbooks
   - Suggests troubleshooting steps
   - Gives escalation procedures
   - Shares common resolutions

### Technology Stack

- **LangGraph**: Multi-agent orchestration
- **LangChain**: LLM application framework
- **MCP (Model Context Protocol)**: Standardized tool access
- **Amazon Bedrock AgentCore**: Production deployment platform
- **FastAPI**: Backend API servers
- **Anthropic Claude / Amazon Nova**: AI models powering the agents

## Project Structure

```
amazon-sre-agent/
├── sre_agent/              # Main agent code
│   ├── cli.py              # Command-line interface
│   ├── multi_agent_langgraph.py  # Core orchestration (1449 lines)
│   ├── graph_builder.py    # Agent workflow graph
│   ├── supervisor.py       # Investigation coordinator
│   ├── agent_nodes.py      # Specialist agent implementations
│   ├── agent_state.py      # Shared state structure
│   ├── constants.py        # Configuration settings
│   └── config/             # Configuration files
│       ├── agent_config.yaml      # Agent-to-tool mapping
│       └── prompts/               # AI prompts for each agent
├── backend/                # Mock backend services
│   ├── servers/            # 4 FastAPI servers (K8s, Logs, Metrics, Runbooks)
│   └── data/               # Mock JSON data
├── ui/                     # Web interfaces
│   └── streamlit_app.py    # Streamlit UI
├── README.md               # Setup instructions
├── pyproject.toml          # Python dependencies
├── Makefile                # Development commands
└── Dockerfile              # Container image
```

## How to Use

### Simple Query Mode
```bash
sre-agent --prompt "Why is payment-service pod failing?"
```

The agent will:
1. Analyze the query
2. Call appropriate agents
3. Generate a detailed report
4. Save to `reports/payment_service_investigation_YYYYMMDD_HHMMSS.md`

### Interactive Mode
```bash
sre-agent --interactive
```

Chat with the agent, ask follow-up questions, and use commands:
- `/help` - Show help
- `/agents` - List available agents
- `/savereport` - Save current investigation
- `/exit` - Quit

## Example Investigation Flow

**Query**: "API response times have degraded 3x in the last hour"

**What Happens**:
```
1. Supervisor creates plan:
   - Step 1: Check performance metrics
   - Step 2: Analyze error rates
   - Step 3: Review resource usage
   - Step 4: Find relevant procedures

2. Metrics Agent investigates:
   ✓ P95 latency: 200ms → 600ms (3x increase)
   ✓ Error rate: 1% → 5%

3. Logs Agent analyzes:
   ✓ Found: "Database timeout errors increased"

4. Kubernetes Agent checks:
   ✓ Database pod CPU at 95%

5. Runbooks Agent suggests:
   ✓ Database scaling procedures
   ✓ Performance optimization steps

6. Supervisor aggregates:
   ✓ Root cause: Database CPU exhaustion
   ✓ Impact: 3x latency, 5% errors
   ✓ Fix: Scale database pods, optimize queries
   ✓ Report saved with full details
```

## Key Features

✅ **Multi-Agent Collaboration**: 5 specialized agents work together
✅ **Real-time Streaming**: See investigation progress live
✅ **Memory-Enabled**: Remembers your preferences
✅ **Production-Ready**: Deploy to Amazon Bedrock AgentCore
✅ **Comprehensive Reports**: Markdown reports with full analysis
✅ **Interactive & Batch**: Use as CLI or chatbot
✅ **Extensible**: Easy to add new agents and data sources

## Backend Architecture

The system uses **4 mock API servers** that simulate real infrastructure:

1. **Kubernetes Server** (Port 8011)
   - `/pods` - Pod status and details
   - `/deployments` - Deployment info
   - `/events` - Cluster events
   - `/nodes` - Node health

2. **Logs Server** (Port 8012)
   - `/search` - Search logs
   - `/errors` - Error logs
   - `/patterns` - Log pattern analysis

3. **Metrics Server** (Port 8013)
   - `/performance` - Latency, throughput
   - `/errors` - Error rates
   - `/availability` - Uptime data

4. **Runbooks Server** (Port 8014)
   - `/search` - Search runbooks
   - `/incident-playbooks` - Incident procedures
   - `/troubleshooting` - Troubleshooting guides

These servers are accessed through the **AgentCore Gateway** using the **MCP (Model Context Protocol)**, which provides:
- Secure authentication
- Standardized tool interface
- Access control
- Rate limiting

## Data Flow

```
User Query
    ↓
CLI Entry Point
    ↓
Multi-Agent Orchestrator
    ↓
Create Investigation Plan
    ↓
┌─────────────────────────────────────┐
│  Route to Specialist Agents         │
│                                      │
│  Agent → MCP Client → Gateway →     │
│  Backend Server → JSON Data →       │
│  Agent → Analysis → Result          │
└─────────────────────────────────────┘
    ↓
Collect All Results
    ↓
Aggregate with AI
    ↓
Generate Markdown Report
    ↓
Save & Display to User
```

## Configuration

### Environment Variables (`.env`)
```bash
# LLM Provider
ANTHROPIC_API_KEY=sk-ant-...

# AgentCore Gateway
GATEWAY_ACCESS_TOKEN=eyJ...

# User Context
USER_ID=alice
SESSION_ID=session-123
```

### Agent Configuration (`agent_config.yaml`)
```yaml
agents:
  kubernetes_agent:
    tools: [get_pod_status, get_deployment_status, ...]
  logs_agent:
    tools: [search_logs, get_error_logs, ...]
  metrics_agent:
    tools: [get_performance_metrics, ...]
  runbooks_agent:
    tools: [search_runbooks, ...]
```

## Deployment Options

### 1. Local Development
```bash
# Start backend servers
./backend/scripts/start_demo_backend.sh

# Run agent
sre-agent --prompt "your query"
```

### 2. Container
```bash
# Build
docker build -t sre-agent .

# Run
docker run -p 8080:8080 sre-agent
```

### 3. Production (AgentCore Runtime)
```bash
# Build and deploy
./deployment/build_and_deploy.sh
uv run python deployment/deploy_agent_runtime.py

# Invoke
uv run python deployment/invoke_agent_runtime.py
```

## Quality & Security

### Code Quality Tools
- **Black**: Code formatting
- **Ruff**: Fast linting
- **MyPy**: Type checking
- **Bandit**: Security scanning
- **PyTest**: Testing

Run all checks:
```bash
make quality
```

### Security Features
- ✅ API key authentication on all servers
- ✅ JWT token validation at gateway
- ✅ HTTPS/TLS for all communications
- ✅ IAM role-based AWS access
- ✅ Input validation with Pydantic
- ✅ Rate limiting with retry logic

## Performance Features

- **Prompt Caching**: LRU cache for frequently used prompts
- **Tool Filtering**: Each agent only loads relevant tools
- **Async I/O**: Non-blocking API calls
- **Streaming**: Real-time progress updates
- **Timeout Protection**: Circuit breakers prevent hangs
- **Connection Pooling**: Reused HTTP connections

## Common Commands

```bash
# Single query
sre-agent --prompt "Check payment-service health"

# Interactive mode
sre-agent --interactive

# Debug mode
sre-agent --debug --prompt "your query"

# Different LLM provider
sre-agent --provider anthropic --prompt "your query"

# Custom output directory
sre-agent --output-dir ./investigations --prompt "your query"

# Start backend servers
cd backend && ./scripts/start_demo_backend.sh

# Stop backend servers
cd backend && ./scripts/stop_demo_backend.sh

# Run quality checks
make quality

# Export architecture diagram
sre-agent --export-graph --graph-output ./architecture.md
```

## Real-World Example Output

**Input**:
```bash
sre-agent --prompt "payment-service pod is crash looping"
```

**Output**:
```
🤖 Multi-Agent System: Processing...

🧭 Supervisor: Routing to kubernetes_agent
   Reasoning: Need to check pod status and events

🔧 Kubernetes Agent:
   💡 Pod is in CrashLoopBackOff with 5 restarts
   Last termination: Exit code 1

🧭 Supervisor: Routing to logs_agent
   Reasoning: Need error logs to find root cause

🔧 Logs Agent:
   💡 Found: "Database connection refused" errors
   Pattern: Connection fails on startup

🧭 Supervisor: Routing to runbooks_agent
   Reasoning: Need remediation procedures

🔧 Runbooks Agent:
   💡 Database Connection Troubleshooting Guide
   Steps: Check credentials, network, DB status

💬 Final Response:

# Payment Service Pod Investigation

## Problem
Pod crash looping (5 restarts, CrashLoopBackOff state)

## Root Cause
Database connection refused on startup

## Evidence
- Pod logs: "Connection refused to db:5432"
- No network policy blocking traffic
- Database service is running

## Resolution
1. Check database credentials in ConfigMap
2. Verify database service DNS resolution
3. Test connectivity: kubectl exec -it payment-service -- nc -zv db 5432
4. Review database logs for connection limits

## References
- Runbook: Database Connection Troubleshooting
- Previous incident: INC-2024-001

📄 Saved to: reports/payment_service_crash_loop_20241114_142530.md
```

## Documentation

For complete details, see:
- **`MANJUNATH_BRANCH_EXPLANATION.md`**: 1100+ line comprehensive technical documentation
- **`README.md`**: Setup and deployment instructions
- **`docs/`**: Additional documentation (examples, architecture, guides)

## Summary

The Amazon SRE Agent is a production-ready, multi-agent AI system that:
- Automates infrastructure troubleshooting
- Collaborates across multiple data sources
- Provides detailed investigation reports
- Can be deployed locally or on AWS
- Is extensible and well-documented

Perfect for SRE teams who want AI-assisted incident investigation and root cause analysis.

---

**For detailed file-by-file explanation, workflow examples, and architecture diagrams, see:**
[MANJUNATH_BRANCH_EXPLANATION.md](MANJUNATH_BRANCH_EXPLANATION.md)
