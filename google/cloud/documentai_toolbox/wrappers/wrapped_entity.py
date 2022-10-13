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

import dataclasses

from google.cloud import documentai


@dataclasses.dataclass
class WrappedEntity:
    r"""Represents a wrapped google.cloud.documentai.Document.Entity.

    Attributes:
        _documentai_entity (google.cloud.documentai.Document.Entity):
            Required.The original google.cloud.documentai.Document.Entity object.
        type_ (str):
            Required. Entity type from a schema e.g. ``Address``.
        mention_text (str):
            Optional. Text value in the document e.g.
            ``1600 Amphitheatre Pkwy``. If the entity is not present in
            the document, this field will be empty.
    """
    _documentai_entity: documentai.Document.Entity = dataclasses.field(
        init=True, repr=False
    )
    type_: str = dataclasses.field(init=True, repr=False)
    mention_text: str = dataclasses.field(init=True, repr=False, default="")

    @classmethod
    def from_documentai_entity(
        cls, documentai_entity: documentai.Document.Entity
    ) -> "WrappedEntity":
        r"""Returns a WrappedEntity from google.cloud.documentai.Document.Entity.

        Args:
            documentai_entity (google.cloud.documentai.Document.Entity):
                Required. A single entity object.

        Returns:
            WrappedEntity:
                A WrappedEntity from google.cloud.documentai.Document.Entity.

        """
        return WrappedEntity(
            _documentai_entity=documentai_entity,
            type_=documentai_entity.type,
            mention_text=documentai_entity.mention_text,
        )
