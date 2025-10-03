import pytest

from artifact_store.cli import main


@pytest.fixture
def init_fs(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")

    fs.create_dir("/data")
    fs.create_file("/data/file.txt", contents="This is artifact 1")

    main(["init"])
    main(["store", "-r", "1", "-t", "t2", "project/a", "artifact1", "/data"])
    main(["store", "-r", "2", "-t", "t1", "project/a", "artifact1", "/data"])
    main(["store", "-r", "1", "project/a", "artifact2", "/data"])

    return fs


@pytest.mark.parametrize("main_args", [
    (["list"]),
    (["list", "-n", "extra_arg"]),
    (["list", "-a", "project/a", "extra_arg"]),
    (["list", "-r"]),
    (["list", "-r", "project/a"]),
    (["list", "-r", "project/a", "artifact1", "extra_arg"]),
    (["list", "-t"]),
    (["list", "-t", "project/a"]),
    (["list", "-t", "project/a", "artifact1", "extra_arg"]),
])
def test_cli_list_argument_combination_failures(init_fs, capsys, main_args):
    with pytest.raises(SystemExit) as e:
        main(main_args)
    assert e.value.code == 2


def test_cli_list_namespaces(init_fs, capsys):
    main(["list", "-n"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "project/a"


def test_cli_list_artifacts(init_fs, capsys):
    main(["list", "-a", "project/a"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "artifact1\nartifact2"


def test_cli_list_artifacts_unknown_namespace(init_fs, capsys):
    with pytest.raises(SystemExit) as e:
        main(["list", "-a", "unknown/ns"])
    assert e.value.code == 1


def test_cli_list_revisions(init_fs, capsys):
    main(["list", "-r", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "1\n2"


def test_cli_list_revisions_with_unknown_namespace(init_fs, capsys):
    with pytest.raises(SystemExit) as e:
        main(["list", "-r", "unknown/ns", "artifact1"])
    assert e.value.code == 1


def test_cli_list_revisions_with_unknown_artifact(init_fs, capsys):
    with pytest.raises(SystemExit) as e:
        main(["list", "-r", "project/a", "artifact3"])
    assert e.value.code == 1


def test_cli_list_tags(init_fs, capsys):
    main(["list", "-t", "project/a", "artifact1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "t1\nt2"


def test_cli_list_tags_with_unknown_namespace(init_fs, capsys):
    with pytest.raises(SystemExit) as e:
        main(["list", "-t", "unknown/ns", "artifact1"])
    assert e.value.code == 1


def test_cli_list_tags_with_unknown_artifact(init_fs, capsys):
    main(["list", "-t", "project/a", "artifact3"])
    captured = capsys.readouterr()
    assert captured.out.strip() == ""
