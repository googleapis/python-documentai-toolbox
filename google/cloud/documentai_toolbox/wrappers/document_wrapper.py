# -*- coding: utf-8 -*-
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
"""Wrappers for Document AI Document type."""

from dataclasses import InitVar, dataclass, field
import re
from typing import List

from google.cloud import documentai
from google.cloud import storage

from google.cloud.documentai_toolbox.wrappers.page_wrapper import PageWrapper
from google.cloud.documentai_toolbox.wrappers.entity_wrapper import EntityWrapper

@dataclass
class DocumentWrapper:
    """Represents a wrapped Document.

    A single Document protobuf message might be written as several JSON files on
    GCS by Document AI's BatchProcessDocuments method.  This class hides away the
    shards from the users and implements convenient methods for searching and
    extracting information within the Document.
    """

    _shards: List[documentai.Document] = field(init=False, repr=False)
    pages: PageWrapper = field(init=False, repr=False)
    entities: EntityWrapper = field(init=False, repr=False)
    gcs_prefix: InitVar[str]

    def __post_init__(self,gcs_prefix):
        self._shards = _read_output(gcs_prefix)
        self.pages = PageWrapper(shards=self._shards)
        self.entities = EntityWrapper(shards=self._shards)
    
    def get_entity_by_type(self,entity_type : str) -> List[str]:
        """Returns a list of entities matching the entity_type."""
        res = []
        for entity in self.entities.entities:
            if entity["entity_type"] == entity_type:
                res.append(entity["entity_value"])
        
        return res
    
    def get_entity_if_type_contains(self,contains_text : str) -> List[str]:
        """Returns a list of entities that have contains_text in them."""
        res = []
        for entity in self.entities.entities:
            if contains_text in entity["entity_type"]:
                res.append({entity["entity_type"] : entity["entity_value"]})
        
        return res



def _read_output(gcs_prefix: str) -> List[documentai.Document]:
    """Returns a list of Document shards."""

    shards = []

    output_bucket, output_prefix = re.match(r"gs://(.*?)/(.*)", gcs_prefix).groups()

    file_check = re.match(r"(.*[.].*$)", output_prefix)

    if file_check is not None:
        raise TypeError("gcs_prefix cannot contain file types")

    storage_client = storage.Client()

    blob_list = storage_client.list_blobs(output_bucket, prefix=output_prefix)

    for blob in blob_list:
        if blob.name.endswith(".json"):
            blob_as_bytes = blob.download_as_bytes()
            shards.append(documentai.Document.from_json(blob_as_bytes))

    return shards