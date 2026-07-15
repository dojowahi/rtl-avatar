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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from config import settings

def check_models(location: str):
    project_id = settings.vertex_project_id or "gen-ai-4all"
    print(f"\n==========================================")
    print(f"Checking models in Vertex AI location: {location} (Project: {project_id})")
    print(f"==========================================")
    
    try:
        client = genai.Client(vertexai=True, project=project_id, location=location)
        models = list(client.models.list())
        print(f"Total models retrieved: {len(models)}")
        
        live_or_bidi_models = []
        for m in models:
            name = getattr(m, 'name', '')
            display = getattr(m, 'display_name', '')
            # Filter specifically for live, preview, bidi, or gemini-3/gemini-2 models
            if any(k in name.lower() for k in ['live', 'bidi', '3.1', '2.0', 'preview']):
                live_or_bidi_models.append((name, display))
                
        if live_or_bidi_models:
            print(f"\nMatched Live/Preview/Bidi models in '{location}':")
            for name, display in sorted(live_or_bidi_models):
                print(f"  - {name} (Display: {display})")
        else:
            print(f"\nNo Live/Preview/Bidi models found in '{location}'.")
            
    except Exception as e:
        print(f"Error listing models in location '{location}': {e}")

if __name__ == "__main__":
    for loc in ["us-central1", "global"]:
        check_models(loc)
