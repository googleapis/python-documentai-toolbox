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

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

from google.cloud import storage

blob_array = [
    [
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard1.json",
            bucket=mock.Mock(),
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/123456789/1/test_shard2.json",
            bucket=mock.Mock(),
        ),
    ],
    [
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
    ],
    [
        storage.Blob(
            name="gs://test-directory/documentai/output/24681012/1/test_shard1.json",
            bucket="gs://test-directory/documentai/output/24681012/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/24681012/1/test_shard2.json",
            bucket="gs://test-directory/documentai/output/24681012/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/24681012/1/test_shard3.json",
            bucket="gs://test-directory/documentai/output/24681012/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/24681012/1/test_shard4.json",
            bucket="gs://test-directory/documentai/output/24681012/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/24681012/1/test_shard5.json",
            bucket="gs://test-directory/documentai/output/24681012/1",
        ),
        storage.Blob(
            name="gs://test-directory/documentai/output/24681012/1/test_shard6.json",
            bucket="gs://test-directory/documentai/output/24681012/1",
        ),
    ],
]

print_parameters = [
    (
        blob_array[1],
        "gs://test-directory/documentai/output/123456789/1",
    ),
    (
        blob_array[2],
        "gs://test-directory/documentai/output/24681012/1",
    ),
]

test_document_param = [
    ("tests/unit/resources/0", "gs://test-directory/documentai/output/123456789/0", 1),
    ("tests/unit/resources/1", "gs://test-directory/documentai/output/123456789/1", 48),
]
