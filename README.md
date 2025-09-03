# Artifact Store

Tools for storing and retrieving artifacts (files and folders) on a locally accessible filesytem path.

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
via the argument `--storage-root`. Before using the a storage root, it must be initialized
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

## Development

Create a virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
``` 

This installs the development dependencies, including `pytest` for running the tests.