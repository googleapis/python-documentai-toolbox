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
#


from google.cloud.documentai_toolbox import page


def test_table_to_csv():
    header_rows = [["This", "Is", "A", "Header", "Test"],["", "", "A", "Sub", "Header"]]
    body_rows = [["This", "Is", "A", "Body", "Test"],["1","2","3","4","5"]]
    table = page.Table(
        documentai_table=None, header_rows=header_rows, body_rows=body_rows
    )
    contents = table.to_csv()

    assert (
        contents
        == """This,Is,A,Header,Test
,,A,Sub,Header
This,Is,A,Body,Test
1,2,3,4,5
"""
    )


def test_table_to_csv_with_empty_body_rows():
    header_rows = [["This", "Is", "A", "Header", "Test"]]
    table = page.Table(documentai_table=None, header_rows=header_rows, body_rows=[])

    contents = table.to_csv()

    assert (
        contents
        == """This,Is,A,Header,Test
"""
    )


def test_table_to_csv_with_empty_header_rows():
    body_rows = [["This"], ["Is"], ["A"], ["Body"], ["Test"]]
    table = page.Table(documentai_table=None, header_rows=[], body_rows=body_rows)

    contents = table.to_csv()

    assert (
        contents
        == """""
This
Is
A
Body
Test
"""
    )


def test_table_to_csv_with_empty_header_rows_and_single_body():
    body_rows = [["Body"]]
    table = page.Table(documentai_table=None, header_rows=[], body_rows=body_rows)

    contents = table.to_csv()

    assert (
        contents
        == """""
Body
"""
    )
