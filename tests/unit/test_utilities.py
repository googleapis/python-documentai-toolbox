# pylint: disable=protected-access
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

import pytest

from google.cloud.documentai_toolbox.utilities import utilities

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

import pytest

test_bucket = "test-directory"
test_prefix = "documentai/input"


@mock.patch("google.cloud.documentai_toolbox.wrappers.document.storage")
def test_create_batches_with_3_documents(mock_storage, capfd):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket

    mock_blobs = []
    for i in range(3):
        mock_blob = mock.Mock(name=f"test_file{i}.pdf")
        mock_blob.content_type = mock.PropertyMock(return_value="application/pdf")
        mock_blob.size = mock.PropertyMock(return_value=1024)
        mock_blob.endswith.return_value = False
        mock_blobs.append(mock_blob)
    client.list_blobs.return_value = mock_blobs

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert out == ""
    assert len(actual) == 1
    assert len(actual[0].gcs_documents.documents) == 3


def test_create_batches_with_invalid_batch_size(capfd):
    with pytest.raises(ValueError):
        utilities.create_batches(
            gcs_bucket_name=test_bucket, gcs_prefix=test_prefix, batch_size=51
        )

        out, err = capfd.readouterr()
        assert "Batch size must be less than" in out
        assert err


@mock.patch("google.cloud.documentai_toolbox.wrappers.document.storage")
def test_create_batches_with_large_folder(mock_storage, capfd):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket

    mock_blobs = []
    for i in range(96):
        mock_blob = mock.Mock(name=f"test_file{i}.pdf")
        mock_blob.content_type = mock.PropertyMock(return_value="application/pdf")
        mock_blob.size = mock.PropertyMock(return_value=1024)
        mock_blob.endswith.return_value = False
        mock_blobs.append(mock_blob)
    client.list_blobs.return_value = mock_blobs

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert out == ""
    assert len(actual) == 2
    assert len(actual[0].gcs_documents.documents) == 50
    assert len(actual[1].gcs_documents.documents) == 46


@mock.patch("google.cloud.documentai_toolbox.wrappers.document.storage")
def test_create_batches_with_invalid_file_type(mock_storage, capfd):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket

    mock_blob = mock.Mock(name=f"test_file.json")
    mock_blob.content_type = mock.PropertyMock(return_value="application/json")
    mock_blob.size = mock.PropertyMock(return_value=1024)
    mock_blob.endswith.return_value = False
    client.list_blobs.return_value = [mock_blob]

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert "Invalid Mime Type" in out
    assert actual == []


@mock.patch("google.cloud.documentai_toolbox.wrappers.document.storage")
def test_create_batches_with_large_file(mock_storage, capfd):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket

    mock_blob = mock.Mock(name=f"test_file.pdf")
    mock_blob.content_type = mock.PropertyMock(return_value="application/pdf")
    mock_blob.size = mock.PropertyMock(return_value=2073741824)
    mock_blob.endswith.return_value = False
    client.list_blobs.return_value = [mock_blob]

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert "File size must be less than" in out
    assert actual == []
