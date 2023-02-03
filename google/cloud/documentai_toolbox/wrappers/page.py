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
from typing import Dict, List, Union

from google.cloud import documentai
from google.cloud import vision

import pandas as pd

ElementWithLayout = Union[
    documentai.Document.Page.Block,
    documentai.Document.Page.Line,
    documentai.Document.Page.Paragraph,
    documentai.Document.Page.Symbol,
    documentai.Document.Page.Table.TableCell,
    documentai.Document.Page.Token,
]

VisionWithLayout = Union[vision.Block, vision.Paragraph, vision.Word, vision.Symbol]


@dataclasses.dataclass
class Table:
    """Represents a wrapped documentai.Document.Page.Table.

    Attributes:
        documentai_table (google.cloud.documentai.Document.Page.Table):
            Required. The original google.cloud.documentai.Document.Page.Table object.
        body_rows (List[List[str]]):
            Required. A list of body rows.
        header_rows (List[List[str]]):
            Required. A list of header rows.
    """

    documentai_table: documentai.Document.Page.Table = dataclasses.field(repr=False)
    body_rows: List[List[str]] = dataclasses.field(repr=False)
    header_rows: List[List[str]] = dataclasses.field(repr=False)

    def to_dataframe(self) -> pd.DataFrame:
        r"""Returns pd.DataFrame from documentai.table

        Returns:
            pd.DataFrame:
                The DataFrame of the table.

        """
        if not self.body_rows:
            return pd.DataFrame(columns=self.header_rows)

        dataframe = pd.DataFrame(self.body_rows)
        if self.header_rows:
            dataframe.columns = self.header_rows
        else:
            dataframe.columns = [None] * len(self.body_rows[0])

        return dataframe

    def to_csv(self) -> str:
        r"""Returns a csv str.

            .. code-block:: python

                from google.cloud.documentai_toolbox import Document

                def sample_table_to_csv():

                    #Wrap document from gcs_path
                    merged_document = Document('gs://abc/def/gh/1')

                    #Use first page
                    page = merged_document.pages[0]

                    #export the first table in page 1 to csv
                    csv_text = page.tables[0].to_csv()

                    print(csv_text)

        Args:
            dataframe (pd.Dataframe):
                Required. Two-dimensional, size-mutable, potentially heterogeneous tabular data.

        Returns:
            str:
                The table in csv format.

        """
        return self.to_dataframe().to_csv(index=False)


def _table_wrapper_from_documentai_table(
    documentai_table: documentai.Document.Page.Table, text: str
) -> Table:
    r"""Returns a Table.

    Args:
        documentai_table (documentai.Document.Page.Table):
            Required. A documentai.Document.Page.Table.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.

    Returns:
        Table:
            A Table.

    """

    header_rows = _table_rows_from_documentai_table_rows(
        table_rows=documentai_table.header_rows, text=text
    )
    body_rows = _table_rows_from_documentai_table_rows(
        table_rows=documentai_table.body_rows, text=text
    )

    return Table(
        documentai_table=documentai_table, body_rows=body_rows, header_rows=header_rows
    )


@dataclasses.dataclass
class Paragraph:
    """Represents a wrapped documentai.Document.Page.Paragraph.

    Attributes:
        documentai_paragraph (google.cloud.documentai.Document.Page.Paragraph):
            Required. The original google.cloud.documentai.Document.Page.Paragraph object.
        text (str):
            Required. UTF-8 encoded text.
    """

    documentai_paragraph: documentai.Document.Page.Paragraph
    text: str


@dataclasses.dataclass
class Line:
    """Represents a wrapped documentai.Document.Page.Line.

    Attributes:
        documentai_line (google.cloud.documentai.Document.Page.Line):
            Required. The original google.cloud.documentai.Document.Page.Line object.
        text (str):
            Required. UTF-8 encoded text.
    """

    documentai_line: documentai.Document.Page.Line
    text: str


def _text_from_element_with_layout(
    element_with_layout: ElementWithLayout, text: str
) -> str:
    r"""Returns a text from a single element.

    Args:
        element_with_layout (ElementWithLayout):
            Required. a element with layout attribute.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.

    Returns:
        str:
            Text from a single element.
    """

    result_text = ""

    if not element_with_layout.layout.text_anchor.text_segments:
        return ""

    for text_segment in element_with_layout.layout.text_anchor.text_segments:
        result_text += text[int(text_segment.start_index) : int(text_segment.end_index)]

    return result_text


def _get_paragraphs(
    paragraphs: List[documentai.Document.Page.Paragraph], text: str
) -> List[Paragraph]:
    r"""Returns a list of Paragraph.

    Args:
        paragraphs (List[documentai.Document.Page.Paragraph]):
            Required. A list of documentai.Document.Page.Paragraph objects.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.
    Returns:
        List[Paragraph]:
             A list of Paragraphs.
    """
    result = []

    for paragraph in paragraphs:
        result.append(
            Paragraph(
                documentai_paragraph=paragraph,
                text=_text_from_element_with_layout(
                    element_with_layout=paragraph, text=text
                ),
            )
        )

    return result


def _get_lines(lines: List[documentai.Document.Page.Line], text: str) -> List[Line]:
    r"""Returns a list of Line.

    Args:
        lines (List[documentai.Document.Page.Line]):
            Required. A list of documentai.Document.Page.Line objects.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.
    Returns:
        List[Line]:
            A list of Lines.
    """
    result = []

    for line in lines:
        result.append(
            Line(
                documentai_line=line,
                text=_text_from_element_with_layout(
                    element_with_layout=line, text=text
                ),
            )
        )

    return result


