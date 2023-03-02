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
"""Document.proto converters."""

from google.cloud.documentai_toolbox.converters.config.converter_helpers import (
    convert_documents_with_config,
)


def convert_from_config(
    project_id: str,
    location: str,
    processor_id: str,
    gcs_input_path: str,
    gcs_output_path: str,
    config_path: str = None,
) -> None:
    convert_documents_with_config(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        gcs_input_path=gcs_input_path,
        gcs_output_path=gcs_output_path,
        config_path=config_path,
    )
