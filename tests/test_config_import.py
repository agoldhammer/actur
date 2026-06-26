def test_read_conf_is_exported_from_config_package():
    from actur.config import read_conf

    assert callable(read_conf)
