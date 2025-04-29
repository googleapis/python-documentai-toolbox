# Copyright 2024 Google LLC
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

import token_detected_languages_sample


def test_token_detected_languages_sample(capsys):
    # Use a test document from the resources directory
    test_file_path = os.path.join(
        os.path.dirname(__file__), "resources", "form_with_tables.json"
    )
    
    # Run the sample
    token_detected_languages_sample.token_detected_languages_sample(
        document_path=test_file_path
    )
    
    # Capture output
    stdout, _ = capsys.readouterr()
    
    # Check that the output contains expected strings
    assert "Token" in stdout
    assert "Detected Languages:" in stdout 