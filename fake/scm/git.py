from fabric.utils import puts
from fake.scm.base import SCMStrategy
from fake.api import task, env, run, paths, cd, test


class Git(SCMStrategy):
    def git(self, cmd):
        return run("git %s" % cmd)

    def check(self):
        self.git("ls-remote --heads %(repo_url)s > /dev/null" % env)

    def test(self):
        return test("[ -f %(repo_path)s/HEAD ]" % paths)

    def clone(self):
        args = (env.repo_url, paths.repo_path)
        self.git("clone --mirror %s %s > /dev/null" % args)

    def update(self):
        self.git("remote update --prune > /dev/null")

    def release(self):
        args = (env.branch, paths.release_path)
        self.git("archive %s | tar -x -f - -C %s" % args)

    def fetch_revision(self):
        return self.git("rev-list --max-count=1 %(branch)s" % env)


# this is safe to do here, because this module will be included as necessary,
# after the env settings in the fabfile.py have been set
strategy = env.get('git_strategy', Git())


@task
def check():
    """
    Check that the repository is reachable.
    """
    strategy.check()


@task
def create_release():
    """
    Copy repo to releases.
    """
    if strategy.test():
        puts("mirror exists at %(repo_path)s" % paths)
    else:
        with cd(paths.deploy_path):
            strategy.clone()

    with cd(paths.repo_path):
        strategy.update()
        run("mkdir -p %(release_path)s" % paths)
        strategy.release()


@task
def set_current_revision():
    with cd(paths.repo_path):
        env.current_revision = strategy.fetch_revision()
