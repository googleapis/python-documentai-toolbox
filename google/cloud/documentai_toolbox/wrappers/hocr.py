# uncompyle6 version 3.9.0
# Python bytecode version base 3.8.0 (3413)
# Decompiled from: Python 3.8.13 (default, Aug  2 2022, 12:17:31) 
# [Clang 13.1.6 (clang-1316.0.21.2.5)]
# Embedded file name: /Users/galzahavi/Documents/GitHub/gal/python-documentai-toolbox/google/cloud/documentai_toolbox/wrappers/hocr_document.py
# Compiled at: 2023-04-05 14:28:21
# Size of source mod 2**32: 10917 bytes
import dataclasses
from typing import List, Union
from google.cloud import documentai

ElementWithLayout = Union[(
 documentai.Document.Page.Paragraph,
 documentai.Document.Page,
 documentai.Document.Page.Token,
 documentai.Document.Page.Block,
 documentai.Document.Page.Line)]

def _get_bounding_box(object: ElementWithLayout, dimensions: documentai.Document.Page.Dimension):
    if object.layout.bounding_poly.vertices:
        min_x, min_y = object.layout.bounding_poly.vertices[0].x, object.layout.bounding_poly.vertices[0].y
        max_x, max_y = object.layout.bounding_poly.vertices[2].x, object.layout.bounding_poly.vertices[2].y
        return f"bbox {int(min_x)} {int(min_y)} {int(max_x)} {int(max_y)}"
    min_x, min_y = object.layout.bounding_poly.normalized_vertices[0].x, object.layout.bounding_poly.normalized_vertices[0].y
    max_x, max_y = object.layout.bounding_poly.normalized_vertices[2].x, object.layout.bounding_poly.normalized_vertices[2].y
    return f"bbox {int(min_x * dimensions.width)} {int(min_y * dimensions.height)} {int(max_x * dimensions.width)} {int(max_y * dimensions.height)}"


def _get_text(object: ElementWithLayout, document_text):
    start_index = object.layout.text_anchor.text_segments[0].start_index
    end_index = object.layout.text_anchor.text_segments[0].end_index
    return document_text[start_index:end_index].replace('/n', '')


def _load_hocr_words(words: List[documentai.Document.Page.Token], document_text: str, dimensions: documentai.Document.Page.Dimension):
    w = []
    for word in words:
        text = _get_text(word, document_text)
        w.append(hOCR_Word(text=text, documentai_word=word, dimensions=dimensions))
    else:
        return w


def _load_hocr_lines(lines: List[documentai.Document.Page.Line], page: documentai.Document.Page, document_text: str):
    l = []
    for line in lines:
        start_index = line.layout.text_anchor.text_segments[0].start_index
        end_index = line.layout.text_anchor.text_segments[0].end_index
        words = [word for word in page.tokens if word.layout.text_anchor.text_segments[0].start_index >= start_index if word.layout.text_anchor.text_segments[0].end_index <= end_index]
        l.append(hOCR_Line(words=words, text=(_get_text(line, document_text)), documentai_line=line, page=page, dimensions=(page.dimension), document_text=document_text))
    else:
        return l


def _load_hocr_paragraphs(paragraphs: List[documentai.Document.Page.Paragraph], page: documentai.Document.Page, document_text: str):
    p = []
    for paragraph in paragraphs:
        start_index = paragraph.layout.text_anchor.text_segments[0].start_index
        end_index = paragraph.layout.text_anchor.text_segments[0].end_index
        lines = [line for line in page.lines if line.layout.text_anchor.text_segments[0].start_index >= start_index if line.layout.text_anchor.text_segments[0].end_index <= end_index]
        p.append(hOCR_Paragraph(lines=lines, page=page, dimensions=(page.dimension), document_text=document_text, documentai_paragraph=paragraph))
    else:
        return p


def _load_hocr_blocks(page: documentai.Document.Page, document_text: str):
    blocks = []
    for block in page.blocks:
        start_index = block.layout.text_anchor.text_segments[0].start_index
        end_index = block.layout.text_anchor.text_segments[0].end_index
        paragraphs = [p for p in page.paragraphs if p.layout.text_anchor.text_segments[0].start_index >= start_index if p.layout.text_anchor.text_segments[0].end_index <= end_index]
        blocks.append(hOCR_Block(paragraphs=paragraphs, page=page, dimensions=(page.dimension), id=1, document_text=document_text, documentai_block=block))
    else:
        return blocks


def _load_pages(pages: List[documentai.Document.Page], document_text: str):
    res_pages = []
    for page in pages:
        res_pages.append(hOCR_Page(documentai_page=(page.documentai_page), document_text=document_text))
    else:
        return res_pages


@dataclasses.dataclass
class hOCR_Word:
    text = dataclasses.field(repr=False)
    text: str
    documentai_word = dataclasses.field(repr=False)
    documentai_word: documentai.Document.Page.Token
    dimensions = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension
    bounding_box = dataclasses.field(init=False, repr=False)
    bounding_box: str
    id = dataclasses.field(init=False, repr=False)
    id: str

    def __post_init__(self):
        self.bounding_box = _get_bounding_box(object=(self.documentai_word), dimensions=(self.dimensions))


@dataclasses.dataclass
class hOCR_Line:
    page = dataclasses.field(repr=False)
    page: documentai.Document.Page
    words = dataclasses.field(repr=False)
    words: List[documentai.Document.Page.Token]
    text = dataclasses.field(repr=False)
    text: str
    documentai_line = dataclasses.field(repr=False)
    documentai_line: str
    document_text = dataclasses.field(repr=False)
    document_text: str
    dimensions = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension
    hocr_words = dataclasses.field(init=False, repr=False)
    hocr_words: List[hOCR_Word]
    bounding_box = dataclasses.field(init=False, repr=False)
    bounding_box: str
    id = dataclasses.field(init=False, repr=False)
    id: str

    def __post_init__(self):
        self.hocr_words = _load_hocr_words(words=(self.words), document_text=(self.document_text), dimensions=(self.dimensions))
        self.bounding_box = _get_bounding_box(object=(self.documentai_line), dimensions=(self.dimensions))


