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

from services import db

def query_reviews():
    print("Querying reviews from database...")
    products = db.get_products()
    for p in products:
        pid = p["product_id"]
        pname = p["name"]
        reviews = db.get_reviews(pid)
        print(f"\nProduct: {pname} ({pid}) - Average Rating: {p.get('rating')}")
        print(f"Reviews Count: {p.get('reviews_count')}")
        for r in reviews:
            print(f"  - {r['customer_name']} ({r['rating']} stars): {r['comment']}")

if __name__ == "__main__":
    query_reviews()
