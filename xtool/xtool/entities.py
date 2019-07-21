from shutil import get_unpack_formats

from environment import Environment

"""
An entity can be a version of XWiki, an instance, a snapshot, …
We wrap the data structures contained in the configuration files in entities so that
we can use helper functions to quickly access computed attributes of an entity.
Entity objects rely directly on their configuration data structure (self.config).
"""
class Entity:
    def __init__(self, config):
        self.config = config

    """
    Allow direct access to the entity JSON content when needed
    """
    def __getitem__(self, key):
        return self.config[key]


class Snapshot(Entity):
    def __init__(self, config):
        super().__init__(config)

    def getFileExtension(self):
        availableFormats = get_unpack_formats()
        for format in availableFormats:
            if format[0] == self.config['format']:
                ## TODO: Refactor to allow check on any possible format
                return format[1][0]
        return ''

    def getFileName(self, includeExtension=True):
        if includeExtension:
            return '{}{}'.format(self.config['name'],
                                  self.getFileExtension())
        else:
            return self.config['name']

    def getPath(self, includeExtension=True):
        return '{}/{}'.format(Environment.snapshotsDir,
                              self.getFileName(includeExtension))
