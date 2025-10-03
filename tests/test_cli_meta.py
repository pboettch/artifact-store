import json

import pytest

from artifact_store.cli import main


@pytest.fixture
def init_fs(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/data")
    fs.create_file("/data/file.txt", contents="This is artifact 1")

    main(["init"])
    main(["store", "-r", "1", "-t", "t2", "-m", "a=1", "-m", "b=test", "project/a", "artifact1", "/data"])
    main(["store", "-r", "2", "-t", "t1", "project/a", "artifact1", "/data"])

    return fs


def test_cli_meta_retrieve_empty_meta(init_fs, capsys):
    main(["meta", "-r", "2", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "{}"


def test_cli_meta_retrieve_basic_meta(init_fs, capsys):
    main(["meta", "-r", "1", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == """{
  "a": "1",
  "b": "test"
}"""


def test_cli_meta_delete_key(init_fs, capsys):
    expected = """{
  "b": "test"
}"""

    main(["meta", "-r", "1", "project/a", "artifact1", "a="])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected

    main(["meta", "-r", "1", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected


def test_cli_meta_delete_all_keys(init_fs, capsys):
    main(["meta", "-r", "1", "project/a", "artifact1", "a=", "b="])
    captured = capsys.readouterr()
    assert captured.out.strip() == "{}"

    main(["meta", "-r", "1", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "{}"


def test_cli_meta_delete_and_re_add_key(init_fs, capsys):
    expected = """{
  "a": "2",
  "b": "test"
}"""
    main(["meta", "-r", "1", "project/a", "artifact1", "a=", "a=2"])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected

    main(["meta", "-r", "1", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected


def test_cli_meta_add_new_kv(init_fs, capsys):
    expected = """{
  "a": "2",
  "b": "test",
  "c": "hello"
}"""
    main(["meta", "-r", "1", "project/a", "artifact1", "c=hello", "a=2"])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected

    main(["meta", "-r", "1", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected


def test_cli_meta_get_internal_keys(init_fs, capsys):
    main(["meta", "-H", "-r", "1", "project/a", "artifact1"])

    expected_meta_filename = "/artifact-store/project/a/artifacts/artifact1-1.meta.json"
    meta = json.loads(open(expected_meta_filename).read())

    expected = f"""{{
  "__API__": "1",
  "__created_at": {meta["__created_at"]},
  "a": "1",
  "b": "test"
}}"""

    captured = capsys.readouterr()
    assert captured.out.strip() == expected


def test_cli_meta_unknown_archive(init_fs):
    with pytest.raises(SystemExit) as e:
        main(["meta", "-r", "1", "project/a", "artifact_unknown"])
    assert e.value.code == 1


def test_cll_meta_invaled_key(init_fs):
    with pytest.raises(SystemExit) as e:
        main(["meta", "-r", "1", "project/a", "artifact1", "invalidmeta"])
    assert e.value.code == 1


def test_cli_meta_delete_unknown_key(init_fs, capsys):
    main(["meta", "-r", "1", "project/a", "artifact1", "unknownkey="])
    captured = capsys.readouterr()
    assert captured.out.strip() == """{
  "a": "1",
  "b": "test"
}"""
