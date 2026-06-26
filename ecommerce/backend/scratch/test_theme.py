import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services first to initialize Vertex AI env variables
import services
from routes.config import fetch_dynamic_brand_theme

def test():
    print("Testing backend routes.config dynamic theme resolver...")
    try:
        res = fetch_dynamic_brand_theme("Home Depot")
        print("Resolved brand theme:")
        print(res)
    except Exception as e:
        print(f"Failed with exception: {e}")

if __name__ == "__main__":
    test()
