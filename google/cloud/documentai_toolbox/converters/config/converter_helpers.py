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

import re
import time
from concurrent import futures
from typing import List

from google.cloud.documentai_toolbox.converters.config.bbox_conversion import (
    _convert_bbox_to_docproto_bbox,
    _get_text_anchor_in_bbox,
)
from google.cloud.documentai_toolbox.converters.config.blocks import (
    load_blocks_from_schema,
)

from google.cloud.documentai_toolbox import document
from google.cloud import documentai, storage


def get_base_ocr(
    project_id: str, location: str, processor_id: str, file_bytes, mime_type: str
) -> documentai.Document:
    r"""Returns documentai.Document from OCR processor.

    Args:
        project_id (JSON):
            Required.
        location (documentai.Document):
            Required.
        processor_id (List[Block]):
            Required.
        file_bytes (List[Block]):
            Required. The bytes of the original pdf.
        mime_type (List[Block]):
            Required. usually "application/pdf".
    Returns:
        documentai.Document:
            A documentai.Document from OCR processor.

    """
    # You must set the api_endpoint if you use a location other than 'us', e.g.:

    client = documentai.DocumentProcessorServiceClient()

    # The full resource name of the processor, e.g.:
    # projects/project_id/locations/location/processor/processor_id
    # You must create new processors in the Cloud Console first
    name = client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    image_content = file_bytes

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=name, raw_document=raw_document)

    result = client.process_document(request=request)
    return result.document


def get_entitiy_content(blocks, docproto):
    r"""Returns a list of documentai.Document entities.

    Args:
        annotated_object (JSON):
            Required.JSON object of the annotated data.
        docproto (documentai.Document):
            Required.The ocr docproto.
        blocks (List[Block]):
            Required. The bytes of the original pdf.
    Returns:
        List[documentai.Document.Entity]:
            A list of documentai.Document entities.
    """
    entities = []
    entity_id = 0

    for block in blocks:

        docai_entity = documentai.Document.Entity()
        if block.confidence != None:
            docai_entity.confidence = block.confidence

        docai_entity.type = block.type_
        docai_entity.mention_text = block.text
        docai_entity.id = str(entity_id)

        entity_id += 1
        # Generates the text anchors from bounding boxes
        if block.bounding_box != None:
            # Converts external bounding box format to docproto bounding box

            b1 = _convert_bbox_to_docproto_bbox(block)

            if block.page_number:
                docai_entity.text_anchor = _get_text_anchor_in_bbox(
                    b1, docproto.pages[int(block.page_number) - 1]
                )
            else:
                docai_entity.text_anchor = _get_text_anchor_in_bbox(
                    b1, docproto.pages[0]
                )

            docai_entity.text_anchor.content = block.text

            page_anchor = documentai.Document.PageAnchor()
            page_ref = documentai.Document.PageAnchor.PageRef()

            page_ref.bounding_poly = b1

            page_anchor.page_refs = [page_ref]
            docai_entity.page_anchor = page_anchor
        entities.append(docai_entity)

    return entities


