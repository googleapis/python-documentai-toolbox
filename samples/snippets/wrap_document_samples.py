# Copyright 2022 Google LLC
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

# [START wrap_document_from_gcs_prefix]

from google.cloud.documentai_toolbox import document

def wrap_document_from_gcs_prefix(gcs_prefix:str):
    wrapped_document = document.Document.from_gcs_prefix(gcs_prefix=gcs_prefix)

    print("Wrapped Document Completed!")
    print(f"\t Number of Pages: {len(wrapped_document.pages)}")
    print(f"\t Number of Entities: {len(wrapped_document.entities)}")

# [END wrap_document_from_gcs_prefix]

# [START wrap_document_from_documentai_document]

from google.cloud.documentai_toolbox import document
import google.cloud.documentai as documentai

def wrap_document_from_documentai_document(docproto_path:str):

    with open(docproto_path,"r") as f:
        docproto = documentai.Document.from_json(f.read())

    wrapped_document = document.Document.from_documentai_document(documentai_document=docproto)

    print("Wrapped Document Completed!")
    print(f"\t Number of Pages: {len(wrapped_document.pages)}")
    print(f"\t Number of Entities: {len(wrapped_document.entities)}")

# [END wrap_document_from_documentai_document]
