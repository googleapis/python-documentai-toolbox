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
"""Python wrappers for Document AI message types."""

from dataclasses import dataclass, field
import re
from typing import List

from google.cloud import documentai
from google.cloud.documentai_toolbox.services import (
    entity_wrapper_service,
)

@dataclass
class EntityWrapper:
    """Represents a wrapped documentai.Document.Page .

    This class hides away the complexity of documentai message types and
    implements convenient methods for searching and extracting information within
    the Document.
    """

    shards: List[documentai.Document]

    entities: List[str] = field(init=False, repr=False, default_factory=lambda: [])

    def __post_init__(self):
        self.entities = entity_wrapper_service._get_entities(self.shards)

    
    def get_entity_by_type(self,entity_type : str) -> List[str]:
        res = []
        for entity in self.entities:
            if entity["entity_type"] == entity_type:
                res.append(entity["entity_value"])
        
        return res
    
    def get_entity_if_type_contains(self,entity_type : str) -> List[str]:
        res = []
        for entity in self.entities:
            if entity_type in entity["entity_type"]:
                res.append({entity["entity_type"] : entity["entity_value"]})
        
        return res
