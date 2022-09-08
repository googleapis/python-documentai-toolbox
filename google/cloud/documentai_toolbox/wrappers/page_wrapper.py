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
"""Wrappers for Document AI Page type."""

from dataclasses import dataclass, field
import re
from typing import List

from google.cloud import documentai


@dataclass
class PageWrapper:
    """Represents a wrapped documentai.Document.Page .

    This class hides away the complexity of documentai page message type and
    implements convenient methods for searching and extracting information within
    the Document.
    """

    shards: List[documentai.Document]

    _lines: List[str] = field(init=False, repr=False, default_factory=lambda: [])
    _paragraphs: List[str] = field(init=False, repr=False, default_factory=lambda: [])
    _tokens: List[str] = field(init=False, repr=False, default_factory=lambda: [])

    def __post_init__(self):
        self._lines = _get_lines(self.shards)
        self._paragraphs = _get_paragraphs(self.shards)
        self._tokens = _get_tokens(self.shards)

    def get_text_on_page(self, page_number: int) -> List[str]:
        """Returns a list of paragraphs on page_number."""
        return self._paragraphs[page_number - 1]

    def search_pages_by_paragraph(self, regex: str) -> List[str]:
        """Returns a list of paragraphs that match the regex."""
        res = []
        for paragraph in self._paragraphs:
            for text in paragraph:
                if re.findall(regex, text) != []:
                    res.append(text)

        return res
    
    def search_pages_by_line(self, regex: str) -> List[str]:
        """Returns a list of lines that match the regex."""
        res = []
        for line in self._lines:
            for text in line:
                if re.findall(regex, text) != []:
                    res.append(text)

        return res


def _get_paragraphs(shards: List[documentai.Document]) -> List[str]:
    """Returns a list of text from Document.page.paragraphs ."""
    result = []
    for shard in shards:
        text = shard.text
        for page in shard.pages:
            result.append(_text_from_layout(page.paragraphs, text))

    return result


def _get_lines(shards: List[documentai.Document]) -> List[str]:
    """Returns a list of text from Document.page.lines ."""
    result = []
    for shard in shards:
        text = shard.text
        for page in shard.pages:
            result.append(_text_from_layout(page.lines, text))

    return result


def _get_tokens(shards: List[documentai.Document]) -> List[str]:
    """Returns a list of text from Document.page.tokens ."""
    result = []
    for shard in shards:
        text = shard.text
        for page in shard.pages:
            result.append(_text_from_layout(page.tokens, text))

    return result


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
