# SRE Agent Project - Comprehensive Overview

## Table of Contents
1. [Jayanth's Original Work (Amazon SRE Agent)](#jayanths-original-work)
2. [Our Development & Enhancements](#our-development--enhancements)
3. [Technical Deep Dive](#technical-deep-dive)
4. [Demo Flow](#demo-flow)

---

## Jayanth's Original Work (Amazon SRE Agent)

### 🎯 Project Vision
**A Multi-Agent Site Reliability Engineering Assistant** that helps SRE teams investigate infrastructure issues using AI agents that collaborate through the Model Context Protocol (MCP).

### 🏗️ Core Architecture Components

#### 1. **Multi-Agent System (LangGraph-based)**
```
┌─────────────┐
│  Supervisor │  ← Orchestrates all agents
└──────┬──────┘
       │
   ┌───┴────┬─────────┬──────────┐
   ▼        ▼         ▼          ▼
┌────┐  ┌────┐   ┌─────┐   ┌──────┐
│ K8s│  │Logs│   │Metrics│  │Runbooks│
└────┘  └────┘   └─────┘   └──────┘
```

**Specialized Agents:**
- **Kubernetes Agent**: Queries pod status, deployments, services, nodes
- **Logs Agent**: Analyzes log patterns, error counts, anomalies
- **Metrics Agent**: Monitors response times, throughput, availability, error rates
- **Runbooks Agent**: Retrieves troubleshooting guides, escalation procedures

#### 2. **Model Context Protocol (MCP) Integration**
- **Purpose**: Standardized protocol for AI agents to discover and use tools
- **AgentCore Gateway**: Provides secure API access with authentication
- **MCP Servers**: Wraps OpenAPI specs into MCP-compatible tools
- **Benefits**: Dynamic tool discovery, versioning, authentication

#### 3. **Backend Demo Infrastructure**
Four FastAPI servers providing mock SRE data:
- **K8s Server** (Port 8011): Kubernetes cluster data
- **Logs Server** (Port 8012): Application logs and patterns
- **Metrics Server** (Port 8013): Performance metrics and trends
- **Runbooks Server** (Port 8014): Operational procedures

Located in: `backend/servers/` and `backend/data/`

#### 4. **Memory & Personalization System**
- **Amazon Bedrock Agent Memory**: Long-term context across sessions
- **User Personas**: Different reporting styles for different roles
  - **Alice**: Technical detailed investigations
  - **Carol**: Executive business-focused summaries
- **Cross-session Learning**: Remembers preferences, past issues

#### 5. **LLM Provider Support**
- **Amazon Bedrock**: Nova and Claude models (production-ready)
- **Anthropic Direct**: Claude models via API
- **Groq**: Fast inference with open models

#### 6. **Deployment Options**
1. **Local Development**: CLI tool with `sre-agent` command
2. **Container**: Docker image with FastAPI wrapper
3. **AWS Production**: Amazon Bedrock AgentCore Runtime
4. **Kubernetes**: Kind/Minikube deployments with Kustomize

### 📊 Key Features Implemented by Jayanth

| Feature | Description |
|---------|-------------|
| **Multi-turn Conversations** | Interactive investigation mode with context |
| **Single Query Mode** | One-shot investigations with comprehensive reports |
| **Streaming Output** | Real-time agent thinking and tool execution |
| **Report Generation** | Markdown reports saved to `reports/` directory |
| **Observability** | OpenTelemetry integration with CloudWatch |
| **Security** | JWT authentication, SSL/TLS, IAM roles |
| **Extensibility** | Easy to add new agents and tools |

### 🔧 Technologies Used
- **Orchestration**: LangGraph (state machines for agent workflows)
- **LLM Integration**: LangChain (unified LLM interface)
- **API Framework**: FastAPI (async Python web framework)
- **Protocol**: MCP (Model Context Protocol)
- **Infrastructure**: Docker, Kubernetes, AWS (EC2, Bedrock, S3)
- **Package Management**: `uv` (fast Python package manager)

### 📁 Project Structure (Jayanth's Code)
```
amazon-sre-agent/
├── sre_agent/                    # Core agent package
│   ├── multi_agent_langgraph.py  # Main orchestration logic
│   ├── graph_builder.py          # LangGraph state machine
│   ├── agent_nodes.py            # Individual agent implementations
│   ├── supervisor.py             # Supervisor agent logic
│   ├── agent_state.py            # Shared state management
│   ├── agent_runtime.py          # FastAPI wrapper for deployment
│   ├── cli.py                    # Command-line interface
│   └── config/
│       ├── agent_config.yaml     # Agent configuration
│       └── prompts/              # System prompts for each agent
│
├── backend/                      # Demo backend servers
│   ├── servers/                  # FastAPI servers (4 services)
│   ├── data/                     # Synthetic SRE data
│   └── scripts/
│       ├── start_demo_backend.sh # Start all backend servers
│       └── stop_demo_backend.sh  # Stop all backend servers
│
├── gateway/                      # AgentCore Gateway setup
│   ├── create_gateway.sh         # Gateway creation script
│   └── mcp_cmds.sh               # MCP tool registration
│
├── deployment/                   # Production deployment
│   ├── build_and_deploy.sh       # Docker build & ECR push
│   └── deploy_agent_runtime.py   # AgentCore Runtime deploy
│
├── k8s/                          # Kubernetes manifests
│   ├── base/                     # Base Kustomize config
│   ├── kind/                     # Kind-specific overlays
│   └── minikube/                 # Minikube-specific overlays
│
└── docs/                         # Comprehensive documentation
    ├── sre_agent_architecture.md
    ├── deployment-guide.md
    ├── memory-system.md
    └── examples/                 # Real investigation examples
```

### 🎬 Demo Capabilities (Jayanth's Implementation)
1. **CLI Integration**: `sre-agent --prompt "..."`
2. **IDE Integration**: VSCode and Cursor MCP connections
3. **Conversation History**: Multi-turn investigations
4. **Memory Personalization**: User-specific reporting
5. **Report Artifacts**: Markdown files with full audit trail

---

## Our Development & Enhancements

### 🎨 1. Web UI Development

#### **Problem Identified**
- Jayanth's implementation only had CLI interface
- No easy way to demo the agent visually
- Users had to use terminal or IDE integrations

#### **Solution: Three UI Options Created**

##### **Option 1: Swagger UI** (Existing from FastAPI)
- Auto-generated from FastAPI OpenAPI spec
- URL: `http://localhost:8080/docs`
- **Pros**: No code needed, interactive API testing
- **Cons**: Not conversational, technical interface

##### **Option 2: Streamlit Chat UI** (`ui/streamlit_app.py`)
```python
# Created a Python-based chat interface
- Direct integration with agent runtime
- Conversation history
- Provider selection (Anthropic/Groq/Bedrock)
- Real-time streaming (future enhancement)
```
**Features:**
- Clean chat interface
- Message history
- Provider selection dropdown
- Markdown rendering

##### **Option 3: Standalone HTML UI** (`ui/enhanced_ui_v2.html`)
```html
<!-- Zero-dependency web chat interface -->
- No Python server needed (after backend starts)
- Modern dark mode design
- Code syntax highlighting
- Smart agent display
- Fixed input area
```

**Features Implemented:**
- ✅ **Fixed Input Area**: Always visible at bottom
- ✅ **Better Visibility**: Larger, more rectangular layout
- ✅ **Smart Agent Display**: Only shows agents that actually worked
- ✅ **Code Highlighting**: JSON and code blocks styled properly
- ✅ **Responsive Design**: Works on different screen sizes
- ✅ **Message Threading**: Clear user/assistant separation
- ✅ **Loading States**: Visual feedback during processing

### 🔧 2. CORS Fix for Web UI

#### **Problem Encountered**
```
Access to fetch at 'http://localhost:8080/invocations' from origin 
'file://' has been blocked by CORS policy
```

#### **Solution Implemented**
Modified `sre_agent/agent_runtime.py` to add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Impact**: Web UI can now communicate with FastAPI backend

### 🚀 3. Quick Setup & Configuration

#### **Environment Setup**
- Fixed `.env` configuration
- Added Groq API key support (when Anthropic credits were low)
- Verified MCP server connections

#### **Backend Server Management**
- Started demo backend servers
- Verified all 4 services running (ports 8011-8014)
- Created simple startup verification

### 📝 4. Documentation Improvements

#### **Created Files:**
- `CORS_FIX.md`: Permanent fix for CORS issues
- Various investigation reports in `reports/`

### 🧪 5. Testing & Validation
- Verified CLI functionality
- Tested API endpoints
- Validated agent-to-backend connectivity
- Confirmed MCP tool loading

---

## Technical Deep Dive

### How the Agent Actually Works

#### **1. Query Flow**
```
User Query
    ↓
[Agent Runtime / CLI]
    ↓
[Supervisor Agent] ← Decides which agents to invoke
    ↓
[Specialized Agents] ← Execute in parallel/sequence
    ↓
[MCP Tools] ← Query backend APIs
    ↓
[Backend Servers] ← Return data
    ↓
[Agents Analyze] ← Process results
    ↓
[Aggregate Node] ← Combine findings
    ↓
[Generate Report] ← Markdown output
    ↓
User Receives Answer
```

#### **2. LangGraph State Machine**
```python
# Nodes in the graph:
1. prepare       → Initialize investigation
2. supervisor    → Decide which agents to call
3. k8s_agent     → Query Kubernetes data
4. logs_agent    → Analyze logs
5. metrics_agent → Check performance metrics
6. runbooks_agent→ Find procedures
7. aggregate     → Combine all findings
```

#### **3. MCP Protocol**
```
Agent                    Gateway                 Backend
  |                         |                       |
  |--[List Tools]---------->|                       |
  |<-[Tool List]------------|                       |
  |                         |                       |
  |--[Call Tool]----------->|--[HTTP Request]------>|
  |                         |<-[HTTP Response]------|
  |<-[Tool Result]----------|                       |
```

#### **4. Memory System**
```
User: Alice
  ↓
[Bedrock Agent Memory]
  ↓
Preferences: {
  "detail_level": "technical",
  "reporting_style": "comprehensive",
  "notification": "team_alert"
}
  ↓
[Investigation]
  ↓
Report customized for Alice's preferences
```

---

## Demo Flow

### **Recommended Demo Script**

#### **1. Introduction** (2 minutes)
> "This is an AI-powered SRE agent that helps investigate infrastructure issues. 
> It uses multiple specialized agents that work together to diagnose problems."

#### **2. Show Architecture** (2 minutes)
- Explain multi-agent system
- Show 4 specialized agents
- Mention MCP protocol for tool discovery

#### **3. Web UI Demo** (5 minutes)

**Open**: `http://localhost:3000/enhanced_ui_v2.html`

**Sample Queries**:
```
1. "What's the status of payment-service pods?"
   → Shows Kubernetes agent in action

2. "Find error patterns in the last hour"
   → Shows Logs agent analysis

3. "Are we experiencing high latency?"
   → Shows Metrics agent checking performance

4. "How do I recover from database connection failures?"
   → Shows Runbooks agent providing procedures
```

**Point Out**:
- Real-time agent execution
- Multiple agents working together
- Smart agent display (only active agents shown)
- Markdown-formatted responses
- Code highlighting

#### **4. CLI Demo** (3 minutes)
```bash
# Show command-line interface
sre-agent --prompt "Investigate high memory usage in production cluster"

# Show interactive mode
sre-agent --interactive
```

#### **5. Report Generation** (2 minutes)
- Show generated markdown reports in `reports/` directory
- Explain audit trail and documentation

#### **6. Technical Highlights** (3 minutes)
- **LangGraph**: State machine orchestration
- **MCP Protocol**: Dynamic tool discovery
- **FastAPI**: Modern async Python framework
- **Streaming**: Real-time output
- **Memory**: User personalization

#### **7. Deployment Options** (2 minutes)
- Local development (what we're running)
- Docker containers
- Kubernetes (Kind/Minikube)
- AWS Production (AgentCore Runtime)

---

## Key Differentiators

### **What Makes This Special?**

1. **Multi-Agent Architecture**
   - Not a single monolithic agent
   - Specialized agents with domain expertise
   - Supervisor coordinates workflow

2. **MCP Protocol Integration**
   - Modern standard for AI tool use
   - Dynamic tool discovery
   - Version management

3. **Production-Ready**
   - Deploys to AWS AgentCore Runtime
   - Observability with CloudWatch
   - Security with IAM and JWT

4. **Memory & Personalization**
   - Remembers user preferences
   - Tailors reports to user role
   - Learns across sessions

5. **Real SRE Workflows**
   - Based on actual SRE practices
   - Runbook integration
   - Escalation procedures

---

## Technical Metrics

### **Performance**
- Average investigation time: 15-30 seconds
- Parallel agent execution
- Streaming output for real-time feedback

### **Scale**
- Handles complex multi-agent orchestrations
- Supports multiple concurrent users (in production)
- Memory system scales with user base

### **Extensibility**
- Add new agents: ~100 lines of code
- Add new tools: Register OpenAPI spec
- Add new backends: Create FastAPI server

---

## Future Enhancements (Potential)

1. **Enhanced UI Features**
   - Real-time streaming in web UI
   - Investigation history browser
   - Visual agent workflow display
   - Export reports as PDF

2. **Agent Improvements**
   - Additional specialized agents (Security, Cost, Compliance)
   - Enhanced error recovery
   - Predictive maintenance

3. **Integration**
   - Slack bot integration
   - PagerDuty integration
   - Jira ticket creation

4. **Analytics**
   - Investigation patterns analysis
   - Agent performance metrics
   - User behavior insights

---

## Summary

### **Jayanth's Contribution**
- ✅ Complete multi-agent SRE system
- ✅ LangGraph orchestration
- ✅ MCP protocol integration
- ✅ Four specialized agents
- ✅ Backend demo infrastructure
- ✅ Memory & personalization
- ✅ Production deployment path
- ✅ Comprehensive documentation

### **Our Enhancements**
- ✅ Three UI options (Swagger, Streamlit, HTML)
- ✅ Modern web chat interface
- ✅ CORS fix for browser access
- ✅ Improved UX (input visibility, smart agent display)
- ✅ Quick setup verification
- ✅ Demo-ready configuration

### **Combined Result**
A production-ready, visually demonstrable, multi-agent SRE assistant that showcases modern AI agent architecture with real-world applicability.

---

## Questions to Anticipate

**Q: How is this different from ChatGPT?**
A: This is specialized for SRE workflows with multiple expert agents, real-time data access, and memory personalization. It's not general chat—it's purpose-built for infrastructure investigation.

**Q: Can this work with real Kubernetes clusters?**
A: Yes! The backend servers are demos, but the architecture supports connecting to real K8s APIs, log systems, and metrics platforms.

**Q: What models does it use?**
A: Flexible: Amazon Bedrock (Nova/Claude), Anthropic Claude, or Groq. Configurable per deployment.

**Q: How long did this take to build?**
A: Jayanth's core system: Professional-grade multi-agent framework (weeks of work). Our enhancements: UI and UX improvements (hours).

**Q: Can non-technical users use this?**
A: Yes! The memory system can tailor reports for executives (like the Carol persona) with business-focused summaries instead of technical details.

---

## Demo URLs (When Running Locally)

- **Web Chat UI**: http://localhost:3000/enhanced_ui_v2.html
- **Swagger API Docs**: http://localhost:8080/docs
- **ReDoc API Docs**: http://localhost:8080/redoc
- **Agent Health Check**: http://localhost:8080/ping
- **K8s Backend**: http://localhost:8011/docs
- **Logs Backend**: http://localhost:8012/docs
- **Metrics Backend**: http://localhost:8013/docs
- **Runbooks Backend**: http://localhost:8014/docs

---

## Contact & Resources

- **GitHub**: Check Jayanth's repository for full code
- **Documentation**: See `docs/` folder for detailed guides
- **Examples**: See `docs/examples/` for investigation samples
- **Architecture**: See `docs/sre_agent_architecture.md`

---

*This presentation guide combines Jayanth's sophisticated multi-agent architecture with our visual and UX enhancements to create a compelling, demonstrable SRE assistant.*

