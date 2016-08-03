from importlib import import_module
import time

from fabric.utils import puts

from fake.utils import Path
from fake.decorators import task
from fake.api import execute, env, paths, run, cd
from fake.tasks.framework import *
from fake.operations import test


# Set defaults
paths.setdefault('deploy_path', '/var/www/app')
paths.setdefault('repo_path', lambda: Path(paths.deploy_path, 'repo'))
paths.setdefault('shared_path', lambda: Path(paths.deploy_path, 'shared'))
paths.setdefault('releases_path', lambda: Path(paths.deploy_path, 'releases'))
paths.setdefault('release_path', lambda: paths.current_path)
paths.setdefault('current_path', lambda: Path(paths.deploy_path, 'current'))

env.setdefault('linked_dirs', [])
env.setdefault('linked_files', [])
env.setdefault('scm', 'git')
env.setdefault('branch', 'master')
env.setdefault('keep_releases', 5)


def _set_scm():
    """
    Import correct SCM module into environment.
    """
    g = globals()
    if 'scm' not in g:
        g['scm'] = import_module("fake.scm.%(scm)s" % env)


@task
def starting():
    """
    Start a deployment, make sure server(s) ready.
    """
    execute('check', host=env.host)
    execute('set_previous_revision', host=env.host)


@task
def check():
    """
    Check required files and directories exist
    """
    if 'deploy_path' not in env or 'repo_url' not in env:
        raise RuntimeError("You must set deploy_path and repo_url in your environment")
    _set_scm()
    execute(scm.check, host=env.host)
    run("mkdir -p %s %s" % (paths.shared_path, paths.releases_path))
    if len(env.linked_dirs) > 0:
        dirs = map(str, paths.shared_path.rooted(env.linked_dirs))
        run("mkdir -p %s" % " ".join(dirs))
    if len(env.linked_files) > 0:
        dirs = [paths.shared_path.join(f).dirname for f in env.linked_files]
        run("mkdir -p %s" % " ".join(dirs))


@task
def set_previous_revision():
    target = paths.release_path.join("REVISION")
    if test("[ -f %s ]" % target):
        env.previous_revision = run('cat %s' % target)


@task
def updating():
    """
    Update server(s) by setting up a new release.
    """
    # this may have been set on a previous run on another server.
    # it's used later, so don't update if it's already been set.
    if 'release_timestamp' not in env:
        env.release_timestamp = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    paths.release_path = paths.releases_path.join(env.release_timestamp)
    _set_scm()
    execute(scm.create_release, host=env.host)
    execute(scm.set_current_revision, host=env.host)
    with cd(paths.release_path):
        run("echo \"%s\" >> REVISION" % env.current_revision)
    execute("symlink_folders", host=env.host)
    execute("symlink_files", host=env.host)


@task
def symlink_folders():
    """
    Symlink linked folders.
    """
    if len(env.linked_dirs) == 0:
        return

    # make sure parents exist in the release path
    dirs = [paths.release_path.join(d).dirname for d in env.linked_dirs]
    run("mkdir -p %s" % " ".join(dirs))

    # link some dirs
    for d in env.linked_dirs:
        target = paths.release_path.join(d)
        source = paths.shared_path.join(d)
        if test("[ -L %s ]" % target):
            continue
        if test("[ -d %s ]" % target):
            run("rm -rf %s" % target)
        run("ln -s %s %s" % (source, target))


@task
def symlink_files():
    """
    Symlink linked files.
    """
    if len(env.linked_files) == 0:
        return

    # make sure parents exist in the release path
    dirs = [paths.release_path.join(f).dirname for f in env.linked_files]
    run("mkdir -p %s" % " ".join(dirs))

    # link some files
    for f in env.linked_files:
        target = paths.release_path.join(f)
        source = paths.shared_path.join(f)
        if test("[ -L %s ]" % target):
            continue
        if test("[ -f %s ]" % target):
            run("rm -f %s" % target)
        run("ln -s %s %s" % (source, target))


@task
def publishing():
    """
    Symlink current release.
    """
    tmp_current_path = paths.release_path.parent.join(paths.current_path.basename)
    run("ln -s %s %s" % (paths.release_path, tmp_current_path))
    run("mv %s %s" % (tmp_current_path, paths.current_path.parent))


@task
def finishing():
    execute("cleanup", host=env.host)


@task
def cleanup():
    """
    Clean up old releases
    """
    puts("Keeping last %i releases" % env.keep_releases)
    releases = run("ls -xtr %(releases_path)s" % paths).split()
    if len(releases) <= env.keep_releases:
        return

    for release in releases[:(len(releases) - env.keep_releases)]:
        run("rm -rf %s" % paths.releases_path.join(release))


@task
def reverting():
    releases = run("ls -xt %s" % paths.releases_path).split()
    if len(releases) < 2:
        raise RuntimeError("Cannot rollback without a previous deploy")
    env.release_timestamp = releases[1]
    paths.release_path = paths.releases_path.join(env.release_timestamp)


@task
def finishing_rollback():
    execute("cleanup_rollback", host=env.host)


@task
def cleanup_rollback():
    """
    Remove and archive rolled-back release.
    """
    last_release = run("ls -xt %s" % paths.releases_path).split()[0]
    last_release_path = paths.releases_path.join(last_release)
    args = (paths.current_path, last_release_path)
    if test("[ `readlink %s` != %s ]" % args):
        fname = Path(paths.deploy_path, "rolled-back-release-%s.tar.gz" % last_release)
        run("tar -czf %s %s" % (fname, last_release_path))
        run("rm -rf %s" % last_release_path)
    else:
        puts("Last release is the current release, skip cleanup_rollback.")
