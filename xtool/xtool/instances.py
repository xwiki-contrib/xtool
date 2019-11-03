import binascii
import logging
import os
import shutil
import subprocess
import zipfile

from environment import Environment

from utils import random_chars


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

    def extractVersion(self, version, instancePath):
        self.logger.debug('Unzipping version in {}'.format(instancePath))
        zipRef = zipfile.ZipFile(self.versionManager.getArchivePath(version), 'r')
        zipRef.extractall(Environment.instancesDir)
        zipRef.close()

        os.rename('{}/{}'.format(Environment.instancesDir,
                                 self.versionManager.getArchiveBaseName(version)), instancePath)

        # Mark the execution scripts executable
        os.chmod('{}/start_xwiki.sh'.format(instancePath), 0o755)
        os.chmod('{}/start_xwiki_debug.sh'.format(instancePath), 0o755)
        os.chmod('{}/stop_xwiki.sh'.format(instancePath), 0o755)

    def create(self, instanceName, version):
        # Check if the name is not already taken
        if instanceName in [instance['name'] for instance in self.configManager.instances()]:
            self.logger.error('An instance with name {} already exists. Aborting.'.format(instanceName))
            return

        # First, check if we have the corresponding version
        self.versionManager.ensureVersion(version)

        # Now we are sure to have a version available.
        # Get the file and unzip it
        instanceFinalPath = self.getInstancePath(instanceName)
        self.extractVersion(version, instanceFinalPath)

        # Update the configuration to record the new instance
        self.configManager.instances().append({'name': instanceName, 'version': version})
        self.configManager.persist()

        self.logger.info('Instance {} created in {}'.format(instanceName, instanceFinalPath))

    def edit(self, instanceName, fileName):
        # Try first to determine the editor that we will have to use
        # If we have something defined in the configuration, then use it
        editor = self.configManager.get('editor')
        if editor is None:
            # Second case : if we don't have anything set in the configuration, use the environment
            if 'EDITOR' in os.environ.keys():
                editor = os.environ['EDITOR']
            else:
                # Finally, use "editor" as the default
                editor = "editor"

        instancePath = self.getInstancePath(instanceName)
        subprocess.call([editor, '{}/webapps/xwiki/WEB-INF/{}'.format(instancePath, fileName)])

    def copy(self, instanceName, newInstanceName):
        # Verify that the instance exists
        matchingInstances = [i for i in self.configManager.instances() if i['name'] == instanceName]

        if len(matchingInstances) == 1:
            # Verify that no instance exists with the new name
            matchingNewInstances = ([i for i in self.configManager.instances()
                if i['name'] == newInstanceName])

            if len(matchingNewInstances) == 0:
                self.logger.info('Creating copy of [{}] with name [{}] ...'
                    .format(instanceName, newInstanceName))
                shutil.copytree(self.getInstancePath(instanceName),
                    self.getInstancePath(newInstanceName))

                self.configManager.instances().append(
                    {'name': newInstanceName, 'version': matchingInstances[0]['version']})
                self.configManager.persist()
            else:
                self.logger.error('An instance with name [{}] already exists'.fomat(newInstanceName))
        else:
            self.logger.error('The instance name [{}] is invalid'.format(instanceName))

    def __startInstance(self, instanceName, debug=False):
        startScript = 'start_xwiki_debug.sh' if debug else 'start_xwiki.sh'

        try:
            # Check if the instance exists
            instancePath = self.getInstancePath(instanceName)
            if os.path.isdir(instancePath):
                subprocess.call(['{}/./{}'.format(instancePath, startScript)])
            else:
                self.logger.error('The instance [{}] folder does not exists.'.format(instanceName))
        except KeyboardInterrupt:
            self.logger.debug('Instance has been killed.')

    def start(self, entityName, debug=False, temp=False):
        # In case debug mode is forced by the config, force it
        debug = debug or self.configManager.get('debug')
        self.logger.debug('Instance debug mode : [{}]'.format(debug))

        # Check if the instance name exists
        if entityName in [i['name'] for i in self.configManager.instances()]:
            self.__startInstance(entityName, debug)
        else:
            # Check that the entityName is a version
            if entityName in self.configManager.versions():
                # Generate a temporary instance id
                instanceName = 'xtool-{}'.format(random_chars(4))
                self.create(instanceName, entityName)
                self.__startInstance(instanceName, debug)
                if temp:
                    self.remove(instanceName)
            else:
                self.logger.error('The entity name [{}] is invalid'.format(entityName))

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
