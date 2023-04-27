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

def _to_hocr(pages: List[documentai.Document.Page], document_text: str, filename: str):
    f = ""

    f += "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    f += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n"
    f += "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"unknown\" lang=\"unknown\">\n"
    f += "<head>\n"
    f += f"<title>{filename}</title>\n"
    f += "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\" />\n"
    f += "<meta name=\"ocr-system\" content=\"Document AI OCR\" />\n"
    f += "<meta name=\"ocr-langs\" content=\"unknown\" />\n"
    f += f"<meta name=\"ocr-number-of-pages\" content=\"{len(pages)}\" />\n"
    f += "<meta name=\"ocr-capabilities\" content=\"ocr_page ocr_carea ocr_par ocr_line ocrx_word\" />\n"
    f += "</head>\n"
    f += "<body>\n"

    pidx = 0
    for page in pages:
        p = page.documentai_page
        start_index = p.layout.text_anchor.text_segments[0].start_index
        end_index = p.layout.text_anchor.text_segments[0].end_index
        page_bounding_box = _get_bounding_box(object=(p), dimensions=(p.dimension))
        f += f"<div class='ocr_page' lang='unknown' title='image \"{filename}\";{page_bounding_box}'>\n"
        bidx = 0
        for b in p.blocks:
            if b.layout.text_anchor.text_segments[0].start_index >= start_index and b.layout.text_anchor.text_segments[0].end_index <= end_index:
                block_bounding_box = _get_bounding_box(object=(b), dimensions=(p.dimension))
                f += f"<span class='ocr_carea' id='block_{pidx}_{bidx}' title='{block_bounding_box}'>\n"
                paridx = 0
                for par in p.paragraphs:
                    if par.layout.text_anchor.text_segments[0].start_index >= start_index and par.layout.text_anchor.text_segments[0].end_index <= end_index:
                        paragraph_bounding_box = _get_bounding_box(object=(par), dimensions=(p.dimension))
                        f += f"<span class='ocr_par' id='par_{pidx}_{bidx}_{paridx}' title='{paragraph_bounding_box}'>\n"
                        lidx = 0
                        for l in p.lines:
                            if l.layout.text_anchor.text_segments[0].start_index >= start_index and l.layout.text_anchor.text_segments[0].end_index <= end_index:
                                line_bounding_box = _get_bounding_box(object=(l), dimensions=(p.dimension))
                                line_text = _get_text(l, document_text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                                f += f"<span class='ocr_line' id='line_{pidx}_{bidx}_{paridx}_{lidx}' title='{line_bounding_box}'>{line_text}</span>\n"
                                widx = 0
                                for t in p.tokens:
                                    if t.layout.text_anchor.text_segments[0].start_index >= start_index and t.layout.text_anchor.text_segments[0].end_index <= end_index:
                                        word_bounding_box = _get_bounding_box(object=(t), dimensions=(p.dimension))
                                        word_text = _get_text(t, document_text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                                        f += f"<span class='ocrx_word' id='word_{pidx}_{bidx}_{paridx}_{lidx}_{widx}' title='{word_bounding_box}'>{word_text}</span>\n"
                                        widx += 1
                                lidx += 1
                        paridx += 1
                bidx += 1
        pidx+=1
    return f
