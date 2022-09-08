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
    page_wrapper_service,
)

@dataclass
class PageWrapper:
    """Represents a wrapped documentai.Document.Page .

    This class hides away the complexity of documentai message types and
    implements convenient methods for searching and extracting information within
    the Document.
    """

    shards: List[documentai.Document]

    _lines: List[str] = field(init=False, repr=False, default_factory=lambda: [])
    _paragraphs: List[str] = field(init=False, repr=False, default_factory=lambda: [])
    _tokens: List[str] = field(init=False, repr=False, default_factory=lambda: [])

    def __post_init__(self):
        self._lines = page_wrapper_service._get_lines(self.shards)
        self._paragraphs = page_wrapper_service._get_paragraphs(self.shards)
        self._tokens = page_wrapper_service._get_tokens(self.shards)

    def get_text_on_page(self, page_number: int) -> List[str]:
        return self._paragraphs[page_number - 1]

    def search_pages_by_paragraph(self, regex: str) -> List[str]:
        res = []
        for paragraph in self._paragraphs:
            for text in paragraph:
                if re.findall(regex, text) != []:
                    res.append(text)

        return res
    
    def search_pages_by_line(self, regex: str) -> List[str]:
        res = []
        for line in self._lines:
            for text in line:
                if re.findall(regex, text) != []:
                    res.append(text)

        return res
