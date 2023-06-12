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
"""Wrappers for Document AI Document type."""

import dataclasses
import re
import copy

from typing import List, TypeVar

from google.cloud import documentai
from google.cloud import storage

from google.cloud.documentai_toolbox.wrappers.entity import Entity

from google.cloud.documentai_toolbox.wrappers.document import Document

_OP_TYPE = documentai.Document.Provenance.OperationType

DocumentWithRevisions=TypeVar("DocumentWithRevisions")

def _get_base_and_revision_bytes(output_bucket: str, output_prefix: str) -> List[bytes]:
    r"""Returns a list of shards as bytes.

    If the filepaths are gs://abc/def/gh/{1,2,3}.json, then output_bucket should be "abc",
    and output_prefix should be "def/gh".

    Args:
        output_bucket (str):
            Required. The name of the output_bucket.

        output_prefix (str):
            Required. The prefix of the folder where files are excluding the bucket name.

    Returns:
        List[bytes]:
            A list of shards as bytes.

    """
    text = ""
    base_doc = []
    revisions_doc = []

    storage_client = storage.Client()

    blob_list = storage_client.list_blobs(output_bucket, prefix=output_prefix)
    pb = documentai.Document.pb()
    for blob in blob_list:
        name = blob.name.split("/")[-1]

        if re.search(r"^doc.dp.bp", name) != None:
            if blob.name.endswith(".dp.bp"):
                blob_as_bytes = blob.download_as_bytes()          
                text = pb.FromString(blob_as_bytes).text
        if re.search(r"^pages_*.*", name) != None:
            if blob.name.endswith(".dp.bp"):
                blob_as_bytes = blob.download_as_bytes()
                base_doc.append(blob_as_bytes)
        elif re.search(r"^rev_*.*", name) != None:
            if blob.name.endswith(".dp.bp"):
                blob_as_bytes = blob.download_as_bytes()
                revisions_doc.append(blob_as_bytes)
            

    return text, base_doc, revisions_doc



def _get_base_docproto(gcs_prefix) -> List[documentai.Document]:
    """
    Given a gcs_prefix this funciont will return a list of documentai.Documents
    from files that follow the pattern pages-.*-to-.*
    """
    base_shards = []
    revision_shards = []
    text = []
    match = re.match(r"gs://(.*?)/(.*)", gcs_prefix)

    if match is None:
        raise ValueError("gcs_prefix does not match accepted format")

    output_bucket, output_prefix = match.groups()

    file_check = re.match(r"(.*[.].*$)", output_prefix)

    if file_check is not None:
        raise ValueError("gcs_prefix cannot contain file types")

    text, base_bytes, revision_bytes = _get_base_and_revision_bytes(
        output_bucket, output_prefix
    )
    page_pb = documentai.Document.Page.pb()
    pb = documentai.Document.pb()
    for byte in base_bytes:
        doc = documentai.Document()
        doc.pages = [page_pb.FromString(byte)]
        doc.text = text
        base_shards.append(doc)

    for byte in revision_bytes:
        revision_shards.append(pb.FromString(byte))

    return base_shards, revision_shards

def _modify_docproto(entities):
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
                    "original_entity": e,
                    "original_type": e.type_,
                    "original_text": e.mention_text,
                    "replace_type": e.type_,
                    "replace_text": e.mention_text,
                }
            )
            entities_array[int(e.id) - 1].replace(documentai_entity=e)
    return entities_array, history


def _get_revised_documents(revision: documentai.Document):
    """
    Given the immutable_document and revisions this function
    will create Document objects correlating to the provenance in revision

        For Example :
            immutable_document = {text:"blah", pages:{documentai.Document.Page}}
            revisions = [
                Revision(rev_id=a1,doc_shard,rev_index,rev,parents=[]),
                Revision(rev_id=a2,doc_shard,rev_index,rev,parents=[a1])
            ]

            This will return :
                [8aba4bb1ec12db8a:{Document1},8aba4bb1ec12d275:{Document2}]
                    Where
                        Document1 = {pages:List[Page],entities:List[Entity],revision_nodes:List[RevisionNodes]...}
                        Document2 = {pages:List[Page],entities:List[Entity],revision_nodes:List[RevisionNodes]...}
    """

    revised_entities, history = _modify_docproto(revision.entities
    )
    return revised_entities, history

def get_level(doc: DocumentWithRevisions):
        try:
            level = 0 
            p = doc.parent
            if p.revision_id:
                while p :
                    p = p.parent
                    level += 1
            return level 
        except:
            return 0
    
