# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# [START documentai_toolbox_list_gcs_document_tree]

import os

from samples.snippets import quickstart_sample

location = "us"
project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
gcs_prefix = "gs://documentai_toolbox_samples/output/123456789"


def test_quickstart(capsys):
    quickstart_sample.quickstart(gcs_prefix=gcs_prefix)
    out, _ = capsys.readouterr()

    assert "toolbox_invoice_test-0.json" in out
    assert "toolbox_large_document_test-0.json" in out
