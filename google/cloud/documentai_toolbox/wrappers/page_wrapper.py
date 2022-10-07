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
import pandas as pd

ElementWithLayout = Union[
    documentai.Document.Page.Paragraph,
    documentai.Document.Page.Line,
    documentai.Document.Page.Token,
    documentai.Document.Page.Table.TableCell,
]


@dataclasses.dataclass
class TableWrapper:
    """Represents a wrapped documentai.Document.Page.Table.

    Attributes:
        _documentai_table (google.cloud.documentai.Document.Page.Table):
            Required.The original google.cloud.documentai.Document.Page.Table object.
        body_rows (List[List[str]]):
            Required.A list of body rows.
        header_rows (List[List[str]]):
            Required.A list of headers.
    """

    _documentai_table: documentai.Document.Page.Table = dataclasses.field(
        init=True, repr=False
    )
    body_rows: List[List[str]] = dataclasses.field(init=True, repr=False)
    header_rows: List[List[str]] = dataclasses.field(init=True, repr=False)

    @classmethod
    def from_documentai_table(
        cls,
        documentai_table: documentai.Document.Page.Table,
        header_rows: List[List[str]],
        body_rows: List[List[str]],
    ) -> "TableWrapper":
        r"""Returns a TableWrapper from google.cloud.documentai.Document.Page.

        Args:
            documentai_table (google.cloud.documentai.Document.Page.Table):
                Required. A single table object.
            header_rows (List[List[str]]):
                Required. a list of header rows.
            body_rows (List[List[str]]):
                Required. a list of body rows.

        Returns:
            TableWrapper:
                A TableWrapper from google.cloud.documentai.Document.Page.Table.

        """
        return TableWrapper(
            _documentai_table=documentai_table,
            header_rows=header_rows,
            body_rows=body_rows,
        )

    def to_csv(self, file_name: str) -> None:
        r"""Writes table to a csv file with ``file_name``

            .. code-block:: python

                from google.cloud.documentai_toolbox import DocumentWrapper

                def sample_table_to_csv():

                    #Wrap document from gcs_path
                    merged_document = DocumentWrapper('gs://abc/def/gh/1')

                    #Use first page
                    page = merged_document.get_page(1)

                    #export the first table in page 1 to csv
                    page.tables[0].to_csv('test_table.csv')

        Args:
            file_name (str):
                Required. A file_name to write table to.

        Returns:
            None.

        """
        rows = self.body_rows if self.body_rows != [] else self.header_rows

        rows.append("\n")
        rows.append("\n")

        df = pd.DataFrame(rows)
        if self.body_rows != [] and self.header_rows != []:
            df.columns = self.header_rows

        df.to_csv(file_name, index=False)


def _get_tables(
    documentai_tables: List[documentai.Document.Page.Table], text: str
) -> List[TableWrapper]:
    r"""Returns a list of TableWrappers.

    Args:
        documentai_tables (List[documentai.Document.Page.Table]):
            Required. A list of documentai.Document.Page.Table.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.

    Returns:
        List[str]:
            A list of strings extracted from the element with layout.

    """
    result = []

    for table in documentai_tables:
        header_rows = []
        body_rows = []

        header_rows = _get_table_row(table.header_rows, text)
        body_rows = _get_table_row(table.body_rows, text)

        result.append(
            TableWrapper.from_documentai_table(
                documentai_table=table, body_rows=body_rows, header_rows=header_rows
            )
        )

    return result


def _get_table_row(
    table_rows: List[documentai.Document.Page.Table.TableRow], text: str
) -> List[str]:
    r"""Returns a list rows from table_rows.

    Args:
        table_rows (documentai.Document.Page.Table.TableRow):
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
        body_rows.append(
            [
                x.replace("\n", "")
                for x in _list_of_text_from_element_with_layout(row.cells, text)
            ]
        )
    return body_rows


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


def _list_of_text_from_element_with_layout(
    element_with_layout: List[ElementWithLayout], text: str
) -> List[str]:
    r"""Returns a list of text from an element with layout.

    Args:
        element_with_layout (List[ElementWithLayout]):
            Required. a list of elements with layout object.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.

    Returns:
        List[str]:
            A list of texts from a List[ElementWithLayout].
    """
    result = []
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for element in element_with_layout:
        result.append(
            _text_from_element_with_layout(element_with_layout=element, text=text)
        )
    return result


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
    """Represents a wrapped documentai.Document.Page.

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
    lines: List[LineWrapper] = dataclasses.field(init=True, repr=False)
    paragraphs: List[ParagraphWrapper] = dataclasses.field(init=True, repr=False)
    tables: List[TableWrapper] = dataclasses.field(init=True, repr=False)

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
            lines=_get_lines(lines=documentai_page.lines, text=text),
            paragraphs=_get_paragraphs(
                paragraphs=documentai_page.paragraphs, text=text
            ),
            tables=_get_tables(documentai_tables=documentai_page.tables, text=text),
        )
