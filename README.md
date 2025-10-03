![test-workflow](https://github.com/pboettch/artifact-store/actions/workflows/python-package.yml/badge.svg)

# Artifact Filesystem Store

Tools for storing and retrieving artifacts (files and folders) on a locally accessible filesystem path.

## Features and Concepts

Artifacts are accessible for both, CIs and local developments - without needing a special blob-server available.

Artifacts have meta-data, custom key-value-pairs, like expire-time and creation-time.

Artifacts can be tagged, like a **latest** or a version.

Artifacts can be stored compressed or as copies. When copies are retrieved, the path inside the artifact-storeage
is accessed.

File access rights inside the storage-backend are handled by the filesystem and are out of scope of this library. 
This said, corruption done to the storage-backend can be fatal.

There is no central database for the artifact-catalog in the store. The filesystem-structure and 
meta-information-files alongside the artifact-archive or -folder are used to keep track.

Identification is done through naming and revisions. Revisions can be retrieved.

The artifact-store root is communicated via an environment variable or an argument to the cli-tool.

Artifacts are assigned to/stored under a namespace. A namespace is essentially a filesystem-path.

A list of folders and an exclusions list can be provided when storing and artifact.

Scripts for CMake and GitHub/GitLab Actions are provided to use the artifact-store in these environments.

## Usage

After installing the project (see below), the command line tool `artifact-store` is available.

A storage root must be provided via the environment variable `ARTIFACT_STORE_ROOT` or
via the argument `--storage-root`. Before using a storage root, it must be initialized
via 

```bash
artifact-store --storage-root <path> init
```

or 

```bash
export ARTIFACT_STORE_ROOT=<path>
artifact-store init
```

Once initialized, artifacts can be stored via

```bash
artifact-store store --revision <rev> --tag <tag> <namespace> <artifact-name> <paths/glob...>
```

and retrieved via

```bash
artifact-store retrieve --revision <rev> <namespace> <artifact-name> <target-path>
```

for revisions and 

```bash
artifact-store retrieve --tag <tag> <namespace> <artifact-name> <target-path>
```

for tags.


The command

```bash
artifact-store tag --tag <tag> <namespace> <artifact-name> <new_tag>
```

or

```bash
artifact-store tag --revision <revision> <namespace> <artifact-name> <tag>
```

can be used to assign tags to revisions or create new tags from existing ones.

```bash
artifact-store meta --tag <tag>|--revision <rev> <namespace> <artifact-name> ["<key>=<value>" ...]
```
can be used to set meta-data key-value-pairs. The command always returns the current
meta-data JSON-formatted.

The command

```bash
artifact-store list -n
```

lists all namespaces,

```bash
artifact-store list -a <namespace>
```
lists all artifacts in a namespace,

```bash
artifact-store list -r <namespace> <artifact-name>
```
lists all revisions of an artifact and

```bash
artifact-store list -t <namespace> <artifact-name>
```
lists all tags of an artifact.


## Development

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

This installs the development dependencies, including `pytest` for running the tests.

## Releases

First bump the version with `bumpver`: e.g.:

```bash
bumpver patch # or 'minor' or 'major'
```

then push the changes and tag:

```bash
git push && git push --tags
``` 

package:

```bash
python3 -m build --wheel
```

and upload to PyPI:

```bash
python3 -m twine upload dist/*
```

See also: https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/