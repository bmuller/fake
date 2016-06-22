from os.path import join, dirname, basename, normpath


class Path(object):
    def __init__(self, *paths):
        self.path = normpath(join(*paths))

    def join(self, *others):
        return Path(str(self), *others)

    def __str__(self):
        return self.path

    def rooted(self, paths):
        return map(self.join, paths)

    @property
    def parent(self):
        return self.join('..')

    @property
    def basename(self):
        return basename(str(self))

    @property
    def dirname(self):
        return dirname(str(self))
