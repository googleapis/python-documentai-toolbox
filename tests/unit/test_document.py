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
from typing import List

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

import pytest
import glob

from google.cloud.documentai_toolbox.wrappers import document

from google.cloud import documentai
from google.cloud import storage


def _get_bytes(file_name):
    result = []
    for filename in glob.glob(os.path.join(file_name, "*.json")):
        with open(os.path.join(os.getcwd(), filename), "rb") as f:
            result.append(f.read())

    return result


def _make_blobs(
    num_blobs: int = 2, bucket: str = "gs://test-directory/documentai/output/123456789"
) -> List[storage.Blob]:
    blob_list = []
    for num in range(num_blobs):
        blob_list.append(
            storage.Blob(
                name=f"{bucket}/1/test_shard{num}.json",
                bucket=mock.Mock(),
            )
        )
    print(blob_list)

    return blob_list


print_parameters = [
    (
        _make_blobs(num_blobs=3),
        "gs://test-directory/documentai/output/123456789/1",
    ),
    (
        _make_blobs(
            num_blobs=6, bucket="gs://test-directory/documentai/output/24681012"
        ),
        "gs://test-directory/documentai/output/24681012/1",
    ),
]

test_document_param = [
    ("tests/unit/resources/0", "gs://test-directory/documentai/output/123456789/0", 1),
    ("tests/unit/resources/1", "gs://test-directory/documentai/output/123456789/1", 48),
]


@pytest.fixture
def get_bytes_mock(request):
    with mock.patch.object(document, "_get_bytes") as byte_factory:
        byte_factory.return_value = _get_bytes(request.param)
        yield byte_factory


@pytest.fixture
def get_storage_mock(request):
    with mock.patch(
        "google.cloud.documentai_toolbox.wrappers.document.storage"
    ) as mock_storage:
        client = mock_storage.Client.return_value

        mock_bucket = mock.Mock()
        mock_bucket.blob.return_value.download_as_string.return_value = "test".encode(
            "utf-8"
        )

        client.Bucket.return_value = mock_bucket

        blob_array = request.param

        client.list_blobs.return_value = blob_array

        yield mock_storage


