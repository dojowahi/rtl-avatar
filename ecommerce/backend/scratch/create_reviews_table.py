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

def run_ddl():
    print("Creating reviews table in Spanner database...")
    ddl_stmt = """
    CREATE TABLE reviews (
      product_id STRING(50) NOT NULL,
      review_id STRING(50) NOT NULL,
      customer_name STRING(255) NOT NULL,
      rating INT64 NOT NULL,
      comment STRING(MAX),
      created_at TIMESTAMP OPTIONS (allow_commit_timestamp=true)
    ) PRIMARY KEY (product_id, review_id),
      INTERLEAVE IN PARENT products ON DELETE CASCADE
    """
    try:
        operation = db.db.update_ddl([ddl_stmt])
        operation.result(timeout=300)
        print("CREATE TABLE reviews executed successfully.")
    except Exception as e:
        print(f"Failed to create table: {e}")

if __name__ == "__main__":
    run_ddl()
