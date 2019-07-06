import logging
import os
import shutil
import subprocess
import zipfile

from configuration import Environment


class InstanceManager:
    logger = logging.getLogger('InstanceManager')

    def __init__(self, configManager, versionManager):
        self.configManager = configManager
        self.versionManager = versionManager

    def getInstancePath(self, instanceName):
        return '{}/{}'.format(Environment.instancesDir, instanceName)

    def list(self):
        rowFormat = '{:<25}| {:<25}'
        print(rowFormat.format('Name', 'Version'))
        for instance in self.configManager.instances():
            print(rowFormat.format(instance['name'], instance['version']))

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
        os.rename('{}/{}'.format(Environment.instancesDir,
                                 self.versionManager.getArchiveBaseName(version)),
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
            # Check if the instance exists
            instancePath = self.getInstancePath(instanceName)
            if os.path.isdir(instancePath):
                subprocess.call(['{}/./{}'.format(instancePath, startScript)])
            else:
                self.logger.error('The instance [{}] does not exists.'.format(instanceName))
        except KeyboardInterrupt:
            self.logger.debug('Instance has been killed.')

    def remove(self, instanceName):
        # Get the corresponding instance dict in the structures.
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
