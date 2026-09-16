# Backend Service - Multimodal Live Avatar Assistant

FastAPI backend service providing authenticated WebSocket proxying to Vertex AI Gemini Live, Model Context Protocol (MCP) JSON-RPC endpoints, and Cloud Spanner vector search capabilities.

For full project documentation, system architecture diagrams, and deployment guides, refer to the root [README.md](../../README.md) and [architecture walkthrough](../doc/architecture_walkthrough.md).

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r pyproject.toml

# Start the development server
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Key Modules

- [main.py](main.py): FastAPI server initialization, static asset mounting, and route registration.
- [auth.py](auth.py): Application Default Credentials (ADC) token generation.
- [database.py](database.py): Cloud Spanner client, cosine distance vector search, and cart/order transactions.
- [config.py](config.py): Environment settings and dynamic configuration loading.
- [routes/websocket.py](routes/websocket.py): Secure WebSocket proxy tunnel to Vertex AI Gemini Live (`/api/live-avatar`).
- [routes/mcp.py](routes/mcp.py): Model Context Protocol server (`/api/mcp`) implementing `tools/list` and `tools/call`.
- [routes/admin.py](routes/admin.py): Admin endpoints for brand theme customization and background data seeding.
- [DatabaseSetup/setup_spanner.py](DatabaseSetup/setup_spanner.py): Spanner instance and database provisioning script.
- [DataGenerator/generate_data.py](DataGenerator/generate_data.py): Synthetic product and embedding generator pipeline.
