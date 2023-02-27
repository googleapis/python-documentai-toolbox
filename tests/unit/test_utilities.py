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


def test_create_batches_with_3_documents(capfd):
    test_bucket = "cloud-samples-data"
    test_prefix = "documentai_toolbox/document_batches/folder_with_3_documents/"

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert out == ""
    assert len(actual) == 1
    assert len(actual[0].gcs_documents.documents) == 3


def test_create_batches_with_invalid_batch_size(capfd):
    test_bucket = "cloud-samples-data"
    test_prefix = "documentai_toolbox/document_batches/folder_with_3_documents/"

    with pytest.raises(ValueError):
        utilities.create_batches(
            gcs_bucket_name=test_bucket, gcs_prefix=test_prefix, batch_size=51
        )

        out, err = capfd.readouterr()
        assert "Batch size must be less than" in out
        assert err


def test_create_batches_with_large_folder(capfd):
    test_bucket = "cloud-samples-data"
    test_prefix = "documentai_toolbox/document_batches/"

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert out == ""
    assert len(actual) == 2
    assert len(actual[0].gcs_documents.documents) == 50
    assert len(actual[1].gcs_documents.documents) == 46


def test_create_batches_with_invalid_file_type(capfd):
    test_bucket = "cloud-samples-data"
    test_prefix = "documentai_toolbox/1/"

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert "Invalid Mime Type" in out
    assert actual == []


def test_create_batches_with_large_file(capfd):
    test_bucket = "cloud-samples-data"
    test_prefix = "documentai_toolbox/file_too_large/"

    actual = utilities.create_batches(
        gcs_bucket_name=test_bucket, gcs_prefix=test_prefix
    )

    out, err = capfd.readouterr()
    assert "File size must be less than" in out
    assert actual == []
