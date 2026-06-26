import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services

def run():
    print("Checking active config in Spanner:")
    row = services.db.get_active_retailer_settings()
    print("Active settings:", row)

if __name__ == '__main__':
    run()
