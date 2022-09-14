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

from dataclasses import dataclass, field
import re
from typing import List

from google.cloud import documentai
from google.cloud import storage

from google.cloud.documentai_toolbox.wrappers import page_wrapper, entity_wrapper


def _entities_from_shards(shards) -> List[entity_wrapper.EntityWrapper]:
    result = []
    for shard in shards:
        for entity in shard.entities:
            result.append(
                entity_wrapper.EntityWrapper(entity, entity.type, entity.mention_text)
            )
    return result


def _pages_from_shards(shards) -> List[page_wrapper.PageWrapper]:
    result = []
    for shard in shards:
        text = shard.text
        for page in shard.pages:
            lines = []
            paragraphs = []
            tokens = []

            lines.append(_text_from_layout(page.lines, text))
            paragraphs.append(_text_from_layout(page.paragraphs, text))
            tokens.append(_text_from_layout(page.tokens, text))

            result.append(page_wrapper.PageWrapper(lines, paragraphs, tokens))

    return result


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


def _text_from_layout(page_entities, text: str) -> List[str]:
    """Returns a list of texts from Document.page ."""
    result = []
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for entity in page_entities:
        result_text = ""
        for text_segment in entity.layout.text_anchor.text_segments:
            start_index = int(text_segment.start_index)
            end_index = int(text_segment.end_index)
            result_text += text[start_index:end_index]
        result.append(text[start_index:end_index])
    return result


@dataclass
class DocumentWrapper:
    """Represents a wrapped Document.

    A single Document protobuf message might be written as several JSON files on
    GCS by Document AI's BatchProcessDocuments method.  This class hides away the
    shards from the users and implements convenient methods for searching and
    extracting information within the Document.
    """

    _shards: List[documentai.Document] = field(init=False, repr=False)
    pages: List[page_wrapper.PageWrapper] = field(init=False, repr=False)
    entities: List[entity_wrapper.EntityWrapper] = field(init=False, repr=False)
    gcs_prefix: str

    def __post_init__(self):
        self._shards = _read_output(self.gcs_prefix)
        self.pages = _pages_from_shards(shards=self._shards)
        self.entities = _entities_from_shards(shards=self._shards)
