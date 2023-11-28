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

from abc import ABC

import dataclasses
from typing import cast, List, Optional, Type

import pandas as pd

from google.cloud import documentai
from google.cloud.documentai_toolbox.constants import ElementWithLayout
from google.cloud.documentai_toolbox.utilities import docai_utilities


@dataclasses.dataclass
class Table:
    """Represents a wrapped documentai.Document.Page.Table.

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.Table):
            Required. The original object.
        body_rows (List[List[str]]):
            Required. A list of body rows.
        header_rows (List[List[str]]):
            Required. A list of header rows.
    """

    documentai_object: documentai.Document.Page.Table = dataclasses.field(repr=False)
    _page: "Page" = dataclasses.field(repr=False)

    _body_rows: Optional[List[List[str]]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _header_rows: Optional[List[List[str]]] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def body_rows(self):
        if self._body_rows is None:
            self._body_rows = _table_rows_from_documentai_table_rows(
                table_rows=list(self.documentai_object.body_rows),
                text=self._page._document_text,
            )
        return self._body_rows

    @property
    def header_rows(self):
        if self._header_rows is None:
            self._header_rows = _table_rows_from_documentai_table_rows(
                table_rows=list(self.documentai_object.header_rows),
                text=self._page._document_text,
            )
        return self._header_rows

    def to_dataframe(self) -> pd.DataFrame:
        r"""Returns pd.DataFrame from documentai.table

        Returns:
            pd.DataFrame:
                The DataFrame of the table.

        """
        if not self.body_rows:
            return pd.DataFrame(columns=self.header_rows)

        if self.header_rows:
            columns = pd.MultiIndex.from_arrays(self.header_rows)
        else:
            columns = [None] * len(self.body_rows[0])

        return pd.DataFrame(self.body_rows, columns=columns)


@dataclasses.dataclass
class FormField:
    """Represents a wrapped documentai.Document.Page.FormField.

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.FormField):
            Required. The original object.
        field_name (str):
            Required. The form field name
        field_value (str):
            Required. The form field value
    """

    documentai_object: documentai.Document.Page.FormField = dataclasses.field(
        repr=False
    )
    _page: "Page" = dataclasses.field(repr=False)

    _field_name: Optional[str] = dataclasses.field(init=False, repr=False, default=None)
    _field_value: Optional[str] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def field_name(self):
        if self._field_name is None:
            self._field_name = _trim_text(
                _text_from_layout(
                    self.documentai_object.field_name, self._page._document_text
                )
            )
        return self._field_name

    @property
    def field_value(self):
        if self._field_value is None:
            self._field_value = _trim_text(
                _text_from_layout(
                    self.documentai_object.field_value, self._page._document_text
                )
            )
        return self._field_value


@dataclasses.dataclass
class _BasePageElement(ABC):
    """Base class for representing a wrapped Document AI Page element (Symbol, Token, Line, Paragraph, Block)."""

    documentai_object: ElementWithLayout = dataclasses.field(repr=False)
    _page: "Page" = dataclasses.field(repr=False)

    _text: Optional[str] = dataclasses.field(init=False, repr=False, default=None)
    _hocr_bounding_box: Optional[str] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def text(self):
        """
        Text of the page element.
        """
        if self._text is None:
            self._text = _text_from_layout(
                layout=self.documentai_object.layout, text=self._page._document_text
            )
        return self._text

    @property
    def hocr_bounding_box(self):
        """
        hOCR bounding box of the page element.
        """
        if self._hocr_bounding_box is None:
            self._hocr_bounding_box = _get_hocr_bounding_box(
                element_with_layout=self.documentai_object,
                page_dimension=self._page.documentai_object.dimension,
            )
        return self._hocr_bounding_box


@dataclasses.dataclass
class Symbol(_BasePageElement):
    """Represents a wrapped documentai.Document.Page.Symbol.
    https://cloud.google.com/document-ai/docs/process-documents-ocr#enable_symbols

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.Symbol):
            Required. The original object.
        text (str):
            Required. The text of the Symbol.
    """

    @property
    def hocr_bounding_box(self):
        # Symbols are not represented in hOCR
        return None


@dataclasses.dataclass
class Token(_BasePageElement):
    """Represents a wrapped documentai.Document.Page.Token.

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.Token):
            Required. The original object.
        text (str):
            Required. The text of the Token.
        symbols (List[Symbol]):
            Optional. The Symbols contained within the Token.
    """

    _symbols: Optional[List[Symbol]] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def symbols(self):
        if self._symbols is None:
            self._symbols = cast(
                List[Symbol],
                _get_children_of_element(self.documentai_object, self._page.symbols),
            )
        return self._symbols


@dataclasses.dataclass
class Line(_BasePageElement):
    """Represents a wrapped documentai.Document.Page.Line.

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.Line):
            Required. The original object.
        text (str):
            Required. The text of the Line.
        _tokens (List[Token]):
            Optional. The Tokens contained within the Line.
    """

    _tokens: Optional[List[Token]] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def tokens(self):
        if self._tokens is None:
            self._tokens = cast(
                List[Token],
                _get_children_of_element(self.documentai_object, self._page.tokens),
            )
        return self._tokens


@dataclasses.dataclass
class Paragraph(_BasePageElement):
    """Represents a wrapped documentai.Document.Page.Paragraph.

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.Paragraph):
            Required. The original object.
        text (str):
            Required. The text of the Paragraph.
        _lines (List[Line]):
            Optional. The Lines contained within the Paragraph.
    """

    _lines: Optional[List[Line]] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def lines(self):
        if self._lines is None:
            self._lines = cast(
                List[Line],
                _get_children_of_element(self.documentai_object, self._page.lines),
            )
        return self._lines


@dataclasses.dataclass
class Block(_BasePageElement):
    """Represents a wrapped documentai.Document.Page.Block.

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.Block):
            Required. The original object.
        text (str):
            Required. The text of the Block.
        _paragraphs (List[Paragraph]):
            Optional. The Paragraphs contained within the Block.
    """

    _paragraphs: Optional[List[Paragraph]] = dataclasses.field(
        init=False, repr=False, default=None
    )

    @property
    def paragraphs(self):
        if self._paragraphs is None:
            self._paragraphs = cast(
                List[Paragraph],
                _get_children_of_element(self.documentai_object, self._page.paragraphs),
            )
        return self._paragraphs


@dataclasses.dataclass
class MathFormula(_BasePageElement):
    """Represents a wrapped documentai.Document.Page.VisualElement with type `math_formula`.
    https://cloud.google.com/document-ai/docs/process-documents-ocr#math_ocr

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page.VisualElement):
            Required. The original object.
        text (str):
            Required. The text of the MathFormula.
    """

    @property
    def hocr_bounding_box(self):
        # Math Formulas are not represented in hOCR
        return None


def _table_rows_from_documentai_table_rows(
    table_rows: List[documentai.Document.Page.Table.TableRow], text: str
) -> List[List[str]]:
    r"""Returns a list of rows from table_rows.

    Args:
        table_rows (List[documentai.Document.Page.Table.TableRow]):
            Required. A documentai.Document.Page.Table.TableRow.
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.

    Returns:
        List[List[str]]:
            A list of table rows.
    """
    return [
        [_text_from_layout(cell.layout, text).replace("\n", "") for cell in row.cells]
        for row in table_rows
    ]


def _get_hocr_bounding_box(
    element_with_layout: ElementWithLayout,
    page_dimension: documentai.Document.Page.Dimension,
) -> Optional[str]:
    r"""Returns a hOCR bounding box string.

    Args:
        element_with_layout (ElementWithLayout):
            Required. an element with layout fields.
        dimension (documentai.Document.Page.Dimension):
            Required. Page dimension.

    Returns:
        Optional[str]:
            hOCR bounding box sring.
    """
    if not element_with_layout.layout.bounding_poly:
        return None

    bbox = docai_utilities.get_bounding_box(
        bounding_poly=element_with_layout.layout.bounding_poly,
        page_dimension=page_dimension,
    )

    if not bbox:
        return None

    min_x, min_y, max_x, max_y = bbox
    return f"bbox {min_x} {min_y} {max_x} {max_y}"


def _text_from_layout(layout: documentai.Document.Page.Layout, text: str) -> str:
    r"""Returns a text from a single layout element.

    Args:
        layout (documentai.Document.Page.Layout):
            Required. an element with layout fields.
        text (str):
            Required. UTF-8 encoded text in reading order
            of the `documentai.Document` containing the layout element.

    Returns:
        str:
            Text from a single element.
    """

    # Note: `layout.text_anchor.text_segments` are indexes into the full Document text.
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document#textsegment
    return "".join(
        text[int(segment.start_index) : int(segment.end_index)]
        for segment in layout.text_anchor.text_segments
    )


def _get_children_of_element(
    element: ElementWithLayout, children: List[ElementWithLayout]
) -> List[ElementWithLayout]:
    r"""Returns a list of children inside element.

    Args:
        element (ElementWithLayout):
            Required. A element in a page.
        children (List[ElementWithLayout]):
            Required. List of wrapped children.

    Returns:
        List[ElementWithLayout]:
            A list of wrapped children that are inside a element.
    """
    start_index = element.layout.text_anchor.text_segments[0].start_index
    end_index = element.layout.text_anchor.text_segments[0].end_index

    return [
        child
        for child in children
        if child.documentai_object.layout.text_anchor.text_segments[0].start_index
        >= start_index
        if child.documentai_object.layout.text_anchor.text_segments[0].end_index
        <= end_index
    ]


def _trim_text(text: str) -> str:
    r"""Remove extra space characters from text (blank, newline, tab, etc.)

    Args:
        text (str):
            Required. UTF-8 encoded text in reading order
            from the document.
    Returns:
        str:
            Text without trailing spaces/newlines
    """
    return text.strip().replace("\n", " ")


@dataclasses.dataclass
class Page:
    """Represents a wrapped documentai.Document.Page .

    Attributes:
        documentai_object (google.cloud.documentai.Document.Page):
            Required. The original object.
        text (str):
            Required. UTF-8 encoded text of the page.
        page_number (int):
            Required. The page number of the `Page`.
        hocr_bounding_box (str):
            Required. hOCR bounding box of the page element.
        symbols (List[Symbol]):
            Optional. A list of visually detected text symbols
            (characters/letters) on the page.
        tokens (List[Token]):
            Required. A list of visually detected text tokens (words) on the
            page.
        lines (List[Line]):
            Required. A list of visually detected text lines on the
            page. A collection of tokens that a human would
            perceive as a line.
        paragraphs (List[Paragraph]):
            Required. A list of visually detected text paragraphs
            on the page. A collection of lines that a human
            would perceive as a paragraph.
        blocks (List[Block]):
            Required. A list of visually detected text blocks
            on the page. A collection of lines that a human
            would perceive as a block.
        form_fields (List[FormField]):
            Optional. A list of visually detected form fields on the
            page.
        tables (List[Table]):
            Optional. A list of visually detected tables on the
            page.
        math_formulas (List[MathFormula]):
            Optional. A list of visually detected math formulas
            on the page.
    """

    documentai_object: documentai.Document.Page = dataclasses.field(repr=False)
    _document_text: str = dataclasses.field(repr=False)

    _text: Optional[str] = dataclasses.field(init=False, repr=False, default=None)
    _page_number: Optional[int] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _form_fields: Optional[List[FormField]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _symbols: Optional[List[Symbol]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _tokens: Optional[List[Token]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _lines: Optional[List[Line]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _paragraphs: Optional[List[Paragraph]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _blocks: Optional[List[Block]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _tables: Optional[List[Table]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _math_formulas: Optional[List[MathFormula]] = dataclasses.field(
        init=False, repr=False, default=None
    )
    _hocr_bounding_box: Optional[str] = dataclasses.field(
        init=False, repr=False, default=None
    )

    def _get_elements(self, element_type: Type, attribute_name: str) -> List:
        """
        Helper method to create elements based on specified type.
        """
        elements = getattr(self.documentai_object, attribute_name)
        return [
            element_type(documentai_object=element, _page=self) for element in elements
        ]

    @property
    def text(self):
        if self._text is None:
            self._text = _text_from_layout(
                self.documentai_object.layout, text=self._document_text
            )
        return self._text

    @property
    def page_number(self):
        if self._page_number is None:
            self._page_number = self.documentai_object.page_number
        return self._page_number

    @property
    def tables(self):
        if self._tables is None:
            self._tables = self._get_elements(Table, "tables")
        return self._tables

    @property
    def form_fields(self):
        if self._form_fields is None:
            self._form_fields = self._get_elements(FormField, "form_fields")
        return self._form_fields

    @property
    def math_formulas(self):
        if self._math_formulas is None:
            self._math_formulas = [
                MathFormula(documentai_object=visual_element, _page=self)
                for visual_element in self.documentai_object.visual_elements
                if visual_element.type_ == "math_formula"
            ]
        return self._math_formulas

    @property
    def symbols(self):
        if self._symbols is None:
            self._symbols = self._get_elements(Symbol, "symbols")
        return self._symbols

    @property
    def tokens(self):
        if self._tokens is None:
            self._tokens = self._get_elements(Token, "tokens")
        return self._tokens

    @property
    def lines(self):
        if self._lines is None:
            self._lines = self._get_elements(Line, "lines")
        return self._lines

    @property
    def paragraphs(self):
        if self._paragraphs is None:
            self._paragraphs = self._get_elements(Paragraph, "paragraphs")
        return self._paragraphs

    @property
    def blocks(self):
        if self._blocks is None:
            self._blocks = self._get_elements(Block, "blocks")
        return self._blocks

    @property
    def hocr_bounding_box(self):
        if self._hocr_bounding_box is None:
            self._hocr_bounding_box = _get_hocr_bounding_box(
                element_with_layout=self.documentai_object,
                page_dimension=self.documentai_object.dimension,
            )
        return self._hocr_bounding_box
