import json
import logging
import os
import os.path

from environment import Environment
from packaging import version

from entities import Snapshot


class ConfigManager:
    logger = logging.getLogger('ConfigManager')

    defaultConfig = {
        'instances': [],
        'versions': [],
        'snapshots': [],
        'preferences': {
            'editor': None,
            'debug': False,
            'snapshot-format': 'xztar'
        }
    }

    def __init__(self):
        self.__ensureExistingFolders()
        self.__loadConfig()

    def __ensureExistingFolders(self):
        foldersToCheck = [Environment.configDir, Environment.dataDir,
                          Environment.instancesDir, Environment.snapshotsDir]

        for folder in foldersToCheck:
            self.logger.debug('Checking directory {}'.format(folder))
            if not os.path.isdir(folder):
                self.logger.info('Creating directory {}'.format(folder))
                os.makedirs(folder)

    def __ensureExistingProperties(self):
        propertiesToCheck = self.defaultConfig.keys()

        configKeys = self.config.keys()
        for property in propertiesToCheck:
            if property not in configKeys:
                self.config[property] = self.defaultConfig[property]

    # Make sure that the given preference is actually something that we want to store
    def __ensureValidPreference(self, preferenceName):
        return preferenceName in self.defaultConfig['preferences'].keys()

    # Load the configuration content
    def __loadConfig(self):
        baseConfigDir = os.path.dirname(Environment.configFilePath)

        if not os.path.exists(baseConfigDir):
            self.logger.info('No configuration directory found, creating {}.'.format(baseConfigDir))
            os.makedirs(baseConfigDir)

        if not os.path.isfile(Environment.configFilePath):
            self.logger.info(
                    'No configuration file found, creating a new one in {}.'.format(Environment.configFilePath))
            self.config = self.defaultConfig
            self.__saveConfig()
        else:
            with open(Environment.configFilePath, 'r+') as configFile:
                self.config = json.load(configFile)
                self.__ensureExistingProperties()
                self.logger.debug(self.config)
                # Create local snapshots
                self.snapshots = []
                for snapshot in self.config['snapshots']:
                    self.snapshots.append(Snapshot(snapshot))

    def __saveConfig(self):
        dumps = json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))
        with open(Environment.configFilePath, 'w+') as configFile:
            configFile.write(dumps)

    def versions(self):
        return self.config['versions']

    def instances(self):
        return self.config['instances']

    def getSnapshot(self, snapshotName):
        matchingSnapshots = [s for s in self.snapshots if s['name'] == snapshotName]
        if len(matchingSnapshots) == 0:
            return None
        else:
            return matchingSnapshots[0]

    def get(self, preferenceName):
        if preferenceName in self.config['preferences'].keys():
            return self.config['preferences'][preferenceName]
        else:
            return None

    """
    Set the given value to the given preference
    * Returns True if the operation succeeded
    * Returns False in case the preference name is not valid
    """
    def set(self, preferenceName, value):
        if self.__ensureValidPreference(preferenceName):
            self.config['preferences'][preferenceName] = value
            return True
        else:
            return False

    def persist(self):
        # Collect the potenial changes in the entities
        #self.config['versions'] = [v.config for v in self.versions]
        #self.config['instances'] = [i.config for i in self.instances]
        self.config['snapshots'] = [s.config for s in self.snapshots]

        # Sort the versions by their number
        self.config['versions'] = sorted(self.config['versions'], key=lambda x: version.parse(x))

        # Sort the instances alphebetically
        self.config['instances'] = sorted(self.config['instances'], key=lambda x: x['name'])

        self.__saveConfig()
