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

import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_change_theme_tool():
    print("Fetching initial config...")
    res = client.get("/api/config")
    assert res.status_code == 200, f"Config retrieval failed: {res.text}"
    initial_config = res.json()
    initial_theme = initial_config.get("theme", {})
    initial_retailer = initial_theme.get("name")
    print(f"Initial active retailer: '{initial_retailer}', theme: {initial_theme}")

    # Target retailer to switch to
    target_retailer = "Best Buy"
    if initial_retailer == "Best Buy":
        target_retailer = "Sephora"

    try:
        print(f"Executing change_theme MCP tool to switch to '{target_retailer}'...")
        rpc_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "change_theme",
                "arguments": {
                    "retailer": target_retailer
                },
                "session_id": "test_session_id"
            }
        }
        
        res = client.post("/api/mcp", json=rpc_payload)
        assert res.status_code == 200, f"MCP tool call failed: {res.text}"
        response_json = res.json()
        print("Tool Call Response:", response_json)
        
        # Assert successful tool completion
        assert "error" not in response_json, f"Tool returned error: {response_json}"
        result = response_json.get("result", {})
        assert not result.get("isError"), f"Tool result marked as error: {result}"
        
        # Verify Spanner configuration updates
        print("Fetching config after theme switch...")
        res = client.get("/api/config")
        assert res.status_code == 200, f"Config retrieval failed: {res.text}"
        updated_config = res.json()
        updated_theme = updated_config.get("theme", {})
        
        print(f"Updated active retailer: '{updated_theme.get('name')}', theme: {updated_theme}")
        assert updated_theme.get("name") == target_retailer, f"Expected active retailer to be '{target_retailer}', got '{updated_theme.get('name')}'"
        assert updated_theme.get("primary") is not None, "Expected primary brand color to be set"
        assert updated_theme.get("persona") == initial_theme.get("persona"), "Expected persona config to be carried over"
        
        print("change_theme MCP tool verified successfully!")
    finally:
        if initial_retailer:
            print(f"Restoring original active retailer: '{initial_retailer}'...")
            restore_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "change_theme",
                    "arguments": {
                        "retailer": initial_retailer
                    },
                    "session_id": "test_session_id"
                }
            }
            client.post("/api/mcp", json=restore_payload)

if __name__ == "__main__":
    test_change_theme_tool()
