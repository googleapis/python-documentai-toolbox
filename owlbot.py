# Copyright 2021 Google LLC
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

"""This script is used to synthesize generated parts of this library."""

import pathlib

import synthtool as s
from synthtool import gcp

REPO_ROOT = pathlib.Path(__file__).parent.absolute()

common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(
    unit_test_python_versions=["3.8", "3.9", "3.10", "3.11", "3.12"],
    system_test_python_versions=["3.8", "3.9", "3.10", "3.11", "3.12"],
    cov_level=99,
    intersphinx_dependencies={
        "pandas": "https://pandas.pydata.org/pandas-docs/stable/"
    },
)
s.move(templated_files, excludes=["docs/multiprocessing.rst", "README.rst"])

# Only test the latest runtime in the `prerelease_deps` session
s.replace("noxfile.py",
    """@nox.session\(python=SYSTEM_TEST_PYTHON_VERSIONS\)
@nox.parametrize\(
    "protobuf_implementation",
    \[ "python", "upb", "cpp" \],
\)
def prerelease_deps\(session, protobuf_implementation\):""",
    """@nox.session(python=SYSTEM_TEST_PYTHON_VERSIONS[-1])
@nox.parametrize(
    "protobuf_implementation",
    ["python", "upb", "cpp"],
)
def prerelease_deps(session, protobuf_implementation):"""
)

# ----------------------------------------------------------------------------
# Run blacken session
# ----------------------------------------------------------------------------

s.shell.run(["nox", "-s", "format"], hide_output=False)
