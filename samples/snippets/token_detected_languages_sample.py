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
#

# [START documentai_toolbox_token_detected_languages]
from typing import Optional

from google.cloud.documentai_toolbox import document

# TODO(developer): Uncomment these variables before running the sample.
# gcs_uri = "gs://bucket/path/to/folder/document.json"


def token_detected_languages_sample(
    gcs_uri: Optional[str] = None,
    document_path: Optional[str] = None,
) -> None:
    """Demonstrates how to access token-level detected languages.

    Args:
        gcs_uri (Optional[str]): 
            URI to a Document JSON file in GCS.
        document_path (Optional[str]): 
            Path to a local Document JSON file.
    """
    if gcs_uri:
        # Load a single Document from a Google Cloud Storage URI
        wrapped_document = document.Document.from_gcs_uri(gcs_uri=gcs_uri)
    elif document_path:
        # Load from local `Document` JSON file
        wrapped_document = document.Document.from_document_path(document_path)
    else:
        raise ValueError("No document source provided.")

    # Display detected languages for tokens in the first page
    if wrapped_document.pages:
        page = wrapped_document.pages[0]
        print(f"Page {page.page_number} Tokens:")
        
        for i, token in enumerate(page.tokens[:10]):  # Limiting to first 10 tokens for brevity
            print(f"Token {i}: '{token.text.strip()}'")
            
            if token.detected_languages:
                print("  Detected Languages:")
                for lang in token.detected_languages:
                    confidence_str = f", confidence: {lang.confidence:.4f}" if hasattr(lang, "confidence") else ""
                    print(f"    - {lang.language_code}{confidence_str}")
            else:
                print("  No language detected")
            print()
# [END documentai_toolbox_token_detected_languages]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--gcs_uri", help="GCS URI to Document JSON.")
    group.add_argument("--document_path", help="Path to local Document JSON file.")
    args = parser.parse_args()

    token_detected_languages_sample(
        gcs_uri=args.gcs_uri,
        document_path=args.document_path,
    ) 