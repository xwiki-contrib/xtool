import os


class Environment:
    configDir = '{}/.xtool/config'.format(os.getenv("HOME"))
    configFilePath = '{}/config.json'.format(configDir)
    dataDir = '{}/.xtool/versions'.format(os.getenv("HOME"))
    instancesDir = '{}/.xtool/instances'.format(os.getenv("HOME"))
    snapshotsDir = '{}/.xtool/snapshots'.format(os.getenv("HOME"))
