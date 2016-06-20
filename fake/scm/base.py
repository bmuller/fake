class SCMStrategy(object):
    def check(self):
        """
        Check that the repository is reachable.
        """
        raise NotImplementedError

    def test(self):
        """
        Determine if the repo has been mirrored.
        """
        raise NotImplementedError

    def clone(self):
        """
        Clone the repo to the cache.
        """
        raise NotImplementedError

    def update(self):
        """
        Update the repo mirror to reflect the origin state.
        """
        raise NotImplementedError

    def release(self):
        """
        Copy repo to releases.
        """
        raise NotImplementedError

    def fetch_revision(self):
        """
        Determine the revision that will be deployed.
        """
        raise NotImplementedError
