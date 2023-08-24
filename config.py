import pathlib


real_path = pathlib.Path.cwd().resolve()

data_path = real_path.joinpath("data")


locales_path = data_path.joinpath("locales")
