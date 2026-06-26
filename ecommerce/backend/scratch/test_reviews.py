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

def test_reviews():
    print("Fetching products from catalog...")
    products = db.get_products(limit=5)
    if not products:
        print("No products found. Please seed the database first.")
        return
        
    target_product = products[0]
    pid = target_product["product_id"]
    pname = target_product["name"]
    print(f"Testing reviews for product: {pname} ({pid})")

    # Add a review
    print("Adding a review...")
    customer_name = "Jane Doe"
    rating = 5
    comment = "Absolutely amazing! Highly recommended."
    
    review_res = db.add_review(
        product_id=pid,
        customer_name=customer_name,
        rating=rating,
        comment=comment
    )
    print(f"Review added: {review_res}")

    # Fetch reviews
    print("Fetching reviews...")
    reviews = db.get_reviews(pid)
    print(f"Reviews found: {reviews}")
    
    # Assertions
    assert len(reviews) > 0, "No reviews found after insert!"
    inserted = reviews[0]
    assert inserted["customer_name"] == customer_name
    assert inserted["rating"] == rating
    assert inserted["comment"] == comment
    print("All review assertions passed successfully!")

if __name__ == "__main__":
    test_reviews()
