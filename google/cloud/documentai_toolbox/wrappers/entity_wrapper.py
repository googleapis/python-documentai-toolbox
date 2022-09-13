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

from dataclasses import dataclass
from typing import List

from google.cloud import documentai

@dataclass
class EntityWrapper:
    """Represents a wrapped documentai.Document.Entity .

    This class hides away the complexity of documentai Entity message type.
    """

    original_entity:documentai.Document.Entity
    type_:str
    mention_text:str
