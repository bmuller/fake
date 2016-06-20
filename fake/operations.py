from fabric.operations import run


def test(cmd):
    return run(cmd, shell=True, quiet=True).succeeded
