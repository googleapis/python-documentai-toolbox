# Copyright 2023 Google LLC
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


# [START documentai_toolbox_merge_document_shards]

from google.cloud import documentai
from google.cloud.documentai_toolbox import document

# TODO(developer): Uncomment these variables before running the sample.
# Given a document.proto or sharded document.proto in path gs://bucket/path/to/folder
# gcs_bucket_name = "bucket"
# gcs_prefix = "path/to/folder"
# output_file_name = "path/to/folder/file.json"


def merge_document_shards_sample(
    gcs_bucket_name: str, gcs_prefix: str, output_file_name: str
) -> None:
    wrapped_document = document.Document.from_gcs(
        gcs_bucket_name=gcs_bucket_name, gcs_prefix=gcs_prefix
    )

    merged_document = wrapped_document.to_merged_documentai_document()

    with open(output_file_name, "w") as f:
        f.write(documentai.Document.to_json(merged_document))

    print(f"Document with {len(wrapped_document.shards)} shards successfully merged.")


# [END documentai_toolbox_merge_document_shards]
