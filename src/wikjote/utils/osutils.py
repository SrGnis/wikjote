import os


def mkdir_if_not_exists(path: str):
    if not os.path.exists(path):
        os.mkdir(path)
