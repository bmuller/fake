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
            result.update(settings if isinstance(settings, dict) else {})
        for role in [r for r in env.roles if r in rdefs]:
            hosts = rdefs[role]
            if isinstance(hosts, dict) and 'hosts' in hosts:
                hosts = hosts['hosts']
            if callable(hosts):
                hosts = hosts()
            if isinstance(hosts, list) and env.host in hosts:
                result['host_roles'].append(role)
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
