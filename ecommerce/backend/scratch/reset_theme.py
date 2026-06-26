import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services

def run():
    print("Resetting active config to Retrail in Spanner...")
    theme = {
        "primary": "#000000",
        "secondary": "#ffffff",
        "font": "Inter, sans-serif",
        "persona": "shopper"
    }
    services.db.save_retailer_settings("Retrail", theme)
    print("Successfully reset active retailer settings to Retrail.")

if __name__ == '__main__':
    run()