@dataclasses.dataclass
class hOCR_Paragraph:
    page = dataclasses.field(repr=False)
    page: documentai.Document.Page
    lines = dataclasses.field(repr=False)
    lines: List[documentai.Document.Page.Line]
    dimensions = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension
    document_text = dataclasses.field(repr=False)
    document_text: str
    documentai_paragraph = dataclasses.field(repr=False)
    documentai_paragraph: documentai.Document.Page.Paragraph
    hocr_lines = dataclasses.field(init=False, repr=False)
    hocr_lines: List[hOCR_Line]
    bounding_box = dataclasses.field(init=False, repr=False)
    bounding_box: str
    id = dataclasses.field(init=False, repr=False)
    id: str

    def __post_init__(self):
        self.hocr_lines = _load_hocr_lines(lines=(self.lines), page=(self.page), document_text=(self.document_text))
        self.bounding_box = _get_bounding_box(object=(self.documentai_paragraph), dimensions=(self.dimensions))


@dataclasses.dataclass
class hOCR_Block:
    page = dataclasses.field(repr=False)
    page: documentai.Document.Page
    paragraphs = dataclasses.field(repr=False)
    paragraphs: List[documentai.Document.Page.Paragraph]
    dimensions = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension
    document_text = dataclasses.field(repr=False)
    document_text: str
    documentai_block = dataclasses.field(repr=False)
    documentai_block: documentai.Document.Page.Block
    id = dataclasses.field(repr=False)
    id: str
    hocr_paragraphs = dataclasses.field(init=False, repr=False)
    hocr_paragraphs: List[hOCR_Paragraph]
    bounding_box = dataclasses.field(init=False, repr=False)
    bounding_box: str

    def __post_init__(self):
        self.hocr_paragraphs = _load_hocr_paragraphs(paragraphs=(self.paragraphs), page=(self.page), document_text=(self.document_text))
        self.bounding_box = _get_bounding_box(object=(self.documentai_block), dimensions=(self.dimensions))


@dataclasses.dataclass
class hOCR_Page:
    documentai_page = dataclasses.field(repr=False)
    documentai_page: documentai.Document.Page
    document_text = dataclasses.field(repr=False)
    document_text: str
    hocr_blocks = dataclasses.field(init=False, repr=False)
    hocr_blocks: List[hOCR_Block]
    bounding_box = dataclasses.field(init=False, repr=False)
    bounding_box: str
    title = dataclasses.field(init=False, repr=False)
    title: str
    id = dataclasses.field(init=False, repr=False)
    id: str

    def __post_init__(self):
        self.hocr_blocks = _load_hocr_blocks(page=(self.documentai_page), document_text=(self.document_text))
        self.bounding_box = _get_bounding_box(object=(self.documentai_page), dimensions=(self.documentai_page.dimension))
        self.title = 'Document'


@dataclasses.dataclass
class hOCR:
    documentai_pages: List[documentai.Document.Page] = dataclasses.field(repr=False)
    documentai_text: List[documentai.Document.Page] = dataclasses.field(repr=False)
    filename: str = dataclasses.field(repr=False)

    hocr_pages: List[hOCR_Page] = dataclasses.field(init=False, repr=False)
    metadata: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.hocr_pages = _load_pages(pages=(self.documentai_pages), document_text=(self.documentai_text))

    def export_hocr(cls):
        f = ""
        f += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"
        f += "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"unknown\" lang=\"unknown\">\n"
        f += "<head>\n"
        f += f"<title>{cls.filename}</title>\n"
        f += "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\" />\n"
        f += "<meta name=\"ocr-system\" content=\"Document AI OCR\" />\n"
        f += "<meta name=\"ocr-langs\" content=\"unknown\" />\n"
        f += f"<meta name=\"ocr-number-of-pages\" content=\"{len(cls.documentai_pages)}\" />\n"
        f += "<meta name=\"ocr-capabilities\" content=\"ocr_page ocr_carea ocr_par ocr_line ocrx_word\" />\n"
        f += "</head>\n"
        f += "<body>\n"
        for pidx,page in enumerate(cls.hocr_pages):
            f += f"<div class='ocr_page' lang='unknown' title='image \"{cls.filename}\";{page.bounding_box}'>\n"
            for bidx,block in enumerate(page.hocr_blocks):
                f += f"<span class='ocr_carea' id='block_{pidx}_{bidx}' title='{block.bounding_box}'>\n"
                for paridx, paragraph in enumerate(block.hocr_paragraphs):
                    f += f"<span class='ocr_par' id='par_{pidx}_{bidx}_{paridx}' title='{paragraph.bounding_box}'>\n"
                    for lidx, line in enumerate(paragraph.hocr_lines):
                        line_text = line.text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        f += f"<span class='ocr_line' id='line_{pidx}_{bidx}_{paridx}_{lidx}' title='{line.bounding_box}'>{line_text}</span>\n"
                        for widx, word in enumerate(line.hocr_words):
                            word_text = word.text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                            f += f"<span class='ocrx_word' id='word_{pidx}_{bidx}_{paridx}_{lidx}_{widx}' title='{word.bounding_box}'>{word_text}</span>\n"
                    f += "</span>\n"
                f += "</span>\n"
            f += "</div>\n"
        f += "</body>\n"
        f += "</html>\n"

        return f
