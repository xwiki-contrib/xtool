import json
import logging
import os
import os.path
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile

class Environment:
    configFilePath = '{}/config/config.json'.format(os.getcwd())
    dataDir = '{}/versions'.format(os.getcwd())
    instancesDir = '{}/instances'.format(os.getcwd())

class ConfigManager:
    logger = logging.getLogger('ConfigManager')

    def __init__(self):
        # Load the configuration content
        self.__loadConfig()

    def __loadConfig(self):
        baseConfigDir = os.path.dirname(Environment.configFilePath)

        if not os.path.exists(baseConfigDir):
            self.logger.info('No configuration directory found, creating {}.'.format(baseConfigDir))
            os.makedirs(baseConfigDir)

        if not os.path.isfile(Environment.configFilePath):
            self.logger.info(
                    'No configuration file found, creating a new one in {}.'.format(Environment.configFilePath))
            with open(Environment.configFilePath, 'w+') as emptyFile:
                emptyFile.write('{"instances":[], "versions":[]}')

        with open(Environment.configFilePath, 'r+') as configFile:
            self.config = json.load(configFile)
            self.logger.debug(self.config)

    def __saveConfig(self):
        baseConfigDir = os.path.dirname(Environment.configFilePath)

        with open(Environment.configFilePath, 'w+') as configFile:
            configFile.write(json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': ')))

    def versions(self):
        return self.config['versions']

    def instances(self):
        return self.config['instances']

    def persist(self):
        self.__saveConfig()

class VersionManager:
    logger = logging.getLogger('VersionManager')

    def __init__(self, configManager):
        self.configManager = configManager

    def __generateDownloadLink(self, version, extension):
        baseURL = ('http://maven.xwiki.org/{}/org/xwiki/platform/xwiki-platform-distribution-flavor-jetty-hsqldb/'
        '{}/xwiki-platform-distribution-flavor-jetty-hsqldb-{}.{}')
        # Make a distinction between SNAPSHOTS and releases
        category = 'snapshots' if version.endswith('-SNAPSHOT') else 'releases'

        return baseURL.format(category, version, version, extension)

    def getArchiveBaseName(self, version):
        return 'xwiki-platform-distribution-flavor-jetty-hsqldb-{}'.format(version)

    # Generate the file name used for a given version
    def getArchiveName(self, version):
        return '{}.zip'.format(self.getArchiveBaseName(version))

    # Generate the file path used for a given version
    def getArchivePath(self, version):
        return '{}/{}'.format(Environment.dataDir, self.getArchiveName(version))

    # Download the given version
    def download(self, version):
        # First, check that we have a version already registered
        self.logger.debug('Downloading version : {}'.format(version))
        self.logger.debug('Downloaded versions : {}'.format(self.configManager.versions()))
        if version in self.configManager.versions():
            self.logger.info('The version {} is already downloaded, skipping.'.format(version))
        else:
            zipDownloadURL = self.__generateDownloadLink(version, 'zip')
            md5DownloadURL = self.__generateDownloadLink(version, 'zip.md5')

            try:
                # Test if we don't get a 404 error or something similar
                self.logger.debug('Testing url [{}]'.format(md5DownloadURL))
                urllib.request.urlopen(md5DownloadURL)

                # Actually download the archive
                self.logger.info('Downloading XWiki {} archive ...'.format(version))
                archive = urllib.request.urlretrieve(zipDownloadURL, self.getArchivePath(version))

                # Mark the instance as present in the instance repository
                self.configManager.versions().append(version)
                self.configManager.persist()

                self.logger.info('Version {} successfully downloaded!'.format(version))
            except urllib.error.HTTPError as e:
                self.logger.debug('Gotten error {}'.format(e))
                self.logger.error('The url [{}] is either unaccessible or unavailable'.format(md5DownloadURL))
                self.logger.warning('Skipping version {}'.format(version))

class InstanceManager:
    logger = logging.getLogger('InstanceManager')

    def __init__(self, configManager, versionManager):
        self.configManager = configManager
        self.versionManager = versionManager

    def getInstancePath(self, instanceName):
        return '{}/{}'.format(Environment.instancesDir, instanceName)

    def create(self, instanceName, version):
        # Check if the name is not already taken
        if instanceName in [instance['name'] for instance in self.configManager.instances()]:
            self.logger.error('An instance with name {} already exists. Aborting.'.format(instanceName))
            return

        # First, check if we have the corresponding version
        if version not in self.configManager.versions():
            self.logger.info('Version {} not in the local repository ; downloading it ...'.format(version))
            self.versionManager.download(version)

        # Now we are sure to have a version available.
        # Get the file and unzip it
        instanceFinalPath = self.getInstancePath(instanceName)
        self.logger.debug('Unzipping version in {}'.format(instanceFinalPath))
        zipRef = zipfile.ZipFile(self.versionManager.getArchivePath(version), 'r')
        zipRef.extractall(Environment.instancesDir)
        zipRef.close()
        os.rename('{}/{}'.format(Environment.instancesDir, self.versionManager.getArchiveBaseName(version)),
                instanceFinalPath)

        # Mark the execution scripts executable
        os.chmod('{}/start_xwiki.sh'.format(instanceFinalPath), 0o755)
        os.chmod('{}/start_xwiki_debug.sh'.format(instanceFinalPath), 0o755)
        os.chmod('{}/stop_xwiki.sh'.format(instanceFinalPath), 0o755)

        # Update the configuration to record the new instance
        self.configManager.instances().append({'name': instanceName, 'version': version})
        self.configManager.persist()

        self.logger.info('Instance {} created in {}'.format(instanceName, instanceFinalPath))

    def start(self, instanceName, debug=False):
        startScript = 'start_xwiki_debug.sh' if debug else 'start_xwiki.sh'

        try:
            subprocess.call(['{}/./{}'.format(self.getInstancePath(instanceName), startScript)])
        except KeyboardInterrupt as e:
            self.logger.debug('Instance has been killed.')

    def remove(self, instanceName):
        # Get the corresponding instance dict in the structureself.
        instanceStruct = None
        for instance in self.configManager.instances():
            if instance['name'] == instanceName:
                instanceStruct = instance

        # Let's first check if we indeed have an instance with that name
        if instanceStruct is not None:
            self.logger.info('Removing instance {} ...'.format(instanceName))
            shutil.rmtree(self.getInstancePath(instanceName))
            self.configManager.instances().remove(instanceStruct)
            self.configManager.persist()
        else:
            self.logger.error('No instance exists with the name [{}]. Skipping.'.format(instanceName))
