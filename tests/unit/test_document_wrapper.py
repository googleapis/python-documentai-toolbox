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

import os

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

import pytest
import glob

from google.cloud.documentai_toolbox.wrappers import DocumentWrapper, document_wrapper

from google.cloud import documentai
from google.cloud import storage


def get_bytes(file_name):
    result = []
    for filename in glob.glob(os.path.join(file_name, "*.json")):
        with open(os.path.join(os.getcwd(), filename), "rb") as f:
            result.append(f.read())

    return result


def test_get_shards_with_gcs_uri_contains_file_type():
    with pytest.raises(ValueError, match="gcs_prefix cannot contain file types"):
        document_wrapper._get_shards(
            "gs://test-directory/documentai/output/123456789/0.json"
        )


def test_get_shards_with_invalid_gcs_uri():
    with pytest.raises(ValueError, match="gcs_prefix does not match accepted format"):
        document_wrapper._get_shards("test-directory/documentai/output/")


def test_get_shards_with_valid_gcs_uri():
    with mock.patch.object(document_wrapper, "_get_bytes") as factory:
        factory.return_value = get_bytes("tests/unit/resources/0")
        actual = document_wrapper._get_shards(
            "gs://test-directory/documentai/output/123456789/0"
        )
        # We are testing only one of the fields to make sure the file content could be loaded.
        assert actual[0].pages[0].page_number == 1


def test_pages_from_shards():
    shards = []
    for byte in get_bytes("tests/unit/resources/0"):
        shards.append(documentai.Document.from_json(byte))

    actual = document_wrapper._pages_from_shards(shards=shards)
    assert len(actual[0].paragraphs) == 31


def test_entities_from_shard():
    shards = []
    for byte in get_bytes("tests/unit/resources/0"):
        shards.append(documentai.Document.from_json(byte))

    actual = document_wrapper._entities_from_shards(shards=shards)

    assert actual[0].mention_text == "$140.00"
    assert actual[0].type_ == "vat"


def test_document_wrapper_with_single_shard():
    with mock.patch.object(document_wrapper, "_get_bytes") as factory:
        factory.return_value = get_bytes("tests/unit/resources/0")
        actual = DocumentWrapper("gs://test-directory/documentai/output/123456789/0")
        assert len(actual.pages) == 1


def test_document_wrapper_with_multiple_shards():
    with mock.patch.object(document_wrapper, "_get_bytes") as factory:
        factory.return_value = get_bytes("tests/unit/resources/1")
        actual = DocumentWrapper("gs://test-directory/documentai/output/123456789/1")
        assert len(actual.pages) == 48


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_wrapper.storage")
def test_get_bytes(mock_storage):

    client = mock_storage.Client.return_value

    mock_bucket = mock.Mock()
    mock_bucket.blob.return_value.download_as_string.return_value = "test".encode(
        "utf-8"
    )

    client.Bucket.return_value = mock_bucket

    blobs = [
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard1.json",
            bucket=mock_bucket,
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard2.json",
            bucket=mock_bucket,
        ),
    ]

    client.list_blobs.return_value = blobs

    actual = document_wrapper._get_bytes(
        "gs://test-directory/documentai/", "output/123456789/1"
    )
    mock_storage.Client.assert_called_once()

    assert actual == [b"", b""]


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_wrapper.storage")
def test_print_gcs_document_tree_with_3_documents(mock_storage, capfd):

    client = mock_storage.Client.return_value

    mock_bucket = mock.Mock()

    client.Bucket.return_value = mock_bucket

    blobs = [
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard1.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard2.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard3.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
    ]

    client.list_blobs.return_value = blobs

    document_wrapper.print_gcs_document_tree(
        "gs://test-directory/documentai/output/123456789/1"
    )

    mock_storage.Client.assert_called_once()

    out, err = capfd.readouterr()
    assert (
        out
        == """gs://test-directory/documentai/output/123456789/1
├──test_shard1.json
├──test_shard2.json
└──test_shard3.json\n\n"""
    )


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_wrapper.storage")
def test_print_gcs_document_tree_with_more_than_5_document(mock_storage, capfd):

    client = mock_storage.Client.return_value

    mock_bucket = mock.Mock()

    client.Bucket.return_value = mock_bucket

    blobs = [
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard1.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard2.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard3.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard4.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard5.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard6.json",
            bucket="gs://test-directory/documentai/output/123456789/1",
        ),
    ]
    client.list_blobs.return_value = blobs

    document_wrapper.print_gcs_document_tree(
        "gs://test-directory/documentai/output/123456789/1"
    )

    mock_storage.Client.assert_called_once()

    out, err = capfd.readouterr()
    assert (
        out
        == """gs://test-directory/documentai/output/123456789/1
├──test_shard1.json
├──test_shard2.json
├──test_shard3.json
├──test_shard4.json
├──test_shard5.json
│  ....
└──test_shard6.json\n\n"""
    )


def test_print_gcs_document_tree_with_gcs_uri_contains_file_type():
    with pytest.raises(ValueError, match="gcs_prefix cannot contain file types"):
        document_wrapper.print_gcs_document_tree(
            "gs://test-directory/documentai/output/123456789/1/test_file.json"
        )


def test_print_gcs_document_tree_with_invalid_gcs_uri():
    with pytest.raises(ValueError, match="gcs_prefix does not match accepted format"):
        document_wrapper.print_gcs_document_tree("documentai/output/123456789/1")


def test_search_page_with_target_string():
    with mock.patch.object(document_wrapper, "_get_bytes") as factory:
        factory.return_value = get_bytes("tests/unit/resources/0")
        document = DocumentWrapper("gs://test-directory/documentai/output/123456789/0")

        actual_string = document.search_pages(target_string="contract")
        actual_regex = document.search_pages(regex=r"\$\d+(?:\.\d+)?")

        assert len(actual_string) == 1
        assert len(actual_regex) == 1


def test_search_page_with_regex_and_str():
    with pytest.raises(
        ValueError,
        match="You can only search with one target either target_string or regex",
    ):
        with mock.patch.object(document_wrapper, "_get_bytes") as factory:
            factory.return_value = get_bytes("tests/unit/resources/0")
            document = DocumentWrapper(
                "gs://test-directory/documentai/output/123456789/0"
            )
            document.search_pages(
                regex=r"^\$?(\d*(\d\.?|\.\d{1,2}))$", target_string="hello"
            )


def test_search_page_with_none():
    with pytest.raises(
        ValueError,
        match="Both target_string or regex cannot be None",
    ):
        with mock.patch.object(document_wrapper, "_get_bytes") as factory:
            factory.return_value = get_bytes("tests/unit/resources/0")
            document = DocumentWrapper(
                "gs://test-directory/documentai/output/123456789/0"
            )
            document.search_pages()


def test_get_entity_if_type_contains():
    with mock.patch.object(document_wrapper, "_get_bytes") as factory:
        factory.return_value = get_bytes("tests/unit/resources/0")
        document = DocumentWrapper("gs://test-directory/documentai/output/123456789/0")

        actual = document.get_entity_if_type_contains(target_type="address")

        assert len(actual) == 2
        assert actual[0].type_ == "receiver_address"
        assert actual[0].mention_text == "222 Main Street\nAnytown, USA"
