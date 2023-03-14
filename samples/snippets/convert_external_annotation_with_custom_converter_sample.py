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

# [START documentai_toolbox_convert_custom_external_annotations]

from asyncio import futures
import re
from google.cloud.documentai_toolbox import converter, constants
from google.cloud.documentai_toolbox.converters.custom.converter_helpers import _get_bytes, _upload_file


def get_files(blob_list,input_prefix,input_bucket):
    r"""
    Custome get_files implementation
    """
    download_pool = futures.ThreadPoolExecutor(10)
    downloads = []
    prev = None
    print("-------- Downloading Started --------")
    for i, blob in enumerate(blob_list):
        if "DS_Store" in blob.name:
            continue

        file_path = blob.name.split("/")
        file_path.pop()
        doc_directory = file_path[-1]
        file_path2 = "/".join(file_path)
        if prev == doc_directory or f"{file_path2}/" == input_prefix:
            continue

        download = download_pool.submit(
            _get_bytes,
            input_bucket,
        )

        downloads.append(download)

        prev = doc_directory

    return downloads

def upload(files,gcs_output_path):
    r"""
    Custome _upload implementation
    """
    match = re.match(r"gs://(.*?)/(.*)", gcs_output_path)

    if match is None:
        raise ValueError("gcs_prefix does not match accepted format")

    output_bucket, output_prefix = match.groups()

    if output_prefix is None:
        output_prefix = "/"

    file_check = re.match(constants.FILE_CHECK_REGEX, output_prefix)

    if file_check:
        raise ValueError("gcs_prefix cannot contain file types")

    download_pool = futures.ThreadPoolExecutor(10)
    uploads = []
    print("-------- Uploading Started --------")
    for i, key in enumerate(files):
        op = output_prefix.split("/")
        op.pop()
        if "config" not in key and "annotations" not in key:
            upload = download_pool.submit(
                _upload_file,
                output_bucket,
                f"{output_prefix}/{key}.json",
                files[key],
            )
            uploads.append(upload)

    futures.wait(uploads)

def convert_external_annotations_sample(
    location: str,
    processor_id: str,
    project_id: str,
    gcs_input_path: str,
    gcs_output_path: str,
) -> None:
    converter.convert_with_custom_functions(
        project_id=project_id,
        location=location,
        processor_id=processor_id,
        gcs_input_path=gcs_input_path,
        gcs_output_path=gcs_output_path,
        _get_files=get_files,
        _upload_file=upload
    )


# [END documentai_toolbox_convert_custom_external_annotations]
