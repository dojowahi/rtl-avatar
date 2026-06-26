import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services

def run():
    print("Resetting active config to Target in Spanner...")
    theme = {
        "primary": "#cc0000",
        "secondary": "#ffffff",
        "font": "Inter, sans-serif",
        "persona": "shopper"
    }
    services.db.save_retailer_settings("Target", theme)
    print("Successfully reset active retailer settings to Target.")

if __name__ == '__main__':
    run()
