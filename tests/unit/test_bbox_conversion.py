from google.cloud import documentai
from google.cloud.documentai_v1.types import geometry
from google.cloud.documentai_toolbox.converters.config import bbox_conversion, blocks


def test_midpoint_in_bpoly():
    box_a = geometry.BoundingPoly()
    vertex_a = geometry.NormalizedVertex()
    vertex_a.x = 2
    vertex_a.y = 2
    box_a.normalized_vertices = [vertex_a]
    box_b = geometry.BoundingPoly()
    vertex_b = geometry.NormalizedVertex()
    vertex_b.x = 1
    vertex_b.y = 1
    vertex_b_max = geometry.NormalizedVertex()
    vertex_b_max.x = 4
    vertex_b_max.y = 4
    box_b.normalized_vertices = [vertex_b, vertex_b_max]
    actual = bbox_conversion._midpoint_in_bpoly(box_a=box_a, box_b=box_b)
    assert actual


def test_merge_text_anchors():
    text_anchor_1 = documentai.Document.TextAnchor()
    text_segment_1 = documentai.Document.TextAnchor.TextSegment()
    text_segment_1.start_index = "0"
    text_segment_1.end_index = "100"
    text_anchor_1.text_segments = [text_segment_1]
    text_anchor_2 = documentai.Document.TextAnchor()
    text_segment_2 = documentai.Document.TextAnchor.TextSegment()
    text_segment_2.start_index = "100"
    text_segment_2.end_index = "200"
    text_anchor_2.text_segments = [text_segment_2]
    expected = documentai.Document.TextAnchor()
    text_segment_3 = documentai.Document.TextAnchor.TextSegment()
    text_segment_3.start_index = "0"
    text_segment_3.end_index = "200"
    expected.text_segments = [text_segment_3]
    actual = bbox_conversion._merge_text_anchors(
        text_anchor_1=text_anchor_1, text_anchor_2=text_anchor_2
    )
    assert actual == expected


def test_get_text_anchor_in_bbox():
    box_a = geometry.BoundingPoly()
    vertex_a = geometry.NormalizedVertex()
    vertex_a.x = 2
    vertex_a.y = 2
    vertex_a_max = geometry.NormalizedVertex()
    vertex_a_max.x = 5
    vertex_a_max.y = 5
    box_a.normalized_vertices = [vertex_a, vertex_a_max]
    box_b = geometry.BoundingPoly()
    vertex_b = geometry.NormalizedVertex()
    vertex_b.x = 1
    vertex_b.y = 1
    vertex_b_max = geometry.NormalizedVertex()
    vertex_b_max.x = 8
    vertex_b_max.y = 8
    box_b.normalized_vertices = [vertex_b, vertex_b_max]
    text_anchor_1 = documentai.Document.TextAnchor()
    text_segment_1 = documentai.Document.TextAnchor.TextSegment()
    text_segment_1.start_index = "0"
    text_segment_1.end_index = "100"
    text_anchor_1.text_segments = [text_segment_1]
    text_anchor_2 = documentai.Document.TextAnchor()
    text_segment_2 = documentai.Document.TextAnchor.TextSegment()
    text_segment_2.start_index = "100"
    text_segment_2.end_index = "200"
    text_anchor_2.text_segments = [text_segment_2]
    page = documentai.Document.Page()
    token1 = documentai.Document.Page.Token()
    token2 = documentai.Document.Page.Token()
    layout1 = documentai.Document.Page.Layout()
    layout1.bounding_poly = box_b
    layout1.text_anchor = text_anchor_1
    layout2 = documentai.Document.Page.Layout()
    layout2.bounding_poly = box_b
    layout2.text_anchor = text_anchor_2
    token1.layout = layout1
    token2.layout = layout2
    page.tokens = [token1, token2]
    actual = bbox_conversion._get_text_anchor_in_bbox(bbox=box_a, page=page)
    expected = documentai.Document.TextAnchor()
    text_segment_3 = documentai.Document.TextAnchor.TextSegment()
    text_segment_3.start_index = "0"
    text_segment_3.end_index = "200"
    expected.text_segments = [text_segment_3]
    assert actual == expected


def test_get_norm_x_max():
    bbox = geometry.BoundingPoly()
    vertex_a_min = geometry.NormalizedVertex()
    vertex_a_min.x = 2
    vertex_a_min.y = 2
    vertex_a_max = geometry.NormalizedVertex()
    vertex_a_max.x = 4
    vertex_a_max.y = 4
    bbox.normalized_vertices = [vertex_a_min, vertex_a_max]
    actual = bbox_conversion._get_norm_x_max(bbox=bbox)
    assert actual == 4


def test_get_norm_x_min():
    bbox = geometry.BoundingPoly()
    vertex_a_min = geometry.NormalizedVertex()
    vertex_a_min.x = 2
    vertex_a_min.y = 2
    vertex_a_max = geometry.NormalizedVertex()
    vertex_a_max.x = 4
    vertex_a_max.y = 4
    bbox.normalized_vertices = [vertex_a_min, vertex_a_max]
    actual = bbox_conversion._get_norm_x_min(bbox=bbox)
    assert actual == 2


def test_get_norm_y_max():
    bbox = geometry.BoundingPoly()
    vertex_a_min = geometry.NormalizedVertex()
    vertex_a_min.x = 2
    vertex_a_min.y = 2
    vertex_a_max = geometry.NormalizedVertex()
    vertex_a_max.x = 4
    vertex_a_max.y = 4
    bbox.normalized_vertices = [vertex_a_min, vertex_a_max]
    actual = bbox_conversion._get_norm_y_min(bbox=bbox)
    assert actual == 2


