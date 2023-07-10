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
"""Wrappers for Document AI Document with revisions."""

import dataclasses
import os
import re
import copy

from typing import List, Tuple

from google.cloud import documentai
from google.cloud import storage

from google.cloud.documentai_toolbox.wrappers.entity import Entity

from google.cloud.documentai_toolbox.wrappers.document import Document

_OP_TYPE = documentai.Document.Provenance.OperationType


def _get_base_and_revision_bytes(
    output_bucket: str, output_prefix: str
) -> Tuple[str, list, list]:
    r"""Returns document text,base docproto and list of revision shards

    Args:
        output_bucket (str):
            Required. The name of the output_bucket.

        output_prefix (str):
            Required. The prefix of the folder where files are excluding the bucket name.

    Returns:
        Tuple[str, list[Bytes], list[Bytes]]:
            document text, list of page bytes from the base document, list of revision bytes from the base document.

    """
    text = ""
    pages_bytes = []
    revision_bytes = []

    storage_client = storage.Client()

    blob_list = storage_client.list_blobs(output_bucket, prefix=output_prefix)
    pb = documentai.Document.pb()
    for blob in blob_list:
        name = os.path.basename(blob.name)
        if blob.name.endswith(".dp.bp"):
            blob_as_bytes = blob.download_as_bytes()
            if re.search(r"^doc.dp.bp", name):
                text = pb.FromString(blob_as_bytes).text
            elif re.search(r"^pages_*.*", name):
                pages_bytes.append(blob_as_bytes)
            elif re.search(r"^rev_*.*", name):
                print(name)
                revision_bytes.append(blob_as_bytes)

    return text, pages_bytes, revision_bytes


def _get_base_docproto(gcs_bucket_name, gcs_prefix) -> Tuple[list, list]:
    r"""
    Returns a list of documentai.Document with pages from the base document and list of revision shards.

    Args:
        gcs_bucket_name (str):
            Required. The gcs bucket.

            Format: Given `gs://{bucket_name}/{optional_folder}/{operation_id}/` where `gcs_bucket_name={bucket_name}`.
        gcs_prefix (str):
            Required. The prefix to the location of the target folder.

            Format: Given `gs://{bucket_name}/{optional_folder}/{target_folder}` where `gcs_prefix={optional_folder}/{target_folder}`.
    Returns:
        Tuple[list[documentai.Document], list[documentai.Document]]:
            list of documentai.Document with base pages, list of revisions.
    """
    base_page_shards = []
    revision_shards = []

    text, base_bytes, revision_bytes = _get_base_and_revision_bytes(
        gcs_bucket_name, gcs_prefix
    )
    page_pb = documentai.Document.Page.pb()
    pb = documentai.Document.pb()
    for byte in base_bytes:
        base_page_shards.append(
            documentai.Document(pages=[page_pb.FromString(byte)], text=text)
        )

    for byte in revision_bytes:
        revision_shards.append(pb.FromString(byte))

    return base_page_shards, revision_shards


def _modify_entities(
    entities: List[documentai.Document.Entity],
) -> Tuple[list, list]:
    r"""Modifies the entities using the providence field in the entities.

    Args:
        entities (List[Entity]):
            A list of documentai.Document.Entity.

    Returns:
        Tuple[list,list]:
            modified entities, Entity history.
    """
    entities_array = []
    history = []
    for e in entities:
        if (
            e.provenance.type_ == _OP_TYPE.ADD
            or e.provenance.type_ == _OP_TYPE.OPERATION_TYPE_UNSPECIFIED
        ):
            entities_array.append(Entity(documentai_entity=e))
            history.append(
                {
                    "object": "Entity",
                    "entity_provenance_type": _OP_TYPE(e.provenance.type_).name,
                    "original_entity": e,
                    "original_type": e.type_,
                    "original_text": e.mention_text,
                }
            )
        elif e.provenance.type_ == _OP_TYPE.REMOVE:
            entity = entities_array.pop(int(e.id) - 1)
            history.append(
                {
                    "object": "Entity",
                    "entity_provenance_type": _OP_TYPE(e.provenance.type_).name,
                    "original_entity": e,
                    "original_type": entity.type_,
                    "original_text": entity.mention_text,
                }
            )
            del entity
        elif e.provenance.type_ == _OP_TYPE.REPLACE:
            history.append(
                {
                    "object": "Entity",
                    "entity_provenance_type": _OP_TYPE(e.provenance.type_).name,
                    "original_entity": entities_array[int(e.id) - 1],
                    "original_type": entities_array[int(e.id) - 1].type_,
                    "original_text": entities_array[int(e.id) - 1].mention_text,
                    "replace_type": e.type_,
                    "replace_text": e.mention_text,
                }
            )
            entities_array[int(e.id) - 1] = e
    return entities_array, history


