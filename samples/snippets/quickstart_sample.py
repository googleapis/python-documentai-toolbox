# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# [START documentai_toolbox_quickstart]

from google.cloud.documentai_toolbox import DocumentWrapper

# TODO(developer): Uncomment these variables before running the sample
# gcs_prefix = 'gs://{bucket}/{optional_folder}/{operation_id}/{folder_id}'


def quickstart(gcs_prefix: str):

    # Wrap the shards in gcs_prefix to a single DocumentWrapper.
    merged_document = DocumentWrapper(gcs_prefix=gcs_prefix)

    for page in merged_document.pages:
        print("Page Stats: ")
        print(f"\t # of Lines: {len(page.lines)}")
        print(f"\t # of Paragraphs: {len(page.paragraphs)}")
        print(f"\t # of Tables: {len(page.tables)}")

        print("This page contains the following text:")
        for paragraph in page.paragraphs:
            print(paragraph.text)


# [END documentai_toolbox_quickstart]
