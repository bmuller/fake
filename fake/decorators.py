from fabric.tasks import WrappedCallableTask
from fake.api import execute, env, settings


class WrappedCallableDependenciesTask(WrappedCallableTask):
    def __init__(self, *args, **kwargs):
        super(WrappedCallableDependenciesTask, self).__init__(*args, **kwargs)
        self.prereqs = []
        self.postreqs = []

    def run(self, *args, **kwargs):
        for func in self.prereqs:
            execute(func, host=env.host)
        # set role specific variables from roledefs
        with settings(**self.role_settings()):
            result = super(WrappedCallableDependenciesTask, self).run(*args, **kwargs)
        for func in self.postreqs:
            execute(func, host=env.host)
        return result

    def role_settings(self):
        result = {'host_roles': []}
        rdefs = env.get('roledefs', {})
        for erole in env.effective_roles:
            settings = rdefs.get(erole, {})
            hosts = rdefs.get(erole, [])
            result.update(settings if isinstance(settings, dict) else {})
            if isinstance(settings, dict) and 'hosts' in settings:
                hosts = settings['hosts']
            if callable(hosts):
                hosts = hosts()
            if env.host in hosts:
                result['host_roles'].append(erole)
        for key in result.iterkeys():
            value = result[key]
            result[key] = value() if callable(value) else value
        return result


def task(*args, **kwargs):
    # if the wrapper hasn't been called
    if args and not kwargs:
        return WrappedCallableDependenciesTask(args[0])

    def wrapper(func):
        return WrappedCallableDependenciesTask(func, *args, **kwargs)

    return wrapper
