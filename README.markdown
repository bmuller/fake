# Fake: Fabric + Make
**Fake** makes Python's [Fabric](http://www.fabfile.org) act like Ruby's [Capistrano](http://capistranorb.com).  "Why in the world add to Fabric," you ask.  Great question!  Fabric is fantastic for streamlining the use of SSH, much like Ruby's [SSHKit](https://github.com/capistrano/sshkit).  Relyable deployments, however, typically involve more than just running a few commands on a remote server.  For instance, the deploy process in Capistrano (and mirrored in this project) relies on a few key features that aren't present in Fabric:

1. the ability to inject tasks in a dependency chain (before you run `TaskA`, always run `TaskB`)
1. configuration variables with values that are role specific
1. configuration values that are evaluated at run time (i.e., the ability to have values that are `callable` at runtime)

**Fake** does two things - it adds this necessary functionality as a layer on top of fabric and then provides a starting template for deploying code (with features like fast rollbacks, etc).

## Installation

```
pip install fake
```

In your `fabfile.py`, just replace instances of `fabric` with `fake`.  For instance, this line:

```python
from fabric.api import env, run, task
```

should become:

```python
from fake.api import env, run, task
```

## Fabric Additions
This section covers some of the additional functionality added to Fabric.

### Task Dependencies
There are a few aditional functions that have been added to enable dependency chains.  For instance, to always run `second` after `first` completes, use the `after` function like this:

```python
from fake.api import task, before, after

@task
def first():
    print 'first'

@task
def second():
    print 'second'
after(first, second)
```

If you run `fab first`, then both the `first` and `second` tasks will run.

To always run `first` as a prerequisite before running `second`, use `before` like this:

```python
from fake.api import task, before, after

@task
def first():
    print 'first'

@task
def second():
    print 'second'
before(second, first)
```

In this case, if you run `fab second`, then both the `first` and `second` tasks will run.

### Role Specific Config
Rather than having lots of tasks that each do the same thing but with different parameters, you can use the [roledefs](http://docs.fabfile.org/en/latest/usage/env.html#roledefs) environment variable to set additional environment variables based on role.  For instance, to set a `branch` variable differently based on role, set it like this:

```python
from fake.api import env, task

env.roledefs = {
    'staging': {
        'hosts': ['staging.example.com'],
        'branch': 'staging'
    },
    'production': {
        'hosts': ['example.com'],
        'branch': 'master'
    }
}

@task
def showbranch():
    print env.branch
```

This will print your two different branches if you run `fab -R staging showbranch` and `fab -R production showbranch`.

### Runtime Config Evaluation
Sometimes, a configuration value can only be known at run time.  One way to handle this situation would be to set an `env` variable to a function that is callable at runtime.  For instance, this would work:

```python
env.get_base_path = some_callable_function
env.app_path = lambda: os.path.join(env.get_base_path(), "app")

@task
def dosomething():
    print "app path is", env.app_path()
```

It works, but what would be nicer is a version of `env` that could automatically call a `callable` value before returning it.  Fake provides a `CallableEnv` that extends `env` to provide this functionality.  Here's an example of what the previous code could become:

```python
from fake.state import CallableEnv

env = CallableEnv(env)
env.get_base_path = some_callable_function
env.app_path = lambda: os.path.join(env.get_base_path, "app")

@task
def dosomething():
    print "app path is", env.app_path
```

It's a small difference syntactically, but makes it quite a bit easier when you don't have to consider whether a value is a `callable` or not.

## Deploying
Capistrano deploys code in roughly these steps:

1. Inside a `deploy_path`, create a `releases`, `shared`, and `repo` directory.
1. Clone a repository into the `repo` directory.
1. Extract a configurable branch into a subdirectory of the `releases` directory.
1. Symlink that subdirectory to a `current` folder in the `deploy_path`
1. Symlink shared files/folders in `shared` into `current`.

This means that your current code lives in `current`, and new deploys just change where that directory links to.  Rollbacks are as easy as changing where `current` points to.  You also get the benefit of automatically retaining the contents of whatever shared files/folders you want to keep (they actually live in the `shared` directory, and just get re-linked inside your `current` folder on each deploy/rollback).

Here's an example of all that's needed in a fabfile to do all of this:

```python
from fake.api import env, run, task
from fake.tasks.deploy import *

env.roledefs = {
    'staging': {
        'hosts': ['staging.example.com'],
        'branch': 'staging'
    },
    'production': {
        'hosts': ['example.com'],
        'branch': 'master'
    }
}

env.forward_agent = True
env.deploy_path = '/home/deployer/app'
env.user = 'deployer'
env.repo_url = 'git@github.com:user/repo.git'
env.linked_dirs = ['static']

@task
def restart():
    run('service gunicorn restart')
after(finished, restart)
```

Then, to deploy to staging it's as simple as running `fab -R staging deploy`.  After the deploy (or rollback) finishes (see the [`framework.py`](fake/tasks/framework.py) file in the `tasks` folder to see the steps) then the gunicorn service would be restarted.
