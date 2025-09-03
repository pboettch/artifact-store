import json
import os
import tarfile

import pytest

from artifact_store.cli import main


@pytest.fixture
def init_fs(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/data")
    fs.create_file("/data/artifact1", contents="This is artifact 1")

    fs.create_file("/data/file.txt")
    fs.create_file("/data/file.md")

    fs.create_dir("/data/a")
    fs.create_file("/data/a/file.txt")
    fs.create_file("/data/a/file.md")
    fs.create_dir("/data/a/a")
    fs.create_file("/data/a/a/file.txt")
    fs.create_file("/data/a/a/file.md")
    fs.create_dir("/data/a/a/a")
    fs.create_file("/data/a/a/a/file.md")
    fs.create_dir("/data/a/b")
    fs.create_file("/data/a/b/file.md")

    fs.create_dir("/data/b")
    fs.create_file("/data/b/file.txt")
    fs.create_file("/data/b/file.md")

    main(["init"])

    return fs


def test_cli_store_one_artifact_roundtrip(init_fs):
    main(["store", "-r", "1", "project/a", "artifact1", "/data"])

    expected_filename = "/artifact-store/project/a/artifacts/artifact1-1.tar.xz"
    assert os.path.isfile(expected_filename)

    expected_meta_filename = "/artifact-store/project/a/artifacts/artifact1-1.meta.json"
    assert os.path.isfile(expected_meta_filename)

    tar = tarfile.open(expected_filename)
    assert len(tar.getnames()) == 17
    f = tar.extractfile("data/artifact1")
    assert f.read() == b"This is artifact 1"


def test_cli_store_one_artifact_and_check_complete_store_root(init_fs):
    main(["store", "-r", "1", "project/a", "artifact1", "/data"])

    files = []
    for root, _, filenames in os.walk("/artifact-store"):
        for f in filenames:
            files.append(os.path.join(root, f))
    assert sorted(files) == sorted([
        "/artifact-store/.artifact_store",
        "/artifact-store/project/a/artifacts/artifact1-1.meta.json",
        "/artifact-store/project/a/artifacts/artifact1-1.tar.xz"])


def test_cli_store_one_artifact_and_tag_latest(init_fs):
    main(["store",
          "-t", "latest",
          "-r", "1",
          "project/a", "artifact1", "/data"])

    assert os.path.islink("/artifact-store/project/a/tags/artifact1-latest")
    assert os.path.realpath(
        "/artifact-store/project/a/tags/artifact1-latest") == "/artifact-store/project/a/artifacts/artifact1-1.tar.xz"

    files = []
    for root, _, filenames in os.walk("/artifact-store"):
        for f in filenames:
            files.append(os.path.join(root, f))
    assert sorted(files) == sorted([
        "/artifact-store/.artifact_store",
        "/artifact-store/project/a/artifacts/artifact1-1.meta.json",
        "/artifact-store/project/a/artifacts/artifact1-1.tar.xz",
        "/artifact-store/project/a/tags/artifact1-latest",
    ])


def test_cli_store_one_artifact_and_tag_and_retag_latest(init_fs):
    main(["store",
          "-t", "latest",
          "-r", "1",
          "project/a", "artifact1", "/data"])

    assert os.path.islink("/artifact-store/project/a/tags/artifact1-latest")
    assert os.path.realpath("/artifact-store/project/a/tags/artifact1-latest") == \
           "/artifact-store/project/a/artifacts/artifact1-1.tar.xz"

    main(["store",
          "-t", "latest",
          "-r", "2",
          "project/a", "artifact1", "/data"])

    assert os.path.islink("/artifact-store/project/a/tags/artifact1-latest")
    assert os.path.realpath("/artifact-store/project/a/tags/artifact1-latest") == \
           "/artifact-store/project/a/artifacts/artifact1-2.tar.xz"

    files = []
    for root, _, filenames in os.walk("/artifact-store"):
        for f in filenames:
            files.append(os.path.join(root, f))
    assert sorted(files) == ["/artifact-store/.artifact_store",
                             "/artifact-store/project/a/artifacts/artifact1-1.meta.json",
                             "/artifact-store/project/a/artifacts/artifact1-1.tar.xz",
                             "/artifact-store/project/a/artifacts/artifact1-2.meta.json",
                             "/artifact-store/project/a/artifacts/artifact1-2.tar.xz",
                             "/artifact-store/project/a/tags/artifact1-latest",
                             ]


def test_cli_store_check_default_metadata(init_fs):
    main(["store", "-r", "1", "project/a", "artifact1", "/data"])

    expected_meta_filename = "/artifact-store/project/a/artifacts/artifact1-1.meta.json"
    assert os.path.isfile(expected_meta_filename)

    with open(expected_meta_filename, "r") as f:
        meta_content = json.load(f)

        assert meta_content["__API__"] == "1"
        assert meta_content["__created_at"] is not None
        assert isinstance(meta_content["__created_at"], int)


def test_cli_store_add_metadata(init_fs):
    main(["store", "-r", "1", "-m", "key1=value1", "-m", "key2=value2", "project/a", "artifact1", "/data"])

    expected_meta_filename = "/artifact-store/project/a/artifacts/artifact1-1.meta.json"
    assert os.path.isfile(expected_meta_filename)

    with open(expected_meta_filename, "r") as f:
        meta_content = json.load(f)

        assert meta_content["key1"] == "value1"
        assert meta_content["key2"] == "value2"


def test_cli_store_invalid_metadata_format(init_fs):
    try:
        main(["store", "-r", "1", "-m", "invalidmeta", "project/a", "artifact1", "/data"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_store_artifact_already_exists(init_fs):
    main(["store", "-r", "1", "project/a", "artifact1", "/data"])

    try:
        main(["store", "-r", "1", "project/a", "artifact1", "/data"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_store_exclude_patterns(init_fs):
    main(["store",
          "-r", "1",
          "--exclude", "*file.txt",  # exclude all file.txt
          "--exclude", "data/artifact1",  # exclude default created artifact-test-file
          "--exclude", "*/a/**/file.md",  # exclude all file.md in a/ and subdirs
          "project", "artifact1", "/data"])

    expected_filename = "/artifact-store/project/artifacts/artifact1-1.tar.xz"
    tar = tarfile.open(expected_filename)
    print(sorted(tar.getnames()))
    assert sorted(tar.getnames()) == ["data",
                                      "data/a",
                                      "data/a/a",
                                      "data/a/a/a",
                                      "data/a/b",
                                      "data/a/file.md",
                                      "data/b",
                                      "data/b/file.md",
                                      "data/file.md",
                                      ]


def test_cli_store_path_globs(init_fs):
    main(["store",
          "-r", "1",
          "project", "artifact1", "data/**/file.md"])

    expected_filename = "/artifact-store/project/artifacts/artifact1-1.tar.xz"
    tar = tarfile.open(expected_filename)

    assert sorted(tar.getnames()) == ['data/a/a/a/file.md',
                                      'data/a/a/file.md',
                                      'data/a/b/file.md',
                                      'data/a/file.md',
                                      'data/b/file.md',
                                      'data/file.md']


def test_cli_store_error_out_if_empty(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    main(["init"])
    try:
        main(["store", "-r", "1", "project/a", "artifact1", "/data"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_store_already_existing_artifact(init_fs):
    main(["store", "-r", "1", "project/a", "artifact1", "/data"])

    try:
        main(["store", "-r", "1", "project/a", "artifact1", "/data"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_store_invalid_artifact_store_root(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/data")

    try:
        main(["store", "-r", "1", "project/a", "artifact1", "/data"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_store_invalid_artifact_store_root_missing_magic_file(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/artifact-store")
    fs.create_dir("/data")

    try:
        main(["store", "-r", "1", "project/a", "artifact1", "/data"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_store_copy_is_not_implemented(init_fs):
    try:
        main(["store", "-r", "1", "-c", "project/a", "artifact1", "/data"])
    except NotImplementedError as e:
        assert str(e) == "Copying files is not implemented yet."
