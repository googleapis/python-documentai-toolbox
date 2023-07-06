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

from google.cloud.documentai_toolbox.wrappers.document_revision import _OP_TYPE

# try/except added for compatibility with python < 3.8
try:
    from unittest import mock
except ImportError:  # pragma: NO COVER
    import mock

import pytest

from google.cloud.documentai_toolbox import document_revision

from google.cloud import documentai


@pytest.fixture
def get_revisions():
    parent = document_revision.DocumentWithRevisions(document=None, revision_nodes=None)
    second_parent = document_revision.DocumentWithRevisions(
        document=None, revision_nodes=None
    )
    child = document_revision.DocumentWithRevisions(document=None, revision_nodes=None)
    second_child = document_revision.DocumentWithRevisions(
        document=None, revision_nodes=None
    )
    sub_child = document_revision.DocumentWithRevisions(
        document=None, revision_nodes=None
    )

    parent.revision_id = 1
    child.revision_id = 2
    second_child.revision_id = 5
    sub_child.revision_id = 3
    second_parent.revision_id = 4

    child.parent = parent
    second_child.parent = parent
    sub_child.parent = child

    parent.root_revision_nodes = [parent, child, sub_child, second_parent, second_child]
    child.root_revision_nodes = [parent, child, sub_child, second_parent, second_child]
    sub_child.root_revision_nodes = [
        parent,
        child,
        sub_child,
        second_parent,
        second_child,
    ]
    second_parent.root_revision_nodes = [
        parent,
        child,
        sub_child,
        second_parent,
        second_child,
    ]
    second_child.root_revision_nodes = [
        parent,
        child,
        sub_child,
        second_parent,
        second_child,
    ]

    parent.all_node_ids = [1, 2, 3, 4, 5]
    child.all_node_ids = [1, 2, 3, 4, 5]
    sub_child.all_node_ids = [1, 2, 3, 4, 5]
    second_parent.all_node_ids = [1, 2, 3, 4, 5]
    second_child.all_node_ids = [1, 2, 3, 4, 5]

    parent.children_ids = [2, 5]
    child.children_ids = [3]

    parent.parent_ids = [1, 4]
    second_parent.parent_ids = [1, 4]

    child.children.append(sub_child)
    parent.children.append(child)
    parent.children.append(second_child)
    second_child.children = []
    second_parent.children = []

    yield [parent, child, sub_child, second_parent, second_child]


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
    assert actual_base_docproto is not None


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_revision.storage")
def test_get_base_docproto(mock_storage):
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

    actual_base_shard, actual_revision_shards = document_revision._get_base_docproto(
        gcs_bucket_name="output", gcs_prefix="prefix"
    )
    with open("tests/unit/resources/revisions/document_text.txt", "r") as f:
        text = f.read()

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


def test_get_revised_entites():
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

    actual_entities = document_revision._get_revised_entites(entities=entities)

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

    actual_entities = document_revision._get_revised_entites(entities=entities)

    assert actual_entities[0][0].type_ == "Replaced Type 2"
    assert actual_entities[0][0].mention_text == "Replaced Mention Text 2"


def test_get_level(get_revisions):
    child_level = document_revision._get_level(get_revisions[2])

    assert child_level == 2

    parent_level = document_revision._get_level(get_revisions[0])

    assert parent_level == 0

    child = get_revisions[2]
    child.revision_id = None
    document_revision._get_level(child)

    assert parent_level == 0


def test_print_child_tree(capfd, get_revisions):

    document_revision._print_child_tree(
        current_revision=get_revisions[2], doc=get_revisions[0], seen=[]
    )

    out, err = capfd.readouterr()

    assert out == "└──1\n  └──2\n    └──>3\n  └──5\n"

    document_revision._print_child_tree(
        current_revision=get_revisions[0], doc=get_revisions[0], seen=[]
    )

    out, err = capfd.readouterr()

    assert out == "└──>1\n  └──2\n    └──3\n  └──5\n"


@mock.patch("google.cloud.documentai_toolbox.wrappers.document_revision.storage")
def test_from_gcs_prefix_with_revisions(mock_storage):
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

    actual_document = (
        document_revision.DocumentWithRevisions.from_gcs_prefix_with_revisions(
            gcs_bucket_name="output", gcs_prefix="prefix"
        )
    )

    assert actual_document.revision_id == "1f35dee33db746e7"
    assert len(actual_document.document.pages) == 1
    assert len(actual_document.document.entities) == 6

    assert actual_document.document.entities[0].type_ == "invoice_date"
    assert actual_document.document.entities[0].mention_text == "01/01/1970"

    assert actual_document.document.entities[5].type_ == "ship_to_address"
    assert (
        actual_document.document.entities[5].mention_text
        == "222 Main Street\nAnytown, USA"
    )


def test_last_revision(get_revisions):
    current_revision = get_revisions[2].last_revision()

    assert current_revision.revision_id == 2

    current_revision = current_revision.last_revision()

    assert current_revision.revision_id == 1

    current_revision = get_revisions[3].last_revision()

    assert current_revision.revision_id == 1

    current_revision = get_revisions[0].last_revision()

    assert current_revision.revision_id == 1

    current_revision = get_revisions[0].last_revision()

    assert current_revision.revision_id == 1


def test_next_revision(get_revisions):
    current_revision = get_revisions[0].next_revision()

    assert current_revision.revision_id == 2

    current_revision = current_revision.next_revision()

    assert current_revision.revision_id == 3

    current_revision = get_revisions[3].next_revision()

    assert current_revision.revision_id == 4

    current_revision = get_revisions[4].next_revision()

    assert current_revision.revision_id == 5

    current_revision = get_revisions[4].next_revision()

    assert current_revision.revision_id == 5


def test_jump_revision(get_revisions):
    jumped_revision = get_revisions[0].jump_revision()

    assert jumped_revision.revision_id == 4

    jumped_revision = get_revisions[1].jump_revision()

    assert jumped_revision.revision_id == 5

    jumped_revision = get_revisions[2].jump_revision()

    assert jumped_revision.revision_id == 3

    jumped_revision = get_revisions[3].jump_revision()

    assert jumped_revision.revision_id == 4

    none_parent = get_revisions[0]
    none_parent.parent = None
    none_parent.parent_ids = None

    assert none_parent.jump_revision().revision_id == 1


def test_jump_to_revision(get_revisions):
    jumped_revision = get_revisions[2].jump_to_revision(1)

    assert jumped_revision.revision_id == 1

    jumped_revision = get_revisions[0].jump_to_revision(1)

    assert jumped_revision.revision_id == 1


def test_jump_to_revision_not_found(get_revisions):
    assert get_revisions[2].jump_to_revision(8) == "Not Found"


def test_print_tree(capfd, get_revisions):

    get_revisions[4].print_tree()

    out, err = capfd.readouterr()

    assert out == "└──1\n  └──2\n    └──3\n  └──>5\n├──4\n"

    get_revisions[2].print_tree()

    out, err = capfd.readouterr()

    assert out == "└──1\n  └──2\n    └──>3\n  └──5\n├──4\n"