def convert_to_docproto_with_config(
    name,
    annotated_bytes,
    schema_bytes,
    document_bytes,
    project_id,
    location,
    processor_id,
    retry_number,
) -> documentai.Document:
    r"""Converts a single document to docproto.

    Args:
        annotated_bytes (str):
            Required.The bytes of the annotated data.
        ocr_bytes (str):
            Required.The bytes of documentai.Document from OCR.
        document_bytes (str):
            Required. The bytes of the original pdf.
        project_id (str):
            Required.
        location (str):
            Required.
        processor_id (str):
            Required.
        retry_number (str):
            Required. The number of seconds needed to wait if an error occured.
        name (str):
            Optional. Name of the document to be converted. This is used for logging.

    Returns:
        documentai.Document:
            documentai.Document object.

    TODO: Depending on input type you will need to modify load_blocks.
          Depening on input format, if your annoated data is not seperate from the base OCR data you will need to modify get_entitiy_content
          Depending on input BoundingBox, if the input BoundingBox object is like https://cloud.google.com/document-ai/docs/reference/rest/v1/Document#BoundingPoly then you will need to
            modify _convert_bbox_to_docproto_bbox since the objects are different.
    """
    try:
        base_docproto = get_base_ocr(
            project_id=project_id,
            location=location,
            processor_id=processor_id,
            file_bytes=document_bytes,
            mime_type="application/pdf",
        )

        # Loads OCR data into Blocks
        # blocks = load_blocks(ocr_object=doc_object)
        blocks = load_blocks_from_schema(
            input_data=annotated_bytes,
            input_schema=schema_bytes,
            base_docproto=base_docproto,
        )

        # # Gets List[documentai.Document.Entity]
        entities = get_entitiy_content(blocks=blocks, docproto=base_docproto)

        base_docproto.entities = entities
        print("Converted : %s\r" % name, end="")
        return base_docproto

    except Exception as e:
        print(e)
        print(f"Could Not Convert {name}\nretrying")
        if retry_number == 6:
            return None
        else:
            time.sleep(retry_number)
            return convert_to_docproto_with_config(
                name,
                annotated_bytes,
                schema_bytes,
                document_bytes,
                project_id,
                location,
                processor_id,
                retry_number=retry_number + 1,
            )


def _get_bytes(
    bucket_name: str,
    prefix: str,
    annotation_file_prefix: str,
    config_file_prefix: str,
    config_path: str = None,
) -> List[bytes]:
    r"""Downloads documents and returns them as bytes.

    Args:
        bucket_name (str):
            Required. The bucket name.
        prefix (str):
            Required. The prefix for the location of the output folder.
        annotation_file_prefix (str):
            Required. The prefix to search for annotation file.
        config_file_prefix (str):
            Required. The prefix to search for config file

    Returns:
        List[Byte,Byte,Byte,str].

    """

    storage_client = document._get_storage_client()
    bucket = storage_client.bucket(bucket_name=bucket_name)
    blobs = storage_client.list_blobs(bucket_or_name=bucket_name, prefix=prefix)

    metadata_blob = None

    try:
        for blob in blobs:
            if "DS_Store" in blob.name:
                continue
            if not blob.name.endswith("/"):
                blob_name = blob.name
                file_name = blob_name.split("/")[-1]
                if annotation_file_prefix in file_name:
                    annotation_blob = blob
                elif config_file_prefix in file_name:
                    metadata_blob = blob
                elif "pdf" in file_name:
                    doc_blob = blob

        if metadata_blob == None and config_path != None:
            metadata_blob = bucket.get_blob(config_path)

        print("Downloaded : %s\r" % prefix.split("/")[-1], end="")
        return [
            annotation_blob.download_as_bytes(),
            doc_blob.download_as_bytes(),
            metadata_blob.download_as_bytes(),
            prefix.split("/")[-1],
            file_name.split(".")[0],
        ]
    except Exception as e:
        raise e


def _upload_file(
    bucket_name,
    output_prefix,
    file,
) -> None:
    r"""Uploads the converted docproto to gcs.

    Args:
        bucket_name (str):
            Required. The bucket name.
        output_prefix (str):
            Required. The prefix for the location of the output folder.
        file (str):
            Required. The docproto file in string format.

    Returns:
        None.

    """
    storage_client = document._get_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(output_prefix)

    print("Uploaded : %s\r" % output_prefix.split("/")[-1], end="")
    blob.upload_from_string(file, content_type="application/json")


def _get_files(blob_list, output_prefix, output_bucket, config_path: str = None):
    download_pool = futures.ThreadPoolExecutor(10)
    downloads = []
    files = []
    did_not_convert = []
    labels = []
    skip = ["DS_Store"]
    prev = None
    print("-------- Downloading Started --------")
    for i, blob in enumerate(blob_list):
        if "DS_Store" in blob.name:
            continue
        else:
            file_path = blob.name.split("/")
            file_path.pop()
            doc_directory = file_path[-1]
            file_path2 = "/".join(file_path)
            if prev == doc_directory or f"{file_path2}/" == output_prefix:
                continue

            download = download_pool.submit(
                _get_bytes,
                output_bucket,
                file_path2,
                "annotation",
                "config",
                config_path,
            )
            downloads.append(download)

            prev = doc_directory

    return downloads


