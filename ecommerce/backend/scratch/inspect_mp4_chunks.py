import os
import sys
import asyncio
import websockets
import json
import base64
import google.auth
import google.auth.transport.requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

async def inspect_chunks():
    project = settings.vertex_project_id or settings.google_cloud_project or "gen-ai-4all"
    location = "us-central1"
    model = "gemini-3.1-flash-live-preview-04-2026"
    
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    token = credentials.token

    ws_url = f"wss://{location}-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent?access_token={token}"

    setup_message = {
        "setup": {
            "model": f"projects/{project}/locations/{location}/publishers/google/models/{model}",
            "generation_config": {
                "response_modalities": ["VIDEO"]
            },
            "avatar_config": {
                "avatar_name": "Vera"
            }
        }
    }

    try:
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps(setup_message))
            await asyncio.wait_for(ws.recv(), timeout=5.0)
            
            prompt_msg = {
                "client_content": {
                    "turns": [{
                        "role": "user",
                        "parts": [{"text": "Say hello and count to five for me."}]
                    }],
                    "turn_complete": True
                }
            }
            await ws.send(json.dumps(prompt_msg))
            
            chunk_count = 0
            for _ in range(20):
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=4.0)
                    data = json.loads(resp)
                    if "serverContent" in data:
                        parts = data["serverContent"].get("modelTurn", {}).get("parts", [])
                        for p in parts:
                            if "inlineData" in p and p["inlineData"].get("mimeType") == "video/mp4":
                                chunk_count += 1
                                raw_bytes = base64.b64decode(p["inlineData"]["data"])
                                hex_header = raw_bytes[:32].hex()
                                ascii_header = "".join([chr(b) if 32 <= b <= 126 else "." for b in raw_bytes[:32]])
                                print(f"Chunk #{chunk_count}: len={len(raw_bytes)} bytes | header={ascii_header} ({hex_header})")
                                if chunk_count >= 6:
                                    return
                except asyncio.TimeoutError:
                    break
    except Exception as e:
        print(f"Failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_chunks())