def test_get_norm_y_min():
    bbox = geometry.BoundingPoly()
    vertex_a_min = geometry.NormalizedVertex()
    vertex_a_min.x = 2
    vertex_a_min.y = 2
    vertex_a_max = geometry.NormalizedVertex()
    vertex_a_max.x = 4
    vertex_a_max.y = 4
    bbox.normalized_vertices = [vertex_a_min, vertex_a_max]
    actual = bbox_conversion._get_norm_y_max(bbox=bbox)
    assert actual == 4


def test_normalize_coordinates():
    actual = bbox_conversion._normalize_coordinates(x=4.0, y=2.0)
    assert actual == 2.0


def test_convert_to_pixels():
    actual = bbox_conversion._convert_to_pixels(x=1, conversion_rate=96)
    assert actual == 96


def test_convert_bbox_units_with_normalized():
    actual = bbox_conversion._convert_bbox_units(
        coordinate=0.5, input_bbox_units="normalized", width=2550, height=3300
    )
    assert actual == 0.5


def test_convert_bbox_units_with_pxl():
    actual = bbox_conversion._convert_bbox_units(
        coordinate=1, input_bbox_units="pxl", width=2550, height=3300
    )
    assert actual == 0.000392157


def test_convert_bbox_units_with_inch():
    actual = bbox_conversion._convert_bbox_units(
        coordinate=1, input_bbox_units="inch", width=2550, height=3300
    )
    assert actual == 0.037647059


def test_convert_bbox_units_with_cm():
    actual = bbox_conversion._convert_bbox_units(
        coordinate=1, input_bbox_units="cm", width=2550, height=3300
    )
    assert actual == 0.014821569


def test_get_multiplier_pxl():
    actual = bbox_conversion._get_multiplier(
        docproto_x=1000, y=1000, input_bbox_units="pxl"
    )
    assert actual == 1.0


def test_get_multiplier_inch():
    actual = bbox_conversion._get_multiplier(
        docproto_x=1000, y=10.416, input_bbox_units="inch"
    )
    assert actual == 1.000064004096262


def test_get_multiplier_cm():
    actual = bbox_conversion._get_multiplier(
        docproto_x=1000, y=26.4585, input_bbox_units="cm"
    )
    assert actual == 1.000000992500985


def test_convert_bbox_to_docproto_bbox_empty_coordinate():
    docproto = documentai.Document()
    page = documentai.Document.Page()
    dimensions = documentai.Document.Page.Dimension()
    dimensions.width = 2550
    dimensions.height = 3300
    page.dimension = dimensions
    docproto.pages = [page]
    with open("tests/unit/resources/converters/test_type_1.json", "r") as (f):
        invoice = f.read()
    with open("tests/unit/resources/converters/test_config_type_1.json", "r") as (f):
        config = f.read()
    b = blocks.load_blocks_from_schema(
        input_data=invoice, input_schema=config, base_docproto=docproto
    )
    b[0].bounding_box = []

    actual = bbox_conversion._convert_bbox_to_docproto_bbox(block=(b[0]))

    assert actual == []


def test_convert_bbox_to_docproto_bbox_type_1():
    docproto = documentai.Document()
    page = documentai.Document.Page()
    dimensions = documentai.Document.Page.Dimension()
    dimensions.width = 2550
    dimensions.height = 3300
    page.dimension = dimensions
    docproto.pages = [page]
    with open("tests/unit/resources/converters/test_type_1.json", "r") as (f):
        invoice = f.read()
    with open("tests/unit/resources/converters/test_config_type_1.json", "r") as (f):
        config = f.read()
    b = blocks.load_blocks_from_schema(
        input_data=invoice, input_schema=config, base_docproto=docproto
    )
    actual = bbox_conversion._convert_bbox_to_docproto_bbox(block=(b[0]))

    assert actual.normalized_vertices != []
    assert actual.vertices == []
    assert "x" in str(actual.normalized_vertices)
    assert "y" in str(actual.normalized_vertices)


def test_convert_bbox_to_docproto_bbox_type_2():
    docproto = documentai.Document()
    page = documentai.Document.Page()
    dimensions = documentai.Document.Page.Dimension()
    dimensions.width = 2550
    dimensions.height = 3300
    page.dimension = dimensions
    docproto.pages = [page]
    with open("tests/unit/resources/converters/test_type_2.json", "r") as (f):
        invoice = f.read()
    with open("tests/unit/resources/converters/test_config_type_2.json", "r") as (f):
        config = f.read()
    b = blocks.load_blocks_from_schema(
        input_data=invoice, input_schema=config, base_docproto=docproto
    )
    actual = bbox_conversion._convert_bbox_to_docproto_bbox(block=(b[0]))

    assert actual.normalized_vertices != []
    assert actual.vertices == []
    assert "x" in str(actual.normalized_vertices)
    assert "y" in str(actual.normalized_vertices)


def test_convert_bbox_to_docproto_bbox_type_3():
    docproto = documentai.Document()
    page = documentai.Document.Page()
    dimensions = documentai.Document.Page.Dimension()
    dimensions.width = 2550
    dimensions.height = 3300
    page.dimension = dimensions
    docproto.pages = [page]
    with open("tests/unit/resources/converters/test_type_3.json", "r") as (f):
        invoice = f.read()
    with open("tests/unit/resources/converters/test_config_type_3.json", "r") as (f):
        config = f.read()
    b = blocks.load_blocks_from_schema(
        input_data=invoice, input_schema=config, base_docproto=docproto
    )

    print(b[0].bounding_type)

    actual = bbox_conversion._convert_bbox_to_docproto_bbox(block=(b[0]))

    assert actual.normalized_vertices != []
    assert actual.vertices == []
    assert "x" in str(actual.normalized_vertices)
    assert "y" in str(actual.normalized_vertices)
