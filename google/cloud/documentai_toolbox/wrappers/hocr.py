import dataclasses
from typing import List, Union
from google.cloud import documentai

from google.cloud.documentai_toolbox.constants import ElementWithLayout


def _get_bounding_box(element_with_layout: ElementWithLayout, dimensions: documentai.Document.Page.Dimension):
    if element_with_layout.layout.bounding_poly.vertices:
        min_x, min_y = element_with_layout.layout.bounding_poly.vertices[0].x, element_with_layout.layout.bounding_poly.vertices[0].y
        max_x, max_y = element_with_layout.layout.bounding_poly.vertices[2].x, element_with_layout.layout.bounding_poly.vertices[2].y
        return f"bbox {int(min_x)} {int(min_y)} {int(max_x)} {int(max_y)}"
    min_x, min_y = element_with_layout.layout.bounding_poly.normalized_vertices[0].x, element_with_layout.layout.bounding_poly.normalized_vertices[0].y
    max_x, max_y = element_with_layout.layout.bounding_poly.normalized_vertices[2].x, element_with_layout.layout.bounding_poly.normalized_vertices[2].y
    return f"bbox {int(min_x * dimensions.width)} {int(min_y * dimensions.height)} {int(max_x * dimensions.width)} {int(max_y * dimensions.height)}"


def _get_text(element_with_layout: ElementWithLayout, document_text):
    start_index = element_with_layout.layout.text_anchor.text_segments[0].start_index
    end_index = element_with_layout.layout.text_anchor.text_segments[0].end_index
    return document_text[start_index:end_index].replace('/n', '')


def _load_hocr_words(words: List[documentai.Document.Page.Token], document_text: str, dimensions: documentai.Document.Page.Dimension):
    w = []
    for word in words:
        text = _get_text(word, document_text)
        w.append(_HocrWord(text=text, documentai_word=word, dimensions=dimensions))
    else:
        return w


def _load_hocr_lines(lines: List[documentai.Document.Page.Line], page: documentai.Document.Page, document_text: str):
    l = []
    for line in lines:
        start_index = line.layout.text_anchor.text_segments[0].start_index
        end_index = line.layout.text_anchor.text_segments[0].end_index
        words = [word for word in page.tokens if word.layout.text_anchor.text_segments[0].start_index >= start_index if word.layout.text_anchor.text_segments[0].end_index <= end_index]
        l.append(_HocrLine(words=words, text=(_get_text(line, document_text)), documentai_line=line, page=page, dimensions=(page.dimension), document_text=document_text))
    else:
        return l


def _load_hocr_paragraphs(paragraphs: List[documentai.Document.Page.Paragraph], page: documentai.Document.Page, document_text: str):
    p = []
    for paragraph in paragraphs:
        start_index = paragraph.layout.text_anchor.text_segments[0].start_index
        end_index = paragraph.layout.text_anchor.text_segments[0].end_index
        lines = [line for line in page.lines if line.layout.text_anchor.text_segments[0].start_index >= start_index if line.layout.text_anchor.text_segments[0].end_index <= end_index]
        p.append(_HocrParagraph(lines=lines, page=page, dimensions=(page.dimension), document_text=document_text, documentai_paragraph=paragraph))
    else:
        return p


def _load_hocr_blocks(page: documentai.Document.Page, document_text: str):
    blocks = []
    for block in page.blocks:
        start_index = block.layout.text_anchor.text_segments[0].start_index
        end_index = block.layout.text_anchor.text_segments[0].end_index
        paragraphs = [p for p in page.paragraphs if p.layout.text_anchor.text_segments[0].start_index >= start_index if p.layout.text_anchor.text_segments[0].end_index <= end_index]
        blocks.append(_HocrBlock(paragraphs=paragraphs, page=page, dimensions=(page.dimension), document_text=document_text, documentai_block=block))
    else:
        return blocks


def _load_pages(pages: List[documentai.Document.Page], document_text: str, filename: str):
    res_pages = []
    for page in pages:
        res_pages.append(_HocrPage(documentai_page=page.documentai_page, document_text=document_text, filename=filename))

    return res_pages


@dataclasses.dataclass
class _HocrWord:
    text: str = dataclasses.field(repr=False)
    documentai_word: documentai.Document.Page.Token = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension = dataclasses.field(repr=False)
    bounding_box: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.bounding_box = _get_bounding_box(element_with_layout=(self.documentai_word), dimensions=(self.dimensions))

    def to_hocr(self, pidx: int,bidx: int, paridx: int, lidx: int, widx: int):
        f = ""
        word_text = self.text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        f += f"<span class='ocrx_word' id='word_{pidx}_{bidx}_{paridx}_{lidx}_{widx}' title='{self.bounding_box}'>{word_text}</span>\n"       
        return f


@dataclasses.dataclass
class _HocrLine:
    page: documentai.Document.Page = dataclasses.field(repr=False)
    words: List[documentai.Document.Page.Token] = dataclasses.field(repr=False)
    text: str = dataclasses.field(repr=False)
    documentai_line: str = dataclasses.field(repr=False)
    document_text: str = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension = dataclasses.field(repr=False)
    hocr_words: List[_HocrWord] = dataclasses.field(init=False, repr=False)
    bounding_box: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.hocr_words = _load_hocr_words(words=(self.words), document_text=(self.document_text), dimensions=(self.dimensions))
        self.bounding_box = _get_bounding_box(element_with_layout=(self.documentai_line), dimensions=(self.dimensions))

    def to_hocr(self, pidx: int,bidx: int, paridx: int, lidx: int):
        f = ""
        line_text = self.text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        f += f"<span class='ocr_line' id='line_{pidx}_{bidx}_{paridx}_{lidx}' title='{self.bounding_box}'>{line_text}</span>\n"      
        if self.hocr_words:
            for widx, word in enumerate(self.hocr_words):
                f += word.to_hocr(pidx=pidx, bidx=bidx, paridx=paridx, lidx=lidx, widx=widx)
        return f

