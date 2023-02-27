# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

from google.cloud.documentai_toolbox.converters.config import blocks, converter_helpers
from google.cloud import documentai, storage


@mock.patch(
    "google.cloud.documentai_toolbox.converters.config.converter_helpers.documentai"
)
def test_get_base_ocr(mock_docai):
    mock_client = mock_docai.DocumentProcessorServiceClient.return_value

    mock_client.process_document.return_value.document = "Done"

    actual = converter_helpers.get_base_ocr(
        project_id="project_id",
        location="location",
        processor_id="processor_id",
        file_bytes="file",
        mime_type="application/pdf",
    )

    mock_client.process_document.assert_called()
    assert actual == "Done"


def test_get_entitiy_content():
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

    actual = converter_helpers.get_entitiy_content(blocks=b, docproto=docproto)

    assert actual[0].type == "BusinessName"
    assert actual[0].mention_text == "normalized 411 I.T. Group"


@mock.patch(
    "google.cloud.documentai_toolbox.converters.config.converter_helpers.get_base_ocr"
)
def test_convert_to_docproto_with_config(mock_ocr):
    docproto = documentai.Document()
    page = documentai.Document.Page()
    dimensions = documentai.Document.Page.Dimension()
    dimensions.width = 2550
    dimensions.height = 3300
    page.dimension = dimensions
    docproto.pages = [page]
    mock_ocr.return_value = docproto

    with open("tests/unit/resources/converters/test_type_3.json", "rb") as (f):
        invoice = f.read()
    with open("tests/unit/resources/converters/test_config_type_3.json", "rb") as (f):
        config = f.read()
    with open("tests/unit/resources/toolbox_invoice_test.pdf", "rb") as (f):
        pdf = f.read()

    actual = converter_helpers.convert_to_docproto_with_config(
        name="test_document",
        annotated_bytes=invoice,
        schema_bytes=config,
        document_bytes=pdf,
        project_id="project_id",
        processor_id="processor_id",
        location="location",
        retry_number=0,
    )

    assert len(actual.pages) == 1
    assert len(actual.entities) == 1
    assert actual.entities[0].type == "BusinessName"
    assert actual.entities[0].mention_text == "normalized 411 I.T. Group"


@mock.patch(
    "google.cloud.documentai_toolbox.converters.config.converter_helpers.get_base_ocr"
)
def test_convert_to_docproto_with_config_with_error(mock_ocr, capfd):
    mock_ocr.return_value = None

    with open("tests/unit/resources/converters/test_type_3.json", "rb") as (f):
        invoice = f.read()
    with open("tests/unit/resources/converters/test_config_type_3.json", "rb") as (f):
        config = f.read()
    with open("tests/unit/resources/toolbox_invoice_test.pdf", "rb") as (f):
        pdf = f.read()

    actual = converter_helpers.convert_to_docproto_with_config(
        name="test_document",
        annotated_bytes=invoice,
        schema_bytes=config,
        document_bytes=pdf,
        project_id="project_id",
        processor_id="processor_id",
        location="location",
        retry_number=6,
    )

    out, err = capfd.readouterr()

    assert actual == None
    assert "Could Not Convert test_document" in out


@mock.patch("google.cloud.documentai_toolbox.wrappers.document.storage")
def test_get_bytes(mock_storage):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket

    mock_blob1 = mock.Mock(name=[])
    mock_blob1.name = "gs://test-directory/1/test-annotations.json"
    mock_blob1.download_as_bytes.return_value = (
        "gs://test-directory/1/test-annotations.json"
    )

    mock_blob2 = mock.Mock(name=[])
    mock_blob2.name = "gs://test-directory/1/test-config.json"
    mock_blob2.download_as_bytes.return_value = "gs://test-directory/1/test-config.json"

    mock_blob3 = mock.Mock(name=[])
    mock_blob3.name = "gs://test-directory/1/test.pdf"
    mock_blob3.download_as_bytes.return_value = "gs://test-directory/1/test.pdf"

    client.list_blobs.return_value = [mock_blob1, mock_blob2, mock_blob3]

    actual = converter_helpers._get_bytes(
        bucket_name="bucket",
        prefix="prefix",
        annotation_file_prefix="annotations",
        config_file_prefix="config",
    )

    assert actual == [
        "gs://test-directory/1/test-annotations.json",
        "gs://test-directory/1/test.pdf",
        "gs://test-directory/1/test-config.json",
        "prefix",
        "test",
    ]


@mock.patch("google.cloud.documentai_toolbox.wrappers.document.storage")
def test_upload_file(mock_storage):
    client = mock_storage.Client.return_value

    converter_helpers._upload_file(
        bucket_name="bucket", output_prefix="prefix", file="file"
    )
    client.bucket.return_value.blob.return_value.upload_from_string.assert_called_with(
        "file", content_type="application/json"
    )


def test_get_files():
    pass


def test_get_docproto_files():
    pass


def test_upload():
    pass


def test_convert_documents_with_config():
    pass
