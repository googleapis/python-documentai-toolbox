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

import dataclasses
from typing import List, Union

from google.cloud import documentai

ElementWithLayout = Union[
    documentai.Document.Page.Paragraph,
    documentai.Document.Page.Line,
    documentai.Document.Page.Token,
]


def _text_from_element_with_layout(
    element_with_layout: ElementWithLayout, text: str
) -> str:
    r"""Returns a text from a single element.
    Args:
        element_with_layout (ElementWithLayout):
            Required. a element with layout object.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.
    Returns:
        str:
            Text from a single element.
    """

    result_text = ""

    if element_with_layout.layout.text_anchor.text_segments == []:
        return ""
    else:
        for text_segment in element_with_layout.layout.text_anchor.text_segments:
            result_text += text[
                int(text_segment.start_index) : int(text_segment.end_index)
            ]

    return result_text


@dataclasses.dataclass
class ParagraphWrapper:
    """Represents a wrapped documentai.Document.Page.Paragraph.
    Attributes:
        _documentai_table (google.cloud.documentai.Document.Page.Paragraph):
            Required.The original google.cloud.documentai.Document.Page.Paragraph object.
        text (str):
            Required. UTF-8 encoded text.
    """

    _documentai_paragraph: documentai.Document.Page.Paragraph
    text: str


@dataclasses.dataclass
class LineWrapper:
    """Represents a wrapped documentai.Document.Page.Line.
    Attributes:
        _documentai_line (google.cloud.documentai.Document.Page.Line):
            Required.The original google.cloud.documentai.Document.Page.Line object.
        text (str):
            Required. UTF-8 encoded text.
    """

    _documentai_line: documentai.Document.Page.Line
    text: str


def _get_paragraphs(
    paragraphs: List[documentai.Document.Page.Paragraph], text: str
) -> List[ParagraphWrapper]:
    r"""Returns a list of ParagraphWrapper.
    Args:
        paragraphs (List[documentai.Document.Page.Paragraph]):
            Required. a list of documentai.Document.Page.Paragraph objects.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.
    Returns:
        List[str]:
            A list of texts from a List[ParagraphWrapper].
    """
    result = []

    for paragraph in paragraphs:
        result.append(
            ParagraphWrapper(
                _documentai_paragraph=paragraph,
                text=_text_from_element_with_layout(paragraph, text),
            )
        )

    return result


def _get_lines(
    lines: List[documentai.Document.Page.Line], text: str
) -> List[LineWrapper]:
    r"""Returns a list of LineWrapper.
    Args:
        paragraphs (List[documentai.Document.Page.Line]):
            Required. a list of documentai.Document.Page.Line objects.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.
    Returns:
        List[str]:
            A list of texts from a List[LineWrapper].
    """
    result = []

    for line in lines:
        result.append(
            LineWrapper(
                _documentai_line=line, text=_text_from_element_with_layout(line, text)
            )
        )

    return result


@dataclasses.dataclass
class PageWrapper:
    """Represents a wrapped documentai.Document.Page .

    Attributes:
        _documentai_page (google.cloud.documentai.Document.Page):
            Required.The original google.cloud.documentai.Document.Page object.
        lines (List[str]):
            Required.A list of visually detected text lines on the
            page. A collection of tokens that a human would
            perceive as a line.
        paragraphs (List[str]):
            Required.A list of visually detected text paragraphs
            on the page. A collection of lines that a human
            would perceive as a paragraph.
    """

    _documentai_page: documentai.Document.Page = dataclasses.field(
        init=True, repr=False
    )
    lines: List[str] = dataclasses.field(init=True, repr=False)
    paragraphs: List[str] = dataclasses.field(init=True, repr=False)

    @classmethod
    def from_documentai_page(
        cls, documentai_page: documentai.Document.Page, text: str
    ) -> "PageWrapper":
        r"""Returns a PageWrapper from google.cloud.documentai.Document.Page.

        Args:
            documentai_page (google.cloud.documentai.Document.Page):
                Required. A single page object.
            text (str):
                Required. UTF-8 encoded text in reading order
                from the document.

        Returns:
            PageWrapper:
                A PageWrapper from google.cloud.documentai.Document.Page.

        """
        return PageWrapper(
            _documentai_page=documentai_page,
            lines=_get_lines(documentai_page.lines, text),
            paragraphs=_get_paragraphs(documentai_page.paragraphs, text),
        )