@dataclasses.dataclass
class _HocrParagraph:
    page: documentai.Document.Page = dataclasses.field(repr=False)
    lines: List[documentai.Document.Page.Line] = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension = dataclasses.field(repr=False)
    document_text: str = dataclasses.field(repr=False)
    documentai_paragraph: documentai.Document.Page.Paragraph = dataclasses.field(repr=False)
    hocr_lines: List[_HocrLine] = dataclasses.field(init=False, repr=False)
    bounding_box: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.hocr_lines = _load_hocr_lines(lines=(self.lines), page=(self.page), document_text=(self.document_text))
        self.bounding_box = _get_bounding_box(element_with_layout=(self.documentai_paragraph), dimensions=(self.dimensions))

    def to_hocr(self, pidx: int,bidx: int, paridx: int):
        f = ""
        f += f"<span class='ocr_par' id='par_{pidx}_{bidx}_{paridx}' title='{self.bounding_box}'>\n"    
        if self.hocr_lines:    
            for lidx,line in enumerate(self.hocr_lines):
                f += line.to_hocr(pidx=pidx, bidx=bidx, paridx=paridx, lidx=lidx)
        f += "</span>\n"
        return f


@dataclasses.dataclass
class _HocrBlock:
    page: documentai.Document.Page = dataclasses.field(repr=False)
    paragraphs: List[documentai.Document.Page.Paragraph] = dataclasses.field(repr=False)
    dimensions: documentai.Document.Page.Dimension = dataclasses.field(repr=False)
    document_text: str = dataclasses.field(repr=False)
    documentai_block: documentai.Document.Page.Block = dataclasses.field(repr=False)
    hocr_paragraphs: List[_HocrParagraph] = dataclasses.field(init=False, repr=False)
    bounding_box: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.hocr_paragraphs = _load_hocr_paragraphs(paragraphs=(self.paragraphs), page=(self.page), document_text=(self.document_text))
        self.bounding_box = _get_bounding_box(element_with_layout=(self.documentai_block), dimensions=(self.dimensions))

    def to_hocr(self, pidx: int,bidx: int):
        f = ""
        f += f"<span class='ocr_carea' id='block_{pidx}_{bidx}' title='{self.bounding_box}'>\n"
        if self.hocr_paragraphs:
            for paridx,paragraph in enumerate(self.hocr_paragraphs):
                f += paragraph.to_hocr(pidx=pidx, bidx=bidx, paridx=paridx)
        f += "</span>\n"
        return f



@dataclasses.dataclass
class _HocrPage:
    documentai_page: documentai.Document.Page = dataclasses.field(repr=False)
    document_text: str = dataclasses.field(repr=False)
    filename: str = dataclasses.field(repr=False)

    hocr_blocks: List[_HocrBlock] = dataclasses.field(init=False, repr=False)
    bounding_box: str = dataclasses.field(init=False, repr=False)
    title: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.hocr_blocks = _load_hocr_blocks(page=(self.documentai_page), document_text=(self.document_text))
        self.bounding_box = _get_bounding_box(element_with_layout=(self.documentai_page), dimensions=(self.documentai_page.dimension))
        self.title = 'Document'
    
    def to_hocr(self, pidx: int):
        f = ""
        f += f"<div class='ocr_page' lang='unknown' title='image \"{self.filename}\";{self.bounding_box}'>\n"
        if self.hocr_blocks:
            for bidx, block in enumerate(self.hocr_blocks):
                f += block.to_hocr(pidx=pidx,bidx=bidx) 
        f += "</div>\n"
        return f



@dataclasses.dataclass
class _Hocr:
    documentai_pages: List[documentai.Document.Page] = dataclasses.field(repr=False)
    documentai_text: List[documentai.Document.Page] = dataclasses.field(repr=False)
    filename: str = dataclasses.field(repr=False)

    hocr_pages: List[_HocrPage] = dataclasses.field(init=False, repr=False)
    metadata: str = dataclasses.field(init=False, repr=False)

    def __post_init__(self):
        self.hocr_pages = _load_pages(pages=(self.documentai_pages), document_text=(self.documentai_text),filename=self.filename)

    def export_hocr(self):
        f = ""
        f += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"
        f += "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"unknown\" lang=\"unknown\">\n"
        f += "<head>\n"
        f += f"<title>{self.filename}</title>\n"
        f += "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\" />\n"
        f += "<meta name=\"ocr-system\" content=\"Document AI OCR\" />\n"
        f += "<meta name=\"ocr-langs\" content=\"unknown\" />\n"
        f += f"<meta name=\"ocr-number-of-pages\" content=\"{len(self.documentai_pages)}\" />\n"
        f += "<meta name=\"ocr-capabilities\" content=\"ocr_page ocr_carea ocr_par ocr_line ocrx_word\" />\n"
        f += "</head>\n"
        f += "<body>\n"
        for pidx,page in enumerate(self.hocr_pages):
            f += page.to_hocr(pidx=pidx)
        f += "</body>\n"
        f += "</html>\n"

        return f
