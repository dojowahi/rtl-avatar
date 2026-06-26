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
    print("Altering retailer_settings table...")
    try:
        operation = db.db.update_ddl(["ALTER TABLE retailer_settings ADD COLUMN assistant_persona STRING(50)"])
        operation.result(timeout=300)
        print("ALTER TABLE executed successfully.")
    except Exception as e:
        print(f"Failed to alter table: {e}")

if __name__ == "__main__":
    run_ddl()
