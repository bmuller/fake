from fabric import context_managers
from fake.utils import Path


def cd(path):
    path = str(path) if isinstance(path, Path) else path
    return context_managers.cd(path)
