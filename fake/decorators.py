from fabric.tasks import WrappedCallableTask
from fake.api import execute, env, settings


class WrappedCallableDependenciesTask(WrappedCallableTask):
    def __init__(self, *args, **kwargs):
        super(WrappedCallableDependenciesTask, self).__init__(*args, **kwargs)
        self.prereqs = []
        self.postreqs = []

    def run(self, *args, **kwargs):
        for func in self.prereqs:
            execute(func)
        # set role specific variables from roledefs
        with settings(**self.role_settings()):
            result = super(WrappedCallableDependenciesTask, self).run(*args, **kwargs)
        for func in self.postreqs:
            execute(func)
        return result

    def role_settings(self):
        result = {}
        rdefs = env.get('roledefs', {})
        for erole in env.effective_roles:
            result.update(rdefs.get(erole, {}))
        return result

def task(*args, **kwargs):
    # if the wrapper hasn't been called
    if args and not kwargs:
        return WrappedCallableDependenciesTask(args[0])

    def wrapper(func):
        return WrappedCallableDependenciesTask(func, *args, **kwargs)

    return wrapper
