import glob
import logging
import os
import shutil
import subprocess
import time

from environment import Environment
import packaging.version

from utils import compute_checksum
from utils import random_chars


class InstanceManager:
    logger = logging.getLogger('InstanceManager')

    def __init__(self, configManager, versionManager):
        self.configManager = configManager
        self.versionManager = versionManager

    def getInstancePath(self, instanceName):
        return '{}/{}'.format(Environment.instancesDir, instanceName)

    def list(self):
        # Sort the instances by version
        sortedInstances = sorted(self.configManager.instances(), key=lambda x: packaging.version.parse(x['version']))
        currentVersion = None
        for instance in sortedInstances:
            if currentVersion is None or currentVersion != instance['version']:
                print('{}:'.format(instance['version']))
                currentVersion = instance['version']
            print('  - {}'.format(instance['name']))

    def linkInstanceToVersion(self, instanceName, instancePath, versionPath):
        self.logger.info('Symlinking the instance [{}] in order to reduce storage space'.format(instanceName))
        # Go through each file that is present in the instancePath and that has a linkable extension ;
        # Check if an equivalent exists in the versionPath.
        # If an equivalent exists and has the same md5sum, remove the jar from the instance and replace it with a
        # symlink to the version
        absoluteInstancePath = os.path.abspath(instancePath)
        for linkableFileExtension in self.configManager.get('linkableFileExtensions'):
            for file in glob.glob('{}/**/*.{}'.format(instancePath, linkableFileExtension), recursive=True):
                if not os.path.isdir(file):
                    # Compute the file absolute
                    absoluteFilePath = os.path.abspath(file)
                    relativeFilePath = absoluteFilePath[len(absoluteInstancePath)+1:]
                    versionFilePath = '{}/{}'.format(versionPath, relativeFilePath)

                    if (os.path.exists(versionFilePath)
                            and (compute_checksum(absoluteFilePath) == compute_checksum(versionFilePath))):
                        # Replace the file
                        self.logger.debug('Replacing file [{}] with symlink to [{}]'
                                          .format(absoluteFilePath, versionFilePath))
                        os.remove(absoluteFilePath)
                        os.symlink(versionFilePath, absoluteFilePath)

    def symlink(self, instanceName):
        instance = self.configManager.getInstance(instanceName)
        if (instance is None):
            self.logger.error('The instance with name [{}] does not exist.', instanceName)
        else:
            self.versionManager.ensureVersion(instance['version'])
            self.linkInstanceToVersion(instanceName,
                                       self.getInstancePath(instanceName),
                                       self.versionManager.getDirectoryPath(instance['version']))
            self.logger.info('The instance with name [{}] has been symlinked'.format(instanceName))

    def create(self, instanceName, version):
        # Check if the name is not already taken
        if instanceName in [instance['name'] for instance in self.configManager.instances()]:
            self.logger.error('An instance with name [{}] already exists. Aborting.'.format(instanceName))
            return

        # First, check if we have the corresponding version
        self.versionManager.ensureVersion(version)

        # Now we are sure to have a version available.
        # Get the file and unzip it
        instancePath = self.getInstancePath(instanceName)
        versionPath = self.versionManager.getDirectoryPath(version)
        shutil.copytree(versionPath, instancePath)
        if self.configManager.get('linkInstanceStorage'):
            self.linkInstanceToVersion(instanceName, instancePath, versionPath)

        # Update the configuration to record the new instance
        self.configManager.instances().append({'name': instanceName, 'version': version})
        self.configManager.persist()

        self.logger.info('Instance {} created in {}'.format(instanceName, instancePath))

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

    def __startInstance(self, instanceName, port=None, debug=False):
        startScript = 'start_xwiki_debug.sh' if debug else 'start_xwiki.sh'

        # Check if the instance exists
        instancePath = self.getInstancePath(instanceName)
        if os.path.isdir(instancePath):
            processArgs = ['{}/./{}'.format(instancePath, startScript)]
            if port is not None:
                processArgs.append('-p')
                processArgs.append(port)

            with subprocess.Popen(processArgs) as instanceProcess:
                try:
                    while instanceProcess.poll() is None:
                        time.sleep(5)
                    self.logger.debug('Instance has terminated by itself with return code : [{}]'
                                      .format(instanceProcess.poll()))
                except KeyboardInterrupt as interrupt:
                    self.logger.debug('Interrupt [{}] recieved, terminating the instance ...'.format(interrupt))
                    instanceProcess.terminate()
                    try:
                        # Give 10 seconds for the instance to stop, else, kill it
                        instanceProcess.wait(10)
                    except subprocess.TimeoutExpired:
                        self.logger.debug('Failed to terminate within 10 seconds, killing the instance ...')
                        instanceProcess.kill()

                    returnCode = instanceProcess.poll()
                    if returnCode is None:
                        self.logger.error('Failed to kill the instance.')
                    else:
                        self.logger.debug('Instance return code : [{}]'.format(returnCode))
        else:
            self.logger.error('The instance [{}] folder does not exists.'.format(instanceName))

    def start(self, entityName, port=None, debug=False, temp=False):
        # In case debug mode is forced by the config, force it
        debug = debug or self.configManager.get('debug')
        self.logger.debug('Instance debug mode : [{}]'.format(debug))

        # Check if the instance name exists
        if entityName in [i['name'] for i in self.configManager.instances()]:
            self.__startInstance(entityName, port, debug)
        else:
            # Check that the entityName is a version
            if entityName in self.configManager.versions():
                # Generate a temporary instance id
                instanceName = 'xtool-{}'.format(random_chars(4))
                self.create(instanceName, entityName)
                self.__startInstance(instanceName, port, debug)
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
