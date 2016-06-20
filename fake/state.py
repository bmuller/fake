from fabric.state import env


class CallableEnv(env.__class__):
    def __getitem__(self, key):
        # if it's set in env, then it trumps whats here
        if key in env:
            return env[key]
        value = super(CallableEnv, self).__getitem__(key)
        return value() if callable(value) else value

paths = CallableEnv()
