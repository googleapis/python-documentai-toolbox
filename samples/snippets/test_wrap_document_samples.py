# Copyright 2020 Google LLC
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

import os

import pytest
from samples.snippets import wrap_document_samples

location = "us"
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
gcs_input_uri = "gs://cloud-samples-data/documentai_toolbox/1/"

def test_wrap_document_from_gcs_prefix(capsys):
    wrap_document_samples.wrap_document_from_gcs_prefix(gcs_prefix=gcs_input_uri)
    out, _ = capsys.readouterr()

    assert "Number of Pages: 32" in out
    assert "Number of Entities: 32" in out