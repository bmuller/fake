"""
Based on https://github.com/capistrano/capistrano/blob/master/lib/capistrano/tasks/framework.rake
"""

from fake.decorators import task
from fake.api import execute, env


@task
def starting():
    """
    Start a deployment, make sure server(s) ready.
    """


@task
def started():
    """
    Started
    """


@task
def updating():
    """
    Update server(s) by setting up a new release.
    """


@task
def updated():
    """
    Updated
    """


@task
def reverting():
    """
    Revert server(s) to previous release.
    """


@task
def reverted():
    """
    Reverted
    """


@task
def publishing():
    """
    Publish the release.
    """


@task
def published():
    """
    Published
    """


@task
def finishing():
    """
    Finish the deployment, clean up server(s).
    """


@task
def finishing_rollback():
    """
    Finish the rollback, clean up server(s).
    """


@task
def finished():
    """
    Finished
    """


@task
def rollback():
    """
    Rollback to previous release.
    """
    tasks = (
        'starting started reverting reverted '
        'publishing published finishing_rollback finished'
    )
    for task in tasks.split():
        execute(task, host=env.host)


@task
def deploy():
    """
    Deploy a new release.
    """
    tasks = (
        'starting started updating updated '
        'publishing published finishing finished'
    )
    for task in tasks.split():
        execute(task, host=env.host)
