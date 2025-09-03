import pytest

from artifact_store.cli import main


@pytest.fixture
def init_fs(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/data")
    fs.create_file("/data/file.txt", contents="This is artifact 1")

    main(["init"])
    main(["store", "-t", "latest", "-r", "1", "project/a", "artifact1", "/data"])

    return fs


def test_cli_retrieve_artifact_with_revision_and_check_content(init_fs):
    main(["retrieve", "-r", "1", "project/a", "artifact1", "/retrieved"])

    with open("/retrieved/artifact1/data/file.txt", "r") as f:
        content = f.read()
    assert content == "This is artifact 1"


def test_cli_retrieve_artifact_with_tag_and_check_content(init_fs):
    main(["retrieve", "-t", "latest", "project/a", "artifact1", "/retrieved"])

    with open("/retrieved/artifact1/data/file.txt", "r") as f:
        content = f.read()
    assert content == "This is artifact 1"


def test_cli_retrieve_artifact_with_unknown_tag(init_fs):
    with pytest.raises(SystemExit) as e:
        main(["retrieve", "-t", "unknown", "project/a", "artifact1", "/retrieved"])
    assert e.value.code == 1


def test_cli_retrieve_artifact_with_unknown_revision(init_fs):
    with pytest.raises(SystemExit) as e:
        main(["retrieve", "-r", "3", "project/a", "artifact1", "/retrieved"])
    assert e.value.code == 1


def test_cli_retrieve_unknown_artifact(init_fs):
    with pytest.raises(SystemExit) as e:
        main(["retrieve", "-r", "1", "project/a", "artifact_not_known", "/retrieved"])
    assert e.value.code == 1
