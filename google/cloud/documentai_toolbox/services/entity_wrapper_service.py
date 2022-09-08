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
"""This module has all of the helper functions needed to merge shards."""
from typing import List

from google.cloud import documentai

def _get_entities(shard_list: List[documentai.Document]):
  """Gets tokens from document shard and returns text in a list."""
  res = []
  for shard in shard_list:
    text = shard.text
    for entity in shard.entities:
      res.append({"entity_type" : entity.type, "entity_value" : entity.mention_text})

  return res