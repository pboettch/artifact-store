import os

import pytest

from artifact_store.cli import main


@pytest.fixture
def init_fs(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/data")
    fs.create_file("/data/file.txt", contents="This is artifact 1")

    main(["init"])
    main(["store", "-r", "1", "project/a", "artifact1", "/data"])
    main(["store", "-r", "2", "project/a", "artifact1", "/data"])

    return fs


def test_cli_tag_artifact_from_revision_and_tag_with_new_tag(init_fs):
    main(['-v', "tag", "-r", "1", "project/a", "artifact1", "latest"])
    main(['-v', "tag", "-r", "2", "project/a", "artifact1", "stable"])

    expected_link = "/artifact-store/project/a/tags/artifact1-latest"
    assert os.path.islink(expected_link)
    assert os.readlink(expected_link) == "/artifact-store/project/a/artifacts/artifact1-1.tar.xz"

    expected_link = "/artifact-store/project/a/tags/artifact1-stable"
    assert os.path.islink(expected_link)
    assert os.readlink(expected_link) == "/artifact-store/project/a/artifacts/artifact1-2.tar.xz"

    main(["tag", "-t", "stable", "project/a", "artifact1", "latest"])

    expected_link = "/artifact-store/project/a/tags/artifact1-latest"
    assert os.path.islink(expected_link)
    assert os.readlink(expected_link) == "/artifact-store/project/a/artifacts/artifact1-2.tar.xz"


def test_cli_tag_artifact_with_tag_and_revision_fails(init_fs):
    try:
        main(["tag", "-r", "1", "-t", "stable", "project/a", "artifact1", "latest"])
    except SystemExit as e:
        assert e.code == 2


def test_cli_tag_artifact_with_unknown_revision(init_fs):
    try:
        main(["tag", "-r", "3", "project/a", "artifact1", "latest"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_tag_artifact_with_unknown_tag(init_fs):
    try:
        main(["tag", "-t", "unknown", "project/a", "artifact1", "latest"])
    except SystemExit as e:
        assert e.code == 1
