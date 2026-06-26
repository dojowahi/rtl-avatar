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

def test_persona_switching():
    print("Fetching current config...")
    res = client.get("/api/config")
    assert res.status_code == 200, f"Failed config retrieval: {res.text}"
    config = res.json()
    print("Initial Theme Config:", config.get("theme"))
    
    current_retailer = config.get("theme", {}).get("name", "Target")
    
    # 1. Switch to Teenager persona
    print(f"Switching persona to 'teenager' for {current_retailer}...")
    res = client.post("/api/admin/retailer", json={
        "retailer": current_retailer,
        "persona": "teenager",
        "products_count": 0,
        "customers_count": 0,
        "orders_count": 0,
        "truncate_db": False
    })
    assert res.status_code == 200, f"Failed updating retailer: {res.text}"
    print("Update Response:", res.json())
    
    # 2. Verify config reflects 'teenager' persona
    print("Fetching config after teenager switch...")
    res = client.get("/api/config")
    assert res.status_code == 200, f"Failed config retrieval: {res.text}"
    config = res.json()
    assert config.get("theme", {}).get("persona") == "teenager", f"Expected teenager persona, got {config.get('theme')}"
    assert "disgruntled" in config.get("systemPrompt").lower(), "Expected teenager system prompt text"
    print("Teenager Persona systemPrompt verified successfully!")

    # 3. Switch back to Shopper persona
    print(f"Switching persona back to 'shopper' for {current_retailer}...")
    res = client.post("/api/admin/retailer", json={
        "retailer": current_retailer,
        "persona": "shopper",
        "products_count": 0,
        "customers_count": 0,
        "orders_count": 0,
        "truncate_db": False
    })
    assert res.status_code == 200, f"Failed updating retailer: {res.text}"
    
    # 4. Verify config reflects 'shopper' persona
    print("Fetching config after shopper switch...")
    res = client.get("/api/config")
    assert res.status_code == 200, f"Failed config retrieval: {res.text}"
    config = res.json()
    assert config.get("theme", {}).get("persona") == "shopper", f"Expected shopper persona, got {config.get('theme')}"
    assert "helpful" in config.get("systemPrompt").lower(), "Expected helpful shopper system prompt text"
    print("Shopper Persona systemPrompt verified successfully!")

if __name__ == "__main__":
    test_persona_switching()
