import tomllib

conf_file_name = "actur.toml"


def read_conf():
    with open(conf_file_name, "rb") as fp:
        conf = tomllib.load(fp)
        print(conf)
