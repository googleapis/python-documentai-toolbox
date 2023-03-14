# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

import dataclasses
from typing import List
import json
from types import SimpleNamespace

from google.cloud import documentai


@dataclasses.dataclass
class Block:
    r"""Represents a Block from OCR data.

    Attributes:
        bounding_box (str):
            Required.
        block_references:
            Optional.
        block_id:
            Optional.
        confidence:
            Optional.
        type_:
            Required.
        text:
            Required.
        page_number:
            Optional.
    """
    bounding_box: dataclasses.field(init=True, repr=False, default=None)
    block_references: dataclasses.field(init=False, repr=False, default=None)
    block_id: dataclasses.field(init=False, repr=False, default=None)
    confidence: dataclasses.field(init=False, repr=False, default=None)
    type_: dataclasses.field(init=True, repr=False, default=None)
    text: dataclasses.field(init=True, repr=False, default=None)
    page_number: dataclasses.field(init=False, repr=False, default=None)
    page_width: dataclasses.field(init=False, repr=False, default=None)
    page_height: dataclasses.field(init=False, repr=False, default=None)
    bounding_width: dataclasses.field(init=False, repr=False, default=None)
    bounding_height: dataclasses.field(init=False, repr=False, default=None)
    bounding_type: dataclasses.field(init=False, repr=False, default=None)
    bounding_unit: dataclasses.field(init=False, repr=False, default=None)
    bounding_x: dataclasses.field(init=False, repr=False, default=None)
    bounding_y: dataclasses.field(init=False, repr=False, default=None)
    docproto_width: dataclasses.field(init=False, repr=False, default=None)
    docproto_height: dataclasses.field(init=False, repr=False, default=None)

    @classmethod
    def create(
        self,
        type_,
        text,
        bounding_box=None,
        block_references=None,
        block_id=None,
        confidence=None,
        page_number=None,
        page_width=None,
        page_height=None,
        bounding_width=None,
        bounding_height=None,
        bounding_type=None,
        bounding_unit=None,
        bounding_x=None,
        bounding_y=None,
        docproto_width=None,
        docproto_height=None,
    ):
        return Block(
            bounding_box=bounding_box,
            block_references=block_references,
            block_id=block_id,
            confidence=confidence,
            type_=type_,
            text=text,
            page_number=page_number,
            page_width=page_width,
            page_height=page_height,
            bounding_width=bounding_width,
            bounding_height=bounding_height,
            bounding_type=bounding_type,
            bounding_unit=bounding_unit,
            bounding_x=bounding_x,
            bounding_y=bounding_y,
            docproto_width=docproto_width,
            docproto_height=docproto_height,
        )


def _load_blocks(
    object, bounding_type, bounding_unit, docproto_width, docproto_height
) -> List[Block]:
    r"""Returns a list of blocks.

    Args:
        object (JSON):
            Required. A JSON of  data.

    Returns:
        List[Block].

    """
    blocks = []
    for i, block in enumerate(object["entities"]):

        bounding_box = block["geometry"]["boundingBox"]
        block_references = []
        block_id = block["id"]
        confidence = block["confidence"] / 100
        type_ = block["blockType"]
        text = block["text"]
        page_number = block["page"]
        page_width = object["page_width"]
        page_height = object["page_width"]
        bounding_width = block["geometry"]["boundingBox"]["width"]
        bounding_height = block["geometry"]["boundingBox"]["height"]
        bounding_type = bounding_type
        bounding_unit = bounding_unit
        bounding_x = bounding_height = block["geometry"]["boundingBox"]["x"]
        bounding_y = bounding_height = block["geometry"]["boundingBox"]["y"]
        docproto_width = docproto_width
        docproto_height = docproto_height

        blocks.append(
            Block.create(
                bounding_box=bounding_box,
                block_references=block_references,
                block_id=block_id,
                confidence=confidence,
                type_=type_,
                text=text,
                page_number=page_number,
                page_width=page_width,
                page_height=page_height,
                bounding_width=bounding_width,
                bounding_height=bounding_height,
                bounding_type=bounding_type,
                bounding_unit=bounding_unit,
                bounding_x=bounding_x,
                bounding_y=bounding_y,
                docproto_width=docproto_width,
                docproto_height=docproto_height,
            )
        )
    return blocks