class TestDocument:

    single_document = []
    common_params = {
        "single_get_bytes": ("get_bytes_mock", [("tests/unit/resources/0")]),
        "print_document_tree": (
            "get_storage_mock, expected",
            print_parameters,
        ),
        "single_doc_storage_mock": ("get_storage_mock", [_make_blobs()]),
        "bytes_mock": (
            "get_bytes_mock, gcs_path, expected",
            test_document_param,
        ),
    }

    def setup_method(self):
        for byte in _get_bytes("tests/unit/resources/0"):
            self.single_document.append(documentai.Document.from_json(byte))

    def test_get_shards_with_gcs_uri_contains_file_type(self):
        with pytest.raises(ValueError, match="gcs_prefix cannot contain file types"):
            document._get_shards(
                "gs://test-directory/documentai/output/123456789/0.json"
            )

    def test_get_shards_with_invalid_gcs_uri(self):
        with pytest.raises(
            ValueError, match="gcs_prefix does not match accepted format"
        ):
            document._get_shards("test-directory/documentai/output/")

    @pytest.mark.parametrize(*common_params["single_get_bytes"], indirect=True)
    def test_get_shards_with_valid_gcs_uri(self, get_bytes_mock):
        actual = document._get_shards(
            "gs://test-directory/documentai/output/123456789/0"
        )
        get_bytes_mock.called_once()
        # We are testing only one of the fields to make sure the file content could be loaded.
        assert actual[0].pages[0].page_number == 1

    def test_pages_from_shards(self):
        actual = document._pages_from_shards(shards=self.single_document)
        assert len(actual[0].paragraphs) == 31

    def test_entities_from_shard(self):
        actual = document._entities_from_shards(shards=self.single_document)
        assert actual[0].mention_text == "$140.00"
        assert actual[0].type_ == "vat"

    @pytest.mark.parametrize(*common_params["bytes_mock"], indirect=["get_bytes_mock"])
    def test_document(self, get_bytes_mock, gcs_path, expected):
        actual = document.Document(gcs_path)
        get_bytes_mock.assert_called_once()
        assert len(actual.pages) == expected

    @pytest.mark.parametrize(
        *common_params["single_doc_storage_mock"], indirect=["get_storage_mock"]
    )
    def test_get_bytes(self, get_storage_mock):
        actual = document._get_bytes(
            "gs://test-directory/documentai/", "output/123456789/1"
        )
        get_storage_mock.Client.assert_called_once()
        assert actual == [b"", b""]

    @pytest.mark.parametrize(
        *common_params["print_document_tree"],
        indirect=["get_storage_mock"],
    )
    def test_print_gcs_document_tree(self, capfd, get_storage_mock, expected):
        document.print_gcs_document_tree(
            "gs://test-directory/documentai/output/123456789/1"
        )
        get_storage_mock.Client.assert_called_once()
        out, err = capfd.readouterr()
        assert expected in out

    def test_print_gcs_document_tree_with_gcs_uri_contains_file_type(self):
        with pytest.raises(ValueError, match="gcs_prefix cannot contain file types"):
            document.print_gcs_document_tree(
                "gs://test-directory/documentai/output/123456789/1/test_file.json"
            )

    def test_print_gcs_document_tree_with_invalid_gcs_uri(self):
        with pytest.raises(
            ValueError, match="gcs_prefix does not match accepted format"
        ):
            document.print_gcs_document_tree("documentai/output/123456789/1")

    @pytest.mark.parametrize(*common_params["single_get_bytes"], indirect=True)
    def test_search_page_with_target_string(self, get_bytes_mock):

        doc = document.Document("gs://test-directory/documentai/output/123456789/0")

        actual_string = doc.search_pages(target_string="contract")

        get_bytes_mock.assert_called_once()
        assert len(actual_string) == 1

    @pytest.mark.parametrize(*common_params["single_get_bytes"], indirect=True)
    def test_search_page_with_target_pattern(self, get_bytes_mock):
        doc = document.Document("gs://test-directory/documentai/output/123456789/0")

        actual_regex = doc.search_pages(pattern=r"\$\d+(?:\.\d+)?")

        get_bytes_mock.assert_called_once()
        assert len(actual_regex) == 1

    @pytest.mark.parametrize(*common_params["single_get_bytes"], indirect=True)
    def test_search_page_with_regex_and_str(self, get_bytes_mock):
        with pytest.raises(
            ValueError,
            match="Exactly one of target_string and pattern must be specified.",
        ):

            doc = document.Document("gs://test-directory/documentai/output/123456789/0")
            doc.search_pages(
                pattern=r"^\$?(\d*(\d\.?|\.\d{1,2}))$", target_string="hello"
            )

            get_bytes_mock.assert_called_once()

    @pytest.mark.parametrize(*common_params["single_get_bytes"], indirect=True)
    def test_search_page_with_none(self, get_bytes_mock):
        with pytest.raises(
            ValueError,
            match="Exactly one of target_string and pattern must be specified.",
        ):
            doc = document.Document("gs://test-directory/documentai/output/123456789/0")
            doc.search_pages()

            get_bytes_mock.assert_called_once()

    @pytest.mark.parametrize(*common_params["single_get_bytes"], indirect=True)
    def test_get_entity_by_type(self, get_bytes_mock):

        doc = document.Document("gs://test-directory/documentai/output/123456789/0")

        actual = doc.get_entity_by_type(target_type="receiver_address")

        get_bytes_mock.assert_called_once()

        assert len(actual) == 1
        assert actual[0].type_ == "receiver_address"
        assert actual[0].mention_text == "222 Main Street\nAnytown, USA"
