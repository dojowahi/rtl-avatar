import os
import sys

# Append parent dir for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai

def test():
    project = "gen-ai-4all"
    location = "us-central1"
    
    print(f"Listing models in Vertex AI project: {project}, location: {location}...\n")
    try:
        # Initialize Google GenAI SDK client for Vertex AI
        client = genai.Client(vertexai=True, project=project, location=location)
        models = client.models.list()
        for m in models:
            name = m.name
            # Clean up the output to be readable
            print(f"- {name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    test()
