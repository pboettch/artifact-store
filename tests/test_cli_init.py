from artifact_store.cli import main


def test_cli_init(fs):
    main(["-s", "/artifact-store", "init"])
    assert fs.exists("/artifact-store/.artifact_store")


def test_cli_init_existing_dir_is_not_storage_root(fs):
    fs.create_dir("/artifact-store")

    try:
        main(["-s", "/artifact-store", "init"])
    except SystemExit as e:
        assert e.code == 1
    assert not fs.exists("/artifact-store/.artifact_store")


def test_cli_init_storage_dir_is_an_existing_file(fs):
    fs.create_file("/artifact-store")
    try:
        main(["-s", "/artifact-store", "init"])
    except SystemExit as e:
        assert e.code == 1
    assert not fs.exists("/artifact-store/.artifact_store")


def test_cli_init_storage_dir_from_environment_variable(fs, monkeypatch):
    monkeypatch.setenv("ARTIFACT_STORE_ROOT", "/artifact-store")
    main(["init"])
    assert fs.exists("/artifact-store/.artifact_store")


def test_cli_no_storage_path(fs):
    try:
        main(["init"])
    except SystemExit as e:
        assert e.code == 1


def test_cli_no_command(fs):
    try:
        main(["-s", "/artifact-store"])
    except SystemExit as e:
        assert e.code == 2


def test_verbose_flag(fs, capsys):
    main(["-s", "/artifact-store", "-v", "init"])
    captured = capsys.readouterr()
    assert captured.err == "Initializing artifact store at '/artifact-store'\n" \
                           "Artifact store initialized at '/artifact-store'\n"