def _print_child_tree(currect_revision: DocumentWithRevisions, doc:DocumentWithRevisions,seen):
    if currect_revision.revision_id == doc.revision_id:
        print(' '*get_level(doc) + '*|--', end = '')
    else:
        print('  '*get_level(doc) + '|--', end = '')
    print(doc.revision_id)
    if doc.children:
        for each in doc.children:
            seen.append(each.revision_id)
            _print_child_tree(currect_revision,each,seen)

@dataclasses.dataclass
class DocumentWithRevisions:
    r"""Represents a wrapped Document.

    A single Document protobuf message might be written as several JSON files on
    GCS by Document AI's BatchProcessDocuments method.  This class hides away the
    shards from the users and implements convenient methods for searching and
    extracting information within the Document.

    Attributes:
        gcs_prefix (str):
            Required.The gcs path to a single processed document.

            Format: `gs://{bucket}/{optional_folder}/{operation_id}/{folder_id}`
                    where `{operation_id}` is the operation-id given from BatchProcessDocument
                    and `{folder_id}` is the number corresponding to the target document.
    """

    document: Document = dataclasses.field(init=True, repr=False)
    revision_nodes: List[documentai.Document] = dataclasses.field(
        init=True, repr=False
    )
    gcs_prefix: str = dataclasses.field(init=True, repr=False, default=None)
    parent_ids : List[str] = dataclasses.field(init=True, repr=False, default=None)

    next_: Document = dataclasses.field(init=False, repr=False, default=None)
    last: Document = dataclasses.field(init=False, repr=False, default=None)
    revision_id: str = dataclasses.field(init=False, repr=False, default=None)
    history: List[str] = dataclasses.field(init=False, repr=False, default_factory=list)
    root_revision: Document = dataclasses.field(init=False, repr=False, default=None)

    parent: DocumentWithRevisions = dataclasses.field(init=False, repr=False, default=None)

    children: List[DocumentWithRevisions] = dataclasses.field(init=False, repr=False, default_factory=list)
    children_ids: List[str] = dataclasses.field(init=False, repr=False, default_factory=list)
    root_revision_nodes: List[DocumentWithRevisions] = dataclasses.field(init=False, repr=False, default_factory=list)

    @classmethod
    def from_gcs_prefix_with_revisions(self, gcs_prefix: str):
        base_docproto, revs = _get_base_docproto(gcs_prefix)

        revisions = [r.revisions for r in revs]
        parent_ids = [r.revisions[0].id for r in revs]
        
        immutable_doc = Document(shards=base_docproto, gcs_prefix=gcs_prefix)
        root_revision_nodes = []

        for rev in revs:
            copied_doc = copy.deepcopy(immutable_doc)
            d = Document(shards=copied_doc.shards, gcs_prefix=copied_doc.gcs_prefix)
            d.entities, history = _get_revised_documents(rev)

            revision_doc = DocumentWithRevisions(document=d,revision_nodes=revisions,gcs_prefix=gcs_prefix,parent_ids=parent_ids)
            revision_doc.history += history

            revision_doc.revision_id = rev.revisions[0].id
            if (rev.revisions[0].parent):
                root_revision_nodes[rev.revisions[0].parent[0]].children.append(revision_doc)
                root_revision_nodes[rev.revisions[0].parent[0]].children_ids.append(revision_doc.revision_id)
                revision_doc.parent = root_revision_nodes[rev.revisions[0].parent[0]]
            else:
                revision_doc.parent = None
            
            root_revision_nodes.append(revision_doc)
        
        for r in root_revision_nodes:
            r.root_revision_nodes = root_revision_nodes
        
        return root_revision_nodes[-1]
    
    def last_revision(self):
        if self.parent:
            current_index = self.parent.children_ids.index(self.revision_id)
            if current_index != 0:
                return self.parent.children[current_index-1]
            elif current_index != None:
                print("hi")
                return self.parent
        return self
    
    def next_revision(self):
        if self.children:
            return self.children[0]
        elif self.parent:
            current_index = self.parent.children_ids.index(self.revision_id)
            if current_index < len(self.parent.children) - 1:
                return self.parent.children[current_index+1]
        return self

    def jump_to_revision(self, id):
        if id == self.revision_id:
            return self

        if id in self.parent_ids:
            return self.root_revision_nodes[self.parent_ids.index(id)]

        return "Not Found"

    def get_revisions(cls):
        return cls.revision_nodes
    
    def print_tree(self):
        seen_id = []

        for root in self.root_revision_nodes:
            if (root == None or root.revision_id == None or root.revision_id in seen_id):
                continue

            if root.children:
                _print_child_tree(self,root,seen_id)
            else:
                if self.revision_id == root.revision_id:
                    print('*|--', end = '')
                else:
                    print('|--', end = '')
                print(root.revision_id)

            seen_id.append(root.revision_id)

    