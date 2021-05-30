import os


class Environment:
    configDir = '{}/.xtool/config'.format(os.getenv("HOME"))
    configFile = 'config.json'
    configFilePath = '{}/{}'.format(configDir, configFile)
    dataDir = '{}/.xtool/versions'.format(os.getenv("HOME"))
    instancesDir = '{}/.xtool/instances'.format(os.getenv("HOME"))
    snapshotsDir = '{}/.xtool/snapshots'.format(os.getenv("HOME"))
