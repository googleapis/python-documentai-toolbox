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
"""Wrappers for Document AI Entity type."""

from dataclasses import dataclass, field
import re
from typing import List

from google.cloud import documentai


@dataclass
class EntityWrapper:
    """Represents a wrapped documentai.Document.Entity .

    This class hides away the complexity of documentai Entity message type.
    """

    shards: List[documentai.Document]

    entities: List[str] = field(init=False, repr=False, default_factory=lambda: [])

    def __post_init__(self):
        self.entities = _get_entities(self.shards)


def _get_entities(shard_list: List[documentai.Document]):
  """Gets entities from document shards and returns a key/value pair list with entity_type and entity_value."""
  res = []
  for shard in shard_list:
    text = shard.text
    for entity in shard.entities:
      res.append({"entity_type" : entity.type, "entity_value" : entity.mention_text})

  return res