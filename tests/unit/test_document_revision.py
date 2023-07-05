# pylint: disable=protected-access
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
import shutil

from google.cloud.documentai_toolbox.wrappers.document_revision import _OP_TYPE

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

import pytest
import glob

from google.cloud.documentai_toolbox import document_revision
from google.cloud.documentai_toolbox import gcs_utilities

from google.cloud import documentai
from google.cloud.vision import AnnotateFileResponse
from google.cloud import storage


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_revision.storage")
def test_get_base_and_revision_bytes(mock_storage):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket

    with open("tests/unit/resources/revisions/doc.dp.bp", "rb") as f:
        doc_bytes = f.read()

    with open("tests/unit/resources/revisions/pages_00001.dp.bp", "rb") as f:
        pages_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00000.dp.bp", "rb") as f:
        rev0_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00001.dp.bp", "rb") as f:
        rev1_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00002.dp.bp", "rb") as f:
        rev2_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00003.dp.bp", "rb") as f:
        rev3_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00004.dp.bp", "rb") as f:
        rev4_bytes = f.read()

    doc = mock.Mock(name=[])
    doc.name = "gs://test-directory/1/doc.dp.bp"
    doc.download_as_bytes.return_value = doc_bytes

    pages_00001 = mock.Mock(name=[])
    pages_00001.name = "gs://test-directory/1/pages_00001.dp.bp"
    pages_00001.download_as_bytes.return_value = pages_bytes

    rev_00000 = mock.Mock(name=[])
    rev_00000.name = "gs://test-directory/1/rev_00000.dp.bp"
    rev_00000.download_as_bytes.return_value = rev0_bytes

    rev_00001 = mock.Mock(name=[])
    rev_00001.name = "gs://test-directory/1/rev_00001.dp.bp"
    rev_00001.download_as_bytes.return_value = rev1_bytes

    rev_00002 = mock.Mock(name=[])
    rev_00002.name = "gs://test-directory/1/rev_00002.dp.bp"
    rev_00002.download_as_bytes.return_value = rev2_bytes

    rev_00003 = mock.Mock(name=[])
    rev_00003.name = "gs://test-directory/1/rev_00003.dp.bp"
    rev_00003.download_as_bytes.return_value = rev3_bytes

    rev_00004 = mock.Mock(name=[])
    rev_00004.name = "gs://test-directory/1/rev_00004.dp.bp"
    rev_00004.download_as_bytes.return_value = rev4_bytes

    client.list_blobs.return_value = [
        doc,
        pages_00001,
        rev_00000,
        rev_00001,
        rev_00002,
        rev_00003,
        rev_00004,
    ]

    (
        actual_text,
        actual_base_docproto,
        actual_revision_doc,
    ) = document_revision._get_base_and_revision_bytes(
        output_bucket="test_output", output_prefix="test_output"
    )

    with open("tests/unit/resources/revisions/document_text.txt", "r") as f:
        expected = f.read()

    assert actual_text == expected
    assert len(actual_revision_doc) == 5
    assert actual_base_docproto != None


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_revision.storage")
def test_get_base_docproto(mock_storage):
    client = mock_storage.Client.return_value
    mock_bucket = mock.Mock()
    client.Bucket.return_value = mock_bucket
    pb = documentai.Document.pb()
    with open("tests/unit/resources/revisions/doc.dp.bp", "rb") as f:
        doc_bytes = f.read()

    with open("tests/unit/resources/revisions/pages_00001.dp.bp", "rb") as f:
        pages_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00000.dp.bp", "rb") as f:
        rev0_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00001.dp.bp", "rb") as f:
        rev1_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00002.dp.bp", "rb") as f:
        rev2_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00003.dp.bp", "rb") as f:
        rev3_bytes = f.read()

    with open("tests/unit/resources/revisions/rev_00004.dp.bp", "rb") as f:
        rev4_bytes = f.read()

    doc = mock.Mock(name=[])
    doc.name = "gs://test-directory/1/doc.dp.bp"
    doc.download_as_bytes.return_value = doc_bytes

    pages_00001 = mock.Mock(name=[])
    pages_00001.name = "gs://test-directory/1/pages_00001.dp.bp"
    pages_00001.download_as_bytes.return_value = pages_bytes

    rev_00000 = mock.Mock(name=[])
    rev_00000.name = "gs://test-directory/1/rev_00000.dp.bp"
    rev_00000.download_as_bytes.return_value = rev0_bytes

    rev_00001 = mock.Mock(name=[])
    rev_00001.name = "gs://test-directory/1/rev_00001.dp.bp"
    rev_00001.download_as_bytes.return_value = rev1_bytes

    rev_00002 = mock.Mock(name=[])
    rev_00002.name = "gs://test-directory/1/rev_00002.dp.bp"
    rev_00002.download_as_bytes.return_value = rev2_bytes

    rev_00003 = mock.Mock(name=[])
    rev_00003.name = "gs://test-directory/1/rev_00003.dp.bp"
    rev_00003.download_as_bytes.return_value = rev3_bytes

    rev_00004 = mock.Mock(name=[])
    rev_00004.name = "gs://test-directory/1/rev_00004.dp.bp"
    rev_00004.download_as_bytes.return_value = rev4_bytes

    client.list_blobs.return_value = [
        doc,
        pages_00001,
        rev_00000,
        rev_00001,
        rev_00002,
        rev_00003,
        rev_00004,
    ]

    actual_base_shard, actual_revision_shards = document_revision._get_base_docproto(
        gcs_prefix="gs://output/prefix"
    )
    with open("tests/unit/resources/revisions/document_text.txt", "r") as f:
        text = f.read()

    page_pb = documentai.Document.Page.pb()
    with open("tests/unit/resources/0/toolbox_invoice_test-0.json", "r") as f:
        expected_base_shard = documentai.Document()
        expected_base_shard.pages = documentai.Document.from_json(f.read()).pages
        expected_base_shard.text = text

    assert actual_base_shard[0].text == expected_base_shard.text
    assert len(actual_base_shard[0].pages) == len(expected_base_shard.pages)
    assert actual_base_shard[0].pages[0].image == expected_base_shard.pages[0].image
    assert len(actual_revision_shards) == 5

    assert actual_revision_shards[0].revisions[0].id == "ebd407c15733ee36"
    assert actual_revision_shards[0].revisions[0].processor == "OCR"


