# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import asyncio
import websockets
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from config import settings
from services import auth_svc, VERTEX_PROJECT_ID, VERTEX_LOCATION, GEMINI_LIVE_API_KEY

logger = logging.getLogger("ecommerce-routes-websocket")
router = APIRouter()

@router.websocket("/api/live-avatar")
@router.websocket("/api/live-avatar/{path:path}")
async def live_avatar_proxy(client_ws: WebSocket, path: str = ""):
    """
    WebSocket endpoint that acts as a secure, authenticated proxy between the React
    client and Google's Gemini Live BidiGenerateContent WebSocket API.
    """
    await client_ws.accept()
    logger.info(f"Client WebSocket connection upgraded for path: {path}")

    # 1. Resolve Auth token and Upstream target
    path_str = client_ws.url.path
    use_vertex = (client_ws.query_params.get("vertex") == "true") or ("aiplatform" in path_str) or settings.google_genai_use_vertexai
    
    model_location = "us-central1" if VERTEX_LOCATION == "global" else (VERTEX_LOCATION or "us-central1")

    if use_vertex:
        target_url = f"wss://{model_location}-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent"
        token = auth_svc.get_token()
        target_url += f"?access_token={token}"
    else:
        target_url = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService/BidiGenerateContent"
        if GEMINI_LIVE_API_KEY:
            target_url += f"?key={GEMINI_LIVE_API_KEY}"

    try:
        # 2. Establish connection to Google upstream
        logger.info(f"Connecting to Gemini Live API: {target_url.split('?')[0]}")
        async with websockets.connect(target_url) as upstream_ws:
            logger.info("Connected to Gemini Live Upstream successfully")

            # Channel setup status
            is_setup_done = False

            async def client_to_upstream():
                nonlocal is_setup_done
                try:
                    async for message in client_ws.iter_text():
                        # Intercept setup to qualify model path with Project/Location coordinates
                        if use_vertex and not is_setup_done:
                            try:
                                data = json.loads(message)
                                if "setup" in data:
                                    setup_cfg = data["setup"]
                                    if "model" in setup_cfg:
                                        raw_model = setup_cfg["model"]
                                        
                                        # Extract core model name
                                        model_name_only = raw_model
                                        if "publishers/google/models/" in model_name_only:
                                            model_name_only = model_name_only.split("publishers/google/models/")[-1]
                                        elif "models/" in model_name_only:
                                            model_name_only = model_name_only.split("models/")[-1]
                                            
                                        qualified_model = f"projects/{VERTEX_PROJECT_ID}/locations/{model_location}/publishers/google/models/{model_name_only}"
                                        setup_cfg["model"] = qualified_model
                                    
                                    # Ensure VIDEO response modality when avatarConfig is present
                                    if "avatarConfig" in setup_cfg or "avatar_config" in setup_cfg:
                                        gen_cfg = setup_cfg.setdefault("generationConfig", {})
                                        gen_cfg["responseModalities"] = ["VIDEO"]
                                    
                                    message = json.dumps(data)
                                    logger.info(f"Updated setup in proxy for model: {setup_cfg.get('model')}")
                                    is_setup_done = True
                            except Exception as parse_err:
                                logger.warning(f"Failed to inspect setup model path: {parse_err}")
                        
                        await upstream_ws.send(message)
                except WebSocketDisconnect:
                    logger.info("Client disconnected.")
                except Exception as e:
                    logger.error(f"Client to Upstream error: {e}")

            async def upstream_to_client():
                try:
                    async for message in upstream_ws:
                        # Forward upstream messages directly to browser client
                        await client_ws.send_text(message)
                except Exception as e:
                    logger.error(f"Upstream to Client error: {e}")

            # Run loops concurrently
            await asyncio.gather(client_to_upstream(), upstream_to_client())

    except Exception as e:
        logger.error(f"Failed to proxy connection: {str(e)}")
        try:
            await client_ws.close(code=1011, reason=str(e))
        except Exception:
            pass
