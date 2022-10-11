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


# [START documentai_toolbox_search_page]
from heapq import merge
from google.cloud.documentai_toolbox import DocumentWrapper

# TODO(developer): Uncomment these variables before running the sample
# gcs_prefix = 'gs://{bucket}/{optional_folder}/{operation_id}/{folder_id}'


def search_page_with_regex(gcs_prefix: str, regex: str):

    # Wrap the shards in gcs_prefix to a single DocumentWrapper.
    merged_document = DocumentWrapper(gcs_prefix=gcs_prefix)

    found_pages = merged_document.search_pages(regex=regex)

    for page in found_pages:
        for paragraph in page.paragraphs:
            print(paragraph)


def search_page_with_str(gcs_prefix: str, target_str: str):

    # Wrap the shards in gcs_prefix to a single DocumentWrapper.
    merged_document = DocumentWrapper(gcs_prefix=gcs_prefix)

    found_pages = merged_document.search_pages(target_string=target_str)

    for page in found_pages:
        for paragraph in page.paragraphs:
            print(paragraph)


# [END documentai_toolbox_search_page]