def _table_rows_from_documentai_table_rows(
    table_rows: List[documentai.Document.Page.Table.TableRow], text: str
) -> List[str]:
    r"""Returns a list of rows from table_rows.

    Args:
        table_rows (List[documentai.Document.Page.Table.TableRow]):
            Required. A documentai.Document.Page.Table.TableRow.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.

    Returns:
        List[str]:
            A list of table rows.
    """
    body_rows = []
    for row in table_rows:
        row_text = []

        for cell in row.cells:
            row_text.append(
                _text_from_element_with_layout(element_with_layout=cell, text=text)
            )

        body_rows.append([x.replace("\n", "") for x in row_text])
    return body_rows


def _convert_languages_to_vision(
    detected_languages: List[documentai.Document.Page.DetectedLanguage],
) -> List[vision.TextAnnotation.DetectedLanguage]:
    vision_detected_languages: List[vision.TextAnnotation.DetectedLanguage] = []

    for language in detected_languages:
        vision_detected_languages.append(
            vision.TextAnnotation.DetectedLanguage(
                language_code=language.language_code, confidence=language.confidence
            )
        )

    return vision_detected_languages


@dataclasses.dataclass
class Page:
    """Represents a wrapped documentai.Document.Page .

    Attributes:
        documentai_page (google.cloud.documentai.Document.Page):
            Required. The original google.cloud.documentai.Document.Page object.
        text: (str):
            Required. The full text of the Document containing the Page.
        lines (List[str]):
            Required. A list of visually detected text lines on the
            page. A collection of tokens that a human would
            perceive as a line.
        paragraphs (List[str]):
            Required. A list of visually detected text paragraphs
            on the page. A collection of lines that a human
            would perceive as a paragraph.
        tables (List[Table]):
            Required. A list of visually detected tables on the
            page.
    """

    documentai_page: documentai.Document.Page = dataclasses.field(repr=False)
    text: str = dataclasses.field(repr=False)

    lines: List[Line] = dataclasses.field(init=False, repr=False)
    paragraphs: List[Paragraph] = dataclasses.field(init=False, repr=False)
    tables: List[Table] = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        tables = []

        for table in self.documentai_page.tables:
            tables.append(
                _table_wrapper_from_documentai_table(
                    documentai_table=table, text=self.text
                )
            )

        self.lines = _get_lines(lines=self.documentai_page.lines, text=self.text)
        self.paragraphs = _get_paragraphs(
            paragraphs=self.documentai_page.paragraphs, text=self.text
        )
        self.tables = tables

    def to_text_annotation_page(self) -> vision.Page:
        vision_page = vision.Page(
            width=int(self.documentai_page.dimension.width),
            height=int(self.documentai_page.dimension.height),
            confidence=self.documentai_page.layout.confidence,
        )

        vision_page.property.detected_languages = _convert_languages_to_vision(
            self.documentai_page.detected_languages
        )

        for block in self.documentai_page.blocks:
            vision_page.blocks.append(self._convert_block_to_vision(block))
        return vision_page

    def _convert_break_to_vision(
        documentai_break: documentai.Document.Page.Token.DetectedBreak,
    ) -> vision.TextAnnotation.DetectedBreak:
        break_type_map = {
            documentai.Document.Page.Token.DetectedBreak.SPACE: vision.TextAnnotation.DetectedBreak.SPACE,
            documentai.Document.Page.Token.DetectedBreak.WIDE_SPACE: vision.TextAnnotation.DetectedBreak.SURE_SPACE,
            documentai.Document.Page.Token.DetectedBreak.HYPHEN: vision.TextAnnotation.DetectedBreak.HYPHEN,
            documentai.Document.Page.Token.DetectedBreak.TYPE_UNSPECIFIED: None,
        }

        return break_type_map.get(
            documentai_break, vision.TextAnnotation.DetectedBreak.UNKNOWN
        )

    def _convert_layout_element_to_vision(
        documentai_layout: documentai.Document.Page.Layout,
    ) -> VisionWithLayout:
        r"""Convert Document AI Layout to Vision format.
        Args:
            documentai_layout documentai.Document.Page.Layout:
                Required. A Document AI Layout element
        Returns:
            VisionWithLayout:
                A Vision element that contains layout and confidence information.
        """
        vision_element: VisionWithLayout = VisionWithLayout(
            confidence=documentai_layout.confidence
        )

        # Some Document AI Outputs don't include the raw vertices
        if documentai_layout.bounding_poly.vertices:
            for vertex in documentai_layout.bounding_poly.vertices:
                vision_element.bounding_box.vertices.append(
                    vision.Vertex(x=int(vertex.x), y=int(vertex.y))
                )
        # else:
        #     for (
        #         normalized_vertex
        #     ) in documentai_layout.bounding_poly.normalized_vertices:
        #         vision_element.bounding_box.vertices.append(
        #             vision.Vertex(x=int(normalized_vertex.x * documentai_page.dimension.width),
        #                           y=int(normalized_vertex.y * documentai_page.dimension.height))
        #         )

        for normalized_vertex in documentai_layout.bounding_poly.normalized_vertices:
            vision_element.bounding_box.normalized_vertices.append(
                vision.NormalizedVertex(x=normalized_vertex.x, y=normalized_vertex.y)
            )

        return vision_element

    def _convert_block_to_vision(
        documentai_block: documentai.Document.Page.Block,
    ) -> vision.Block:
        vision_block = vision.Block(block_type=vision.Block.BlockType.TEXT)
        vision_block.property.detected_languages = _convert_languages_to_vision(
            documentai_block.detected_languages
        )
        return vision_block