def _get_level(current_revision: "DocumentWithRevisions") -> int:
    r"""Returns the level of the current revision in the revision tree.

    Args:
        current_revision (DocumentWithRevisions):
            The current revision.

    Returns:
        int:
            The level of the current revision in the revision tree.
    """
    level = 0
    p = current_revision.parent
    while hasattr(p, "parent"):
        level += 1
        p = p.parent
    return level


def _print_child_tree(
    current_revision: "DocumentWithRevisions",
    doc: "DocumentWithRevisions",
    seen: List[str],
):
    r"""Prints the revision tree of a child revision.

    Args:
        None.

    Returns:
        None.
    """
    tab = "  " * _get_level(doc)

    if doc.children:
        if current_revision.revision_id == doc.revision_id:
            print(tab + "└──>", end="")
        else:
            print(tab + "└──", end="")
        print(doc.revision_id)
        for each in doc.children:
            seen.append(each.revision_id)
            _print_child_tree(current_revision, each, seen)
    else:
        if current_revision.revision_id == doc.revision_id:
            print(tab + "└──>", end="")
        else:
            print(tab + "└──", end="")
        print(doc.revision_id)


@dataclasses.dataclass
class DocumentWithRevisions:
    r"""Represents a wrapped Document.

    A single Document protobuf message with revisions will be written as several `dp.bp` files on
    GCS by Document AI's Processor Training UI.  This class hides away the
    shards from the users and implements convenient methods for reading and moving between different document revisions.

    Users should initilize the DocumentWithRevision class by using `from_gcs_prefix_with_revisions` function.

    Attributes:
        document (documentai.Document):
            Required. The Document AI document.
        revision_nodes (List[documentai.Document]):
            Required. A list of Document AI document revisions.
        gcs_bucket_name (str):
            Required. The gcs bucket.

            Format: Given `gs://{bucket_name}/{optional_folder}/{operation_id}/` where `gcs_bucket_name={bucket_name}`.
        gcs_prefix (str):
            Required.The gcs path to a single processed document.

            Format: `gs://{bucket}/{optional_folder}/{operation_id}/{folder_id}`
                    where `{operation_id}` is the operation-id given from BatchProcessDocument
                    and `{folder_id}` is the number corresponding to the target document.
        parent_ids (List[str]):
            Required. A list of parent ids.
            Parents are defined as nodes with 1 or more children.
        all_node_ids (List[str]):
            Required. A list of all the node ids.
    """

    document: Document = dataclasses.field(repr=False)
    revision_nodes: List[documentai.Document] = dataclasses.field(repr=False)
    gcs_bucket_name: str = dataclasses.field(repr=False, default=None)
    gcs_prefix: str = dataclasses.field(repr=False, default=None)
    parent_ids: List[str] = dataclasses.field(repr=False, default=None)
    all_node_ids: List[str] = dataclasses.field(repr=False, default=None)

    next_: Document = dataclasses.field(init=False, repr=False, default=None)
    last: Document = dataclasses.field(init=False, repr=False, default=None)
    revision_id: str = dataclasses.field(init=False, repr=False, default=None)
    history: List[str] = dataclasses.field(init=False, repr=False, default_factory=list)
    root_revision: Document = dataclasses.field(init=False, repr=False, default=None)

    parent: "DocumentWithRevisions" = dataclasses.field(
        init=False, repr=False, default=None
    )

    children: List["DocumentWithRevisions"] = dataclasses.field(
        init=False, repr=False, default_factory=list
    )
    children_ids: List[str] = dataclasses.field(
        init=False, repr=False, default_factory=list
    )
    root_revision_nodes: List["DocumentWithRevisions"] = dataclasses.field(
        init=False, repr=False, default_factory=list
    )

    @classmethod
    def from_gcs_prefix_with_revisions(self, gcs_bucket_name: str, gcs_prefix: str):
        r"""Loads DocumentWithRevision from Cloud Storage.

        Args:
            gcs_bucket_name (str):
                Required. The gcs bucket.

                Format: Given `gs://{bucket_name}/{optional_folder}/{operation_id}/` where `gcs_bucket_name={bucket_name}`.
            gcs_prefix (str):
                Required. The prefix to the location of the target folder.

                Format: Given `gs://{bucket_name}/{optional_folder}/{target_folder}` where `gcs_prefix={optional_folder}/{target_folder}`.
        Returns:
            Document:
                A document from gcs.
        """
        base_docproto, revs = _get_base_docproto(
            gcs_bucket_name=gcs_bucket_name, gcs_prefix=gcs_prefix
        )

        revisions = [r.revisions for r in revs]
        parent_ids = [r.revisions[0].id for r in revs if not r.revisions[0].parent]
        all_node_ids = [r.revisions[0].id for r in revs]

        immutable_doc = Document(
            shards=base_docproto, gcs_bucket_name=gcs_bucket_name, gcs_prefix=gcs_prefix
        )
        root_revision_nodes = []

        for rev in revs:
            copied_doc = copy.deepcopy(immutable_doc)
            d = Document(
                shards=copied_doc.shards,
                gcs_bucket_name=copied_doc.gcs_bucket_name,
                gcs_prefix=copied_doc.gcs_prefix,
            )
            d.entities, history = _modify_entities(rev.entities)

            revision_doc = DocumentWithRevisions(
                document=d,
                revision_nodes=revisions,
                gcs_bucket_name=gcs_bucket_name,
                gcs_prefix=gcs_prefix,
                parent_ids=parent_ids,
                all_node_ids=all_node_ids,
            )
            revision_doc.history += history

            revision_doc.revision_id = rev.revisions[0].id
            if rev.revisions[0].parent:
                root_revision_nodes[rev.revisions[0].parent[0]].children.append(
                    revision_doc
                )
                root_revision_nodes[rev.revisions[0].parent[0]].children_ids.append(
                    revision_doc.revision_id
                )
                revision_doc.parent = root_revision_nodes[rev.revisions[0].parent[0]]
            else:
                revision_doc.parent = None

            root_revision_nodes.append(revision_doc)

        for r in root_revision_nodes:
            r.root_revision_nodes = root_revision_nodes

        return root_revision_nodes[-1]

    def last_revision(self):
        r"""Goes to the previous revision.

            This should be used if you want to go to the previous revision.

            For example: Given revision tree with current revision being 3
            ```
                └──1
                    └──2
                      └──>3
                    └──5
                ├──4
            ```
            If you use `next_revision()` the next revision will be 2

        Args:
            None
        Returns:
            DocumentWithRevisions:
                The next DocumentWithRevision object.
        """
        if self.parent:
            current_index = self.parent.children_ids.index(self.revision_id)
            if current_index != 0:
                return self.parent.children[current_index - 1]
            elif current_index is not None:
                return self.parent
        elif self.revision_id in self.parent_ids:
            non_parent_index = self.parent_ids.index(self.revision_id)
            if non_parent_index > 0:
                next_parent = self.parent_ids[non_parent_index - 1]
                index = self.all_node_ids.index(next_parent)
                return self.root_revision_nodes[index]
            else:
                return self
        return self

    def next_revision(self):
        r"""Goes to the next revision.

            This should be used if the current revision has children and you want to go into the children.

            For example: Given revision tree with current revision being 2
            ```
                └──1
                    └──>2
                      └──3
                    └──5
                ├──4
            ```
            If you use `next_revision()` the next revision will be 3

        Args:
            None
        Returns:
            DocumentWithRevisions:
                The next DocumentWithRevision object.
        """
        if self.children != []:
            return self.children[0]
        elif self.parent:
            current_index = self.parent.children_ids.index(self.revision_id)
            if current_index < len(self.parent.children) - 1:
                return self.parent.children[current_index + 1]
        elif self.revision_id in self.parent_ids:
            non_parent_index = self.parent_ids.index(self.revision_id)
            if non_parent_index < len(self.parent_ids) - 1:
                next_parent = self.parent_ids[non_parent_index + 1]
                index = self.all_node_ids.index(next_parent)
                return self.root_revision_nodes[index]
            else:
                return self

        return self

    def jump_revision(self) -> "DocumentWithRevisions":
        r"""Jumps over revision.

            This should be used if the current revision has children and you want to go to the next parent revision.

            For example: Given revision tree with current revision being 2
            ```
                └──1
                    └──>2
                      └──3
                    └──5
                ├──4
            ```
            If you use `jump_revision()` the next revision will be 5

        Args:
            None
        Returns:
            DocumentWithRevisions:
                The next DocumentWithRevision object.
        """
        if self.parent is not None:
            current_index = self.parent.children_ids.index(self.revision_id)
            if current_index < len(self.parent.children) - 1:
                return self.parent.children[current_index + 1]
        elif self.parent_ids:
            non_parent_index = self.parent_ids.index(self.revision_id)
            if non_parent_index < len(self.parent_ids) - 1:
                next_parent = self.parent_ids[non_parent_index + 1]
                index = self.all_node_ids.index(next_parent)
                return self.root_revision_nodes[index]

        return self

    def jump_to_revision(self, id: str) -> "DocumentWithRevisions":
        r"""Jumps to a specific revision.
        Args:
            id (str):
                The id of the revision to jump to.

        Returns:
            DocumentWithRevisions:
                A DocumentWithRevision object with specified id.

        """

        if id == self.revision_id:
            return self

        if id in self.all_node_ids:
            return self.root_revision_nodes[self.all_node_ids.index(id)]

        return "Not Found"

    def print_tree(self) -> None:
        r"""Prints the revision tree.

        Args:
            None.

        Returns:
            None.
        """
        seen_id = []

        for root in self.root_revision_nodes:
            if root is None or root.revision_id is None or root.revision_id in seen_id:
                continue

            if root.children:
                _print_child_tree(self, root, seen_id)
            else:
                if self.revision_id == root.revision_id:
                    print("└──>", end="")
                else:
                    print("├──", end="")
                print(root.revision_id)

            seen_id.append(root.revision_id)
