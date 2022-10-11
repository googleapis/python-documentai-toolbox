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


# [START documentai_toolbox_get_entity_by_type]

from google.cloud.documentai_toolbox import DocumentWrapper

# TODO(developer): Uncomment these variables before running the sample
# gcs_prefix = 'gs://{bucket}/{optional_folder}/{operation_id}/{folder_id}'


def get_entity_by_type_using_str(gcs_prefix: str, target_type: str):

    # Wrap the shards in gcs_prefix to a single DocumentWrapper.
    merged_document = DocumentWrapper(gcs_prefix=gcs_prefix)

    found_entities = merged_document.get_entity_if_type_contains(target_type=str)

    # Print entities containing target_type
    for entity in found_entities:
        print(f"type_:{entity.type_} mention_text:{entity.mention_text}\n")


# [END documentai_toolbox_get_entity_by_type]