def _get_docproto_files(f, project_id, location, processor_id, output_prefix):

    did_not_convert = []
    files = {}
    unique_types = []
    for future in f:
        blobs = future.result()
        docproto = convert_to_docproto_with_config(
            annotated_bytes=blobs[0],
            document_bytes=blobs[1],
            schema_bytes=blobs[2],
            project_id=project_id,
            location=location,
            processor_id=processor_id,
            retry_number=1,
            name=blobs[3],
        )

        for entity in docproto.entities:
            if entity.type_ not in unique_types:
                unique_types.append(entity.type_)

        if docproto == None:
            did_not_convert.append(f"{output_prefix}/{blobs[3]}")
            continue

        files[blobs[3]] = str(documentai.Document.to_json(docproto))

    return files, unique_types, did_not_convert


def _upload(files, gcs_output_path):
    match = re.match(r"gs://(.*?)/(.*)", gcs_output_path)

    if match is None:
        raise ValueError("gcs_prefix does not match accepted format")

    output_bucket, output_prefix = match.groups()

    if output_prefix == None:
        output_prefix = "/"

    file_check = re.match(r"(.*[.].*$)", output_prefix)

    if file_check is not None:
        raise ValueError("gcs_prefix cannot contain file types")

    download_pool = futures.ThreadPoolExecutor(10)
    uploads = []
    print("-------- Uploading Started --------")
    for i, key in enumerate(files):
        op = output_prefix.split("/")
        op.pop()
        prefix = "/".join(op)
        if "config" not in key and "annotations" not in key:
            _upload = download_pool.submit(
                _upload_file,
                output_bucket,
                f"{output_prefix}/{key}.json",
                files[key],
            )
            uploads.append(_upload)

    futures.wait(uploads)


def convert_documents_with_config(
    gcs_input_path: str,
    gcs_output_path: str,
    project_id: str,
    location: str,
    processor_id: str,
    config_path: str = None,
) -> None:
    r"""Converts all documents in gcs_path to docproto.

    Args:
        gcs_input_path (str):
            Required. The gcs path to the folder containing all non docproto documents.

            Format: `gs://{bucket}/{optional_folder}`
        gcs_output_path (str):
            Required. The gcs path to the folder to upload the converted docproto documents to.

            Format: `gs://{bucket}/{optional_folder}`
        project_id (str):
            Required.
        location (str):
            Required.
        processor_id (str):
            Required.

    Returns:
        None.

    """
    match = re.match(r"gs://(.*?)/(.*)", gcs_input_path)

    if match is None:
        raise ValueError("gcs_prefix does not match accepted format")

    output_bucket, output_prefix = match.groups()

    if output_prefix == None:
        output_prefix = "/"

    file_check = re.match(r"(.*[.].*$)", output_prefix)

    if file_check is not None:
        raise ValueError("gcs_prefix cannot contain file types")

    storage_client = document._get_storage_client()

    blob_list = storage_client.list_blobs(output_bucket, prefix=output_prefix)

    downloads = _get_files(
        blob_list=blob_list,
        output_prefix=output_prefix,
        output_bucket=output_bucket,
        config_path=config_path,
    )

    f, _ = futures.wait(downloads)

    print("-------- Finished Downloading --------")

    print("-------- Converting Started --------")

    files = []
    did_not_convert = []
    labels = []

    files, labels, did_not_convert = _get_docproto_files(
        f, project_id, location, processor_id, output_prefix
    )

    print("-------- Finished Converting --------")
    if did_not_convert != []:
        print(f"Did not convert {len(did_not_convert)} documents")
        print(did_not_convert)

    _upload(files, gcs_output_path)

    print("-------- Finished Uploading --------")
    print("-------- Schema Information --------")
    print(f"Unique Entity Types: {labels}")


# [min,min],[max,min],[max,max],[min,max]
