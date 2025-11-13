# How to Add CORS Support to Agent Runtime

## Problem
Opening HTML files directly (file://) causes CORS errors when calling the API.

## Solution 1: Use Web Server (Current - No Code Changes)
```bash
# Serve HTML files through HTTP
cd ui
python3 -m http.server 3000

# Open: http://localhost:3000/enhanced_ui.html
```

## Solution 2: Add CORS to FastAPI (Permanent Fix)

Edit `sre_agent/agent_runtime.py`:

```python
# Add this import at the top (around line 9)
from fastapi.middleware.cors import CORSMiddleware

# Add this after creating the FastAPI app (after line 47)
app = FastAPI(title="SRE Agent Runtime", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then restart the agent:
```bash
# Kill existing agent
kill $(cat /tmp/sre_agent_runtime.pid)

# Start with CORS enabled
uv run uvicorn sre_agent.agent_runtime:app --host 0.0.0.0 --port 8080
```

Now you can open HTML files directly without a web server!

## Which Should You Use?

- **Development**: Use web server (Solution 1) - simpler
- **Production**: Add CORS (Solution 2) - more control over security
- **Quick Test**: Use web server (Solution 1) - already running!

## Current Status
✅ Web server running on: http://localhost:3000
✅ Agent runtime on: http://localhost:8080
✅ Enhanced UI: http://localhost:3000/enhanced_ui.html