def test_modify_docproto():
    with open("tests/unit/resources/0/toolbox_invoice_test-0.json", "r") as f:
        docproto = documentai.Document.from_json(f.read())
    e0 = docproto.entities[0]
    e0.type_ = "Type 1"
    e0.mention_text = "Mention Text 1"
    e0.id = "1"
    e0.provenance.type_ = _OP_TYPE.ADD

    e1 = docproto.entities[1]
    e1.type_ = "Type 2"
    e1.mention_text = "Mention Text 2"
    e1.id = "2"
    e1.provenance.type_ = _OP_TYPE.ADD

    entities = [e0, e1]

    actual_entities = document_revision._modify_docproto(entities=entities)

    assert actual_entities[0][0].type_ == "Type 1"
    assert actual_entities[0][0].mention_text == "Mention Text 1"

    assert actual_entities[0][1].type_ == "Type 2"
    assert actual_entities[0][1].mention_text == "Mention Text 2"

    e2 = documentai.Document.Entity(
        type_="Type 1", mention_text="Mention Text 1", id="1"
    )
    e2.provenance.type_ = _OP_TYPE.REMOVE

    e3 = documentai.Document.Entity(
        type_="Replaced Type 2", mention_text="Replaced Mention Text 2", id="1"
    )
    e3.provenance.type_ = _OP_TYPE.REPLACE

    entities = [e0, e1, e2, e3]

    actual_entities = document_revision._modify_docproto(entities=entities)

    assert actual_entities[0][0].type_ == "Replaced Type 2"
    assert actual_entities[0][0].mention_text == "Replaced Mention Text 2"


def test_get_revised_documents():
    with open("tests/unit/resources/0/toolbox_invoice_test-0.json", "r") as f:
        docproto = documentai.Document.from_json(f.read())

    e0 = docproto.entities[0]
    e0.type_ = "Type 1"
    e0.mention_text = "Mention Text 1"
    e0.id = "1"
    e0.provenance.type_ = _OP_TYPE.ADD

    e1 = docproto.entities[1]
    e1.type_ = "Type 2"
    e1.mention_text = "Mention Text 2"
    e1.id = "2"
    e1.provenance.type_ = _OP_TYPE.ADD

    e2 = documentai.Document.Entity(
        type_="Type 1", mention_text="Mention Text 1", id="1"
    )
    e2.provenance.type_ = _OP_TYPE.REMOVE

    e3 = documentai.Document.Entity(
        type_="Replaced Type 2", mention_text="Replaced Mention Text 2", id="1"
    )
    e3.provenance.type_ = _OP_TYPE.REPLACE

    docproto.entities = [e0, e1, e2, e3]

    actual_revised_entities, history = document_revision._get_revised_entities(
        revision=docproto
    )

    assert actual_revised_entities[0].type_ == "Replaced Type 2"
    assert actual_revised_entities[0].mention_text == "Replaced Mention Text 2"

    assert history[0]["entity_provenance_type"] == "ADD"
    assert history[0]["original_text"] == "Mention Text 1"

    assert history[3]["entity_provenance_type"] == "REPLACE"
    assert history[3]["original_text"] == "Replaced Mention Text 2"


def test_get_level():
    parent = document_revision.DocumentWithRevisions(document=None, revision_nodes=None)
    child = document_revision.DocumentWithRevisions(document=None, revision_nodes=None)
    sub_child = document_revision.DocumentWithRevisions(document=None, revision_nodes=None)
    parent.revision_id = 1
    child.revision_id = 2
    sub_child.revision_id = 3

    parent.children.append(child)
    child.parent = parent
    sub_child.parent = child

    actual_level = document_revision.get_level(sub_child)
    
    assert actual_level == 2

    parent_level = document_revision.get_level(parent)

    assert parent_level == 0


# def test_print_child_tree():
#     pass

# def test_from_gcs_prefix_with_revisions():
#     pass

# def test_last_revision():
#     pass

# def test_next_revision():
#     pass

# def test_jump_revision():
#     pass

# def test_jump_to_revision():
#     pass

# def test_get_revisions():
#     pass

# def print_tree():
#     pass
