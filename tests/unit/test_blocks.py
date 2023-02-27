from google.cloud import documentai
from google.cloud.documentai_v1.types import geometry
from google.cloud.documentai_toolbox.converters.config import blocks


def test_create():
    actual = blocks.Block.create(
        type_="test_type",
        text="test_text",
        bounding_box="",
        block_references="",
        block_id="",
        confidence="",
        page_number="",
        page_width="",
        page_height="",
        bounding_width="",
        bounding_height="",
        bounding_type="",
        bounding_unit="",
        bounding_x="",
        bounding_y="",
        docproto_width="",
        docproto_height="",
    )

    assert actual.type_ == "test_type"
    assert actual.text == "test_text"


def test_get_target_object():
    test_json_data = {
        "document": {"entities": [{}, {"text": "test_text", "type": "test_type"}]}
    }

    text = blocks._get_target_object(
        json_data=test_json_data, target_object="document.entities.1.text"
    )
    type = blocks._get_target_object(
        json_data=test_json_data, target_object="document.entities.1.type"
    )

    assert text == "test_text"
    assert type == "test_type"


def test_get_target_object_with_one_object():
    test_json_data = {"document": "document_test"}

    text = blocks._get_target_object(json_data=test_json_data, target_object="document")

    assert text == "document_test"


def test_get_target_object_without_target():
    test_json_data = {
        "document": {"entities": [{}, {"text": "test_text", "type": "test_type"}]}
    }

    text = blocks._get_target_object(
        json_data=test_json_data, target_object="entities.text"
    )

    assert text == None


def test_load_blocks_from_schema():
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

    actual = blocks.load_blocks_from_schema(
        input_data=invoice, input_schema=config, base_docproto=docproto
    )

    assert actual[0].text == "normalized 411 I.T. Group"
    assert actual[0].type_ == "BusinessName"
